### README.md

# YouTube Video Downloader

YouTube Video Downloader is a simple desktop application that allows you to download YouTube videos and their audio tracks, combine them, and save the output as a single file.

## Features

- Download video and audio separately from YouTube
- Combine video and audio into a single file
- Easy-to-use graphical interface

## Requirements

- Python 3.6+
- yt-dlp
- ffmpeg

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/youtube-video-downloader.git
    cd youtube-video-downloader
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Download and install [ffmpeg](https://ffmpeg.org/download.html), and make sure `ffmpeg` is in your system PATH.

## Usage

### Running the Application

To run the application, use the following command:

```bash
python youtube_downloader.py
```

### Creating an Executable

If you prefer to distribute the application as an executable file, follow these steps:

1. Make sure you have [PyInstaller](https://www.pyinstaller.org/) installed:
    ```bash
    pip install pyinstaller
    ```

2. Place the `ffmpeg` executable in `ffmpeg/bin/ffmpeg.exe` and your icon file in `resources/icon.ico`.

3. Create the executable using the provided spec file:
    ```bash
    pyinstaller --onefile youtube_downloader.spec
    ```

### Pre-built Executable

If you don't want to compile the executable yourself, you can download the pre-built executable from [here](https://example.com/your-executable-download-link).

## How to Use the Application

1. Open the application.
2. Enter the YouTube video URL in the provided input field.
3. Click "Paste URL" to paste a URL from your clipboard.
4. Click "Download" to start downloading the video and audio.
5. The application will display progress and status updates.
6. Once the download and combination are complete, the output file will be saved to your Downloads folder.

## Contributing

If you want to contribute to this project, feel free to fork the repository and submit pull requests. 

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```
