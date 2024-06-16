import os
import subprocess
import yt_dlp as youtube_dl
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import re
import sys

SAVE_PATH = os.path.join(os.path.expanduser("~"), "Downloads") #My - D:\\Download
threads = []
video_file_path = ""
audio_file_path = ""

def clear_previous_files(video_file, audio_file):
    if os.path.exists(video_file):
        os.remove(video_file)
    if os.path.exists(audio_file):
        os.remove(audio_file)

def progress_hook(d, progress_var, status_var, current_status):
    if d['status'] == 'downloading':
        progress_var.set((d["downloaded_bytes"]/d["total_bytes"]*100) if d["total_bytes"] is not None else 0.0)
    elif d['status'] == 'finished':
        progress_var.set(100)
        if current_status == 'video':
            status_var.set("Video downloaded. Downloading audio...")
        elif d['status'] == 'finished' and current_status == 'audio':
            status_var.set("Audio downloaded.")
            root.update_idletasks()
            progress_bar.pack_forget()

def download_youtube_video(url, progress_var, status_var):
    global video_file_path, audio_file_path
    try:
        status_var.set("Downloading video...")
        root.update_idletasks()
        progress_var.set(0)
        
        # Download video
        video_opts = {
            'format': 'bestvideo',
            'outtmpl': os.path.join(SAVE_PATH, 'video.%(ext)s'),
            'progress_hooks': [lambda d: progress_hook(d, progress_var, status_var, 'video')]
        }
        with youtube_dl.YoutubeDL(video_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_ext = info_dict['ext']
            ydl.download([url])
        
        status_var.set("Downloading audio...")
        root.update_idletasks()
        progress_var.set(0)
        
        # Download audio
        audio_opts = {
            'format': 'bestaudio',
            'outtmpl': os.path.join(SAVE_PATH, 'audio.%(ext)s'),
            'progress_hooks': [lambda d: progress_hook(d, progress_var, status_var, 'audio')]
        }
        with youtube_dl.YoutubeDL(audio_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            audio_ext = info_dict['ext']
            ydl.download([url])
        
        video_file_path = os.path.join(SAVE_PATH, f'video.{video_ext}')
        audio_file_path = os.path.join(SAVE_PATH, f'audio.{audio_ext}')
        
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
        status_var.set(f"Error: {e}")
        root.update_idletasks()
        progress_var.set(0)
        return None, None, None

def sanitize_filename(filename):
    # Replace all invalid characters with underscores
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
    try:
        status_var.set("Combining video and audio...")
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
            status_var.set(f"Combined video saved to:{os.linesep}{output_path}")
            print(f"Combined video saved to:{os.linesep}{output_path}")
        else:
            status_var.set("Error: Output file is empty or not created.")
            print("Error: Output file is empty or not created.")
        
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)
    except subprocess.CalledProcessError as e:
        status_var.set(f"Error: {e}")
        print("FFmpeg stdout:", e.stdout)
        print("FFmpeg stderr:", e.stderr)

def download_and_combine(url, progress_var, status_var):
    video_path, audio_path, video_title = download_youtube_video(url, progress_var, status_var)
    if video_path and audio_path:
        sanitized_title = sanitize_filename(video_title)
        output_path = os.path.join(SAVE_PATH, f'{sanitized_title}_output.mp4')
        combine_video_audio(video_path, audio_path, output_path, status_var)

def on_download_click():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "URL cannot be empty. Please enter a valid URL.")
        return
    
    # Reset state before starting a new download
    progress_var.set(0)
    status_var.set("")
    
    # Show the progress bar
    progress_bar.pack(padx=10, pady=10, fill=tk.X)
    
    thread = threading.Thread(target=download_and_combine, args=(url, progress_var, status_var))
    threads.append(thread)
    thread.start()

def on_exit_click():
    # Terminate all active threads
    for thread in threads:
        if thread.is_alive():
            thread.join()
    
    # Remove temporary files
    if os.path.exists(video_file_path):
        os.remove(video_file_path)
    if os.path.exists(audio_file_path):
        os.remove(audio_file_path)
    
    root.destroy()

def on_paste_click():
    try:
        url_entry.delete(0, tk.END)
        url_entry.insert(0, root.clipboard_get())
    except tk.TclError:
        messagebox.showerror("Error", "No text found in clipboard")

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

# Create the main window
root = tk.Tk()
root.title("YouTube Video Downloader")

# Set the icon for the window
if hasattr(sys, '_MEIPASS'):
    icon_path = os.path.join(sys._MEIPASS, 'resources', 'icon.ico')
else:
    icon_path = os.path.join(os.path.abspath("."), 'resources', 'icon.ico')

root.iconbitmap(icon_path)

# Set initial size
root.geometry("500x200")

# Create and place widgets
label = tk.Label(root, text="Enter YouTube video URL:")
label.pack(padx=10, pady=5)

url_entry = tk.Entry(root, width=50)
url_entry.pack(padx=10, pady=5)
url_entry.focus_set()  # Set focus to the text entry field

paste_button = tk.Button(root, text="Paste URL", command=on_paste_click)
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

# Center the window and start the main loop
root.update_idletasks()  # Update "requested size" from geometry manager
center_window(root)
root.mainloop()
