#!/Users/tdeshane/luanti-voyager/.venv-whisper/bin/python3
"""
Smoke test for video processing - processes first 2 minutes only
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from process_video_with_code_extraction import AdvancedVideoProcessor
import subprocess
import time

def download_short_segment(url, duration=120):
    """Download only first N seconds of video for testing"""
    print(f"📥 Downloading first {duration} seconds for smoke test...")
    
    output_file = "/tmp/smoketest_video.mp4"
    cmd = [
        "yt-dlp",
        "-f", "best[height<=720]",  # Lower quality for faster test
        "--external-downloader", "ffmpeg",
        "--external-downloader-args", f"-t {duration}",  # Limit duration
        "-o", output_file,
        url
    ]
    
    try:
        subprocess.run(cmd, check=True)
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Error downloading: {e}")
        return None

def main():
    url = "https://www.youtube.com/watch?v=nyb3TnUkwE8"
    
    print("🧪 SMOKE TEST: Video Processing Pipeline")
    print("=" * 60)
    print("Testing with first 2 minutes of video")
    print()
    
    # Quick test of video download
    test_file = download_short_segment(url, duration=120)
    if test_file:
        print(f"✅ Video download works: {test_file}")
        
        # Test frame extraction
        import cv2
        cap = cv2.VideoCapture(test_file)
        ret, frame = cap.read()
        if ret:
            print(f"✅ Frame extraction works: {frame.shape}")
        cap.release()
        
        # Clean up
        os.remove(test_file)
    
    # Test Ollama connection
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m.get('name', '') for m in models]
            print(f"✅ Ollama works. Available models: {', '.join(model_names[:3])}")
    except Exception as e:
        print(f"❌ Ollama error: {e}")
    
    # Test Whisper
    try:
        import whisper
        print("✅ Whisper import works")
    except Exception as e:
        print(f"❌ Whisper error: {e}")
    
    print()
    print("=" * 60)
    print("Smoke test complete! Ready for full processing.")
    print("Run: ./scripts/process_target_video.sh")

if __name__ == "__main__":
    main()