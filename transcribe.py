"""This module transcribes a translated SRT file into the timings and indexes of a source SRT file."""

import os
import argparse
import re

# Read first .srt file:
def read_srt_file(file_path):
    """
    Read the contents of an SRT file and return it as a list of lines.
    """
    with open(file_path, "r", encoding="latin-1") as file:
        lines = file.readlines()
    return lines

# Write to a new .srt file:
def write_srt_file(file_path, lines):
    """
    Write the given lines to an SRT file.
    """
    with open(file_path, "w", encoding="latin-1") as file:
        file.writelines(lines)

def clean_up_srt_file(file_path):
    regex = re.compile(r"(?P<index>\d+)\s*(?P<timing>\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3})\s*(?P<text>.*\n?.*)")
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    cleaned_lines = []
    matches = regex.finditer("".join(lines))
    for match in matches:
        index = match.group("index")
        timing = match.group("timing")
        text = match.group("text").replace("\n", " ").strip()
        cleaned_lines.append(f"{index}\n{timing}\n{text}\n\n")
    return "".join(cleaned_lines).strip() + "\n"

def export_cleaned_srt(file_path, cleaned_lines):
    """
    Export the cleaned SRT lines to a new file.
    """
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(cleaned_lines)


def __main__():
    parser = argparse.ArgumentParser(description="Transcribe SRT files.")
    parser.add_argument("source", type=str, help="Path to the source SRT file.")
    parser.add_argument("translation", type=str, help="Path to the translated SRT file.")
    parser.add_argument("output_dir", type=str, help="Directory to save the output SRT file.")
    parser.add_argument("--suffix", type=str, default="_transcribed", help="Suffix for the output file name.")
    args = parser.parse_args()

    source_file = args.source
    translation_file = args.translation
    output_dir = args.output_dir
    suffix = args.suffix

    # Read the source and translation SRT files
    source_lines = read_srt_file(source_file)
    translation_lines = read_srt_file(translation_file)

    # Transcribe the translated text into the source SRT file timings and indexes:
    i = 0
    while i < len(source_lines):
        if source_lines[i].strip().isdigit():
            # This is a subtitle index line
            index = source_lines[i].strip()
            i += 1
            # This is a timecode line
            timecode = source_lines[i].strip()
            i += 1
            # This is the subtitle text line
            text = source_lines[i].strip()

            # Find the corresponding translation line
            if i < len(translation_lines):
                translation_text = translation_lines[i]
                # Replace the text with the translated text
                source_lines[i] = translation_text
        else:
            i += 1

    # Check if the output directory exists, if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Output directory created: {output_dir}")
    else:
        print(f"Output directory already exists: {output_dir}")

    # Write the transcribed lines to a new SRT file
    output_file = os.path.join(output_dir, os.path.basename(source_file).replace(".srt", f"{suffix}.srt"))
    write_srt_file(output_file, source_lines)
    print(f"Transcribed SRT file saved to: {output_file}")

if __name__ == "__main__":
    __main__()
