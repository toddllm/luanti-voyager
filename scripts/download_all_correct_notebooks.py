#!/usr/bin/env python3
"""
Download ALL AI Makerspace notebooks with CORRECT URLs from the Awesome AIM Index
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
        'url': None,
        'note': 'No Code listed in AI Makerspace index'
    },
    {
        'issue': 22,
        'title': 'Planner Executor',
        'url': 'https://github.com/AI-Maker-Space/LangGraph-Event',  # Found LangGraph event which covers planning
        'type': 'github'
    },
    {
        'issue': 23,
        'title': 'Multi-Agent Swarm',
        'url': 'https://colab.research.google.com/drive/1NumpfFNIPxsyjmruJ3jzyxxX2HY8V0MO',
        'type': 'colab'
    },
    {
        'issue': 24,
        'title': 'MCP and A2A Protocols',
        'url': 'https://github.com/AI-Maker-Space/MCP-Event',  # MCP Event repo
        'type': 'github'
    },
    {
        'issue': 25,
        'title': 'Production RAG',
        'url': 'https://colab.research.google.com/drive/1KGVxiwc2zoY9v6f3IQfs8qJIZeGeMKAq',
        'type': 'colab'
    },
    {
        'issue': 26,
        'title': 'LLM Optimization',
        'url': 'https://github.com/AI-Maker-Space/vLLM-Event-AIM',  # vLLM optimization event
        'type': 'github'
    },
    {
        'issue': 27,
        'title': 'Agent Observability',
        'url': 'https://github.com/AI-Maker-Space/Building-with-Autogen-AIM',  # Has observability aspects
        'type': 'github'
    },
    {
        'issue': 28,
        'title': 'Guardrails',
        'url': 'https://colab.research.google.com/drive/1rnxxK3zY4dEX4T0SSUgIC1OgdOKfuqVB',
        'type': 'colab'
    },
    {
        'issue': 29,
        'title': 'Fine-tuning',
        'url': 'https://colab.research.google.com/drive/1oqd8PrUx_6NPlNCP2TLxMYn_z44rN_Ot',  # Fine-tuning notebook
        'type': 'colab'
    },
    {
        'issue': 30,
        'title': 'Agent Evaluation',
        'url': 'https://github.com/AI-Maker-Space/Production-RAG-AIM',  # Has RAGAS evaluation
        'type': 'github'
    }
]

def download_colab_notebook(url, output_path):
    """Download public Colab notebook"""
    match = re.search(r'/drive/([a-zA-Z0-9-_]+)', url)
    if not match:
        print(f"  ❌ Could not extract Colab file ID from URL")
        return False
        
    file_id = match.group(1)
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    print(f"  Downloading Colab notebook...")
    
    try:
        response = requests.get(download_url, timeout=30)
        
        if response.status_code == 200:
            try:
                notebook_data = response.json()
                if 'cells' in notebook_data or 'nbformat' in notebook_data:
                    with open(output_path, 'w') as f:
                        json.dump(notebook_data, f, indent=2)
                    print(f"  ✅ Downloaded: {output_path} ({len(response.content):,} bytes)")
                    return True
                else:
                    print(f"  ❌ Response is not a valid notebook")
                    return False
            except json.JSONDecodeError:
                print(f"  ❌ Response is not JSON (likely private)")
                return False
        else:
            print(f"  ❌ HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def download_github_notebooks(repo_url, output_dir, issue_num, title):
    """Download notebooks from GitHub repository"""
    # Extract owner/repo from URL
    match = re.search(r'github.com/([^/]+)/([^/]+)', repo_url)
    if not match:
        print(f"  ❌ Invalid GitHub URL")
        return False
        
    owner, repo = match.groups()
    
    # Search for .ipynb files in the repo
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    
    print(f"  Searching GitHub repo {owner}/{repo} for notebooks...")
    
    try:
        response = requests.get(api_url)
        if response.status_code != 200:
            print(f"  ❌ Could not access repo (may be private)")
            return False
            
        files = response.json()
        notebooks_found = []
        
        # Look for notebook files
        for file in files:
            if file['name'].endswith('.ipynb'):
                notebooks_found.append(file)
            elif file['type'] == 'dir' and file['name'] in ['notebooks', 'code', 'examples']:
                # Check subdirectories
                subdir_response = requests.get(file['url'])
                if subdir_response.status_code == 200:
                    subfiles = subdir_response.json()
                    for subfile in subfiles:
                        if subfile['name'].endswith('.ipynb'):
                            notebooks_found.append(subfile)
        
        if not notebooks_found:
            print(f"  ⚠️ No notebooks found in repo")
            return False
            
        # Download the first notebook found
        notebook = notebooks_found[0]
        download_url = notebook['download_url']
        
        print(f"  Found notebook: {notebook['name']}")
        response = requests.get(download_url)
        
        if response.status_code == 200:
            output_path = output_dir / f"{issue_num:02d}_{title.lower().replace(' ', '_')}.ipynb"
            with open(output_path, 'w') as f:
                f.write(response.text)
            print(f"  ✅ Downloaded: {output_path} ({len(response.content):,} bytes)")
            return True
        else:
            print(f"  ❌ Could not download notebook")
            return False
            
    except Exception as e:
        print(f"  ❌ Error accessing GitHub: {e}")
        return False

def main():
    notebook_dir = Path("docs/ai-makerspace-resources/notebooks")
    notebook_dir.mkdir(parents=True, exist_ok=True)
    
    print("Downloading ALL AI Makerspace Notebooks")
    print("=" * 60)
    
    success_count = 0
    no_notebook_count = 0
    failed_count = 0
    
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
        
        # Download based on type
        if nb.get('type') == 'github':
            if download_github_notebooks(nb['url'], notebook_dir, nb['issue'], nb['title']):
                success_count += 1
            else:
                failed_count += 1
        else:  # colab
            if download_colab_notebook(nb['url'], output_path):
                success_count += 1
            else:
                failed_count += 1
    
    print(f"\n{'=' * 60}")
    print(f"Summary:")
    print(f"  ✅ Downloaded: {success_count} notebooks")
    print(f"  ⚠️ No notebook: {no_notebook_count} (expected)")
    print(f"  ❌ Failed: {failed_count}")
    print(f"\nTotal notebooks available: {success_count}")
    
    # List all notebooks
    print(f"\nNotebooks in directory:")
    for file in sorted(notebook_dir.glob("*.ipynb")):
        size = file.stat().st_size
        print(f"  {file.name} ({size:,} bytes)")

if __name__ == "__main__":
    main()