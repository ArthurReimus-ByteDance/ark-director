import importlib.util
import json
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / '.agents/skills/showcase-html/scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('showcase', SCRIPTS / 'generate_showcase.py')
showcase = importlib.util.module_from_spec(spec)
spec.loader.exec_module(showcase)
import selection_service as selection


class ShowcaseRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.manifest = self.root / 'shot.md'
        self.original = '---\nother:\n  hero: keep.png\nselected_variants:\n  hero: "old.png" # choice\ncustom: |\n  Text\n---\nBody unchanged\n'
        self.manifest.write_text(self.original)
        for name in ('old.png', 'new.png'):
            (self.root / name).write_bytes(b'fixture')
        self.data = {'title': 'Fixture', 'sections': [{'kind': 'grid', 'cards': [
            {'id': 'hero', 'manifest': 'shot.md', 'field': 'selected_variants', 'key': 'hero', 'media': {'src': name, 'type': 'image'}}
            for name in ('old.png', 'new.png')
        ]}]}
        (self.root / 'showcase.json').write_text(json.dumps(self.data))
        self.service = selection.SelectionService(self.root, self.data)

    def files(self):
        return {str(path.relative_to(self.root)): path.read_bytes() for path in self.root.rglob('*') if path.is_file()}

    def test_map_update_preserves_unrelated_fields_comment_quotes_and_body(self):
        result = self.service.apply({'hero': 'new.png'})
        self.assertTrue(result['ok'])
        self.assertIn('other:\n  hero: keep.png', self.manifest.read_text())
        self.assertIn('hero: "new.png" # choice', self.manifest.read_text())
        self.assertIn('custom: |\n  Text', self.manifest.read_text())
        self.assertTrue(self.manifest.read_text().endswith('---\nBody unchanged\n'))
        self.assertEqual(json.loads((self.root / 'selection.json').read_text())['selections'], {'hero': 'new.png'})

    def test_invalid_batches_have_zero_writes(self):
        for values in ([], {}, {'missing': 'new.png'}, {'hero': '../new.png'}, {'hero': 'unregistered.png'}, {'hero': None}, {'hero': 'new.png', 'missing': 'old.png'}):
            with self.subTest(values=values):
                before = self.files()
                with self.assertRaises(selection.SelectionError):
                    self.service.apply(values)
                self.assertEqual(before, self.files())

    def test_stale_revision_rejects_concurrent_edit(self):
        revision = selection.revision(self.root, self.service.registry)
        self.manifest.write_text(self.original.replace('Text', 'Human edit'))
        before = self.files()
        with self.assertRaises(selection.SelectionConflict):
            self.service.apply({'hero': 'new.png'}, revision)
        self.assertEqual(before, self.files())

    def test_outside_paths_and_symlinks_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / 'outside.md'
            target.write_text(self.original)
            (self.root / 'link.md').symlink_to(target)
            for filename in (str(target), '../outside.md', 'link.md'):
                with self.subTest(filename=filename):
                    self.data['sections'][0]['cards'][0]['manifest'] = filename
                    self.data['sections'][0]['cards'][1]['manifest'] = filename
                    service = selection.SelectionService(self.root, self.data)
                    before = self.files()
                    with self.assertRaises(selection.SelectionError):
                        service.apply({'hero': 'new.png'})
                    self.assertEqual(before, self.files())
                    self.assertEqual(target.read_text(), self.original)

    def test_unsupported_or_invalid_yaml_has_zero_writes(self):
        for frontmatter in ('---\nselected_variants: invalid\n---\nBody', '---\nkey: one\nkey: two\n---\nBody', '---\nother: &anchor {hero: old.png}\nselected_variants: *anchor\n---\nBody', 'Body only'):
            with self.subTest(frontmatter=frontmatter):
                self.manifest.write_text(frontmatter)
                before = self.files()
                with self.assertRaises(selection.SelectionError):
                    self.service.apply({'hero': 'new.png'})
                self.assertEqual(before, self.files())

    def test_interrupted_commit_rolls_forward_once_with_audit(self):
        original_write = selection.atomic_write
        calls = []
        def fail_after_first_manifest(path, content):
            calls.append(path.name)
            if path.name == 'selection.json':
                raise OSError('simulated disk error')
            original_write(path, content)
        with patch.object(selection, 'atomic_write', side_effect=fail_after_first_manifest), self.assertRaises(selection.SelectionConflict):
            self.service.apply({'hero': 'new.png'})
        self.assertTrue((self.root / '.selection-journal.json').exists())
        snapshot = self.service.snapshot()
        self.assertEqual(snapshot['selections'], {'hero': 'new.png'})
        self.assertFalse((self.root / '.selection-journal.json').exists())
        self.assertEqual(len((self.root / 'selection.log').read_text().splitlines()), 1)
        self.service.snapshot()
        self.assertEqual(len((self.root / 'selection.log').read_text().splitlines()), 1)

    def test_recovery_preserves_intervening_user_edit(self):
        original = selection.atomic_write
        with patch.object(selection, 'atomic_write', wraps=selection.atomic_write) as writer:
            def interrupted(path, content):
                if path.name == 'selection.json':
                    raise OSError('disk error')
                original(path, content)
            writer.side_effect = interrupted
            with self.assertRaises(selection.SelectionConflict):
                self.service.apply({'hero': 'new.png'})
        self.manifest.write_text(self.original.replace('Text', 'New user edit'))
        with self.assertRaises(selection.SelectionConflict):
            self.service.snapshot()
        self.assertIn('New user edit', self.manifest.read_text())

    def test_takes_registry_is_embedded_in_generated_page(self):
        data = {'title': 'Takes', 'sections': [{'kind': 'takes', 'groups': [{'takes': [{'id': 'shot', 'manifest': 'shot.md', 'filename': 'new.png', 'media': {'src': 'new.png'}}]}]}]}
        output = showcase.generate(self.root, data, 'index.html')
        self.assertIn('"selectableRegistry": {"shot":', output.read_text())
        self.assertEqual(selection.collect_selectable(data)['shot']['variants'], {'new.png': 'new.png'})

    def test_check_fails_without_writing_even_with_contact_sheets(self):
        (self.root / 'new.png').unlink()
        before = self.files()
        result = subprocess.run([sys.executable, str(SCRIPTS / 'generate_showcase.py'), str(self.root), '--check', '--contact-sheets'], check=False, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(before, self.files())

    def test_check_valid_is_read_only(self):
        before = self.files()
        result = subprocess.run([sys.executable, str(SCRIPTS / 'generate_showcase.py'), str(self.root), '--check', '--contact-sheets'], check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, self.files())

    def test_cli_apply_uses_same_validation(self):
        before = self.files()
        result = subprocess.run([sys.executable, str(SCRIPTS / 'generate_showcase.py'), str(self.root), '--apply', '{"hero":"unknown.png"}'], check=False, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(before, self.files())
        result = subprocess.run([sys.executable, str(SCRIPTS / 'generate_showcase.py'), str(self.root), '--apply', '{"hero":"new.png"}'], check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.service.snapshot()['selections'], {'hero': 'new.png'})

    def test_concurrent_writers_reject_second_stale_save(self):
        self.manifest.write_text(self.original.replace("old.png", "earlier.png"))
        revision = selection.revision(self.root, self.service.registry)
        barrier = threading.Barrier(2)
        outcomes = []
        def save(filename):
            barrier.wait()
            try:
                outcomes.append(self.service.apply({'hero': filename}, revision)['ok'])
            except selection.SelectionConflict:
                outcomes.append('conflict')
        workers = [threading.Thread(target=save, args=(filename,)) for filename in ('new.png', 'old.png')]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(5)
            self.assertFalse(worker.is_alive())
        self.assertCountEqual(outcomes, [True, 'conflict'])

    def test_changed_showcase_registry_requires_restart(self):
        (self.root / 'showcase.json').write_text(json.dumps({'sections': []}))
        before = self.files()
        with self.assertRaises(selection.SelectionConflict):
            self.service.apply({'hero': 'new.png'})
        self.assertEqual(before, self.files())

    def test_crlf_body_and_frontmatter_are_preserved(self):
        self.manifest.write_bytes(self.original.replace('\n', '\r\n').encode())
        self.service.apply({'hero': 'new.png'})
        updated = self.manifest.read_bytes()
        self.assertIn(b'hero: "new.png" # choice\r\n', updated)
        self.assertTrue(updated.endswith(b'---\r\nBody unchanged\r\n'))

    def test_corrupt_journal_is_reported_and_preserved(self):
        journal = self.root / '.selection-journal.json'
        for content in ('{broken', '[]', '{"version":1,"files":{"shot.md":null}}'):
            journal.write_text(content)
            with self.assertRaises(selection.SelectionConflict):
                self.service.snapshot()
            self.assertEqual(journal.read_text(), content)
            self.assertEqual(self.manifest.read_text(), self.original)

    def test_title_is_escaped(self):
        output = showcase.generate(self.root, {'title': '</title><script>bad()</script>', 'sections': []}, 'index.html')
        self.assertNotIn('</title><script>bad()', output.read_text())

    def test_audio_codec_uses_probe_evidence(self):
        probe = {'duration': 1, 'size_bytes': 32, 'width': 16, 'height': 16, 'fps': 24, 'codec': 'h264', 'has_audio': True, 'audio_codecs': ['opus']}
        with patch.object(showcase, '_run_ffprobe', return_value=probe):
            self.assertIn('h264 + opus', showcase._ffprobe_chips(self.root / 'new.png'))


if __name__ == '__main__':
    unittest.main()
