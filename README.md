# [UtilityBox](.)

This is a collection of one-shot scripts that I use to make my life easier. Too simple to warrant a repo of their own, but too useful to not have them somewhere. I hope you find some of them useful too.

(Kinda like a collection of dotfiles, but for scripts.)

## Table of Contents

- [UtilityBox](#utilitybox)
  - [Table of Contents](#table-of-contents)
  - [Requirements](#requirements)
  - [Scripts](#scripts)
  - [Testing](#testing)
  - [Contributing](#contributing)

## Requirements

- Python 3.8+ for the Python scripts.
- [ffmpeg](https://ffmpeg.org/) (with `ffprobe`) for `switch_video_merger.py`.

## Scripts

- [`shift.py`](./shift.py): A python script to shift the time of a subtitle file by a given amount of seconds. Use `-b` to batch-process every `.srt` file in a directory (output mirrors the input layout under `./adjusted`, or a custom `--output-dir`).
- [`transcribe.py`](./transcribe.py): A python script that transcribes a translated SRT file into the timings and indexes of a source SRT file, matching subtitles by index number.
  ```sh
  python3 transcribe.py <source.srt> <translation.srt> <output_dir>
  ```
- [`switch_video_merger.py`](./switch_video_merger.py): Merges consecutive Nintendo Switch screen-capture recordings (`*_s.mp4`) into single files, grouping clips by their filename timestamps.
  ```sh
  python3 switch_video_merger.py [folder]
  ```
- [`restore_permissions.sh`](./restore_permissions.sh): A bash script to restore default directory (`755`) and file (`644`) permissions in a given directory.
  ```sh
  ./restore_permissions.sh <directory>
  ```

## Testing

Run the test suite (stdlib `unittest`, no extra dependencies):

```sh
python3 -m unittest discover -s tests
```

## Contributing

Pull requests are welcome.

Please open an issue to discuss what you'd like to change before making major changes.

Please make sure to update and/or add appropriate tests when applicable.

This project is licensed under the [GPL-3.0 License](./LICENSE).