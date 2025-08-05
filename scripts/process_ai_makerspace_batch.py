#!/Users/tdeshane/luanti-voyager/.venv-whisper/bin/python3
"""
Batch process AI Makerspace resources:
1. Download videos
2. Transcribe with Whisper
3. Download notebooks
4. Synthesize with Ollama
5. Create implementation guides
"""

import os
import sys
import subprocess
import json
import requests
from pathlib import Path
from datetime import datetime
import re
import time

class AIResourceProcessor:
    def __init__(self, base_dir="docs/ai-makerspace-resources"):
        self.base_dir = Path(base_dir)
        self.audio_dir = self.base_dir / "audio"
        self.transcript_dir = self.base_dir / "transcripts"
        self.notebook_dir = self.base_dir / "notebooks"
        self.synthesis_dir = self.base_dir / "synthesis"
        self.guides_dir = self.base_dir / "implementation-guides"
        
        # Create directories
        for dir in [self.audio_dir, self.transcript_dir, self.notebook_dir, 
                   self.synthesis_dir, self.guides_dir]:
            dir.mkdir(parents=True, exist_ok=True)
    
    def download_video_audio(self, youtube_url, output_name):
        """Download audio from YouTube video"""
        output_path = self.audio_dir / f"{output_name}.mp3"
        
        if output_path.exists():
            print(f"Audio already exists: {output_path}")
            return output_path
            
        print(f"Downloading audio: {youtube_url}")
        
        cmd = [
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", str(output_path),
            "--no-playlist",
            youtube_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Downloaded: {output_path}")
            return output_path
        else:
            print(f"❌ Download failed: {result.stderr}")
            return None
    
    def transcribe_audio(self, audio_path, model="large-v3"):
        """Transcribe audio with Whisper"""
        transcript_path = self.transcript_dir / f"{audio_path.stem}.json"
        
        if transcript_path.exists():
            print(f"Transcript already exists: {transcript_path}")
            with open(transcript_path, 'r') as f:
                return json.load(f)
        
        print(f"Transcribing: {audio_path}")
        
        # Import whisper here to ensure it's in the right environment
        import whisper
        
        model_obj = whisper.load_model(model)
        result = model_obj.transcribe(
            str(audio_path),
            language="en",
            verbose=False,
            fp16=False
        )
        
        # Save transcript
        with open(transcript_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ Transcribed: {transcript_path}")
        return result
    
    def download_notebook(self, notebook_url, output_name):
        """Download Jupyter notebook from Colab or GitHub"""
        notebook_path = self.notebook_dir / f"{output_name}.ipynb"
        
        if notebook_path.exists():
            print(f"Notebook already exists: {notebook_path}")
            return notebook_path
        
        print(f"Downloading notebook: {notebook_url}")
        
        # Convert Colab URL to download URL
        if "colab.research.google.com" in notebook_url:
            # Extract file ID
            match = re.search(r'/drive/([a-zA-Z0-9-_]+)', notebook_url)
            if match:
                file_id = match.group(1)
                download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            else:
                print(f"❌ Could not extract file ID from Colab URL")
                return None
        else:
            download_url = notebook_url
        
        try:
            response = requests.get(download_url, timeout=30)
            if response.status_code == 200:
                with open(notebook_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Downloaded notebook: {notebook_path}")
                return notebook_path
            else:
                print(f"❌ Failed to download notebook: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error downloading notebook: {e}")
            return None
    
    def extract_notebook_code(self, notebook_path):
        """Extract code cells from notebook"""
        with open(notebook_path, 'r') as f:
            notebook = json.load(f)
        
        code_cells = []
        for cell in notebook.get('cells', []):
            if cell.get('cell_type') == 'code':
                source = ''.join(cell.get('source', []))
                if source.strip():
                    code_cells.append(source)
        
        return code_cells
    
    def synthesize_with_ollama(self, transcript, notebook_code, issue_title, model="qwen2.5-coder:32b"):
        """Use Ollama to create comprehensive synthesis"""
        print(f"Synthesizing with {model}...")
        
        # Prepare context
        context = {
            "issue_title": issue_title,
            "transcript_text": transcript.get('text', ''),
            "code_examples": notebook_code[:5] if notebook_code else []  # First 5 code cells
        }
        
        # Create prompt for Ollama
        prompt = f"""You are an expert developer creating an implementation guide for integrating "{issue_title}" into Luanti Voyager, a Minecraft-like game with AI agents.

Based on the following AI Makerspace session transcript and code examples, create a comprehensive implementation guide.

TRANSCRIPT EXCERPT (first 5000 chars):
{context['transcript_text'][:5000]}

NOTEBOOK CODE EXAMPLES:
{chr(10).join(f"```python\n{code}\n```" for code in context['code_examples'])}

Create a detailed implementation guide that includes:
1. Core concepts and how they apply to game agents
2. Step-by-step implementation plan
3. Code patterns adapted for Luanti
4. Integration points with existing codebase
5. Testing strategies
6. Performance considerations

Format as markdown suitable for developers."""
        
        # Call Ollama
        cmd = [
            "ollama", "run", model,
            "--verbose",
            prompt
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"❌ Ollama error: {result.stderr}")
                return None
        except subprocess.TimeoutExpired:
            print("⏱️ Ollama timed out after 5 minutes")
            return None
        except Exception as e:
            print(f"❌ Error calling Ollama: {e}")
            return None
    
    def process_resource(self, resource_info):
        """Process a single AI Makerspace resource"""
        issue_num = resource_info['issue']
        title = resource_info['title']
        youtube_url = resource_info.get('youtube_url')
        notebook_url = resource_info.get('notebook_url')
        
        print(f"\n{'='*60}")
        print(f"Processing Issue #{issue_num}: {title}")
        print(f"{'='*60}")
        
        # Step 1: Download and transcribe video
        transcript = None
        if youtube_url:
            audio_path = self.download_video_audio(youtube_url, f"{issue_num}_{title.lower().replace(' ', '_')}")
            if audio_path:
                transcript = self.transcribe_audio(audio_path)
        
        # Step 2: Download and process notebook
        notebook_code = []
        if notebook_url:
            notebook_path = self.download_notebook(notebook_url, f"{issue_num}_{title.lower().replace(' ', '_')}")
            if notebook_path:
                notebook_code = self.extract_notebook_code(notebook_path)
                print(f"📓 Extracted {len(notebook_code)} code cells from notebook")
        
        # Step 3: Synthesize with Ollama
        if transcript or notebook_code:
            synthesis = self.synthesize_with_ollama(
                transcript or {"text": ""}, 
                notebook_code, 
                title
            )
            
            if synthesis:
                # Save synthesis
                synthesis_path = self.synthesis_dir / f"{issue_num}_{title.lower().replace(' ', '_')}.md"
                with open(synthesis_path, 'w') as f:
                    f.write(f"# {title} - AI Synthesis\n\n")
                    f.write(f"Issue: #{issue_num}\n")
                    f.write(f"Generated: {datetime.now().isoformat()}\n\n")
                    f.write(synthesis)
                
                print(f"✅ Synthesis saved: {synthesis_path}")
                
                # Create implementation guide
                self.create_implementation_guide(issue_num, title, transcript, notebook_code, synthesis)
        
        return True
    
    def create_implementation_guide(self, issue_num, title, transcript, notebook_code, synthesis):
        """Create final implementation guide"""
        guide_path = self.guides_dir / f"{issue_num}_{title.lower().replace(' ', '_')}.md"
        
        with open(guide_path, 'w') as f:
            f.write(f"# {title} - Luanti Voyager Implementation Guide\n\n")
            f.write(f"Issue: #{issue_num}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            f.write("## Overview\n\n")
            f.write("This guide provides a comprehensive implementation plan ")
            f.write(f"for integrating {title} into Luanti Voyager.\n\n")
            
            if synthesis:
                f.write("## AI-Generated Implementation Plan\n\n")
                f.write(synthesis)
                f.write("\n\n")
            
            if notebook_code:
                f.write("## Key Code Examples from Notebook\n\n")
                for i, code in enumerate(notebook_code[:3]):
                    f.write(f"### Example {i+1}\n\n")
                    f.write("```python\n")
                    f.write(code)
                    f.write("\n```\n\n")
            
            f.write("## Next Steps\n\n")
            f.write("1. Review the generated implementation plan\n")
            f.write("2. Adapt code patterns to Luanti's architecture\n")
            f.write("3. Create tests for new functionality\n")
            f.write("4. Submit PR with implementation\n")
        
        print(f"✅ Implementation guide saved: {guide_path}")

def main():
    """Process Vector Memory resource as POC"""
    processor = AIResourceProcessor()
    
    # Vector Memory resource (Issue #21)
    resource = {
        'issue': 21,
        'title': 'Vector Memory',
        'youtube_url': 'https://youtu.be/XwUD9uXL0eg',
        'notebook_url': 'https://colab.research.google.com/drive/1vy73KW_Kz83nt9Sw8h8LM9GOPaA3gNST'
    }
    
    processor.process_resource(resource)
    
    print("\n✨ POC Complete! Check the generated files in docs/ai-makerspace-resources/")

if __name__ == "__main__":
    main()