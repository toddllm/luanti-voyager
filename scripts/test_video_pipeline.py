#!/Users/tdeshane/luanti-voyager/.venv-whisper/bin/python3
"""
Test script to verify video processing pipeline components
"""

import sys
import subprocess
import requests
from pathlib import Path

def check_command(cmd, name):
    """Check if a command is available"""
    try:
        subprocess.run([cmd, "--version"], capture_output=True, check=True)
        print(f"✅ {name} is installed")
        return True
    except:
        print(f"❌ {name} is NOT installed")
        return False

def check_python_package(package_name):
    """Check if a Python package is installed"""
    try:
        __import__(package_name)
        print(f"✅ Python package '{package_name}' is installed")
        return True
    except ImportError:
        print(f"❌ Python package '{package_name}' is NOT installed")
        return False

def check_ollama():
    """Check if Ollama is running and has the model"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✅ Ollama is running")
            
            # Check for gpt-oss:120b model
            models = response.json().get('models', [])
            has_model = any('gpt-oss:120b' in model.get('name', '') for model in models)
            
            if has_model:
                print("✅ gpt-oss:120b model is available")
            else:
                print("⚠️  gpt-oss:120b model is NOT available")
                print("   Run: ollama pull gpt-oss:120b")
            return True
        else:
            print("❌ Ollama responded with error")
            return False
    except:
        print("❌ Ollama is NOT running")
        print("   Start with: ollama serve")
        return False

def main():
    print("🔍 Checking Video Processing Pipeline Dependencies")
    print("=" * 50)
    print()
    
    all_good = True
    
    # Check system commands
    print("System Commands:")
    all_good &= check_command("ffmpeg", "FFmpeg")
    all_good &= check_command("yt-dlp", "yt-dlp")
    print()
    
    # Check Python packages
    print("Python Packages:")
    all_good &= check_python_package("cv2")
    all_good &= check_python_package("PIL")
    all_good &= check_python_package("numpy")
    all_good &= check_python_package("whisper")
    all_good &= check_python_package("requests")
    print()
    
    # Check Ollama
    print("LLM Service:")
    all_good &= check_ollama()
    print()
    
    # Final status
    print("=" * 50)
    if all_good:
        print("✅ All dependencies are satisfied!")
        print("   You can run: ./scripts/process_target_video.sh")
    else:
        print("⚠️  Some dependencies are missing.")
        print("   Install missing components before running the pipeline.")
        print()
        print("Quick fixes:")
        print("  - FFmpeg: brew install ffmpeg")
        print("  - yt-dlp: pip install yt-dlp")
        print("  - Python packages: pip install -r scripts/requirements_video_processing.txt")
        print("  - Ollama: https://ollama.ai/download")
        sys.exit(1)

if __name__ == "__main__":
    main()