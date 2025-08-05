#!/usr/bin/env python3
"""
Download and analyze MCP and A2A Event repositories
"""

import os
import subprocess
import json
from pathlib import Path
import shutil

repos = [
    {
        'issue': 24,
        'name': 'MCP-Event',
        'url': 'https://github.com/AI-Maker-Space/MCP-Event.git',
        'title': 'MCP Protocol'
    },
    {
        'issue': 24,
        'name': 'AIM-A2A-Event', 
        'url': 'https://github.com/AI-Maker-Space/AIM-A2A-Event.git',
        'title': 'A2A Protocol'
    }
]

def clone_repo(repo_info, base_dir):
    """Clone repository and analyze contents"""
    repo_name = repo_info['name']
    repo_path = base_dir / repo_name
    
    print(f"\n📦 Processing {repo_name}")
    print("=" * 50)
    
    # Clone if not exists
    if not repo_path.exists():
        print(f"Cloning {repo_info['url']}...")
        cmd = ['git', 'clone', repo_info['url'], str(repo_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Clone failed: {result.stderr}")
            return None
    else:
        print(f"✅ Repository already exists")
    
    # Analyze repository structure
    print(f"\n📂 Repository structure:")
    
    # Find Python files
    python_files = list(repo_path.rglob("*.py"))
    notebook_files = list(repo_path.rglob("*.ipynb"))
    
    print(f"  Python files: {len(python_files)}")
    print(f"  Notebooks: {len(notebook_files)}")
    
    # List key files
    key_files = []
    for pattern in ["*.py", "*.ipynb", "*.md", "requirements.txt", "Dockerfile"]:
        files = list(repo_path.rglob(pattern))
        key_files.extend(files)
    
    print(f"\n📄 Key files found:")
    for file in sorted(key_files)[:20]:  # Show first 20
        rel_path = file.relative_to(repo_path)
        size = file.stat().st_size
        print(f"  {rel_path} ({size:,} bytes)")
    
    return {
        'path': repo_path,
        'python_files': python_files,
        'notebook_files': notebook_files,
        'key_files': key_files
    }

def extract_code_samples(repo_info, repo_analysis):
    """Extract key code samples from repository"""
    samples = []
    
    # Get main Python files
    for py_file in repo_analysis['python_files'][:5]:  # First 5 Python files
        try:
            with open(py_file, 'r') as f:
                content = f.read()
                if len(content) > 100:  # Skip tiny files
                    samples.append({
                        'file': py_file.name,
                        'content': content[:1000],  # First 1000 chars
                        'full_size': len(content)
                    })
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    return samples

def create_combined_synthesis(mcp_analysis, a2a_analysis):
    """Create a combined notebook-style content for MCP and A2A"""
    
    # Create synthetic notebook content
    notebook_content = {
        "cells": []
    }
    
    # Add MCP code samples
    if mcp_analysis and mcp_analysis.get('samples'):
        notebook_content["cells"].append({
            "cell_type": "markdown",
            "source": "# MCP (Model Context Protocol) Implementation\n\nFrom AI-Maker-Space/MCP-Event repository"
        })
        
        for sample in mcp_analysis['samples'][:3]:
            notebook_content["cells"].append({
                "cell_type": "code",
                "source": sample['content']
            })
    
    # Add A2A code samples
    if a2a_analysis and a2a_analysis.get('samples'):
        notebook_content["cells"].append({
            "cell_type": "markdown", 
            "source": "# A2A (Agent-to-Agent) Protocol Implementation\n\nFrom AI-Maker-Space/AIM-A2A-Event repository"
        })
        
        for sample in a2a_analysis['samples'][:3]:
            notebook_content["cells"].append({
                "cell_type": "code",
                "source": sample['content']
            })
    
    return notebook_content

def main():
    base_dir = Path("docs/ai-makerspace-resources/repos")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    print("Downloading MCP and A2A Event Repositories")
    print("=" * 60)
    
    analyses = {}
    
    # Process each repository
    for repo in repos:
        analysis = clone_repo(repo, base_dir)
        if analysis:
            # Extract code samples
            samples = extract_code_samples(repo, analysis)
            analyses[repo['name']] = {
                'repo': repo,
                'analysis': analysis,
                'samples': samples
            }
            
            print(f"\n✅ Extracted {len(samples)} code samples from {repo['name']}")
    
    # Create combined notebook
    if 'MCP-Event' in analyses and 'AIM-A2A-Event' in analyses:
        print("\n📓 Creating combined notebook content...")
        
        notebook = create_combined_synthesis(
            analyses.get('MCP-Event'),
            analyses.get('AIM-A2A-Event')
        )
        
        # Save as notebook
        notebook_path = Path("docs/ai-makerspace-resources/notebooks/24_mcp_and_a2a_protocols.ipynb")
        with open(notebook_path, 'w') as f:
            json.dump(notebook, f, indent=2)
        
        print(f"✅ Created synthetic notebook: {notebook_path}")
        
        # Also save analysis summary
        summary_path = Path("docs/ai-makerspace-resources/notebooks/24_mcp_a2a_analysis.json")
        with open(summary_path, 'w') as f:
            json.dump({
                'mcp_files': len(analyses['MCP-Event']['analysis']['python_files']),
                'a2a_files': len(analyses['AIM-A2A-Event']['analysis']['python_files']),
                'total_samples': len(analyses['MCP-Event']['samples']) + len(analyses['AIM-A2A-Event']['samples']),
                'repos_analyzed': 2
            }, f, indent=2)
    
    print("\n" + "=" * 60)
    print("Repository analysis complete!")
    print("\nNext steps:")
    print("1. Review the extracted code samples")
    print("2. Run synthesis on the combined MCP/A2A content")
    print("3. Create implementation guide for game integration")

if __name__ == "__main__":
    main()