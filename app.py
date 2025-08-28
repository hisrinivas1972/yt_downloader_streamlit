import streamlit as st
import yt_dlp
import os
import subprocess
import requests
import stat

# ---------- Download FFmpeg (once per session) ----------
def download_ffmpeg():
    ffmpeg_url = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.zip"
    ffmpeg_zip = "ffmpeg.zip"

    if not os.path.exists("ffmpeg"):
        st.info("Downloading FFmpeg...")
        with open(ffmpeg_zip, "wb") as f:
            f.write(requests.get(ffmpeg_url).content)
        subprocess.run(["unzip", ffmpeg_zip, "-d", "./"])
        # Find the binary
        for root, dirs, files in os.walk("./"):
            for file in files:
                if file == "ffmpeg":
                    ffmpeg_path = os.path.join(root, file)
                    os.chmod(ffmpeg_path, os.stat(ffmpeg_path).st_mode | stat.S_IEXEC)
                    return ffmpeg_path
    return "./ffmpeg"  # Fallback

ffmpeg_path = download_ffmpeg()

# ---------- Set yt-dlp config with custom ffmpeg path ----------
st.title("🎞️ YouTube Shorts Downloader + Audio/Video Splitter")

youtube_url = st.text_input("Paste a YouTube Shorts URL:")

if st.button("Download and Process") and youtube_url:
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

    base_name = os.path.splitext(video_filename)[0]

    # Extract audio
    audio_file = f"{base_name}_audio.mp3"
    subprocess.run([
        ffmpeg_path, "-i", video_filename, "-q:a", "0", "-map", "a", audio_file, "-y"
    ])

    # Crop video and remove audio
    video_no_audio = f"{base_name}_video_no_audio_no_text.mp4"
    subprocess.run([
        ffmpeg_path, "-i", video_filename, "-an", "-filter:v",
        "crop=in_w:in_h-200:0:0", "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        video_no_audio, "-y"
    ])

    st.success("Done! Download your files below:")
    st.video(video_no_audio)
    st.audio(audio_file)

    st.download_button("Download Audio (MP3)", open(audio_file, "rb"), file_name=os.path.basename(audio_file))
    st.download_button("Download Cropped Video (MP4)", open(video_no_audio, "rb"), file_name=os.path.basename(video_no_audio))
