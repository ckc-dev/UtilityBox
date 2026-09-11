#!/usr/bin/env python3
"""This module provides functions to adjust the timing of SRT subtitles."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_timestamp(timestamp: str) -> float:
    """Parse an SRT timestamp ('HH:MM:SS,mmm') into seconds as a float."""
    time_part, ms_part = timestamp.split(",")
    hours, minutes, seconds = (int(part) for part in time_part.split(":"))
    return hours * 3600 + minutes * 60 + seconds + int(ms_part) / 1000


def format_timestamp(seconds: float) -> str:
    """Format a number of seconds as an SRT timestamp, clamped at zero.

    The value is rounded to the nearest millisecond before decomposition, so
    fractional shifts cannot produce artifacts like ``,1000``.
    """
    seconds = max(0, seconds)
    total_ms = round(seconds * 1000)
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    sec, ms = divmod(rem, 1_000)
    return f"{hours:02d}:{minutes:02d}:{sec:02d},{ms:03d}"


def adjust_srt_timing(input_file: str, time_shift_seconds: float) -> list[str]:
    """
    Adjust the timing of subtitles in an SRT file.

    Parameters:
    - input_file (str): Path to the input SRT file.
    - time_shift_seconds (float): Time shift in seconds.

    Returns:
    - list of str: Adjusted SRT lines.
    """
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    adjusted_lines = []
    for line in lines:
        if " --> " in line:
            start, end = line.strip().split(" --> ")
            start_seconds = parse_timestamp(start) + time_shift_seconds
            end_seconds = parse_timestamp(end) + time_shift_seconds
            line = f"{format_timestamp(start_seconds)} --> {format_timestamp(end_seconds)}\n"
        adjusted_lines.append(line)

    return adjusted_lines


def save_adjusted_srt(output_file: str, adjusted_lines: list[str]) -> None:
    """
    Save adjusted SRT lines to an output file.

    Parameters:
    - output_file (str): Path to the output SRT file.
    - adjusted_lines (list of str): Adjusted SRT lines.
    """
    with open(output_file, "w", encoding="utf-8") as file:
        file.writelines(adjusted_lines)


def output_filename(input_name: str, suffix: str) -> str:
    """
    Generate an output file name from the input file name and a suffix.
    """
    path = Path(input_name)
    return f"{path.stem}_{suffix}{path.suffix}"


def adjust_file(input_file: Path, output_file: Path, time_shift_seconds: float) -> None:
    """Adjust one SRT file's timing and save it to ``output_file``."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    save_adjusted_srt(output_file, adjust_srt_timing(input_file, time_shift_seconds))
    print(f"Adjusted subtitle saved to: {output_file}")


def main(argv: list[str] | None = None) -> None:
    """
    Adjust SRT subtitle timing.

    Parses command-line arguments, processes SRT files,
    and saves adjusted subtitles.
    """
    parser = argparse.ArgumentParser(description="Adjust SRT subtitle timing.")
    parser.add_argument("input", help="Input SRT file or directory")
    parser.add_argument("-s", "--shift", type=float, default=0, help="Time shift in seconds")
    parser.add_argument("-b", "--batch", action="store_true", help="Process all SRT files in the directory")
    parser.add_argument("-o", "--output-dir", default="./adjusted", help="Directory to save adjusted SRT files (default: %(default)s)")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    suffix = "{:g}".format(args.shift)

    if input_path.is_dir():
        if not args.batch:
            print("Batch mode not enabled. Use '-b' option to process all SRT files in the directory.")
            return
        for src in sorted(input_path.rglob("*.srt")):
            if not src.is_file():
                continue
            rel_dir = src.relative_to(input_path).parent
            output_path = Path(args.output_dir) / rel_dir / output_filename(src.name, suffix)
            adjust_file(src, output_path, args.shift)
    elif input_path.is_file() and input_path.suffix.lower() == ".srt":
        output_path = Path(args.output_dir) / output_filename(input_path.name, suffix)
        adjust_file(input_path, output_path, args.shift)
    else:
        print("Invalid input. Please provide a valid SRT file or directory.")


if __name__ == "__main__":
    main()