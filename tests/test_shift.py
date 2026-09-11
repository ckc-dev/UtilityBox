import tempfile
import unittest

import shift


class TimestampTestCase(unittest.TestCase):
    def test_parse_timestamp(self):
        self.assertEqual(shift.parse_timestamp("00:01:02,500"), 62.5)
        self.assertEqual(shift.parse_timestamp("01:00:00,000"), 3600.0)

    def test_format_timestamp(self):
        self.assertEqual(shift.format_timestamp(3661.125), "01:01:01,125")
        self.assertEqual(shift.format_timestamp(62.5), "00:01:02,500")

    def test_format_timestamp_clamps_at_zero(self):
        self.assertEqual(shift.format_timestamp(-5), "00:00:00,000")

    def test_format_timestamp_round_trip(self):
        self.assertEqual(
            shift.parse_timestamp(shift.format_timestamp(3661.125)),
            3661.125,
        )


class OutputFilenameTestCase(unittest.TestCase):
    def test_output_filename(self):
        self.assertEqual(shift.output_filename("ep01.srt", "-1.5"), "ep01_-1.5.srt")
        self.assertEqual(shift.output_filename("ep02.srt", "1"), "ep02_1.srt")


class AdjustSrtTimingTestCase(unittest.TestCase):
    def test_adjust_forward(self):
        with tempfile.NamedTemporaryFile("w", suffix=".srt", encoding="utf-8", delete=False) as f:
            f.write("1\n00:00:01,000 --> 00:00:03,000\nHello\n")
            path = f.name
        self.addCleanup(lambda: __import__("os").unlink(path))

        lines = shift.adjust_srt_timing(path, 2.0)
        self.assertEqual(lines[1], "00:00:03,000 --> 00:00:05,000\n")
        self.assertEqual(lines[2], "Hello\n")

    def test_adjust_backwards_clamps_at_zero(self):
        with tempfile.NamedTemporaryFile("w", suffix=".srt", encoding="utf-8", delete=False) as f:
            f.write("1\n00:00:01,000 --> 00:00:03,000\nHello\n")
            path = f.name
        self.addCleanup(lambda: __import__("os").unlink(path))

        lines = shift.adjust_srt_timing(path, -5.0)
        self.assertEqual(lines[1], "00:00:00,000 --> 00:00:00,000\n")

    def test_adjust_leaves_non_timing_lines_untouched(self):
        with tempfile.NamedTemporaryFile("w", suffix=".srt", encoding="utf-8", delete=False) as f:
            f.write("1\n00:00:01,000 --> 00:00:03,000\nHello\n\n2\n")
            path = f.name
        self.addCleanup(lambda: __import__("os").unlink(path))

        lines = shift.adjust_srt_timing(path, 1.0)
        self.assertEqual(lines[0], "1\n")
        self.assertEqual(lines[3], "\n")
        self.assertEqual(lines[4], "2\n")


if __name__ == "__main__":
    unittest.main()