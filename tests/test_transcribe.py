import os
import tempfile
import unittest

import transcribe


def _run(source, translation):
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "source.srt")
        trans = os.path.join(tmp, "translation.srt")
        with open(src, "w", encoding="utf-8") as f:
            f.write(source)
        with open(trans, "w", encoding="utf-8") as f:
            f.write(translation)
        return transcribe.transcribe_srt(src, trans)


def _block(index, timing, text):
    return f"{index}\n{timing}\n{text}"


class TranscribeTestCase(unittest.TestCase):
    def test_replaces_text_by_index(self):
        source = _block(1, "00:00:01,000 --> 00:00:02,000", "Hello")
        translation = _block(1, "00:00:00,800 --> 00:00:02,100", "Bonjour")
        expected = _block(1, "00:00:01,000 --> 00:00:02,000", "Bonjour")

        self.assertEqual(_run(source, translation), expected + "\n")

    def test_keeps_source_timings(self):
        source = _block(1, "00:01:30,000 --> 00:01:35,500", "Hello")
        translation = _block(1, "00:00:00,000 --> 00:00:05,000", "Bonjour")

        result = _run(source, translation)
        self.assertIn("00:01:30,000 --> 00:01:35,500", result)
        self.assertNotIn("00:00:00,000 --> 00:00:05,000", result)

    def test_matches_despite_multiline_source_text(self):
        source = _block(2, "00:00:03,000 --> 00:00:04,000", "line one\nline two")
        translation = _block(2, "00:00:03,000 --> 00:00:04,000", "une seule ligne")

        self.assertEqual(_run(source, translation), _block(2, "00:00:03,000 --> 00:00:04,000", "une seule ligne") + "\n")

    def test_keeps_original_text_when_index_missing(self):
        source = _block(5, "00:00:05,000 --> 00:00:06,000", "keep me")
        translation = _block(1, "00:00:01,000 --> 00:00:02,000", "other")

        self.assertEqual(_run(source, translation), source + "\n")

    def test_matches_by_index_even_when_translation_is_reordered(self):
        source = (
            _block(1, "00:00:01,000 --> 00:00:02,000", "A") + "\n\n"
            + _block(2, "00:00:03,000 --> 00:00:04,000", "B")
        )
        translation = (
            _block(2, "00:00:03,500 --> 00:00:04,000", "Y") + "\n\n"
            + _block(1, "00:00:00,000 --> 00:00:02,000", "X")
        )
        expected = (
            _block(1, "00:00:01,000 --> 00:00:02,000", "X") + "\n\n"
            + _block(2, "00:00:03,000 --> 00:00:04,000", "Y")
        )

        self.assertEqual(_run(source, translation), expected + "\n")

    def test_preserves_utf8_text(self):
        source = _block(1, "00:00:01,000 --> 00:00:02,000", "La chèvre")
        translation = _block(1, "00:00:01,000 --> 00:00:02,000", "L'élève a dit « ça »")

        self.assertEqual(_run(source, translation), _block(1, "00:00:01,000 --> 00:00:02,000", "L'élève a dit « ça »") + "\n")


if __name__ == "__main__":
    unittest.main()