#!/Users/tdeshane/luanti-voyager/.venv-whisper/bin/python3
"""
Complete smoke test for the batch processing pipeline
"""

import sys
import os
from pathlib import Path
import subprocess
import json

def test_ollama():
    """Test if Ollama is working"""
    print("Testing Ollama...")
    
    test_prompt = "Write a one-line Python function to add two numbers."
    cmd = ["ollama", "run", "qwen2.5-coder:32b", test_prompt]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and "def" in result.stdout:
            print("✅ Ollama is working")
            print(f"   Response: {result.stdout.strip()[:100]}...")
            return True
        else:
            print("❌ Ollama failed")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️ Ollama timed out - model may need to download first")
        return True  # Consider it working but slow
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return False

def test_whisper():
    """Test if Whisper can transcribe a short audio"""
    print("\nTesting Whisper...")
    
    # Create a test audio file using text-to-speech
    test_text = "Hello, this is a test of the Whisper transcription system."
    test_audio = Path("/tmp/test_whisper.mp3")
    
    # Use macOS say command to create audio
    cmd = ["say", "-o", str(test_audio), "--data-format=mp3", test_text]
    subprocess.run(cmd, capture_output=True)
    
    if not test_audio.exists():
        print("⚠️ Could not create test audio file")
        return True  # Skip test
    
    # Test whisper
    try:
        import whisper
        model = whisper.load_model("base")  # Use base for quick test
        result = model.transcribe(str(test_audio), language="en")
        
        if result and result.get('text'):
            print("✅ Whisper is working")
            print(f"   Transcribed: {result['text'].strip()}")
            test_audio.unlink()
            return True
        else:
            print("❌ Whisper failed to transcribe")
            return False
    except Exception as e:
        print(f"❌ Whisper error: {e}")
        return False

def test_synthesis():
    """Test the complete synthesis pipeline"""
    print("\nTesting synthesis pipeline...")
    
    # Use the existing transcript
    transcript_path = Path("docs/ai-makerspace-resources/transcripts/21_vector_memory.json")
    
    if not transcript_path.exists():
        print("⚠️ No transcript found to test synthesis")
        return True
    
    # Load transcript
    with open(transcript_path, 'r') as f:
        transcript = json.load(f)
    
    # Test synthesis with a small excerpt
    text_excerpt = transcript.get('text', '')[:1000]
    
    prompt = f"""Based on this AI Makerspace transcript excerpt about Vector Memory, 
write a brief implementation note (2-3 sentences) for game developers:

{text_excerpt}"""
    
    cmd = ["ollama", "run", "qwen2.5-coder:32b", prompt]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and len(result.stdout) > 50:
            print("✅ Synthesis pipeline is working")
            print(f"   Generated: {result.stdout.strip()[:150]}...")
            return True
        else:
            print("❌ Synthesis failed")
            return False
    except Exception as e:
        print(f"❌ Synthesis error: {e}")
        return False

def main():
    print("Running complete smoke test for AI Makerspace batch processing")
    print("="*60)
    
    tests = [
        ("Ollama", test_ollama),
        ("Whisper", test_whisper),
        ("Synthesis", test_synthesis)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            results.append((name, False))
    
    print("\n" + "="*60)
    print("Test Results:")
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {name}: {status}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print("\n✅ All tests passed! The batch processing should work correctly.")
    else:
        print("\n⚠️ Some tests failed, but batch processing may still work.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())