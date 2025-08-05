#!/usr/bin/env python3
"""
Get YouTube video descriptions to find notebook links
"""

import subprocess
import re

# YouTube URLs for the 6 missing notebooks
videos = [
    {
        'issue': 21,
        'title': 'Vector Memory',
        'url': 'https://youtu.be/XwUD9uXL0eg'
    },
    {
        'issue': 22,
        'title': 'Planner Executor',
        'url': 'https://www.youtube.com/watch?v=PsjMHb4nl24'
    },
    {
        'issue': 24,
        'title': 'MCP and A2A Protocols',
        'url': 'https://www.youtube.com/watch?v=uDYHn1WlqaE'
    },
    {
        'issue': 27,
        'title': 'Agent Observability',
        'url': 'https://www.youtube.com/watch?v=Ibd0kRTL4oA'
    },
    {
        'issue': 29,
        'title': 'Fine-tuning',
        'url': 'https://www.youtube.com/watch?v=FdBCMJn6NaI'
    },
    {
        'issue': 30,
        'title': 'Agent Evaluation',
        'url': 'https://www.youtube.com/watch?v=2lN0LQ_6WSc'
    }
]

def get_video_info(url):
    """Use yt-dlp to get video description"""
    cmd = ['yt-dlp', '--dump-json', '--no-playlist', url]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            return data.get('description', '')
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def find_notebook_links(description):
    """Find Colab and GitHub links in description"""
    links = []
    
    # Patterns to find
    patterns = [
        r'https://colab\.research\.google\.com/[^\s\)]+',
        r'https://github\.com/[^\s\)]+',
        r'https://drive\.google\.com/[^\s\)]+',
        r'https://tinyurl\.com/[^\s\)]+'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, description)
        links.extend(matches)
    
    return links

def main():
    print("Checking YouTube Video Descriptions for Notebook Links")
    print("=" * 60)
    
    for video in videos:
        print(f"\n[{video['issue']}] {video['title']}")
        print(f"Video: {video['url']}")
        
        description = get_video_info(video['url'])
        
        if description:
            print(f"Description length: {len(description)} chars")
            
            # Find links
            links = find_notebook_links(description)
            
            if links:
                print("Found links:")
                for link in links:
                    if 'colab' in link or 'github' in link or 'notebook' in link.lower():
                        print(f"  📓 {link}")
                    else:
                        print(f"  🔗 {link}")
            else:
                print("  ❌ No notebook links found")
                
            # Show first part of description
            print("\nDescription preview:")
            print(description[:300] + "...")
        else:
            print("  ❌ Could not get description")
    
    print("\n" + "=" * 60)
    print("Note: Some links might be in pinned comments, which require browser access")

if __name__ == "__main__":
    main()