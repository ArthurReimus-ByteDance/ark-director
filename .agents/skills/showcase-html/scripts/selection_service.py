import contextlib
import datetime
import fcntl
import hashlib
import io
import json
import os
import re
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError


class SelectionError(ValueError):
    pass


class SelectionConflict(SelectionError):
    pass


def contained_path(root, relative, must_exist=True):
    if not isinstance(relative, str) or not relative or '\\' in relative:
        raise SelectionError('Expected a nonempty project-relative path')
    value = Path(relative)
    if value.is_absolute() or '..' in value.parts:
        raise SelectionError(f'Path must remain inside the project: {relative}')
    path = root / value
    if not path.resolve().is_relative_to(root.resolve()):
        raise SelectionError(f'Symlink escapes the project: {relative}')
    if must_exist and not path.is_file():
        raise SelectionError(f'Missing file: {relative}')
    return path


def parse_frontmatter(text):
    match = re.match(r'\A---(\r?\n)(.*?)(\r?\n)---(?=\r?\n|$)(.*)\Z', text, re.DOTALL)
    if not match:
        raise SelectionError('Expected YAML frontmatter enclosed by --- lines')
    yaml = YAML(typ='rt')
    yaml.preserve_quotes = True
    yaml.width = 4096
    try:
        document = yaml.load((match[2] + match[3]).replace('\r\n', '\n'))
    except YAMLError as error:
        raise SelectionError(f'Unsupported or invalid YAML: {error}') from error
    if not isinstance(document, Mapping):
        raise SelectionError('Frontmatter must be a mapping')
    if re.search(r'(^|\s)[&*][\w-]+', match[2]):
        raise SelectionError('Selection editing does not support YAML anchors or aliases; expand them explicitly first')
    return yaml, document, match


def edited_manifest(text, meta, filename):
    yaml, document, match = parse_frontmatter(text)
    field = meta.get('field', 'selected_variant')
    if field == 'selected_variants':
        key = meta.get('key')
        if not isinstance(key, str) or not key.strip():
            raise SelectionError('selected_variants requires a nonempty key')
        if field not in document:
            document[field] = {}
        if not isinstance(document[field], Mapping):
            raise SelectionError('selected_variants must be a mapping')
        document[field][key] = filename
    elif field == 'selected_variant':
        if isinstance(document.get(field), (Mapping, list)):
            raise SelectionError('selected_variant must be a scalar')
        document[field] = filename
    else:
        raise SelectionError(f'Unsupported selection field: {field}')
    output = io.StringIO()
    yaml.dump(document, output)
    newline = match[1]
    frontmatter = output.getvalue().rstrip('\n').replace('\n', newline)
    return '---' + newline + frontmatter + newline + '---' + match[4]


def collect_selectable(data):
    registry: dict[str, dict[str, Any]] = {}
    if not isinstance(data, dict) or not isinstance(data.get('sections'), list):
        raise SelectionError('showcase.json requires a sections array')
    targets: dict[tuple[str, str, str | None], str] = {}
    for section in data['sections']:
        cards = section.get('cards', [])
        if section.get('kind') == 'takes':
            cards = [take for group in section.get('groups', []) for take in group.get('takes', [])]
        for card in cards:
            if not card.get('id') and not card.get('manifest'):
                continue
            asset_id = card.get('id')
            if not isinstance(asset_id, str) or not asset_id or not card.get('manifest'):
                raise SelectionError('Selectable cards require a string id and manifest')
            source = card.get('media', {}).get('src')
            if not isinstance(source, str) or not source:
                raise SelectionError(f'{asset_id}: selectable cards require media.src')
            filename = card.get('filename', Path(source).name)
            if filename != Path(source).name or not isinstance(filename, str):
                raise SelectionError(f'{asset_id}: filename must match media basename')
            meta = {'manifest': card['manifest'], 'field': card.get('field', 'selected_variant'), 'key': card.get('key')}
            if meta['field'] not in ('selected_variant', 'selected_variants'):
                raise SelectionError(f'{asset_id}: unsupported selection field')
            if meta['field'] == 'selected_variants' and (not isinstance(meta['key'], str) or not meta['key']):
                raise SelectionError(f'{asset_id}: selected_variants requires key')
            target = (meta['manifest'], meta['field'], meta['key'])
            if target in targets and targets[target] != asset_id:
                raise SelectionError(f'{asset_id}: manifest selection target belongs to another id')
            targets[target] = asset_id
            if asset_id in registry:
                if any(registry[asset_id][key] != value for key, value in meta.items()):
                    raise SelectionError(f'{asset_id}: inconsistent variant metadata')
            else:
                registry[asset_id] = {**meta, 'variants': {}}
            existing = registry[asset_id]['variants'].get(filename)
            if existing and existing != source:
                raise SelectionError(f'{asset_id}: duplicate filename maps to different media')
            registry[asset_id]['variants'][filename] = source
    return registry


def read_selection(registry, root):
    selections = {}
    for asset_id, meta in registry.items():
        path = contained_path(root, meta['manifest'])
        _, document, _ = parse_frontmatter(path.read_bytes().decode('utf-8'))
        value = document.get(meta['field'])
        if meta['field'] == 'selected_variants':
            if value is not None and not isinstance(value, Mapping):
                raise SelectionError(f'{asset_id}: selected_variants must be a mapping')
            value = value.get(meta['key']) if value else None
        if value is not None:
            if not isinstance(value, str):
                raise SelectionError(f'{asset_id}: selected value must be a string')
            selections[asset_id] = value
    return selections


def revision(root, registry):
    hashes = {}
    for meta in registry.values():
        path = contained_path(root, meta['manifest'])
        hashes[meta['manifest']] = hashlib.sha256(path.read_bytes()).hexdigest()
    hashes['registry'] = hashlib.sha256(json.dumps(registry, sort_keys=True).encode()).hexdigest()
    showcase = root / 'showcase.json'
    if showcase.exists():
        hashes['showcase.json'] = hashlib.sha256(contained_path(root, 'showcase.json').read_bytes()).hexdigest()
    return hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()


def validate_selections(root, registry, selections):
    if not isinstance(selections, dict) or not selections:
        raise SelectionError('selections must be a nonempty mapping of asset ids to filenames')
    prepared: dict[str, str] = {}
    for asset_id, filename in selections.items():
        if asset_id not in registry:
            raise SelectionError(f'{asset_id}: not a selectable asset')
        if not isinstance(filename, str) or not filename.strip() or re.search(r'[\\/\r\n]', filename):
            raise SelectionError(f'{asset_id}: invalid filename')
        meta = registry[asset_id]
        if filename not in meta['variants']:
            raise SelectionError(f'{asset_id}: variant is not registered: {filename}')
        contained_path(root, meta['variants'][filename])
        path = contained_path(root, meta['manifest'])
        current = prepared.get(meta['manifest'], path.read_bytes().decode('utf-8'))
        prepared[meta['manifest']] = edited_manifest(current, meta, filename)
    for name in ('selection.json', 'selection.log', '.selection-journal.json', '.selection.lock'):
        contained_path(root, name, must_exist=False)
    return {'registry': registry, 'selections': dict(selections), 'prepared': prepared, 'revision': revision(root, registry)}


def atomic_write(path, content):
    descriptor, temporary = tempfile.mkstemp(prefix='.selection-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if path.exists():
            os.chmod(temporary, path.stat().st_mode & 0o777)
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextlib.contextmanager
def writer_lock(root):
    path = contained_path(root, '.selection.lock', must_exist=False)
    with path.open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def recover_selection(root):
    journal_path = contained_path(root, '.selection-journal.json', must_exist=False)
    if not journal_path.exists():
        return
    try:
        journal = json.loads(journal_path.read_text())
    except (json.JSONDecodeError, UnicodeError) as error:
        raise SelectionConflict('Unreadable selection recovery journal; inspect it before saving') from error
    if not isinstance(journal, dict):
        raise SelectionConflict('Invalid selection recovery journal; inspect it before saving')
    if journal.get('version') != 1 or not isinstance(journal.get('files'), dict):
        raise SelectionConflict('Invalid selection recovery journal; inspect it before saving')
    for relative, entry in journal['files'].items():
        if not isinstance(entry, dict) or not isinstance(entry.get('after'), str) or not (entry.get('before') is None or isinstance(entry['before'], str)):
            raise SelectionConflict('Invalid recovery entry; journal retained for inspection')
        path = contained_path(root, relative, must_exist=False)
        current = path.read_bytes().decode('utf-8') if path.exists() else None
        if current not in (entry['before'], entry['after']):
            raise SelectionConflict(f'Recovery conflicts with a later edit: {relative}; journal retained')
    for relative, entry in journal['files'].items():
        path = contained_path(root, relative, must_exist=False)
        if path.exists() and path.read_bytes().decode('utf-8') == entry['after']:
            continue
        atomic_write(path, entry['after'].encode('utf-8'))
    journal_path.unlink()


def apply_selection_batch(root, batch, expected_revision):
    registry = batch['registry']
    if expected_revision != revision(root, registry):
        raise SelectionConflict('Stale selection revision; reload the page or preview current manifests')
    with writer_lock(root):
        recover_selection(root)
        if expected_revision != revision(root, registry):
            raise SelectionConflict('Stale selection revision; reload before saving')
        batch = validate_selections(root, registry, batch['selections'])
        selected = read_selection(registry, root)
        selected.update(batch['selections'])
        targets = dict(batch['prepared'])
        targets['selection.json'] = json.dumps({'project': root.name, 'selections': selected}, indent=2, ensure_ascii=False) + '\n'
        audit_path = contained_path(root, 'selection.log', must_exist=False)
        audit = audit_path.read_text() if audit_path.exists() else ''
        record = {'ts': datetime.datetime.now(datetime.UTC).isoformat(), 'event': 'save', 'applied': list(batch['selections']), 'selections': batch['selections'], 'total': len(batch['selections']), 'errors': []}
        targets['selection.log'] = audit + json.dumps(record, ensure_ascii=False) + '\n'
        journal: dict[str, Any] = {'version': 1, 'files': {}}
        for relative, after in targets.items():
            path = contained_path(root, relative, must_exist=False)
            journal['files'][relative] = {'before': path.read_bytes().decode('utf-8') if path.exists() else None, 'after': after}
        journal_path = root / '.selection-journal.json'
        atomic_write(journal_path, json.dumps(journal, ensure_ascii=False).encode('utf-8'))
        try:
            recover_selection(root)
        except OSError as error:
            raise SelectionConflict('Selection commit interrupted; recovery journal retained. Retry recovery before further edits') from error
        return {'ok': True, 'applied': list(batch['selections']), 'errors': [], 'revision': revision(root, registry), 'selections': read_selection(registry, root)}


class SelectionService:
    def __init__(self, root, data):
        self.root = Path(root).resolve()
        self.registry = collect_selectable(data)
        self.showcase_hash = self._showcase_hash()

    def _showcase_hash(self):
        path = self.root / 'showcase.json'
        return hashlib.sha256(contained_path(self.root, 'showcase.json').read_bytes()).hexdigest() if path.exists() else None

    def _check_showcase(self):
        if self._showcase_hash() != self.showcase_hash:
            raise SelectionConflict('showcase.json changed; restart the review server before saving')

    def snapshot(self):
        self._check_showcase()
        with writer_lock(self.root):
            recover_selection(self.root)
            return {'selections': read_selection(self.registry, self.root), 'revision': revision(self.root, self.registry)}

    def apply(self, selections, expected_revision=None):
        self._check_showcase()
        batch = validate_selections(self.root, self.registry, selections)
        return apply_selection_batch(self.root, batch, expected_revision or batch['revision'])
