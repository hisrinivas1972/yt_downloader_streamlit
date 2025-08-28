import os
import stat
import subprocess
import streamlit as st
import yt_dlp

FFMPEG_PATH = "/tmp/ffmpeg"

def download_ffmpeg():
    if os.path.isfile(FFMPEG_PATH):
        return
    url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
    tar_path = "/tmp/ffmpeg.tar.xz"
    st.info("Downloading ffmpeg binary (~30MB)...")
    subprocess.run(["curl", "-L", url, "-o", tar_path], check=True)
    subprocess.run(["tar", "-xf", tar_path, "-C", "/tmp"], check=True)
    extracted_dir = None
    for entry in os.listdir("/tmp"):
        if entry.startswith("ffmpeg") and os.path.isdir(os.path.join("/tmp", entry)):
            extracted_dir = os.path.join("/tmp", entry)
            break
    if extracted_dir is None:
        st.error("Failed to find extracted ffmpeg directory.")
        st.stop()
    src_ffmpeg = os.path.join(extracted_dir, "ffmpeg")
    if not os.path.isfile(src_ffmpeg):
        st.error("ffmpeg binary not found inside extracted archive.")
        st.stop()
    os.rename(src_ffmpeg, FFMPEG_PATH)
    os.chmod(FFMPEG_PATH, stat.S_IRWXU)  # Make executable
    st.success("ffmpeg downloaded and ready.")

def get_ffmpeg_dir():
    return os.path.dirname(FFMPEG_PATH)

st.title("▶ YouTube Shorts Downloader (Streamlit Cloud Compatible)")

download_ffmpeg()

uploaded_cookies = st.file_uploader("Upload your YouTube cookies.txt (optional)", type=["txt"])

youtube_url = st.text_input("Enter YouTube Shorts URL:")

if st.button("Download & Process") and youtube_url:
    cookie_path = None
    if uploaded_cookies is not None:
        cookie_path = "/tmp/cookies.txt"
        with open(cookie_path, "wb") as f:
            f.write(uploaded_cookies.getbuffer())
        st.success("Cookies uploaded!")

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': 'downloaded.%(ext)s',
        'ffmpeg_location': get_ffmpeg_dir(),
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/115.0.0.0 Safari/537.36',
        },
        'geo_bypass': True,
    }

    if cookie_path:
        ydl_opts['cookiefile'] = cookie_path

    with st.spinner("Downloading video..."):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                video_filename = ydl.prepare_filename(info)
        except Exception as e:
            st.error(f"Download error: {e}")
            st.stop()

    base = os.path.splitext(video_filename)[0]

    audio_file = f"{base}_audio.mp3"
    with st.spinner("Extracting audio..."):
        subprocess.run([
            FFMPEG_PATH, "-i", video_filename, "-q:a", "0", "-map", "a", audio_file, "-y"
        ], check=True)

    cropped_video = f"{base}_cropped.mp4"
    with st.spinner("Cropping video and removing audio..."):
        subprocess.run([
            FFMPEG_PATH, "-i", video_filename, "-an", "-filter:v",
            "crop=in_w:in_h-200:0:0", "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            cropped_video, "-y"
        ], check=True)

    st.success("Processing complete!")

    st.subheader("▶ Cropped Video")
    st.video(cropped_video)
    with open(cropped_video, "rb") as f:
        st.download_button("⬇️ Download Cropped Video", f, file_name=os.path.basename(cropped_video))

    st.subheader("🎵 Extracted Audio")
    st.audio(audio_file)
    with open(audio_file, "rb") as f:
        st.download_button("⬇️ Download Audio", f, file_name=os.path.basename(audio_file))
