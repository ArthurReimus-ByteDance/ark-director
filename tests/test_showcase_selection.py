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

    def lifecycle_canvas(self):
        (self.root / 'project.md').write_text('# Project brief\n')
        (self.root / 'prompt_hero.md').write_text('A precise hero image prompt.\n')
        stages = []
        labels = {
            'brief-development': 'Brief and development',
            'scene-breakdown': 'Scene and production breakdown',
            'canon-elements': 'Canon and elements',
            'storyboard-visual-plan': 'Storyboard and visual plan',
            'audio-preparation': 'Audio preparation',
            'shot-generation': 'Shot generation',
            'assembly-review': 'Assembly and review',
            'delivery': 'Delivery',
        }
        for stage_id in showcase.CANVAS_STAGE_IDS:
            stage = {'id': stage_id, 'label': labels[stage_id], 'status': 'pending', 'sources': []}
            if stage_id == 'brief-development':
                stage.update({'status': 'active', 'sources': [{'path': 'project.md', 'kind': 'brief'}]})
            stages.append(stage)
        return {
            'title': 'Lifecycle canvas fixture',
            'canvas': {'currentStage': 'brief-development', 'stages': stages},
            'sections': [{
                'id': 'concepts',
                'title': 'Concepts',
                'stage': 'brief-development',
                'kind': 'grid',
                'cards': [{
                    'type': 'elem',
                    'media': {'type': 'image', 'src': 'new.png'},
                    'promptFile': 'prompt_hero.md',
                    'refs': [{'name': 'Hero canon', 'role': '@Image 1', 'kind': 'img', 'path': 'old.png'}],
                }],
            }],
        }

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

    def test_lifecycle_canvas_embeds_prompts_and_detects_stale_sources(self):
        data = self.lifecycle_canvas()
        (self.root / 'showcase.json').write_text(json.dumps(data))
        output = showcase.generate(self.root, data, 'index.html', expected_stage='brief-development')
        embedded = showcase.embedded_showcase_data(output)
        self.assertEqual(embedded['canvasBuild']['currentStage'], 'brief-development')
        self.assertEqual(embedded['sections'][0]['cards'][0]['prompt'], 'A precise hero image prompt.\n')
        self.assertEqual(embedded['canvas']['stages'][0]['counts']['media'], 2)
        self.assertEqual(embedded['canvas']['stages'][0]['counts']['prompts'], 1)
        self.assertEqual(showcase.canvas_sync_errors(data, self.root, output, 'brief-development'), [])
        (self.root / 'prompt_hero.md').write_text('A changed prompt.\n')
        self.assertIn('stale', showcase.canvas_sync_errors(data, self.root, output, 'brief-development')[0])

    def test_lifecycle_canvas_requires_ordered_stages_and_expected_checkpoint(self):
        data = self.lifecycle_canvas()
        data['canvas']['stages'].pop()
        errors = showcase.canvas_validation_errors(data, self.root, 'canon-elements')
        self.assertTrue(any('stage mismatch' in error.lower() for error in errors))
        self.assertTrue(any('all eight production stages' in error for error in errors))

    def test_lifecycle_canvas_requires_prompt_files_and_reference_paths(self):
        data = self.lifecycle_canvas()
        card = data['sections'][0]['cards'][0]
        card['prompt'] = (self.root / 'prompt_hero.md').read_text()
        del card['promptFile']
        del card['refs'][0]['path']
        errors = showcase.canvas_validation_errors(data, self.root, 'brief-development')
        self.assertTrue(any('require promptFile' in error for error in errors))
        self.assertTrue(any('reference requires' in error for error in errors))

    def test_stage_check_is_read_only_and_rejects_stale_html(self):
        data = self.lifecycle_canvas()
        (self.root / 'showcase.json').write_text(json.dumps(data))
        missing_stage = subprocess.run([
            sys.executable,
            str(SCRIPTS / 'generate_showcase.py'),
            str(self.root),
        ], check=False, capture_output=True, text=True)
        self.assertNotEqual(missing_stage.returncode, 0)
        self.assertIn('require --stage', missing_stage.stderr)
        generate = subprocess.run([
            sys.executable,
            str(SCRIPTS / 'generate_showcase.py'),
            str(self.root),
            '--stage',
            'brief-development',
        ], check=False, capture_output=True, text=True)
        self.assertEqual(generate.returncode, 0, generate.stderr)
        before = self.files()
        check = subprocess.run([
            sys.executable,
            str(SCRIPTS / 'generate_showcase.py'),
            str(self.root),
            '--check',
            '--stage',
            'brief-development',
        ], check=False, capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stderr)
        self.assertEqual(before, self.files())
        (self.root / 'project.md').write_text('# Changed project brief\n')
        stale = subprocess.run([
            sys.executable,
            str(SCRIPTS / 'generate_showcase.py'),
            str(self.root),
            '--check',
            '--stage',
            'brief-development',
        ], check=False, capture_output=True, text=True)
        self.assertNotEqual(stale.returncode, 0)
        self.assertIn('stale', stale.stdout)

    def test_init_creates_canvas_once_without_overwriting(self):
        (self.root / 'showcase.json').unlink()
        (self.root / 'project.md').write_text('# New project\n')
        command = [
            sys.executable,
            str(SCRIPTS / 'generate_showcase.py'),
            str(self.root),
            '--init',
        ]
        first = subprocess.run(command, check=False, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        data = json.loads((self.root / 'showcase.json').read_text())
        self.assertEqual(data['canvas']['currentStage'], 'brief-development')
        self.assertEqual(len(data['canvas']['stages']), 8)
        original = (self.root / 'showcase.json').read_bytes()
        second = subprocess.run(command, check=False, capture_output=True, text=True)
        self.assertNotEqual(second.returncode, 0)
        self.assertEqual((self.root / 'showcase.json').read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
