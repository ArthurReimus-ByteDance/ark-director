import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave
from array import array
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DUBBING = ROOT / '.agents/skills/audio-dubbing/scripts'
SPLITTING = ROOT / '.agents/skills/audio-split/scripts'


def media_duration(path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'json', str(path)], capture_output=True, text=True, check=True,
    )
    return float(json.loads(result.stdout)['format']['duration'])


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'ffmpeg and ffprobe required')
class AudioToolsTests(unittest.TestCase):
    media_directory: tempfile.TemporaryDirectory[str]
    source: Path
    video: Path

    @classmethod
    def setUpClass(cls):
        cls.media_directory = tempfile.TemporaryDirectory(prefix='audio-regression-source-')
        cls.source = Path(cls.media_directory.name) / 'source.wav'
        subprocess.run(
            ['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
             'anullsrc=r=44100:cl=stereo', '-t', '60.5', str(cls.source)], check=True,
        )
        cls.video = Path(cls.media_directory.name) / 'video.mp4'
        subprocess.run(
            ['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
             'color=c=black:s=32x32:r=25', '-t', '2', '-an',
             '-c:v', 'mpeg4', str(cls.video)], check=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.media_directory.cleanup()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='audio-regression-')
        self.addCleanup(self.directory.cleanup)
        self.work = Path(self.directory.name)

    def audio(self, duration, name='input.wav'):
        target = self.work / name
        subprocess.run(
            ['ffmpeg', '-v', 'error', '-i', str(self.source), '-t', str(float(duration)), str(target)],
            check=True,
        )
        return target

    def run_script(self, name, *arguments, env=None):
        directory = SPLITTING if name == 'split_segments.sh' else DUBBING
        return subprocess.run(
            ['/bin/bash', str(directory / name), *map(str, arguments)],
            capture_output=True, text=True, cwd=self.work, env=env, timeout=60, check=False,
        )

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_mix_treats_shell_substitutions_quotes_spaces_and_colons_as_literal_paths(self):
        source = self.audio('.2', 'voice$(touch injected) \' quote:part.wav')
        output = self.work / 'result `touch other`.wav'
        result = self.run_script('mix_segments.sh', '1.125', output, f'{source}:125')
        self.assert_success(result)
        self.assertFalse((self.work / 'injected').exists())
        self.assertFalse((self.work / 'other').exists())
        self.assertAlmostEqual(media_duration(output), 1.125, places=4)

    def test_mix_rejects_invalid_numbers_without_creating_output(self):
        source = self.audio('.2')
        for duration, offset in [('0', '0'), ('nan', '0'), ('1;touch injected', '0'),
                                 ('1', '-1'), ('1', 'NaN'), ('1', '0|0;anull')]:
            with self.subTest(duration=duration, offset=offset):
                output = self.work / 'invalid.wav'
                result = self.run_script('mix_segments.sh', duration, output, f'{source}:{offset}')
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())

    def test_mix_validates_all_numeric_values_before_running_media_tools(self):
        source = self.audio('0.2')
        binaries = self.work / 'bin'
        binaries.mkdir()
        (binaries / 'python3').symlink_to(sys.executable)
        dirname = shutil.which('dirname')
        assert dirname is not None
        (binaries / 'dirname').symlink_to(dirname)
        for name in ('ffmpeg', 'ffprobe'):
            executable = binaries / name
            executable.write_text('#!/bin/sh\nprintf called > media-tool-called\nexit 1\n')
            executable.chmod(0o755)
        environment = dict(os.environ, PATH=str(binaries))
        result = self.run_script('mix_segments.sh', '1', self.work / 'output.wav',
                                 f'{source}:0', f'{source}:1;anull', env=environment)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.work / 'media-tool-called').exists())

    def test_mix_does_not_execute_filename_shell_substitution(self):
        source = self.audio('0.2', 'voice$(touch injected).wav')
        result = self.run_script('mix_segments.sh', '1', self.work / 'output.wav', f'{source}:0')
        self.assertFalse((self.work / 'injected').exists())
        self.assert_success(result)

    def test_mix_preserves_overlap_levels_and_pads_silence(self):
        source = self.work / 'constant.wav'
        with wave.open(str(source), 'wb') as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(44100)
            audio.writeframes(array('h', [3000] * 4410).tobytes())
        output = self.work / 'mixed.wav'
        self.assert_success(self.run_script('mix_segments.sh', '0.2', output, f'{source}:0', f'{source}:50'))
        with wave.open(str(output), 'rb') as audio:
            self.assertEqual(audio.getnchannels(), 2)
            samples = array('h', audio.readframes(audio.getnframes()))
        first = samples[int(.025 * 44100) * 2]
        overlap = samples[int(.075 * 44100) * 2]
        self.assertGreater(first, 1000)
        self.assertAlmostEqual(overlap / first, 2, delta=.01)
        self.assertEqual(samples[int(.18 * 44100) * 2], 0)

    def test_mix_rejects_missing_audio_stream_and_missing_file(self):
        for source in [self.video, self.work / 'missing.wav']:
            with self.subTest(source=source):
                result = self.run_script('mix_segments.sh', '1', self.work / 'output.wav', f'{source}:0')
                self.assertNotEqual(result.returncode, 0)

    def test_missing_executable_reports_required_dependency(self):
        source = self.audio('.2')
        binaries = self.work / 'bin'
        binaries.mkdir()
        (binaries / 'python3').symlink_to(sys.executable)
        dirname = shutil.which('dirname')
        assert dirname is not None
        (binaries / 'dirname').symlink_to(dirname)
        environment = dict(os.environ, PATH=str(binaries))
        result = self.run_script('mix_segments.sh', '1', self.work / 'output.wav', f'{source}:0', env=environment)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ffmpeg is required', result.stderr + result.stdout)

    def test_split_fractional_boundaries_obey_encoded_mp3_limit(self):
        for duration in ['29.999', '30', '30.001', '30.5', '60.5']:
            with self.subTest(duration=duration):
                source = self.audio(duration, f'source-{duration}.wav')
                output = self.work / f'split-{duration}'
                result = self.run_script('split_segments.sh', '-i', source, '-o', output, '-m', '30')
                self.assert_success(result)
                clips = list(output.glob('seg*.mp3'))
                self.assertTrue(clips)
                for clip in clips:
                    self.assertLessEqual(media_duration(clip), 30)
                    self.assertLessEqual(clip.stat().st_size, 10_000_000)

    def test_split_overlap_stays_inside_encoded_limit(self):
        output = self.work / 'overlap'
        result = self.run_script('split_segments.sh', '-i', self.source, '-o', output,
                                 '-m', '30', '--overlap', '2')
        self.assert_success(result)
        for clip in output.glob('seg*.mp3'):
            self.assertLessEqual(media_duration(clip), 30)
        manifest = (output / 'manifest.txt').read_text()
        self.assertIn('offset=', manifest)

    def test_subtitle_table_uses_actual_manifest_offsets_with_overlap(self):
        subtitle = self.work / 'script.srt'
        subtitle.write_text('1\n00:00:28,500 --> 00:00:29,000\nAn overlap line.\n')
        output = self.work / 'timed'
        self.assert_success(self.run_script('split_segments.sh', self.source, output,
                                            '-m', '30', '--overlap', '2', '-s', subtitle, '--wav'))
        result = subprocess.run([sys.executable, str(SPLITTING / 'srt_timestamps.py'),
                                 'table', str(subtitle), '--manifest', str(output / 'manifest.txt')],
                                capture_output=True, text=True, check=False)
        self.assert_success(result)
        self.assertIn('[28.5s:29.0s] An overlap line.', result.stdout)
        self.assertIn('[0.5s:1.0s] An overlap line.', result.stdout)

    def test_split_rejects_empty_audio_and_malformed_subtitles(self):
        empty = self.work / 'empty.wav'
        empty.touch()
        result = self.run_script('split_segments.sh', empty, self.work / 'empty-output', '-m', '30')
        self.assertNotEqual(result.returncode, 0)
        malformed = self.work / 'invalid.srt'
        malformed.write_text('1\nnot a timestamp\nwords\n')
        result = self.run_script('split_segments.sh', self.source, self.work / 'invalid-subtitles', '-m', '30', '-s', malformed)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('malformed subtitle', result.stderr)

    def test_split_subtitle_crossing_cutoff_preserves_cue_and_limits(self):
        subtitle = self.work / 'script.srt'
        subtitle.write_text('1\n00:00:29,000 --> 00:00:33,000\nA complete line.\n')
        output = self.work / 'subtitles'
        result = self.run_script('split_segments.sh', self.source, output, '-m', '30', '-s', subtitle)
        self.assert_success(result)
        manifest = (output / 'manifest.txt').read_text()
        self.assertIn('offset=29s', manifest)
        for clip in output.glob('seg*.mp3'):
            self.assertLessEqual(media_duration(clip), 30)

    def test_split_rejects_unsatisfiable_subtitle_limits_and_leaves_no_outputs(self):
        subtitle = self.work / 'script.srt'
        subtitle.write_text('1\n00:00:00,000 --> 00:00:40,000\nA long continuous line.\n')
        output = self.work / 'subtitles'
        result = self.run_script('split_segments.sh', self.source, output, '-m', '30', '-s', subtitle)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('subtitle', (result.stderr + result.stdout).lower())
        self.assertFalse((output / 'manifest.txt').exists())
        self.assertEqual(list(output.glob('seg*')), [])

    def test_split_rejects_invalid_cut_order_options_and_overlap(self):
        cases = [('20', '10'), ('20', '20'), ('nan',), ('-n', '0'),
                 ('-m', '0'), ('-m', '30', '-n', '3'), ('-m', '30', '--overlap', '30')]
        for index, arguments in enumerate(cases):
            with self.subTest(arguments=arguments):
                result = self.run_script('split_segments.sh', self.source, self.work / f'invalid-{index}', *arguments)
                self.assertNotEqual(result.returncode, 0)

    def test_split_enforces_actual_byte_limit_and_preserves_existing_files(self):
        source = self.audio('.5')
        output = self.work / 'small'
        output.mkdir()
        existing = output / 'seg1.wav'
        existing.write_text('unrelated existing file')
        result = self.run_script('split_segments.sh', source, output, '--wav', '-m', '30', '--max-bytes', '100')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('actual encoded size', result.stderr)
        self.assertEqual(existing.read_text(), 'unrelated existing file')
        self.assertFalse((output / 'manifest.txt').exists())

    def test_generic_split_keeps_long_user_requested_clips(self):
        output = self.work / 'generic'
        result = self.run_script('split_segments.sh', self.source, output, '40', '--wav')
        self.assert_success(result)
        self.assertAlmostEqual(media_duration(output / 'seg1.wav'), 40, places=4)

    def test_reference_mode_rejects_oversized_explicit_clips(self):
        result = self.run_script('split_segments.sh', self.source, self.work / 'reference', '40', '--reference', '--wav')
        self.assertNotEqual(result.returncode, 0)

    def test_mux_uses_video_duration_and_preserves_similarly_named_files(self):
        source_audio = self.audio('1', 'original.wav')
        generated = self.audio('.25', 'voice.wav')
        sentinel = self.work / '_padded_voice.wav'
        sentinel.write_text('keep this file')
        output = self.work / 'dub.mp4'
        result = self.run_script('verify_and_mux.sh', source_audio, generated, self.video, output)
        self.assert_success(result)
        self.assertAlmostEqual(media_duration(output), 2, delta=.1)
        self.assertEqual(sentinel.read_text(), 'keep this file')
        metadata = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(output)],
                                  capture_output=True, text=True, check=True)
        self.assertEqual([stream['codec_type'] for stream in json.loads(metadata.stdout)['streams']], ['video', 'audio'])

    def test_mux_trims_long_audio_and_supports_concurrent_runs(self):
        generated = self.audio('3')
        def run(index):
            output = self.work / f'dub-{index}.mp4'
            result = self.run_script('verify_and_mux.sh', self.source, generated, self.video, output)
            self.assert_success(result)
            self.assertAlmostEqual(media_duration(output), 2, delta=.1)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(run, range(2)))
        self.assertEqual(list(self.work.glob('.audio-mux-*')), [])

    def test_mux_rejects_missing_stream_before_overwriting_output(self):
        generated = self.audio('.2')
        output = self.work / 'existing.mp4'
        output.write_text('keep this output')
        result = self.run_script('verify_and_mux.sh', self.source, generated, self.source, output)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_text(), 'keep this output')


if __name__ == '__main__':
    unittest.main()
