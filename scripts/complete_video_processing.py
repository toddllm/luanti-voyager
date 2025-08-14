#!/usr/bin/env python3
"""
Complete the video processing that crashed - extract code from frames and generate analysis
"""

import json
import requests
import base64
from pathlib import Path
import time

def extract_code_from_frames(frames_dir, json_file, limit=20):
    """Extract code from the detected frames using Ollama"""
    
    # Load existing results
    with open(json_file, 'r') as f:
        results = json.load(f)
    
    # Get list of frame files
    frames = sorted(Path(frames_dir).glob("*.png"))[:limit]
    
    print(f"Found {len(frames)} frames to process (limiting to {limit})")
    
    code_frames = []
    ollama_url = "http://localhost:11434/api/generate"
    
    for i, frame_path in enumerate(frames):
        print(f"Processing frame {i+1}/{len(frames)}: {frame_path.name}")
        
        # Extract timestamp from filename (e.g., frame_000150_5s.png)
        parts = frame_path.stem.split('_')
        if len(parts) >= 3:
            timestamp = int(parts[2].replace('s', ''))
        else:
            timestamp = i * 5
        
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
        
        payload = {
            "model": "gpt-oss:120b",
            "prompt": prompt,
            "images": [image_data],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 2000
            }
        }
        
        try:
            response = requests.post(ollama_url, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                code = result.get('response', 'NO_CODE_FOUND')
                if code != 'NO_CODE_FOUND' and code != 'ERROR: Failed to extract code':
                    code_frames.append({
                        'timestamp': timestamp,
                        'time_str': f"{timestamp//60:02d}:{timestamp%60:02d}",
                        'code': code,
                        'frame': frame_path.name
                    })
                    print(f"  ✓ Extracted code from frame")
                else:
                    print(f"  - No code found in frame")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        time.sleep(1)  # Rate limiting
    
    # Update results
    results['code_frames'] = code_frames
    
    # Analyze with LLM
    print("\nAnalyzing content with LLM...")
    analysis = analyze_content(results['transcript']['text'][:10000], code_frames)
    results['analysis'] = analysis
    results['status'] = 'completed'
    
    # Save updated results
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Saved results to {json_file}")
    
    # Create markdown report
    create_report(results, json_file.parent)
    
    return results

def analyze_content(transcript_text, code_frames):
    """Analyze transcript and code using LLM"""
    
    code_snippets = "\n\n---\n\n".join([
        f"Code at {item['time_str']}:\n{item['code']}" 
        for item in code_frames if item.get('code')
    ])
    
    prompt = f"""Analyze this programming tutorial video content and provide a comprehensive summary.

TRANSCRIPT (excerpt):
{transcript_text}

EXTRACTED CODE SNIPPETS:
{code_snippets if code_snippets else "No code snippets were extracted from the video frames."}

The video is about GPT-OSS (GPT Open Source Software) from OpenAI, discussing the Harmony Response Format and open weight reasoning models.

Please provide:
1. Main Topic and Objectives
2. Key Concepts Explained
3. Code Implementation Steps (if any)
4. Important Patterns or Techniques
5. Best Practices Mentioned
6. Tools and Technologies Discussed
7. Practical Applications

Format your response as a structured analysis that developers can use as a reference."""
    
    ollama_url = "http://localhost:11434/api/generate"
    payload = {
        "model": "gpt-oss:120b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 4000
        }
    }
    
    try:
        response = requests.post(ollama_url, json=payload, timeout=120)
        if response.status_code == 200:
            result = response.json()
            return {
                'analysis': result.get('response', ''),
                'model': 'gpt-oss:120b',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
    except Exception as e:
        return {'error': str(e)}
    
    return {'error': 'Failed to analyze'}

def create_report(results, output_dir):
    """Create markdown report"""
    
    report_file = output_dir / "nyb3TnUkwE8_Building_Production_Ready_Multi_Agent_Systems_report.md"
    
    with open(report_file, 'w') as f:
        f.write("# Video Analysis Report\n\n")
        f.write(f"**URL:** {results.get('url', 'N/A')}\n")
        f.write(f"**Title:** GPT-OSS - Open Source Software LLM from OpenAI\n")
        f.write(f"**Actual Topic:** GPT-OSS, Harmony Response Format, Open Weight Reasoning Models\n")
        f.write(f"**Duration:** ~63 minutes (based on transcript)\n\n")
        
        f.write("## Transcript Summary\n\n")
        transcript_text = results['transcript']['text'][:1500]
        f.write(f"{transcript_text}...\n\n")
        
        if results.get('code_frames'):
            f.write("## Extracted Code Snippets\n\n")
            for frame in results['code_frames'][:10]:
                f.write(f"### Code at {frame['time_str']}\n\n")
                f.write("```python\n")
                f.write(frame['code'][:500])
                f.write("\n```\n\n")
        else:
            f.write("## Code Extraction\n\n")
            f.write("No code snippets were successfully extracted from the video frames.\n\n")
        
        f.write("## LLM Analysis\n\n")
        if 'analysis' in results and isinstance(results['analysis'], dict):
            analysis_text = results['analysis'].get('analysis', 'Analysis not available.')
            f.write(analysis_text)
        else:
            f.write("Analysis pending or not available.\n")
    
    print(f"✅ Report saved to {report_file}")

def main():
    base_dir = Path("docs/video-analysis/multi-agent-systems")
    json_file = base_dir / "analysis" / "nyb3TnUkwE8_Building_Production_Ready_Multi_Agent_Systems_complete.json"
    frames_dir = base_dir / "frames"
    
    if not json_file.exists():
        print("❌ JSON file not found")
        return
    
    print("🔄 Completing video processing...")
    print("=" * 60)
    
    # Process frames and complete analysis
    extract_code_from_frames(frames_dir, json_file, limit=10)  # Process first 10 frames
    
    print("\n✨ Processing complete!")
    print(f"View report: cat {base_dir}/analysis/*_report.md")

if __name__ == "__main__":
    main()