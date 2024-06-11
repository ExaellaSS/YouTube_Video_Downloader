### README.md

# YouTube Video Downloader

This is a simple YouTube video downloader built with Python and Tkinter. 
The program allows you to download videos from YouTube by providing a URL. 
It downloads both video and audio streams, combines them into a single file, and saves it to your computer.

~~## Requirements

- Python 3.x
- yt-dlp
- FFmpeg
- Tkinter (usually included with Python installations)

## Installation

1. **Install Python**:
   Make sure you have Python installed on your computer. You can download it from [python.org](https://www.python.org/).

2. **Install yt-dlp**:
   Open a terminal or command prompt and run:
   ```sh
   pip install yt-dlp
   ```

3. **Install FFmpeg**:
   Download and install FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html). Make sure FFmpeg is added to your system's PATH.

## Usage

1. **Run the Program**:
   Save the Python script in a file, e.g., `youtube_downloader.py`. Open a terminal or command prompt, navigate to the directory where you saved the script, and run:
   ```sh
   python youtube_downloader.py
   ```

2. **Enter the YouTube URL**:
   - Copy the URL of the YouTube video you want to download.
   - Paste the URL into the text field in the program.

3. **Download the Video**:
   - Click the "Download" button.
   - The program will display progress bars and status messages as it downloads and combines the video and audio streams.
   - Once the download and combination are complete, a message will be displayed with the location of the saved video file.

4. **Exit the Program**:
   - Click the "Exit" button to close the program. Any temporary files created during the download process will be deleted.~~

## Notes

- Ensure that you have a stable internet connection while using the program.
- If you encounter any issues, make sure that yt-dlp and FFmpeg are correctly installed and accessible from your terminal or command prompt.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

```
YouTubeVideoDownloader/
│
├── youtube_downloader.py
├── youtube_downloader.exe
└── README.md
```
