import customtkinter as ctk
import threading
import requests
import yt_dlp
from pathlib import Path
import os

# Download Path
DOWNLOAD_PATH = str(Path.home() / "Downloads")

cancel_download = False

def start_gui():
    def fetch_resolutions():
        url = url_entry.get()
        if not url:
            result_label.configure(text="Please enter a valid YouTube URL.", text_color="red")
            return

        try:
            ydl_opts = {'noprogress': True, 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                formats = info_dict.get('formats', [])
                recommended_resolutions = [144, 240, 360, 480, 720, 1080, 1440, 2160]
                available_resolutions = [f"{f['height']}p" for f in formats if f.get('height') in recommended_resolutions]
                resolution_combobox.configure(values=sorted(set(available_resolutions), key=lambda x: int(x[:-1])))
                if available_resolutions:
                    resolution_combobox.set(available_resolutions[0])  # Set default
                    result_label.configure(text="")
                else:
                    resolution_combobox.set("")  # Clear combobox if no resolutions
                    result_label.configure(text="No available resolutions found.", text_color="orange")
        except Exception as e:
            result_label.configure(text=f"Could not fetch resolutions: {str(e)}", text_color="red")

        progress_bar.set(0)  # Reset the progress bar when fetching new resolutions

    def call_api():
        url = url_entry.get()
        resolution = resolution_combobox.get()

        if not url:
            result_label.configure(text="Please enter a valid YouTube URL.", text_color="red")
            return

        data = {"url": url, "resolution": resolution}
        progress_bar.set(0)  # Reset progress bar

        threading.Thread(target=download_video_thread, args=(url, resolution)).start()

    def progress_hook(d):
        if d['status'] == 'downloading':
            downloaded_bytes = d.get('downloaded_bytes', 0)
            total_bytes = d.get('total_bytes', 1)  # Avoid division by zero
            progress_percentage = downloaded_bytes / total_bytes
            progress_bar.set(progress_percentage)
        elif d['status'] == 'finished':
            progress_bar.set(1)  # Complete the progress bar when done
            result_label.configure(text="Download complete!", text_color="green")

    def download_video_thread(url, resolution):
        global cancel_download
        cancel_download = False

        def download_hook(d):
            if cancel_download:
                result_label.configure(text="Download cancelled.", text_color="orange")
                return
            progress_hook(d)  # Pass progress data to the hook

        ydl_opts = {
            'format': f'bestvideo[height={resolution[:-1]}]+bestaudio/best',  # Resolution-based format
            'progress_hooks': [download_hook],  # Custom hook for progress
            'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s')  # Save location
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            result_label.configure(text=f"An error occurred: {str(e)}", text_color="red")

    def cancel_download_action():
        global cancel_download
        cancel_download = True
        result_label.configure(text="Download cancelled.", text_color="orange")

    # Set up CustomTkinter GUI
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("YouTube Video Downloader")
    root.geometry("600x400")

    # GUI Elements
    title_label = ctk.CTkLabel(root, text="YouTube Video Downloader", font=("Helvetica", 18, "bold"))
    title_label.pack(pady=20)

    url_label = ctk.CTkLabel(root, text="Enter YouTube Video URL:")
    url_label.pack(pady=5)

    url_entry = ctk.CTkEntry(root, width=400)
    url_entry.pack(pady=5)

    fetch_res_button = ctk.CTkButton(root, text="Fetch Resolutions", command=fetch_resolutions)
    fetch_res_button.pack(pady=10)

    resolution_combobox = ctk.CTkComboBox(root, width=200, values=[""])  # Start with empty values
    resolution_combobox.set("")  # Clear any placeholder text
    resolution_combobox.pack(pady=5)

    progress_bar = ctk.CTkProgressBar(root, width=400)
    progress_bar.set(0)  # Initialize progress bar to 0
    progress_bar.pack(pady=20)

    download_button = ctk.CTkButton(root, text="Download Video", command=call_api)
    download_button.pack(pady=10)

    cancel_button = ctk.CTkButton(root, text="Cancel", command=cancel_download_action, fg_color="red")
    cancel_button.pack(pady=10)

    result_label = ctk.CTkLabel(root, text="")
    result_label.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    start_gui()
