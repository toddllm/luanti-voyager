#!/Users/tdeshane/luanti-voyager/.venv-whisper/bin/python3
"""
Advanced video processor with code extraction from frames
Processes YouTube videos to extract:
1. Full transcript using Whisper
2. Code snippets from video frames
3. Analysis using local LLM (gpt-oss:120b via Ollama)
"""

import os
import sys
import subprocess
import json
import requests
from pathlib import Path
from datetime import datetime
import cv2
import base64
from typing import Dict, List, Any, Optional
import numpy as np
from PIL import Image
import io
import whisper
import hashlib
import time

class AdvancedVideoProcessor:
    def __init__(self, output_dir="docs/video-analysis"):
        self.output_dir = Path(output_dir)
        self.temp_dir = Path("/tmp/video-processing")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Create output directories
        self.dirs = {
            'video': self.output_dir / 'videos',
            'audio': self.output_dir / 'audio',
            'transcripts': self.output_dir / 'transcripts',
            'frames': self.output_dir / 'frames',
            'code': self.output_dir / 'extracted-code',
            'analysis': self.output_dir / 'analysis'
        }
        
        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Ollama API endpoint
        self.ollama_url = "http://localhost:11434/api/generate"
        
    def download_video(self, youtube_url: str, title: str = None) -> tuple[Path, Path]:
        """Download YouTube video and extract audio"""
        print(f"📥 Downloading video from: {youtube_url}")
        
        # Get video info first
        info_cmd = ["yt-dlp", "--get-title", "--get-id", youtube_url]
        try:
            result = subprocess.run(info_cmd, capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')
            video_title = lines[0] if not title else title
            video_id = lines[1]
        except:
            video_title = title or "unknown"
            video_id = hashlib.md5(youtube_url.encode()).hexdigest()[:8]
        
        # Create safe filename
        safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')[:100]  # Limit length
        
        video_file = self.dirs['video'] / f"{video_id}_{safe_title}.mp4"
        audio_file = self.dirs['audio'] / f"{video_id}_{safe_title}.mp3"
        
        # Download full video (needed for frame extraction)
        video_cmd = [
            "yt-dlp",
            "-f", "best[height<=1080]",  # Limit to 1080p for processing
            "-o", str(video_file),
            "--no-playlist",
            youtube_url
        ]
        
        try:
            print("  Downloading video...")
            subprocess.run(video_cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error downloading video: {e}")
            return None, None
        
        # Extract audio for transcription
        audio_cmd = [
            "ffmpeg",
            "-i", str(video_file),
            "-vn",
            "-acodec", "mp3",
            "-ab", "192k",
            "-ar", "44100",
            "-y",
            str(audio_file)
        ]
        
        try:
            print("  Extracting audio...")
            subprocess.run(audio_cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error extracting audio: {e}")
            return video_file, None
        
        print(f"✅ Downloaded: {video_file.name}")
        return video_file, audio_file
    
    def transcribe_audio(self, audio_file: Path, model_size: str = "large-v3") -> Dict:
        """Transcribe audio using Whisper"""
        print(f"🎤 Transcribing with Whisper {model_size}...")
        
        model = whisper.load_model(model_size)
        
        result = model.transcribe(
            str(audio_file),
            language="en",
            verbose=True,
            fp16=False,  # CPU mode
            word_timestamps=True  # Get word-level timestamps
        )
        
        # Save transcript
        transcript_file = self.dirs['transcripts'] / f"{audio_file.stem}.json"
        with open(transcript_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Save plain text version
        text_file = self.dirs['transcripts'] / f"{audio_file.stem}.txt"
        with open(text_file, 'w') as f:
            f.write(result['text'])
        
        print(f"✅ Transcript saved: {transcript_file.name}")
        return result
    
    def detect_code_frames(self, video_file: Path, sample_interval: int = 5) -> List[Dict]:
        """Extract frames that likely contain code"""
        print(f"🎬 Analyzing video for code frames...")
        
        cap = cv2.VideoCapture(str(video_file))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        code_frames = []
        frame_interval = int(fps * sample_interval)  # Sample every N seconds
        
        for frame_idx in range(0, total_frames, frame_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            # Check if frame likely contains code
            if self._is_code_frame(frame):
                timestamp = frame_idx / fps
                frame_info = {
                    'frame_idx': frame_idx,
                    'timestamp': timestamp,
                    'time_str': self._format_timestamp(timestamp)
                }
                
                # Save frame
                frame_filename = f"frame_{frame_idx:06d}_{int(timestamp)}s.png"
                frame_path = self.dirs['frames'] / frame_filename
                cv2.imwrite(str(frame_path), frame)
                
                frame_info['path'] = frame_path
                code_frames.append(frame_info)
                
                print(f"  Found code frame at {frame_info['time_str']}")
        
        cap.release()
        print(f"✅ Found {len(code_frames)} code frames")
        return code_frames
    
    def _is_code_frame(self, frame: np.ndarray) -> bool:
        """Detect if frame likely contains code using heuristics"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Check for characteristics of code editors:
        # 1. High contrast (dark or light theme)
        # 2. Horizontal lines (code lines)
        # 3. Monospace text patterns
        
        # Calculate histogram to check contrast
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        
        # Check if it's predominantly dark (dark theme) or light (light theme)
        dark_pixels = np.sum(hist[:50])
        light_pixels = np.sum(hist[200:])
        total_pixels = frame.shape[0] * frame.shape[1]
        
        is_high_contrast = (dark_pixels > total_pixels * 0.3) or (light_pixels > total_pixels * 0.3)
        
        # Detect horizontal edges (code lines)
        edges = cv2.Canny(gray, 50, 150)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
        
        # Count horizontal lines
        num_lines = cv2.countNonZero(horizontal_lines)
        has_many_lines = num_lines > (frame.shape[0] * 10)  # Threshold for line density
        
        # Look for text-like patterns (simplified)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        text_density = cv2.countNonZero(binary) / total_pixels
        has_text_pattern = 0.1 < text_density < 0.9
        
        return is_high_contrast and (has_many_lines or has_text_pattern)
    
    def extract_code_with_ollama(self, frame_path: Path, model: str = "gpt-oss:120b") -> str:
        """Use Ollama vision model to extract code from frame"""
        print(f"  🤖 Extracting code from {frame_path.name} using {model}...")
        
        # Convert image to base64
        with open(frame_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        prompt = """You are analyzing a screenshot from a programming tutorial video. 
        Extract any code visible in this image. 
        Format the code properly with correct indentation.
        If there are multiple code blocks, separate them clearly.
        If there's no code visible, respond with 'NO_CODE_FOUND'.
        
        Important: Only extract the actual code, not UI elements or comments about the code.
        """
        
        # Call Ollama API with image
        payload = {
            "model": model,
            "prompt": prompt,
            "images": [image_data],
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for accuracy
                "num_predict": 2000
            }
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'NO_CODE_FOUND')
            else:
                print(f"    ⚠️ Ollama returned status {response.status_code}")
                return "ERROR: Failed to extract code"
        except Exception as e:
            print(f"    ⚠️ Error calling Ollama: {e}")
            return "ERROR: " + str(e)
    
    def analyze_with_llm(self, transcript: Dict, extracted_code: List[Dict], model: str = "gpt-oss:120b") -> Dict:
        """Analyze transcript and code using LLM for comprehensive summary"""
        print(f"🧠 Analyzing content with {model}...")
        
        # Prepare context
        code_snippets = "\n\n---\n\n".join([
            f"Code at {item['time_str']}:\n{item['code']}" 
            for item in extracted_code if item.get('code') and item['code'] != 'NO_CODE_FOUND'
        ])
        
        transcript_text = transcript.get('text', '')[:10000]  # Limit transcript length
        
        prompt = f"""Analyze this programming tutorial video content and provide a comprehensive summary.

TRANSCRIPT (excerpt):
{transcript_text}

EXTRACTED CODE SNIPPETS:
{code_snippets}

Please provide:
1. Main Topic and Objectives
2. Key Concepts Explained
3. Code Implementation Steps (in order)
4. Important Code Patterns or Techniques
5. Best Practices Mentioned
6. Common Pitfalls or Warnings
7. Dependencies and Tools Used
8. Practical Applications

Format your response as a structured analysis that developers can use as a reference."""
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 4000
            }
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            if response.status_code == 200:
                result = response.json()
                return {
                    'analysis': result.get('response', ''),
                    'model': model,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'error': f"LLM returned status {response.status_code}"}
        except Exception as e:
            return {'error': str(e)}
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
    
    def process_video(self, youtube_url: str, title: str = None) -> Dict:
        """Complete processing pipeline"""
        print(f"\n{'='*60}")
        print(f"🚀 Processing Video: {youtube_url}")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        results = {
            'url': youtube_url,
            'title': title,
            'processing_time': None,
            'status': 'started'
        }
        
        # Step 1: Download video and audio
        video_file, audio_file = self.download_video(youtube_url, title)
        if not video_file or not audio_file:
            results['status'] = 'download_failed'
            return results
        
        results['video_file'] = str(video_file)
        results['audio_file'] = str(audio_file)
        
        # Step 2: Transcribe audio
        transcript = self.transcribe_audio(audio_file)
        results['transcript'] = {
            'text': transcript.get('text', ''),
            'duration': transcript.get('duration', 0),
            'language': transcript.get('language', 'en')
        }
        
        # Step 3: Extract code frames
        code_frames = self.detect_code_frames(video_file)
        results['code_frames'] = []
        
        # Step 4: Extract code from frames
        for frame_info in code_frames[:20]:  # Limit to 20 frames to avoid overload
            code = self.extract_code_with_ollama(frame_info['path'])
            frame_info['code'] = code
            results['code_frames'].append({
                'timestamp': frame_info['timestamp'],
                'time_str': frame_info['time_str'],
                'code': code if code != 'NO_CODE_FOUND' else None
            })
            time.sleep(1)  # Rate limiting for Ollama
        
        # Step 5: Comprehensive analysis
        analysis = self.analyze_with_llm(transcript, results['code_frames'])
        results['analysis'] = analysis
        
        # Step 6: Save complete results
        output_file = self.dirs['analysis'] / f"{video_file.stem}_complete.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Create markdown report
        self._create_markdown_report(results)
        
        # Calculate processing time
        results['processing_time'] = time.time() - start_time
        results['status'] = 'completed'
        
        print(f"\n✅ Processing complete in {results['processing_time']:.1f} seconds")
        print(f"📁 Results saved to: {output_file}")
        
        return results
    
    def _create_markdown_report(self, results: Dict) -> Path:
        """Create a markdown report from results"""
        video_name = Path(results.get('video_file', 'unknown')).stem
        report_file = self.dirs['analysis'] / f"{video_name}_report.md"
        
        with open(report_file, 'w') as f:
            f.write(f"# Video Analysis Report\n\n")
            f.write(f"**URL:** {results['url']}\n")
            f.write(f"**Title:** {results.get('title', 'N/A')}\n")
            f.write(f"**Duration:** {results['transcript'].get('duration', 0):.1f} seconds\n")
            processing_time = results.get('processing_time', 0)
            if processing_time is not None:
                f.write(f"**Processing Time:** {processing_time:.1f} seconds\n\n")
            else:
                f.write(f"**Processing Time:** Not available\n\n")
            
            f.write("## Transcript Summary\n\n")
            transcript_text = results['transcript']['text'][:1000]
            f.write(f"{transcript_text}...\n\n")
            
            f.write("## Extracted Code Snippets\n\n")
            for frame in results['code_frames']:
                if frame.get('code') and frame['code'] != 'NO_CODE_FOUND':
                    f.write(f"### Code at {frame['time_str']}\n\n")
                    f.write("```python\n")
                    f.write(frame['code'])
                    f.write("\n```\n\n")
            
            f.write("## LLM Analysis\n\n")
            if 'analysis' in results and 'analysis' in results['analysis']:
                f.write(results['analysis']['analysis'])
            else:
                f.write("Analysis not available.\n")
        
        print(f"📝 Markdown report saved: {report_file}")
        return report_file

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Process video with code extraction")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--title", help="Video title (optional)")
    parser.add_argument("--model", default="gpt-oss:120b", help="Ollama model to use")
    parser.add_argument("--whisper-model", default="large-v3", help="Whisper model size")
    parser.add_argument("--output-dir", default="docs/video-analysis", help="Output directory")
    
    args = parser.parse_args()
    
    processor = AdvancedVideoProcessor(output_dir=args.output_dir)
    
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code != 200:
            print("⚠️ Warning: Ollama doesn't seem to be running. Start it with: ollama serve")
            print("  Code extraction will fail without Ollama.")
    except:
        print("⚠️ Warning: Cannot connect to Ollama. Start it with: ollama serve")
    
    # Process the video
    results = processor.process_video(args.url, args.title)
    
    if results['status'] == 'completed':
        print("\n🎉 Success! Video processed successfully.")
    else:
        print(f"\n❌ Processing failed with status: {results['status']}")
        sys.exit(1)

if __name__ == "__main__":
    main()