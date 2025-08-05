#!/usr/bin/env python3
"""
Re-process ONLY the resources that have real notebooks
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Resources with actual notebooks
resources_with_notebooks = [
    {
        'issue': 23,
        'title': 'Multi-Agent Swarm',
        'youtube_url': 'https://www.youtube.com/watch?v=M-FKvHA0tVw',
    },
    {
        'issue': 25,
        'title': 'Production RAG',
        'youtube_url': 'https://www.youtube.com/watch?v=85BIMT9X38Q',
    },
    {
        'issue': 26,
        'title': 'LLM Optimization',
        'youtube_url': 'https://www.youtube.com/watch?v=6xEW0TDROA8',
    },
    {
        'issue': 28,
        'title': 'Guardrails',
        'youtube_url': 'https://www.youtube.com/watch?v=p-gpZg1kH7U',
    }
]

def main():
    print(f"\n{'='*60}")
    print(f"Re-processing Resources with Real Notebooks")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    print(f"Processing {len(resources_with_notebooks)} resources with notebooks...")
    print("This will use real notebook code instead of mock content.\n")
    
    log_file = Path(f"logs/notebook_reprocess_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    log_file.parent.mkdir(exist_ok=True)
    
    success_count = 0
    
    # Process each resource
    for i, resource in enumerate(resources_with_notebooks, 1):
        print(f"[{i}/{len(resources_with_notebooks)}] Re-processing {resource['title']}...")
        
        # Create command to process this resource
        cmd = [sys.executable, "scripts/enhanced_batch_processor.py"]
        
        # Pass resource data via environment variables
        env = {
            **subprocess.os.environ,
            'RESOURCE_ISSUE': str(resource['issue']),
            'RESOURCE_TITLE': resource['title'],
            'RESOURCE_YOUTUBE': resource.get('youtube_url', ''),
            'RESOURCE_NOTEBOOK': ''  # Not used anymore, notebooks are read from disk
        }
        
        # Run processor
        with open(log_file, 'a') as log:
            log.write(f"\n[{i}/{len(resources_with_notebooks)}] Processing {resource['title']}...\n")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            log.write(result.stdout)
            if result.stderr:
                log.write(f"ERRORS:\n{result.stderr}\n")
        
        if result.returncode == 0:
            print(f"✅ Completed {resource['title']}")
            success_count += 1
        else:
            print(f"❌ Failed {resource['title']}")
            # Show error
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
        
        # Brief pause between resources
        if i < len(resources_with_notebooks):
            print("Waiting 5 seconds before next resource...")
            subprocess.run(["sleep", "5"])
    
    print(f"\n{'='*60}")
    print(f"Notebook re-processing complete!")
    print(f"Finished: {datetime.now().isoformat()}")
    print(f"Success: {success_count}/{len(resources_with_notebooks)}")
    print(f"Log file: {log_file}")
    print(f"{'='*60}\n")
    
    # Show summary of what was skipped
    print("Resources skipped (no notebooks):")
    skipped = [21, 22, 24, 27, 29, 30]
    for num in skipped:
        print(f"  - Issue #{num}")

if __name__ == "__main__":
    main()