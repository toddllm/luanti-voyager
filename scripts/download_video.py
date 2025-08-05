#!/Users/tdeshane/luanti-voyager/.venv-whisper/bin/python3
"""Download YouTube video and extract audio only"""

import subprocess
import sys
from pathlib import Path

def download_audio(url, output_path):
    """Download audio from YouTube video"""
    cmd = [
        "yt-dlp",
        "-x",  # Extract audio only
        "--audio-format", "mp3",
        "--audio-quality", "0",  # Best quality
        "-o", str(output_path),
        "--no-playlist",
        url
    ]
    
    result = subprocess.run(cmd)
    return result.returncode == 0

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: download_video.py <youtube_url> <output_path>")
        sys.exit(1)
    
    url = sys.argv[1]
    output = sys.argv[2]
    
    print(f"Downloading audio from: {url}")
    print(f"Saving to: {output}")
    
    if download_audio(url, output):
        print("✅ Download complete!")
    else:
        print("❌ Download failed!")
        sys.exit(1)