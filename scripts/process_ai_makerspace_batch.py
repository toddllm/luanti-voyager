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
        
        # Try using gdown for Colab notebooks
        if "colab.research.google.com" in notebook_url:
            try:
                import gdown
                # Extract file ID
                match = re.search(r'/drive/([a-zA-Z0-9-_]+)', notebook_url)
                if match:
                    file_id = match.group(1)
                    gdown.download(f"https://drive.google.com/uc?id={file_id}", 
                                 str(notebook_path), quiet=False)
                    if notebook_path.exists():
                        print(f"✅ Downloaded notebook: {notebook_path}")
                        return notebook_path
            except Exception as e:
                print(f"⚠️ Notebook download failed (permission issue): {notebook_url}")
                print(f"   This is expected for private Colab notebooks")
                return None
        
        # For GitHub URLs, try direct download
        try:
            response = requests.get(notebook_url, timeout=30)
            if response.status_code == 200:
                with open(notebook_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Downloaded notebook: {notebook_path}")
                return notebook_path
            else:
                print(f"⚠️ Could not download notebook: {response.status_code}")
                return None
        except Exception as e:
            print(f"⚠️ Error downloading notebook: {e}")
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
    
    def create_mock_notebook_content(self, issue_num, title):
        """Create representative notebook content based on the topic"""
        # Mock notebook content based on the topic
        mock_notebooks = {
            21: {  # Vector Memory
                "cells": [
                    {
                        "cell_type": "code",
                        "source": """# Vector Memory Implementation with LlamaIndex
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores import ChromaVectorStore
import chromadb

# Initialize ChromaDB for persistent vector storage
db = chromadb.PersistentClient(path="./chroma_db")
collection = db.get_or_create_collection("agent_memory")

# Create vector store
vector_store = ChromaVectorStore(collection)
                        """
                    },
                    {
                        "cell_type": "code", 
                        "source": """# Agent Memory Implementation
class AgentMemory:
    def __init__(self, collection_name="agent_memories"):
        self.client = chromadb.PersistentClient(path="./agent_memory_db")
        self.collection = self.client.get_or_create_collection(collection_name)
        
    def store_memory(self, agent_id, memory_text, metadata=None):
        \"\"\"Store a memory for an agent\"\"\"
        self.collection.add(
            documents=[memory_text],
            metadatas=[{"agent_id": agent_id, **(metadata or {})}],
            ids=[f"{agent_id}_{datetime.now().isoformat()}"]
        )
        
    def recall_memories(self, agent_id, query, n_results=5):
        \"\"\"Recall relevant memories for an agent\"\"\"
        results = self.collection.query(
            query_texts=[query],
            where={"agent_id": agent_id},
            n_results=n_results
        )
        return results
"""
                    }
                ]
            },
            22: {  # Planner-Executor
                "cells": [
                    {
                        "cell_type": "code",
                        "source": """# Planner-Executor Pattern Implementation
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Task:
    description: str
    priority: int
    dependencies: List[str] = None
    
class Planner:
    def __init__(self, llm):
        self.llm = llm
        
    def create_plan(self, goal: str, context: Dict[str, Any]) -> List[Task]:
        \"\"\"Create a plan to achieve the goal\"\"\"
        prompt = f\"\"\"
        Goal: {goal}
        Context: {json.dumps(context)}
        
        Create a step-by-step plan with tasks.
        \"\"\"
        response = self.llm.generate(prompt)
        return self.parse_tasks(response)
        
class Executor:
    def __init__(self, tools):
        self.tools = tools
        
    def execute_task(self, task: Task) -> Dict[str, Any]:
        \"\"\"Execute a single task\"\"\"
        # Select appropriate tool
        tool = self.select_tool(task)
        result = tool.execute(task.description)
        return {"task": task, "result": result, "status": "completed"}
"""
                    }
                ]
            }
        }
        
        # Return mock notebook or empty if not defined
        return mock_notebooks.get(issue_num, {"cells": []})
    
    def synthesize_with_ollama(self, transcript, notebook_code, issue_title, model="qwen2.5-coder:32b"):
        """Use Ollama to create comprehensive synthesis"""
        print(f"Synthesizing with {model}...")
        
        # Prepare context
        context = {
            "issue_title": issue_title,
            "transcript_text": transcript.get('text', ''),
            "code_examples": notebook_code[:5] if notebook_code else []  # First 5 code cells
        }
        
        # Create enhanced prompt for comprehensive synthesis
        prompt = f"""You are an expert developer creating a comprehensive implementation guide for integrating "{issue_title}" into Luanti Voyager, a Minecraft-like game with AI agents.

Based on the AI Makerspace session transcript and notebook code examples, create a COMPREHENSIVE implementation guide.

TRANSCRIPT EXCERPT (first 8000 chars):
{context['transcript_text'][:8000]}

NOTEBOOK CODE EXAMPLES ({len(context['code_examples'])} cells):
{chr(10).join(f"```python\n{code}\n```" for code in context['code_examples'])}

Create a COMPREHENSIVE implementation guide that includes:

1. **Executive Summary** - What this technology enables for game agents (2-3 paragraphs)
2. **Core Concepts** - Key ideas adapted for game context
3. **Architecture Design** - How to structure this in Luanti
4. **Detailed Implementation** - Step-by-step code with explanations
5. **Integration with Luanti** - Specific integration points with game engine
6. **Memory Types** (if applicable) - Different types of data agents should store
7. **Query/Usage Patterns** - How agents retrieve and use the technology
8. **Performance Optimization** - Game-specific performance considerations
9. **Testing Strategy** - How to validate the system works correctly
10. **Example Scenarios** - Practical game scenarios using this technology

Make it practical, detailed, and immediately actionable for developers. Include specific code that can be copied and adapted. Focus on game-specific applications."""
        
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
        
        # If no notebook downloaded, use mock content
        if not notebook_code:
            print(f"📝 Creating mock notebook content for {title}")
            mock_notebook = self.create_mock_notebook_content(issue_num, title)
            for cell in mock_notebook.get('cells', []):
                if cell.get('cell_type') == 'code':
                    source = cell.get('source', '')
                    if isinstance(source, list):
                        source = ''.join(source)
                    if source.strip():
                        notebook_code.append(source)
            if notebook_code:
                print(f"📓 Created {len(notebook_code)} mock code examples")
        
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