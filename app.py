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
    st.sidebar.info("Downloading ffmpeg binary (~30MB)...")
    subprocess.run(["curl", "-L", url, "-o", tar_path], check=True)
    subprocess.run(["tar", "-xf", tar_path, "-C", "/tmp"], check=True)
    os.remove(tar_path)  # Cleanup tar file

    extracted_dir = next(
        (os.path.join("/tmp", d) for d in os.listdir("/tmp")
         if d.startswith("ffmpeg") and os.path.isdir(os.path.join("/tmp", d))),
        None
    )
    if extracted_dir is None:
        st.sidebar.error("Failed to find extracted ffmpeg directory.")
        st.stop()

    src_ffmpeg = os.path.join(extracted_dir, "ffmpeg")
    if not os.path.isfile(src_ffmpeg):
        st.sidebar.error("ffmpeg binary not found inside extracted archive.")
        st.stop()

    os.rename(src_ffmpeg, FFMPEG_PATH)
    os.chmod(FFMPEG_PATH, stat.S_IRWXU)  # Make executable
    st.sidebar.success("ffmpeg downloaded and ready.")

def get_ffmpeg_dir():
    return os.path.dirname(FFMPEG_PATH)

st.title("▶ YouTube Shorts Downloader (Streamlit Cloud Compatible)")

download_ffmpeg()

# Sidebar Inputs
st.sidebar.header("Input Options")
uploaded_cookies = st.sidebar.file_uploader("Upload your YouTube cookies.txt (optional)", type=["txt"])
youtube_url = st.sidebar.text_input("Enter YouTube Shorts URL:")
download_btn = st.sidebar.button("Download & Process")

if download_btn and youtube_url:
    cookie_path = None
    if uploaded_cookies is not None:
        cookie_path = "/tmp/cookies.txt"
        with open(cookie_path, "wb") as f:
            f.write(uploaded_cookies.getbuffer())
        st.sidebar.success("Cookies uploaded!")

    # --- Download subtitles only ---
    subtitle_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,
        'skip_download': True,
        'subtitleslangs': ['en'],
        'outtmpl': '/tmp/%(title)s.%(ext)s',
        'quiet': True,
    }
    if cookie_path:
        subtitle_opts['cookiefile'] = cookie_path

    with st.spinner("Downloading subtitles (if available)..."):
        try:
            with yt_dlp.YoutubeDL(subtitle_opts) as ydl:
                ydl.download([youtube_url])
            st.success("Subtitles downloaded (if available).")
        except Exception as e:
            st.warning(f"Subtitle download error (maybe no subtitles available): {e}")

    # --- Download video & audio ---
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': '/tmp/downloaded.%(ext)s',
        'ffmpeg_location': get_ffmpeg_dir(),
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/115.0.0.0 Safari/537.36',
        },
        'geo_bypass': True,
        'quiet': True,
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
        try:
            subprocess.run([
                FFMPEG_PATH, "-i", video_filename, "-q:a", "0", "-map", "a", audio_file, "-y"
            ], check=True)
        except subprocess.CalledProcessError as e:
            st.error(f"Audio extraction failed: {e}")
            st.stop()

    cropped_video = f"{base}_cropped.mp4"
    with st.spinner("Cropping video and removing audio..."):
        try:
            subprocess.run([
                FFMPEG_PATH, "-i", video_filename, "-an", "-filter:v",
                "crop=in_w:in_h-200:0:0", "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                cropped_video, "-y"
            ], check=True)
        except subprocess.CalledProcessError as e:
            st.error(f"Video cropping failed: {e}")
            st.stop()

    st.success("Processing complete!")

    # --- Display original video ---
    st.subheader("🎞️ Original Video (from YouTube)")
    st.video(video_filename)
    with open(video_filename, "rb") as f:
        st.download_button("⬇️ Download Original Video", f, file_name=os.path.basename(video_filename))

    # --- Display cropped video ---
    st.subheader("▶ Cropped Video (no audio)")
    st.video(cropped_video)
    with open(cropped_video, "rb") as f:
        st.download_button("⬇️ Download Cropped Video", f, file_name=os.path.basename(cropped_video))

    # --- Display extracted audio ---
    st.subheader("🎵 Extracted Audio")
    st.audio(audio_file)
    with open(audio_file, "rb") as f:
        st.download_button("⬇️ Download Audio", f, file_name=os.path.basename(audio_file))

    # --- Provide subtitle download if subtitles exist ---
    subtitle_files = [f for f in os.listdir("/tmp") if f.startswith(info.get('title', '')) and f.endswith(('.vtt', '.srt', '.ass'))]
    if subtitle_files:
        st.subheader("💬 Subtitles")
        for sub_file in subtitle_files:
            sub_path = os.path.join("/tmp", sub_file)
            with open(sub_path, "rb") as f:
                st.download_button(f"⬇️ Download Subtitle: {sub_file}", f, file_name=sub_file)
    else:
        st.info("No subtitles were found or downloaded.")
