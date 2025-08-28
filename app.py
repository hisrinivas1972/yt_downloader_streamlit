# app.py
import streamlit as st
import yt_dlp
import os
import subprocess

st.title("YouTube Short Downloader + Audio/Video Splitter")

# Input: YouTube URL
youtube_url = st.text_input("Enter YouTube Shorts URL:")

if st.button("Download & Process") and youtube_url:
    with st.spinner("Downloading video..."):
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': 'downloaded.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            video_filename = ydl.prepare_filename(info)

    base_name = os.path.splitext(video_filename)[0]

    # 1. Extract audio
    audio_file = f"{base_name}_audio.mp3"
    subprocess.run([
        "ffmpeg", "-i", video_filename, "-q:a", "0", "-map", "a", audio_file, "-y"
    ])

    # 2. Crop and remove audio
    video_no_audio = f"{base_name}_video_no_audio_no_text.mp4"
    subprocess.run([
        "ffmpeg", "-i", video_filename, "-an", "-filter:v",
        "crop=in_w:in_h-200:0:0", "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        video_no_audio, "-y"
    ])

    st.success("Processing complete!")

    # Display video and audio download links
    st.video(video_no_audio)
    st.audio(audio_file)

    st.download_button("Download Audio (MP3)", open(audio_file, "rb"), file_name=audio_file)
    st.download_button("Download Cropped Video (MP4)", open(video_no_audio, "rb"), file_name=video_no_audio)
