# YouTube Shorts Downloader (Streamlit Cloud Compatible)

[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-orange)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Live App](https://img.shields.io/badge/launch-app-success)](https://ytdownloaderapp-cetcap87fwtakddr2w2jg9.streamlit.app/)
[![GitHub Repo](https://img.shields.io/badge/view%20on-GitHub-blue)](https://github.com/hisrinivas1972/yt_downloader_streamlit)

A Streamlit web app to download YouTube Shorts videos, extract audio, crop the video, and download subtitles — all compatible with Streamlit Cloud.


## 🚀 Clone & Run Locally

```bash

# Clone the repository
git clone https://github.com/hisrinivas1972/yt_downloader_streamlit.git

# Navigate into the project folder
cd yt_downloader_streamlit

---

## Features

- Download YouTube Shorts videos with best video and audio quality.
- Extract audio to MP3.
- Crop video (removes 200px from bottom).
- Download English subtitles (manual & automatic).
- Download original, cropped video, audio, and subtitles separately.
- **Uploading YouTube `cookies.txt` is required** to access age-restricted or region-locked videos.
- Inputs moved to sidebar for cleaner UI.
- Auto-downloads static ffmpeg binary for Streamlit Cloud compatibility.

# Install dependencies
pip install streamlit yt-dlp

# Run the Streamlit app
streamlit run app.py

## How to Use

1. Launch the app (locally or on Streamlit Cloud).
2. Enter YouTube Shorts URL in the sidebar.
3. **Upload your YouTube `cookies.txt` file (required for age-restricted or region-locked videos).**
4. Click **Download & Process**.
5. View and download original video, cropped video, audio, and subtitles on the main page.

## Requirements

- Python 3.7+
- [Streamlit](https://streamlit.io/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)

## Installation

```bash
pip install streamlit yt-dlp
