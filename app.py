import os
import streamlit as st

# Fix permissions for static-ffmpeg cache/lock files on Streamlit Cloud
os.environ["XDG_CACHE_HOME"] = "/tmp"

import yt_dlp
import subprocess
from static_ffmpeg import run as sffmpeg_run

def get_ffmpeg_path():
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
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                video_filename = ydl.prepare_filename(info)
        except Exception as e:
            st.error(f"Download error: {e}")
            st.stop()

    base = os.path.splitext(video_filename)[0]

    # Extract audio only
    audio_file = f"{base}_audio.mp3"
    with st.spinner("Extracting audio..."):
        subprocess.run([
            ffmpeg_path, "-i", video_filename, "-q:a", "0", "-map", "a", audio_file, "-y"
        ])

    # Crop video (remove audio, crop bottom 200px)
    cropped_video = f"{base}_cropped.mp4"
    with st.spinner("Cropping video and removing audio..."):
        subprocess.run([
            ffmpeg_path, "-i", video_filename, "-an", "-filter:v",
            "crop=in_w:in_h-200:0:0", "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            cropped_video, "-y"
        ])

    st.success("Processing complete!")

    st.subheader("▶ Cropped Video")
    st.video(cropped_video)
    st.download_button("⬇️ Download Cropped Video", open(cropped_video, "rb"), file_name=os.path.basename(cropped_video))

    st.subheader("🎵 Extracted Audio")
    st.audio(audio_file)
    st.download_button("⬇️ Download Audio", open(audio_file, "rb"), file_name=os.path.basename(audio_file))
