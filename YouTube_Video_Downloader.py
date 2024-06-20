import os
import threading
import re
import sys
import uuid
import time
import webbrowser
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.core.clipboard import Clipboard
from kivy.uix.scrollview import ScrollView
import yt_dlp as youtube_dl

SAVE_PATH = "D:\\Download" #"/storage/emulated/0/Download"
stop_event = threading.Event()
last_progress = 0
real_download_started = False
lock = threading.Lock()

class YouTubeDownloaderApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10)
        
        self.url_input = TextInput(hint_text='Enter YouTube video URLs (one per line)', size_hint=(1, 0.3))
        self.layout.add_widget(self.url_input)
        
        self.progress_bar = ProgressBar(max=100, size_hint=(1, 0.1))
        self.layout.add_widget(self.progress_bar)
        
        self.status_label = Label(text='Status: Ready', size_hint=(1, 0.1))
        self.layout.add_widget(self.status_label)
        
        button_layout = BoxLayout(size_hint=(1, 0.1))
        
        self.download_button = Button(text='Download', on_press=self.on_download_click)
        button_layout.add_widget(self.download_button)
        
        self.clear_button = Button(text='Clear', on_press=self.on_clear_click)
        button_layout.add_widget(self.clear_button)
        
        self.paste_button = Button(text='Paste', on_press=self.on_paste_click)
        button_layout.add_widget(self.paste_button)
        
        self.layout.add_widget(button_layout)
        
        return self.layout

    def on_download_click(self, instance):
        urls = self.url_input.text.strip().split("\n")
        if not urls:
            self.show_error("Error", "URL list cannot be empty. Please enter valid URLs.")
            return
        
        self.progress_bar.value = 0
        self.status_label.text = "Status: Ready"
        
        stop_event.clear()
        
        thread = threading.Thread(target=self.start_sequential_download, args=(urls,))
        thread.start()

    def on_clear_click(self, instance):
        self.url_input.text = ""

    def on_paste_click(self, instance):
        current_text = self.url_input.text.strip()
        new_text = Clipboard.paste()
        if current_text:
            self.url_input.text += "\n" + new_text
        else:
            self.url_input.text = new_text

    def show_error(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.8))
        popup.open()

    def start_sequential_download(self, urls):
        for url in urls:
            if stop_event.is_set():
                break
            if "playlist" in url:
                self.download_youtube_playlist(url)
            else:
                self.download_and_combine([url])
        if not stop_event.is_set():
            self.status_label.text = "\nAll downloads completed."
        self.progress_bar.value = 0

    def download_youtube_playlist(self, url):
        try:
            self.status_label.text = "\nFetching playlist info..."
            self.root.update_idletasks()

            ydl_opts = {
                'extract_flat': True,
                'skip_download': True,
                'quiet': True,
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(url, download=False)
            
            if 'entries' in result:
                video_urls = [entry['url'] for entry in result['entries']]
                self.download_and_combine(video_urls)
            else:
                self.status_label.text = "Error: No videos found in playlist."
        except Exception as e:
            if not stop_event.is_set():
                self.status_label.text = f"Error: {e}"
            self.root.update_idletasks()

    def download_and_combine(self, urls):
        for url in urls:
            if stop_event.is_set():
                break
            self.progress_bar.value = 0
            video_path, audio_path, video_title = self.download_youtube_video(url)
            if video_path and audio_path:
                sanitized_title = self.sanitize_filename(video_title)
                output_path = os.path.join(SAVE_PATH, f'{sanitized_title}.mp4')
                self.combine_video_audio(video_path, audio_path, output_path)
        if not stop_event.is_set():
            self.status_label.text = "\nAll downloads completed."
        self.progress_bar.value = 0

    def download_youtube_video(self, url):
        if stop_event.is_set():
            return None, None, None
        try:
            self.status_label.text = "Downloading video..."
            self.progress_bar.value = 0
            
            unique_id = uuid.uuid4().hex
            video_filename = f'video_{unique_id}.%(ext)s'
            audio_filename = f'audio_{unique_id}.%(ext)s'
            
            with lock:
                video_opts = {
                    'format': 'bestvideo',
                    'outtmpl': os.path.join(SAVE_PATH, video_filename),
                    'progress_hooks': [self.progress_hook]
                }
                with youtube_dl.YoutubeDL(video_opts) as ydl:
                    info_dict = ydl.extract_info(url, download=False)
                    video_ext = info_dict['ext']
                    ydl.download([url])
            
            time.sleep(5)
            
            if stop_event.is_set():
                return None, None, None
            
            self.status_label.text = "Downloading audio..."
            self.progress_bar.value = 0
            
            with lock:
                audio_opts = {
                    'format': 'bestaudio',
                    'outtmpl': os.path.join(SAVE_PATH, audio_filename),
                    'progress_hooks': [self.progress_hook]
                }
                with youtube_dl.YoutubeDL(audio_opts) as ydl:
                    info_dict = ydl.extract_info(url, download=False)
                    audio_ext = info_dict['ext']
                    ydl.download([url])
            
            video_file_path = os.path.join(SAVE_PATH, f'video_{unique_id}.{video_ext}')
            audio_file_path = os.path.join(SAVE_PATH, f'audio_{unique_id}.{audio_ext}')
            
            if not os.path.exists(video_file_path) or os.path.getsize(video_file_path) == 0:
                self.status_label.text = "Error: Video file not found or is empty."
                self.progress_bar.value = 0
                return None, None, None
            
            if not os.path.exists(audio_file_path) or os.path.getsize(audio_file_path) == 0:
                self.status_label.text = "Error: Audio file not found or is empty."
                self.progress_bar.value = 0
                return None, None, None
            
            return video_file_path, audio_file_path, info_dict['title']
        except Exception as e:
            if not stop_event.is_set():
                self.status_label.text = f"Error: {e}"
            self.progress_bar.value = 0
            return None, None, None

    def sanitize_filename(self, filename):
        return re.sub(r'[\\/*?:"<>|]', "", filename)

    def get_unique_filename(self, path):
        base, ext = os.path.splitext(path)
        counter = 1
        new_path = path
        while os.path.exists(new_path):
            new_path = f"{base}_{counter}{ext}"
            counter += 1
        return new_path

    def combine_video_audio(self, video_path, audio_path, output_path):
        if stop_event.is_set():
            return
        try:
            self.status_label.text = "\nCombining video and audio..."
            
            output_path = self.get_unique_filename(output_path)
            
            command = [
                'ffmpeg',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-strict', 'experimental',
                output_path
            ]
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print("FFmpeg command:", ' '.join(command))
            print("FFmpeg stdout:", result.stdout)
            print("FFmpeg stderr:", result.stderr)

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                self.status_label.text = f"Combined video saved to: {output_path}"
                print(f"Combined video saved to: {output_path}")
            else:
                self.status_label.text = "Error: Output file is empty or not created."
                print("Error: Output file is empty or not created.")
            
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except subprocess.CalledProcessError as e:
            if not stop_event.is_set():
                self.status_label.text = f"Error: {e}"
            print("FFmpeg stdout:", e.stdout)
            print("FFmpeg stderr:", e.stderr)
        finally:
            self.progress_bar.value = 0

    def progress_hook(self, d):
        global last_progress, real_download_started
        if d['status'] == 'downloading':
            if 'fragment_index' in d and 'fragment_count' in d:
                current_progress = (d['fragment_index'] / d['fragment_count']) * 100
                real_download_started = True
            elif 'downloaded_bytes' in d and 'total_bytes' in d and d['total_bytes'] is not None:
                current_progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                real_download_started = True
            elif 'downloaded_bytes' in d and 'total_bytes_estimate' in d and d['total_bytes_estimate'] is not None:
                current_progress = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                real_download_started = True
            else:
                current_progress = last_progress
            
            if real_download_started and current_progress > last_progress:
                self.progress_bar.value = current_progress
                last_progress = current_progress
                self.status_label.text = f"Downloading... {current_progress:.2f}%"
        elif d['status'] == 'finished':
            if real_download_started:
                self.progress_bar.value = 100
            last_progress = 0
            real_download_started = False
            self.status_label.text = "Download completed."
        self.root.update_idletasks()

if __name__ == '__main__':
    YouTubeDownloaderApp().run()

