#!/usr/bin/env python3
"""
Update GitHub issues with correct notebook URLs
"""

import subprocess
import json

# Correct information for each issue
updates = [
    {
        'issue': 21,
        'title': 'Vector Memory',
        'update': 'No notebook provided in AI Makerspace index (listed as "No Code")'
    },
    {
        'issue': 23,
        'title': 'Multi-Agent Swarm',
        'notebook_url': 'https://colab.research.google.com/drive/1NumpfFNIPxsyjmruJ3jzyxxX2HY8V0MO',
        'update': 'Correct notebook URL found and downloaded'
    },
    {
        'issue': 25,
        'title': 'Production RAG',
        'notebook_url': 'https://colab.research.google.com/drive/1KGVxiwc2zoY9v6f3IQfs8qJIZeGeMKAq',
        'update': 'Correct notebook URL found and downloaded'
    },
    {
        'issue': 26,
        'title': 'LLM Optimization',
        'notebook_url': 'https://github.com/AI-Maker-Space/vLLM-Event-AIM',
        'update': 'Found vLLM notebook in GitHub repo'
    },
    {
        'issue': 28,
        'title': 'Guardrails',
        'notebook_url': 'https://colab.research.google.com/drive/1rnxxK3zY4dEX4T0SSUgIC1OgdOKfuqVB',
        'update': 'Correct notebook URL found and downloaded'
    }
]

def update_issue(issue_num, update_info):
    """Update a GitHub issue with correct information"""
    print(f"\nUpdating Issue #{issue_num}: {update_info.get('title', '')}")
    
    # Get current issue body
    cmd = f"gh issue view {issue_num} --json body"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  ❌ Failed to get issue: {result.stderr}")
        return False
    
    current_body = json.loads(result.stdout)['body']
    
    # Add update note
    updated_body = current_body + f"\n\n---\n## Update: Correct Notebook Information\n\n"
    
    if 'notebook_url' in update_info:
        updated_body += f"✅ **Correct Notebook URL**: {update_info['notebook_url']}\n\n"
    
    updated_body += f"**Status**: {update_info['update']}\n\n"
    updated_body += "*(Updated after verifying against AI-Maker-Space/Awesome-AIM-Index)*"
    
    # Update the issue
    cmd = ['gh', 'issue', 'edit', str(issue_num), '--body', updated_body]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"  ✅ Updated successfully")
        return True
    else:
        print(f"  ❌ Update failed: {result.stderr}")
        return False

def main():
    print("Updating GitHub Issues with Correct Notebook URLs")
    print("=" * 60)
    
    success_count = 0
    
    for update in updates:
        if update_issue(update['issue'], update):
            success_count += 1
    
    print(f"\n{'=' * 60}")
    print(f"Updated {success_count}/{len(updates)} issues")
    
    print("\nNote: Issues not updated either:")
    print("  - Already have correct URLs")
    print("  - No notebooks exist for that topic")
    print("  - Are private/inaccessible repos")

if __name__ == "__main__":
    main()