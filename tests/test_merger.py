import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

import switch_video_merger as merger


class ParseFilenameTimeTestCase(unittest.TestCase):
    def test_parses_switch_filename(self):
        self.assertEqual(
            merger.parse_filename_time("2026042920170100_s.mp4"),
            datetime(2026, 4, 29, 20, 17, 1),
        )

    def test_rejects_unparseable_name(self):
        self.assertIsNone(merger.parse_filename_time("garbage_s.mp4"))


class ConcatEscapeTestCase(unittest.TestCase):
    def test_escapes_single_quotes(self):
        self.assertEqual(merger._concat_escape("it's"), "it'\\''s")

    def test_leaves_plain_paths_alone(self):
        self.assertEqual(merger._concat_escape("/tmp/a b/c.mp4"), "/tmp/a b/c.mp4")


class GroupVideosTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def _make(self, name):
        (self.dir / name).touch()

    def test_consecutive_clips_form_single_batch(self):
        self._make("2026042916000000_s.mp4")
        self._make("2026042916000005_s.mp4")
        with mock.patch(
            "switch_video_merger.probe_duration",
            side_effect=lambda p: 2.0,
        ):
            batches = merger.group_videos(self.dir)

        self.assertEqual(len(batches), 1)
        self.assertEqual(len(batches[0]), 2)

    def test_gap_beyond_max_gap_splits_batches(self):
        self._make("2026042916000000_s.mp4")  # ends 16:00:02
        self._make("2026042916010000_s.mp4")  # starts 16:01:00, gap 58s > 32
        with mock.patch(
            "switch_video_merger.probe_duration",
            side_effect=lambda p: 2.0,
        ):
            batches = merger.group_videos(self.dir, max_gap=32)

        self.assertEqual(len(batches), 2)

    def test_gap_within_max_gap_stays_together(self):
        self._make("2026042916000000_s.mp4")  # ends 16:00:02
        self._make("2026042916002000_s.mp4")  # starts 16:00:20, gap 18s <= 32
        with mock.patch(
            "switch_video_merger.probe_duration",
            side_effect=lambda p: 2.0,
        ):
            batches = merger.group_videos(self.dir, max_gap=32)

        self.assertEqual(len(batches), 1)

    def test_isolates_unparseable_filenames(self):
        self._make("garbage_s.mp4")
        self._make("2026042916000000_s.mp4")
        self._make("2026042916000005_s.mp4")
        with mock.patch(
            "switch_video_merger.probe_duration",
            side_effect=lambda p: 2.0,
        ):
            batches = merger.group_videos(self.dir)

        self.assertEqual(len(batches), 2)
        self.assertEqual(batches[0][0].name, "garbage_s.mp4")
        self.assertEqual([v.name for v in batches[1]], [
            "2026042916000000_s.mp4",
            "2026042916000005_s.mp4",
        ])

    def test_sorts_videos_chronologically(self):
        self._make("2026042916000005_s.mp4")
        self._make("2026042916000000_s.mp4")
        with mock.patch(
            "switch_video_merger.probe_duration",
            side_effect=lambda p: 2.0,
        ):
            batches = merger.group_videos(self.dir)

        self.assertEqual(
            [v.name for v in batches[0]],
            ["2026042916000000_s.mp4", "2026042916000005_s.mp4"],
        )

    def test_ignores_non_capture_files(self):
        self._make("2026042916000000_s.mp4")
        (self.dir / "notes.txt").touch()
        with mock.patch(
            "switch_video_merger.probe_duration",
            side_effect=lambda p: 2.0,
        ):
            batches = merger.group_videos(self.dir)

        self.assertEqual(len(batches), 1)
        self.assertEqual(len(batches[0]), 1)


if __name__ == "__main__":
    unittest.main()