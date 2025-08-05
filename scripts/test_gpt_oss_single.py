#!/usr/bin/env python3
"""
Test GPT-OSS with a single AI Makerspace topic
"""

import subprocess
import json
from pathlib import Path

# Test with Multi-Agent Swarm which has a real notebook
topic = {
    "issue_num": 23,
    "title": "Multi-Agent Swarm",
    "youtube_url": "https://www.youtube.com/watch?v=l5bp5VD7t_4",
    "notebook_url": "https://github.com/AI-Maker-Space/AIM-Swarm-Lab/blob/main/Swarm_Agent_Notebook_Aug8.ipynb"
}

# Load transcript
transcript_path = Path("docs/ai-makerspace-resources/transcripts/23_multi-agent_swarm.json")
if transcript_path.exists():
    with open(transcript_path) as f:
        transcript = json.load(f)
    print(f"✅ Loaded transcript with {len(transcript.get('text', ''))} characters")
else:
    print("❌ No transcript found")
    exit(1)

# Load notebook
notebook_path = Path("docs/ai-makerspace-resources/notebooks/23_multi-agent_swarm.ipynb")
notebook_code = []
if notebook_path.exists():
    with open(notebook_path) as f:
        notebook = json.load(f)
    
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = ''.join(cell.get('source', []))
            if source.strip():
                notebook_code.append(source)
    
    print(f"✅ Loaded {len(notebook_code)} code cells from notebook")

# Create a simple prompt
prompt = f"""You are an expert game developer creating an implementation guide for integrating "Multi-Agent Swarm" into Luanti Voyager, an open-source Minecraft-like game with AI agents.

Based on the following transcript excerpt and notebook code, create a concise implementation guide.

TRANSCRIPT (first 2000 chars):
{transcript.get('text', '')[:2000]}

NOTEBOOK CODE (first 3 examples):
{chr(10).join(f"```python\\n{code[:200]}\\n```" for code in notebook_code[:3])}

Create a SHORT implementation guide (max 500 words) that includes:
1. Core concept in 2-3 sentences
2. Basic implementation approach for game agents
3. One simple code example

Keep it concise and practical."""

print("\n🤖 Testing gpt-oss:20b with simple prompt...")
print(f"📝 Prompt length: {len(prompt)} characters")

# Test with gpt-oss
cmd = ["ollama", "run", "gpt-oss:20b", prompt]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode == 0:
        print("\n✅ Success! Output:")
        print("-" * 60)
        print(result.stdout)
        print("-" * 60)
        print(f"Output length: {len(result.stdout)} characters")
    else:
        print(f"❌ Error: {result.stderr}")
except subprocess.TimeoutExpired:
    print("⏱️ Timed out after 5 minutes")
except Exception as e:
    print(f"❌ Exception: {e}")