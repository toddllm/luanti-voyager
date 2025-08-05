#!/usr/bin/env python3
"""
Download AI Makerspace notebooks from GitHub and Colab
"""

import os
import re
import json
import requests
from pathlib import Path
from datetime import datetime

# Notebook URLs from the issues
notebooks = [
    {
        'issue': 21,
        'title': 'Vector Memory',
        'url': 'https://colab.research.google.com/drive/1vy73KW_Kz83nt9Sw8h8LM9GOPaA3gNST'
    },
    {
        'issue': 22,
        'title': 'Planner Executor',
        'url': 'https://github.com/ruvnet/AI-Makerspace/blob/main/12-2024/Week-1/Notebook_1_Planner_Executor.ipynb'
    },
    {
        'issue': 23,
        'title': 'Multi-Agent Swarm',
        'url': 'https://colab.research.google.com/drive/1zM3aeD23XcJCBL0Y3hGBEfBq0k6WGVdZ'
    },
    {
        'issue': 24,
        'title': 'MCP and A2A Protocols',
        'url': 'https://github.com/ruvnet/AI-Makerspace/blob/main/11-2024/Week-3/Notebook_3_MCP_A2A.ipynb'
    },
    {
        'issue': 25,
        'title': 'Production RAG',
        'url': 'https://colab.research.google.com/drive/1-vEMKHQ9G4p3vHO-a9rTdgQjTcQJlhBS'
    },
    {
        'issue': 26,
        'title': 'LLM Optimization',
        'url': 'https://github.com/ruvnet/AI-Makerspace/blob/main/11-2024/Week-1/Notebook_1_vLLM_Optimization.ipynb'
    },
    {
        'issue': 27,
        'title': 'Agent Observability',
        'url': 'https://colab.research.google.com/drive/1tcD_U3rTDPBKXQjT8Y90lLnSJ3VJfDg7'
    },
    {
        'issue': 28,
        'title': 'Guardrails',
        'url': 'https://github.com/ruvnet/AI-Makerspace/blob/main/10-2024/Week-3/Notebook_3_Guardrails.ipynb'
    },
    {
        'issue': 29,
        'title': 'Fine-tuning',
        'url': 'https://colab.research.google.com/drive/17xQ6nCgcvC1xq7ER4kZp4HCN3sLLVJoN'
    },
    {
        'issue': 30,
        'title': 'Agent Evaluation',
        'url': 'https://github.com/ruvnet/AI-Makerspace/blob/main/09-2024/Week-4/Notebook_4_RAGAS_Evaluation.ipynb'
    }
]

def download_github_notebook(url, output_path):
    """Download notebook from GitHub"""
    # Convert blob URL to raw URL
    raw_url = url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
    
    print(f"  Downloading from GitHub: {raw_url}")
    response = requests.get(raw_url)
    
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"  ✅ Downloaded: {output_path}")
        return True
    else:
        print(f"  ❌ Failed to download: {response.status_code}")
        return False

def attempt_colab_download(url, output_path):
    """Attempt to download Colab notebook (usually fails due to permissions)"""
    # Extract file ID
    match = re.search(r'/drive/([a-zA-Z0-9-_]+)', url)
    if not match:
        print(f"  ❌ Could not extract Colab file ID")
        return False
        
    file_id = match.group(1)
    
    # Try different download methods
    methods = [
        f"https://drive.google.com/uc?export=download&id={file_id}",
        f"https://drive.google.com/uc?id={file_id}",
        f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    ]
    
    for method_url in methods:
        print(f"  Trying: {method_url}")
        try:
            response = requests.get(method_url, timeout=10)
            if response.status_code == 200 and 'text/html' not in response.headers.get('content-type', ''):
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"  ✅ Downloaded: {output_path}")
                return True
        except Exception as e:
            print(f"  ❌ Method failed: {e}")
    
    print(f"  ❌ All Colab download methods failed (expected for private notebooks)")
    return False

def create_public_notebook_reference(notebook_info, output_path):
    """Create a reference file for notebooks we can't download"""
    reference = {
        "title": notebook_info['title'],
        "issue": notebook_info['issue'],
        "url": notebook_info['url'],
        "type": "colab" if "colab" in notebook_info['url'] else "github",
        "status": "private_or_restricted",
        "created": datetime.now().isoformat(),
        "note": "Could not download automatically. Please manually export from Colab or request access."
    }
    
    with open(output_path.with_suffix('.json'), 'w') as f:
        json.dump(reference, f, indent=2)
    
    print(f"  📝 Created reference file: {output_path.with_suffix('.json')}")

def main():
    # Create notebooks directory
    notebook_dir = Path("docs/ai-makerspace-resources/notebooks")
    notebook_dir.mkdir(parents=True, exist_ok=True)
    
    print("Downloading AI Makerspace Notebooks")
    print("=" * 60)
    
    success_count = 0
    
    for nb in notebooks:
        print(f"\n[{nb['issue']}] {nb['title']}")
        output_path = notebook_dir / f"{nb['issue']:02d}_{nb['title'].lower().replace(' ', '_')}.ipynb"
        
        if output_path.exists():
            print(f"  ✅ Already exists: {output_path}")
            success_count += 1
            continue
        
        # Try to download
        if 'github.com' in nb['url']:
            if download_github_notebook(nb['url'], output_path):
                success_count += 1
            else:
                create_public_notebook_reference(nb, output_path)
        else:  # Colab
            if not attempt_colab_download(nb['url'], output_path):
                create_public_notebook_reference(nb, output_path)
    
    print(f"\n{'=' * 60}")
    print(f"Summary: Downloaded {success_count}/{len(notebooks)} notebooks")
    print(f"Created reference files for restricted notebooks")
    
    # List what we have
    print(f"\nNotebook directory contents:")
    for file in sorted(notebook_dir.iterdir()):
        size = file.stat().st_size
        print(f"  {file.name} ({size:,} bytes)")

if __name__ == "__main__":
    main()