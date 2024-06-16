import os
import subprocess
import yt_dlp as youtube_dl
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import re
import sys
from tkinter import filedialog
from PIL import Image, ImageTk
import webbrowser
import time
import uuid

SAVE_PATH = "D://Download"
stop_event = threading.Event()  # Событие для остановки потоков
last_progress = 0  # Глобальная переменная для отслеживания последнего значения прогресса
real_download_started = False
lock = threading.Lock()  # Блокировка для синхронизации потоков

def clear_previous_files(video_file, audio_file):
    if os.path.exists(video_file):
        os.remove(video_file)
    if os.path.exists(audio_file):
        os.remove(audio_file)

def progress_hook(d, progress_var, status_var, current_status):
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
            progress_var.set(current_progress)
            last_progress = current_progress
            status_var.set(f"Downloading {current_status}... {current_progress:.2f}%")
            root.update_idletasks()
    elif d['status'] == 'finished':
        if real_download_started:
            progress_var.set(100)
        last_progress = 0  # Сброс значения после завершения скачивания
        real_download_started = False
        if current_status == 'video':
            status_var.set("Video downloaded. Wait...")
        elif current_status == 'audio':
            status_var.set("Audio downloaded.")
    root.update_idletasks()

def download_youtube_video(url, progress_var, status_var):
    if stop_event.is_set():
        return None, None, None
    try:
        status_var.set("Downloading video...")
        root.update_idletasks()
        progress_var.set(0)
        progress_bar.pack(padx=10, pady=10, fill=tk.X)  # Показываем прогресс-бар
        
        # Generate unique file names
        unique_id = uuid.uuid4().hex
        video_filename = f'video_{unique_id}.%(ext)s'
        audio_filename = f'audio_{unique_id}.%(ext)s'
        
        with lock:  # Синхронизируем доступ к загрузке видео и аудио
            # Download video
            video_opts = {
                'format': 'bestvideo',
                'outtmpl': os.path.join(SAVE_PATH, video_filename),
                'progress_hooks': [lambda d: progress_hook(d, progress_var, status_var, 'video')]
            }
            with youtube_dl.YoutubeDL(video_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                video_ext = info_dict['ext']
                ydl.download([url])
        
        # Add a delay to ensure the file is fully released
        time.sleep(5)
        
        if stop_event.is_set():
            return None, None, None
        
        status_var.set("Downloading audio...")
        root.update_idletasks()
        progress_var.set(0)
        
        with lock:  # Синхронизируем доступ к загрузке видео и аудио
            # Download audio
            audio_opts = {
                'format': 'bestaudio',
                'outtmpl': os.path.join(SAVE_PATH, audio_filename),
                'progress_hooks': [lambda d: progress_hook(d, progress_var, status_var, 'audio')]
            }
            with youtube_dl.YoutubeDL(audio_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                audio_ext = info_dict['ext']
                ydl.download([url])
        
        video_file_path = os.path.join(SAVE_PATH, f'video_{unique_id}.{video_ext}')
        audio_file_path = os.path.join(SAVE_PATH, f'audio_{unique_id}.{audio_ext}')
        
        if not os.path.exists(video_file_path) or os.path.getsize(video_file_path) == 0:
            status_var.set("Error: Video file not found or is empty.")
            progress_var.set(0)
            return None, None, None
        
        if not os.path.exists(audio_file_path) or os.path.getsize(audio_file_path) == 0:
            status_var.set("Error: Audio file not found or is empty.")
            progress_var.set(0)
            return None, None, None
        
        return video_file_path, audio_file_path, info_dict['title']
    except Exception as e:
        if not stop_event.is_set():
            status_var.set(f"Error: {e}")
        root.update_idletasks()
        progress_var.set(0)
        return None, None, None

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def get_unique_filename(path):
    base, ext = os.path.splitext(path)
    counter = 1
    new_path = path
    while os.path.exists(new_path):
        new_path = f"{base}_{counter}{ext}"
        counter += 1
    return new_path

def combine_video_audio(video_path, audio_path, output_path, status_var):
    if stop_event.is_set():
        return
    try:
        status_var.set("\nCombining video and audio...")
        progress_bar.pack_forget()  # Hide progress bar during combination
        root.update_idletasks()
        
        # Get a unique file name if the file already exists
        output_path = get_unique_filename(output_path)
        
        if hasattr(sys, '_MEIPASS'):
            ffmpeg_path = os.path.join(sys._MEIPASS, 'ffmpeg.exe')
        else:
            ffmpeg_path = 'ffmpeg'

        command = [
            ffmpeg_path,
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            output_path
        ]
        result = subprocess.run(command, check=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print("FFmpeg command:", ' '.join(command))
        print("FFmpeg stdout:", result.stdout)
        print("FFmpeg stderr:", result.stderr)

        # Check that the file was created and is not empty
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            status_var.set(f"{os.linesep}Combined video saved to:{os.linesep}{output_path}")
            print(f"{os.linesep}Combined video saved to:{os.linesep}{output_path}")
        else:
            status_var.set("Error: Output file is empty or not created.")
            print("Error: Output file is empty или не создан.")
        
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)
    except subprocess.CalledProcessError as e:
        if not stop_event.is_set():
            status_var.set(f"Error: {e}")
        print("FFmpeg stdout:", e.stdout)
        print("FFmpeg stderr:", e.stderr)
    finally:
        progress_bar.pack(padx=10, pady=10, fill=tk.X)  # Show progress bar again after combining
        root.update_idletasks()

def download_and_combine(urls, progress_var, status_var):
    for url in urls:
        if stop_event.is_set():
            break
        progress_var.set(0)  # Reset progress bar for each video
        video_path, audio_path, video_title = download_youtube_video(url, progress_var, status_var)
        if video_path and audio_path:
            sanitized_title = sanitize_filename(video_title)
            output_path = os.path.join(SAVE_PATH, f'{sanitized_title}.mp4')
            combine_video_audio(video_path, audio_path, output_path, status_var)
    if not stop_event.is_set():
        status_var.set("\nAll downloads completed.")
    progress_bar.pack_forget()  # Hide progress bar at the end of all downloads
    progress_var.set(0)  # Reset progress bar value

def download_youtube_playlist(url, progress_var, status_var):
    try:
        status_var.set("\nFetching playlist info...")
        root.update_idletasks()

        ydl_opts = {
            'extract_flat': True,
            'skip_download': True,
            'quiet': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=False)
        
        if 'entries' in result:
            video_urls = [entry['url'] for entry in result['entries']]
            download_and_combine(video_urls, progress_var, status_var)
        else:
            status_var.set("Error: No videos found in playlist.")
    except Exception as e:
        if not stop_event.is_set():
            status_var.set(f"Error: {e}")
        root.update_idletasks()

def start_sequential_download(urls):
    for url in urls:
        if stop_event.is_set():
            break
        if "playlist" in url:
            download_youtube_playlist(url, progress_var, status_var)
        else:
            download_and_combine([url], progress_var, status_var)

def on_download_click():
    urls = url_entry.get("1.0", tk.END).strip().split("\n")
    if not urls:
        messagebox.showerror("Error", "URL list cannot be empty. Please enter valid URLs.")
        return
    
    # Reset state before starting a new download
    progress_var.set(0)
    status_var.set("")
    
    stop_event.clear()  # Clear the stop event before starting new downloads
    
    # Start sequential download in a separate thread
    thread = threading.Thread(target=start_sequential_download, args=(urls,))
    thread.start()

def on_exit_click():
    stop_event.set()  # Signal all threads to stop
    root.destroy()  # Destroy the main window

def on_paste_click():
    try:
        current_text = url_entry.get("1.0", tk.END).strip()
        new_text = root.clipboard_get()
        if current_text:
            url_entry.insert(tk.END, "\n" + new_text)
        else:
            url_entry.insert(tk.END, new_text)
    except tk.TclError:
        messagebox.showerror("Error", "No text found in clipboard")

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def open_vk():
    webbrowser.open_new("https://vk.com/exaella")

def open_telegram():
    webbrowser.open_new("https://t.me/ExaellaSS")

def open_github():
    webbrowser.open_new("https://github.com/ExaellaSS/YouTube_Video_Downloader")

# Create the main window
root = tk.Tk()
root.title("YouTube Video Downloader")
root.attributes('-topmost', True)  # Окно поверх остальных

# Set the icon for the window
if hasattr(sys, '_MEIPASS'):
    icon_path = os.path.join(sys._MEIPASS, 'resources', 'icon.ico')
else:
    icon_path = os.path.join(os.path.abspath("."), 'resources', 'icon.ico')

root.iconbitmap(icon_path)

# Set initial size
root.geometry("500x325")

# Create and place widgets
label = tk.Label(root, text="Enter YouTube video URLs (one per line):")
label.pack(padx=10, pady=5)

url_entry = tk.Text(root, width=70, height=5)
url_entry.pack(padx=10, pady=5)
url_entry.focus_set()  # Set focus to the text entry field

paste_button = tk.Button(root, text="Paste URLs", command=on_paste_click)
paste_button.pack(padx=10, pady=5)

button_frame = tk.Frame(root)
button_frame.pack(padx=10, pady=5)

download_button = tk.Button(button_frame, text="Download", command=on_download_click)
download_button.pack(side=tk.LEFT, padx=5)

exit_button = tk.Button(button_frame, text="Exit", command=on_exit_click)
exit_button.pack(side=tk.LEFT, padx=5)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)

status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, wraplength=450)
status_label.pack(padx=10, pady=5)

# Adding the social media icons
icon_frame = tk.Frame(root)
icon_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

# VK icon
vk_icon_path = "resources/vk.png"
if hasattr(sys, '_MEIPASS'):
    vk_icon_path = os.path.join(sys._MEIPASS, 'resources', 'vk.png')

if os.path.exists(vk_icon_path):
    vk_icon = Image.open(vk_icon_path)
    vk_icon = vk_icon.resize((30, 30), Image.LANCZOS)
    vk_photo = ImageTk.PhotoImage(vk_icon)
    vk_button = tk.Button(icon_frame, image=vk_photo, command=open_vk, borderwidth=0)
    vk_button.pack(side=tk.LEFT, padx=5)
else:
    print(f"Error: The file {vk_icon_path} does not exist.")

# Telegram icon
telegram_icon_path = "resources/telegram.png"
if hasattr(sys, '_MEIPASS'):
    telegram_icon_path = os.path.join(sys._MEIPASS, 'resources', 'telegram.png')

if os.path.exists(telegram_icon_path):
    telegram_icon = Image.open(telegram_icon_path)
    telegram_icon = telegram_icon.resize((30, 30), Image.LANCZOS)
    telegram_photo = ImageTk.PhotoImage(telegram_icon)
    telegram_button = tk.Button(icon_frame, image=telegram_photo, command=open_telegram, borderwidth=0)
    telegram_button.pack(side=tk.LEFT, padx=5)
else:
    print(f"Error: The file {telegram_icon_path} does not exist.")

# GitHub icon
github_icon_path = "resources/github.png"
if hasattr(sys, '_MEIPASS'):
    github_icon_path = os.path.join(sys._MEIPASS, 'resources', 'github.png')

if os.path.exists(github_icon_path):
    github_icon = Image.open(github_icon_path)
    github_icon = github_icon.resize((30, 30), Image.LANCZOS)
    github_photo = ImageTk.PhotoImage(github_icon)
    github_button = tk.Button(icon_frame, image=github_photo, command=open_github, borderwidth=0)
    github_button.pack(side=tk.LEFT, padx=5)
else:
    print(f"Error: The file {github_icon_path} does not exist.")

# Center the window and start the main loop
root.update_idletasks()  # Update "requested size" from geometry manager
center_window(root)
root.mainloop()
