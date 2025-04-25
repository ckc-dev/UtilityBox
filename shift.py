"""This module provides functions to adjust the timing of SRT subtitles."""

import os
import argparse


def adjust_srt_timing(input_file, time_shift_seconds):
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
            # Parse the SRT time format, e.g., "00:01:23,456 --> 00:01:25,678",
            # extracting and adjusting the timing.
            start, end = line.strip().split(" --> ")

            start_time, start_ms = start.split(",")
            start_seconds = (int(start_time.split(":")[0]) * 3600 +
                             int(start_time.split(":")[1]) * 60 +
                             int(start_time.split(":")[2])) + int(start_ms) / 1000

            end_time, end_ms = end.split(",")
            end_seconds = (int(end_time.split(":")[0]) * 3600 +
                           int(end_time.split(":")[1]) * 60 +
                           int(end_time.split(":")[2])) + int(end_ms) / 1000

            start_seconds += time_shift_seconds
            end_seconds += time_shift_seconds

            # Format the adjusted times back into the SRT format.
            start_time = "{:02d}:{:02d}:{:02d},{:03d}".format(
                int(start_seconds // 3600),
                int((start_seconds % 3600) // 60),
                int(start_seconds % 60),
                int((start_seconds % 1) * 1000)
            )

            end_time = "{:02d}:{:02d}:{:02d},{:03d}".format(
                int(end_seconds // 3600),
                int((end_seconds % 3600) // 60),
                int(end_seconds % 60),
                int((end_seconds % 1) * 1000)
            )

            line = f"{start_time} --> {end_time}\n"

        adjusted_lines.append(line)

    return adjusted_lines


def save_adjusted_srt(output_file, adjusted_lines):
    """
    Save adjusted SRT lines to an output file.

    Parameters:
    - output_file (str): Path to the output SRT file.
    - adjusted_lines (list of str): Adjusted SRT lines.
    """
    with open(output_file, "w", encoding="utf-8") as file:
        file.writelines(adjusted_lines)


def get_output_file_path(input_file, output_dir, suffix):
    """
    Generate output file path using input file, output directory, and suffix.

    Parameters:
    - input_file (str): Path to the input SRT file.
    - output_dir (str): Directory to save the adjusted SRT file.
    - suffix (str): Suffix to be added to the output file name.

    Returns:
    - str: Output file path.
    """
    base_name, extension = os.path.splitext(os.path.basename(input_file))
    output_file = f"{base_name}_{suffix}{extension}"
    return os.path.join(output_dir, output_file)


def main():
    """
    Adjust SRT subtitle timing.

    Parses command-line arguments, processes SRT files,
    and saves adjusted subtitles.
    """
    parser = argparse.ArgumentParser(description="Adjust SRT subtitle timing.")
    parser.add_argument("input", help="Input SRT file or directory")
    parser.add_argument("-s", "--shift", type=float, default=0, help="Time shift in seconds")
    parser.add_argument("-b", "--batch", action="store_true", help="Process all SRT files in the directory")

    args = parser.parse_args()

    input_path = args.input
    time_shift_seconds = args.shift
    batch_mode = args.batch

    if os.path.isdir(input_path):
        if batch_mode:
            for root, dirs, files in os.walk(input_path):
                for file in files:
                    if file.lower().endswith(".srt"):
                        input_file_path = os.path.join(root, file)
                        adjusted_lines = adjust_srt_timing(input_file_path, time_shift_seconds)

                        output_directory = "./adjusted"
                        os.makedirs(output_directory, exist_ok=True)

                        output_file_path = get_output_file_path(input_file_path, output_directory, str(time_shift_seconds))
                        save_adjusted_srt(output_file_path, adjusted_lines)
                        print(f"Adjusted subtitle saved to: {output_file_path}")
        else:
            print("Batch mode not enabled. Use '-b' option to process all SRT files in the directory.")
    elif os.path.isfile(input_path) and input_path.lower().endswith(".srt"):
        adjusted_lines = adjust_srt_timing(input_path, time_shift_seconds)

        output_directory = "./adjusted"
        os.makedirs(output_directory, exist_ok=True)

        output_file_path = get_output_file_path(input_path, output_directory, str(time_shift_seconds))
        save_adjusted_srt(output_file_path, adjusted_lines)
        print(f"Adjusted subtitle saved to: {output_file_path}")
    else:
        print("Invalid input. Please provide a valid SRT file or directory.")


if __name__ == "__main__":
    main()
