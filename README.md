# README.md

## YouTube Video Downloader

This is a YouTube Video Downloader built with Python using the `yt_dlp` library for downloading videos and audio from YouTube. It has a graphical user interface (GUI) built with Tkinter.

## Features

- Download videos and audio from YouTube
- Combine video and audio files into a single file
- Download entire YouTube playlists
- User-friendly GUI with progress bar and status updates
- Supports pasting URLs from the clipboard
- Social media links for easy access

## Requirements

- Python 3.x
- Required Python libraries:
  - `yt-dlp==2024.5.27`
  - `pillow==10.3.0`
- Other Required:
  - `yt_dlp`
  - `tkinter`
  - `Pillow`
  - `uuid`
  - `subprocess`
  - `re`
  - `sys`
  - `webbrowser`
  - `time`
  - `os`
  - `threading`
  - `tkinter.ttk`

## Installation

1. Clone the repository:

```sh
git clone https://github.com/ExaellaSS/YouTube_Video_Downloader.git
```

2. Navigate to the project directory:

```sh
cd YouTube_Video_Downloader
```

3. Install the required libraries:

```sh
pip install -r requirements.txt
```

## Building the Executable

You can build the executable using PyInstaller with the provided spec file.

1. Ensure you have PyInstaller installed:

```sh
pip install pyinstaller
```

2. Run PyInstaller with the spec file:

```sh
pyinstaller YouTube_Video_Downloader.spec
```

This will create a `dist` directory with the executable.

## Usage

1. Run the `youtube_downloader.py` script:

```sh
python youtube_downloader.py
```

2. Enter YouTube video URLs (one per line) in the text box.

3. Click the "Paste URLs" button to paste URLs from your clipboard.

4. Click the "Clear" button to remove links from the form.

5. Click the "Download" button to start downloading the videos and audio.

6. The progress bar and status label will show the current status of the download process.

7. Once the download is complete, the video and audio files will be combined and saved to the specified download path.

## GUI Elements

- **URL Entry**: A text box to enter YouTube video URLs (one per line).
- **Paste URLs Button**: A button to paste URLs from the clipboard.
- **Download Button**: A button to start the download process.
- **Exit Button**: A button to exit the application.
- **Progress Bar**: A progress bar to show the download progress.
- **Status Label**: A label to show the current status of the download process.
- **Social Media Icons**: Buttons to open VK, Telegram, and GitHub pages.

## Code Overview

- `clear_previous_files(video_file, audio_file)`: Removes previous files if they exist.
- `progress_hook(d, progress_var, status_var, current_status)`: Updates the progress bar and status label during the download process.
- `download_youtube_video(url, progress_var, status_var)`: Downloads video and audio from YouTube.
- `sanitize_filename(filename)`: Removes illegal characters from the filename.
- `get_unique_filename(path)`: Ensures the filename is unique.
- `combine_video_audio(video_path, audio_path, output_path, status_var)`: Combines video and audio files into a single file.
- `download_and_combine(urls, progress_var, status_var)`: Downloads and combines multiple videos and audio files.
- `download_youtube_playlist(url, progress_var, status_var)`: Downloads all videos from a YouTube playlist.
- `start_sequential_download(urls)`: Starts the sequential download process for multiple URLs.
- `on_download_click()`: Handles the download button click event.
- `on_exit_click()`: Handles the exit button click event.
- `on_paste_click()`: Handles the paste button click event.
- `center_window(window)`: Centers the main window on the screen.
- `open_vk()`, `open_telegram()`, `open_github()`: Opens the respective social media pages.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [yt_dlp](https://github.com/yt-dlp/yt-dlp) for the YouTube downloading functionality.
- [Tkinter](https://docs.python.org/3/library/tkinter.html) for the GUI.
- [Pillow](https://python-pillow.org/) for handling images.
- [FFmpeg](https://ffmpeg.org/) for combining video and audio files.

## Contact

For any questions or suggestions, please contact [ExaellaSS](https://github.com/ExaellaSS).
