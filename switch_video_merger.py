#!/usr/bin/env python3
"""Merge consecutive Nintendo Switch screen-capture recordings into single files."""

import argparse
import logging
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_FOLDER = "./input"
MAX_GAP_SECONDS = 32

log = logging.getLogger("merger")


def parse_filename_time(filename):
    """Extract a datetime from the Switch video filename.

    Example: 2026042920170100_s.mp4 -> 2026-04-29 20:17:01
    """
    time_str = Path(filename).name[:14]
    try:
        return datetime.strptime(time_str, "%Y%m%d%H%M%S")
    except ValueError:
        return None


def probe_duration(path):
    """Return a video's duration in seconds, or None if it can't be determined."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError, OSError) as exc:
        log.warning("Could not determine duration of %s: %s", Path(path).name, exc)
        return None


def group_videos(directory, max_gap=MAX_GAP_SECONDS):
    """Group videos into sequential batches based on start/end timestamps.

    Consecutive recordings belong to the same batch when the gap between the end
    of one clip and the start of the next is at most ``max_gap`` seconds.
    """
    path = Path(directory)
    videos = sorted(
        (f for f in path.glob("*_s.mp4") if f.is_file()),
        key=lambda f: (parse_filename_time(f.name) or datetime.min, f.name),
    )
    if not videos:
        return []

    batches = []
    current_batch = []
    previous_start = None
    previous_end = None
    force_split = False

    for video in videos:
        start = parse_filename_time(video.name)

        if start is None:
            log.warning("Skipping unparseable filename: %s", video.name)
            if current_batch:
                batches.append(current_batch)
            current_batch = [video]
            previous_start = previous_end = None
            force_split = True
            continue

        if force_split:
            if current_batch:
                batches.append(current_batch)
            current_batch = []
            force_split = False
        elif previous_start is not None:
            prev_end = previous_end if previous_end is not None else previous_start
            if (start - prev_end).total_seconds() > max_gap:
                batches.append(current_batch)
                current_batch = []

        current_batch.append(video)
        previous_start = start
        duration = probe_duration(video)
        previous_end = start + timedelta(seconds=duration) if duration is not None else None

    if current_batch:
        batches.append(current_batch)

    return batches


def _concat_escape(value):
    """Escape a path for use inside an ffmpeg concat list file."""
    return value.replace("'", "'\\''")


def process_batch(directory, batch):
    """Merge a batch of videos and move the originals into a sources subfolder."""
    if len(batch) < 2:
        log.info("Skipping isolated video: %s", batch[0].name)
        return

    base_dir = Path(directory)
    final_name = batch[-1].name.removesuffix(".mp4")
    target_folder = base_dir / final_name
    sources_folder = target_folder / "sources"
    final_video_path = target_folder / f"{final_name}.mp4"

    log.info("Processing batch: %s -> %s", batch[0].name, batch[-1].name)

    target_folder.mkdir(parents=True, exist_ok=True)
    sources_folder.mkdir(parents=True, exist_ok=True)

    list_file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, dir=target_folder
    )
    list_file_path = Path(list_file.name)

    merged = False
    try:
        with list_file:
            for video in batch:
                absolute = str((base_dir / video.name).resolve())
                list_file.write(f"file '{_concat_escape(absolute)}'\n")

        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file_path),
            "-c", "copy",
            str(final_video_path),
        ]
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "ffmpeg failed")

        merged = True

        for video in batch:
            destination = sources_folder / video.name
            if destination.exists():
                destination.unlink()
            shutil.move(str(video), str(destination))

        log.info("Success! Merged into %s", final_video_path)
    except Exception as exc:
        log.error("Error merging batch %s: %s", final_name, exc)
        if not merged:
            if final_video_path.exists():
                final_video_path.unlink()
            if sources_folder.exists() and not any(sources_folder.iterdir()):
                shutil.rmtree(target_folder, ignore_errors=True)
    finally:
        list_file_path.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Merge consecutive Nintendo Switch screen captures."
    )
    parser.add_argument(
        "folder", nargs="?", default=DEFAULT_FOLDER,
        help=f"folder containing '*_s.mp4' captures (default: {DEFAULT_FOLDER})",
    )
    parser.add_argument(
        "--max-gap", type=float, default=MAX_GAP_SECONDS,
        help=f"max seconds between the end of one clip and the start of the next "
             f"to keep them in the same batch (default: {MAX_GAP_SECONDS})",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    folder = Path(args.folder)
    if not folder.is_dir():
        parser.error(f"folder does not exist: {folder}")

    for batch in group_videos(folder, args.max_gap):
        process_batch(folder, batch)


if __name__ == "__main__":
    main()
