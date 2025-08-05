#!/usr/bin/env python3
"""
Download AI Makerspace notebooks with CORRECT URLs from the Awesome AIM Index
"""

import os
import re
import json
import requests
from pathlib import Path
from datetime import datetime

# CORRECTED notebook URLs from AI-Maker-Space/Awesome-AIM-Index
notebooks = [
    {
        'issue': 21,
        'title': 'Vector Memory',
        'url': None,  # Listed as "No Code" in the index
        'note': 'No notebook provided in AI Makerspace index'
    },
    {
        'issue': 22,
        'title': 'Planner Executor',
        'url': None,  # Need to find correct URL
        'note': 'Need to check AI Makerspace index'
    },
    {
        'issue': 23,
        'title': 'Multi-Agent Swarm',
        'url': 'https://colab.research.google.com/drive/1NumpfFNIPxsyjmruJ3jzyxxX2HY8V0MO'
    },
    {
        'issue': 24,
        'title': 'MCP and A2A Protocols',
        'url': None,  # Need to find correct URL
        'note': 'Need to check AI Makerspace index'
    },
    {
        'issue': 25,
        'title': 'Production RAG',
        'url': 'https://colab.research.google.com/drive/1KGVxiwc2zoY9v6f3IQfs8qJIZeGeMKAq'
    },
    {
        'issue': 26,
        'title': 'LLM Optimization',
        'url': None,  # Need to find correct URL
        'note': 'Need to check AI Makerspace index'
    },
    {
        'issue': 27,
        'title': 'Agent Observability',
        'url': None,  # Not found in index
        'note': 'No notebook found in AI Makerspace index'
    },
    {
        'issue': 28,
        'title': 'Guardrails',
        'url': 'https://colab.research.google.com/drive/1rnxxK3zY4dEX4T0SSUgIC1OgdOKfuqVB'
    },
    {
        'issue': 29,
        'title': 'Fine-tuning',
        'url': None,  # Need to find correct URL
        'note': 'Need to check AI Makerspace index'
    },
    {
        'issue': 30,
        'title': 'Agent Evaluation',
        'url': None,  # Need to find correct URL
        'note': 'Need to check AI Makerspace index'
    }
]

def download_colab_notebook(url, output_path):
    """Download public Colab notebook"""
    # Extract file ID
    match = re.search(r'/drive/([a-zA-Z0-9-_]+)', url)
    if not match:
        print(f"  ❌ Could not extract Colab file ID from URL")
        return False
        
    file_id = match.group(1)
    
    # Try the export URL for public Colab notebooks
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    print(f"  Attempting download from: {download_url}")
    
    try:
        response = requests.get(download_url, timeout=30)
        
        # Check if we got a notebook (JSON) or HTML error page
        if response.status_code == 200:
            try:
                # Try to parse as JSON to verify it's a notebook
                notebook_data = response.json()
                if 'cells' in notebook_data or 'nbformat' in notebook_data:
                    with open(output_path, 'w') as f:
                        json.dump(notebook_data, f, indent=2)
                    print(f"  ✅ Downloaded: {output_path}")
                    return True
                else:
                    print(f"  ❌ Response is not a valid notebook")
                    return False
            except json.JSONDecodeError:
                print(f"  ❌ Response is not JSON (likely an error page)")
                return False
        else:
            print(f"  ❌ HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    # Create notebooks directory
    notebook_dir = Path("docs/ai-makerspace-resources/notebooks")
    notebook_dir.mkdir(parents=True, exist_ok=True)
    
    print("Downloading AI Makerspace Notebooks (Corrected URLs)")
    print("=" * 60)
    
    success_count = 0
    no_notebook_count = 0
    
    for nb in notebooks:
        print(f"\n[{nb['issue']}] {nb['title']}")
        
        if nb['url'] is None:
            print(f"  ⚠️ {nb.get('note', 'No URL available')}")
            no_notebook_count += 1
            continue
            
        output_path = notebook_dir / f"{nb['issue']:02d}_{nb['title'].lower().replace(' ', '_')}.ipynb"
        
        if output_path.exists():
            print(f"  ✅ Already exists: {output_path}")
            success_count += 1
            continue
        
        # Try to download
        if download_colab_notebook(nb['url'], output_path):
            success_count += 1
    
    print(f"\n{'=' * 60}")
    print(f"Summary:")
    print(f"  Downloaded: {success_count} notebooks")
    print(f"  No notebook available: {no_notebook_count}")
    print(f"  Need to check: {len(notebooks) - success_count - no_notebook_count}")
    
    print(f"\nNext steps:")
    print(f"1. Check AI-Maker-Space/Awesome-AIM-Index for missing notebook URLs")
    print(f"2. Some sessions may genuinely have no code notebooks")
    print(f"3. Test one of the correct URLs to verify download method")

if __name__ == "__main__":
    main()