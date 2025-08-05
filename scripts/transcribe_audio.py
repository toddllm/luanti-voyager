#!/Users/tdeshane/luanti-voyager/.venv-whisper/bin/python3
"""Transcribe audio file using Whisper"""

import sys
import json
from pathlib import Path
import whisper

def transcribe_file(audio_path, model_name="large-v3"):
    """Transcribe audio file and save as JSON"""
    print(f"Loading Whisper {model_name} model...")
    model = whisper.load_model(model_name)
    
    print(f"Transcribing {audio_path}...")
    result = model.transcribe(
        str(audio_path),
        language="en",
        verbose=True,  # Show progress
        fp16=False     # CPU mode
    )
    
    # Save transcript
    output_path = audio_path.with_suffix('.json')
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"✅ Transcript saved to: {output_path}")
    
    # Also save plain text
    text_path = audio_path.with_suffix('.txt')
    with open(text_path, 'w') as f:
        f.write(result['text'])
    
    print(f"✅ Plain text saved to: {text_path}")
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: transcribe_audio.py <audio_file> [model_name]")
        sys.exit(1)
    
    audio_file = Path(sys.argv[1])
    model = sys.argv[2] if len(sys.argv) > 2 else "large-v3"
    
    if not audio_file.exists():
        print(f"Error: {audio_file} not found")
        sys.exit(1)
    
    transcribe_file(audio_file, model)