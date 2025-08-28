import streamlit as st
import yt_dlp
import os
import subprocess
from static_ffmpeg import run as sffmpeg_run

def get_ffmpeg_path():
    # Automatically ensures FFmpeg is downloaded and returns path
    ffmpeg, ffprobe = sffmpeg_run.get_or_fetch_platform_executables_else_raise()
    return ffmpeg

st.set_page_config(page_title="YouTube Shorts Downloader", layout="centered")
st.title("▶ YouTube Shorts Downloader (Streamlit Cloud Compatible)")

youtube_url = st.text_input("Enter YouTube Shorts URL:")

if st.button("Download & Process") and youtube_url:
    ffmpeg_path = get_ffmpeg_path()

    with st.spinner("Downloading video..."):
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': 'downloaded.%(ext)s',
            'ffmpeg_location': ffmpeg_path,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            video_filename = ydl.prepare_filename(info)

    base = os.path.splitext(video_filename)[0]

    # Extract audio
    audio = f"{base}_audio.mp3"
    subprocess.run([ffmpeg_path, "-i", video_filename, "-q:a", "0", "-map", "a", audio, "-y"])

    # Crop and mute video
    cropped = f"{base}_cropped.mp4"
    subprocess.run([
        ffmpeg_path, "-i", video_filename, "-an", "-filter:v",
        "crop=in_w:in_h-200:0:0", "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        cropped, "-y"
    ])

    st.success("Processing complete!")
    st.video(cropped)
    st.download_button("Download Cropped Video", open(cropped, "rb"), file_name=cropped)
    st.audio(audio)
    st.download_button("Download Audio", open(audio, "rb"), file_name=audio)
