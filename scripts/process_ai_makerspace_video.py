#!/Users/tdeshane/luanti-voyager/.venv-whisper/bin/python3
"""
Process AI Makerspace YouTube videos:
1. Download video
2. Extract audio
3. Transcribe with Whisper
4. Create developer-focused summary
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import argparse
from datetime import datetime
import uuid
import whisper

class VideoProcessor:
    def __init__(self, output_dir="docs/ai-makerspace-resources"):
        self.output_dir = Path(output_dir)
        self.temp_dir = Path("/tmp/ai-makerspace-processing")
        self.temp_dir.mkdir(exist_ok=True)
        
    def download_video(self, youtube_url, title):
        """Download YouTube video and extract audio"""
        print(f"Downloading: {title}")
        
        # Create safe filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')
        
        video_file = self.temp_dir / f"{safe_title}.mp4"
        audio_file = self.temp_dir / f"{safe_title}.mp3"
        
        # Download video (audio only for faster processing)
        cmd = [
            "yt-dlp",
            "-f", "bestaudio/best",
            "-o", str(video_file),
            "--no-playlist",
            youtube_url
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error downloading video: {e}")
            return None
        
        # Extract audio with ffmpeg
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", str(video_file),
            "-vn",  # No video
            "-acodec", "mp3",
            "-ab", "192k",
            "-ar", "44100",
            "-y",  # Overwrite
            str(audio_file)
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error extracting audio: {e}")
            return None
        
        # Clean up video file
        video_file.unlink(missing_ok=True)
        
        return audio_file
    
    def transcribe_audio(self, audio_file, model_size="large-v3"):
        """Transcribe audio using Whisper"""
        print(f"Transcribing with Whisper {model_size}...")
        
        # Load model (will use cached version from ~/.cache/whisper/)
        model = whisper.load_model(model_size)
        
        # Transcribe
        result = model.transcribe(
            str(audio_file),
            language="en",
            verbose=False,
            fp16=False  # Disable for CPU
        )
        
        return result
    
    def extract_key_points(self, transcript):
        """Extract developer-relevant key points from transcript"""
        # This is a simple extraction - could be enhanced with LLM
        key_points = {
            "implementation_steps": [],
            "code_patterns": [],
            "best_practices": [],
            "gotchas": [],
            "tools_mentioned": []
        }
        
        # Simple keyword-based extraction
        implementation_keywords = ["implement", "build", "create", "code", "function", "class", "method"]
        pattern_keywords = ["pattern", "architecture", "design", "approach", "structure"]
        practice_keywords = ["best practice", "should", "recommend", "important", "tip"]
        gotcha_keywords = ["gotcha", "warning", "careful", "issue", "problem", "error"]
        tool_keywords = ["library", "framework", "tool", "package", "import"]
        
        segments = transcript.get('segments', [])
        
        for segment in segments:
            text = segment['text'].lower()
            
            # Check for different types of content
            if any(keyword in text for keyword in implementation_keywords):
                key_points["implementation_steps"].append({
                    "text": segment['text'],
                    "timestamp": segment['start']
                })
            
            if any(keyword in text for keyword in pattern_keywords):
                key_points["code_patterns"].append({
                    "text": segment['text'],
                    "timestamp": segment['start']
                })
            
            if any(keyword in text for keyword in practice_keywords):
                key_points["best_practices"].append({
                    "text": segment['text'],
                    "timestamp": segment['start']
                })
            
            if any(keyword in text for keyword in gotcha_keywords):
                key_points["gotchas"].append({
                    "text": segment['text'],
                    "timestamp": segment['start']
                })
            
            if any(keyword in text for keyword in tool_keywords):
                key_points["tools_mentioned"].append({
                    "text": segment['text'],
                    "timestamp": segment['start']
                })
        
        return key_points
    
    def create_synthesis(self, title, transcript, key_points):
        """Create a developer-focused synthesis document"""
        synthesis = f"""# {title} - Developer Synthesis

## Overview
This synthesis extracts the most relevant information for implementing this feature in Luanti Voyager.

## Key Implementation Steps
"""
        
        # Add implementation steps with timestamps
        for point in key_points["implementation_steps"][:10]:  # Top 10
            timestamp = self.format_timestamp(point["timestamp"])
            synthesis += f"\n### [{timestamp}] {point['text'][:100]}...\n"
        
        synthesis += "\n## Code Patterns Discussed\n"
        for point in key_points["code_patterns"][:5]:
            timestamp = self.format_timestamp(point["timestamp"])
            synthesis += f"\n### [{timestamp}] {point['text'][:100]}...\n"
        
        synthesis += "\n## Best Practices\n"
        for point in key_points["best_practices"][:5]:
            synthesis += f"- {point['text']}\n"
        
        synthesis += "\n## Potential Gotchas\n"
        for point in key_points["gotchas"][:5]:
            synthesis += f"- ⚠️ {point['text']}\n"
        
        synthesis += "\n## Tools and Libraries Mentioned\n"
        tools = set()
        for point in key_points["tools_mentioned"]:
            # Extract tool names (simple approach)
            words = point['text'].split()
            for word in words:
                if word.lower() in ['langchain', 'llama', 'chroma', 'qdrant', 'vllm', 'guardrails']:
                    tools.add(word)
        
        for tool in sorted(tools):
            synthesis += f"- {tool}\n"
        
        return synthesis
    
    def format_timestamp(self, seconds):
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def process_video(self, youtube_url, title, issue_number):
        """Complete processing pipeline for a video"""
        print(f"\nProcessing: {title}")
        print("=" * 50)
        
        # Download and extract audio
        audio_file = self.download_video(youtube_url, title)
        if not audio_file:
            return False
        
        # Transcribe
        transcript = self.transcribe_audio(audio_file)
        
        # Extract key points
        key_points = self.extract_key_points(transcript)
        
        # Save transcript
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')
        
        transcript_file = self.output_dir / "transcripts" / f"{issue_number}_{safe_title}.json"
        with open(transcript_file, 'w') as f:
            json.dump(transcript, f, indent=2)
        
        # Create synthesis
        synthesis = self.create_synthesis(title, transcript, key_points)
        
        synthesis_file = self.output_dir / "synthesis" / f"{issue_number}_{safe_title}.md"
        with open(synthesis_file, 'w') as f:
            f.write(synthesis)
        
        # Clean up
        audio_file.unlink(missing_ok=True)
        
        print(f"✅ Completed: {title}")
        print(f"   - Transcript: {transcript_file}")
        print(f"   - Synthesis: {synthesis_file}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description="Process AI Makerspace videos")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("title", help="Video title")
    parser.add_argument("issue", help="Issue number (e.g., 21)")
    parser.add_argument("--model", default="large-v3", help="Whisper model size")
    
    args = parser.parse_args()
    
    processor = VideoProcessor()
    processor.process_video(args.url, args.title, args.issue)

if __name__ == "__main__":
    main()