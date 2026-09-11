#!/usr/bin/env python3
"""This module transcribes a translated SRT file into the timings and indexes of a source SRT file."""

import argparse
import os


def read_srt_file(file_path):
    """Read the contents of an SRT file and return it as a list of lines."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.readlines()


def parse_srt_blocks(lines):
    """Parse SRT lines into a list of (index, timing, text) tuples.

    Blocks are separated by blank lines. ``text`` may span multiple lines
    and is joined into a single string.
    """
    blocks = []
    index = None
    timing = None
    text = []

    def flush_block():
        if timing is not None:
            blocks.append((index, timing, "\n".join(text)))
        return None, None, []

    for raw in lines:
        line = raw.rstrip("\n")
        if " --> " in line:
            timing = line
        elif line.isdigit():
            index = line
        elif line:
            text.append(line)
        else:
            index, timing, text = flush_block()

    flush_block()
    return blocks


def transcribe_srt(source_path, translation_path):
    """Return source SRT content with text replaced by the matching translation.

    Text is matched by subtitle index number, so the source and translated
    files do not need to share the same line layout.
    """
    translation = {
        str(index): text
        for index, timing, text in parse_srt_blocks(read_srt_file(translation_path))
        if index is not None
    }

    output_blocks = []
    for index, timing, text in parse_srt_blocks(read_srt_file(source_path)):
        if index is not None and index in translation:
            text = translation[index]
        output_blocks.append("\n".join(part for part in (index, timing, text) if part is not None))

    return "\n\n".join(output_blocks) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Transcribe SRT files.")
    parser.add_argument("source", type=str, help="Path to the source SRT file.")
    parser.add_argument("translation", type=str, help="Path to the translated SRT file.")
    parser.add_argument("output_dir", type=str, help="Directory to save the output SRT file.")
    parser.add_argument("--suffix", type=str, default="_transcribed", help="Suffix for the output file name.")
    args = parser.parse_args()

    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Output directory created: {output_dir}")
    else:
        print(f"Output directory already exists: {output_dir}")

    output_file = os.path.join(
        output_dir,
        f"{os.path.splitext(os.path.basename(args.source))[0]}{args.suffix}.srt",
    )
    transcribed = transcribe_srt(args.source, args.translation)
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(transcribed)
    print(f"Transcribed SRT file saved to: {output_file}")


if __name__ == "__main__":
    main()