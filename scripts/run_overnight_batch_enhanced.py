#!/Users/tdeshane/luanti-voyager/.venv-whisper/bin/python3
"""
Enhanced overnight batch processor for all 10 AI Makerspace resources
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

# All 10 resources to process
resources = [
    {
        'issue': 21,
        'title': 'Vector Memory',
        'youtube_url': 'https://youtu.be/XwUD9uXL0eg',
        'notebook_url': 'https://colab.research.google.com/drive/1vy73KW_Kz83nt9Sw8h8LM9GOPaA3gNST'
    },
    {
        'issue': 22,
        'title': 'Planner Executor',
        'youtube_url': 'https://www.youtube.com/watch?v=PsjMHb4nl24',
        'notebook_url': 'https://github.com/ruvnet/AI-Makerspace/blob/main/12-2024/Week-1/Notebook_1_Planner_Executor.ipynb'
    },
    {
        'issue': 23,
        'title': 'Multi-Agent Swarm',
        'youtube_url': 'https://www.youtube.com/watch?v=M-FKvHA0tVw',
        'notebook_url': 'https://colab.research.google.com/drive/1zM3aeD23XcJCBL0Y3hGBEfBq0k6WGVdZ'
    },
    {
        'issue': 24,
        'title': 'MCP and A2A Protocols',
        'youtube_url': 'https://www.youtube.com/watch?v=uDYHn1WlqaE',
        'notebook_url': 'https://github.com/ruvnet/AI-Makerspace/blob/main/11-2024/Week-3/Notebook_3_MCP_A2A.ipynb'
    },
    {
        'issue': 25,
        'title': 'Production RAG',
        'youtube_url': 'https://www.youtube.com/watch?v=85BIMT9X38Q',
        'notebook_url': 'https://colab.research.google.com/drive/1-vEMKHQ9G4p3vHO-a9rTdgQjTcQJlhBS'
    },
    {
        'issue': 26,
        'title': 'LLM Optimization',
        'youtube_url': 'https://www.youtube.com/watch?v=6xEW0TDROA8',
        'notebook_url': 'https://github.com/ruvnet/AI-Makerspace/blob/main/11-2024/Week-1/Notebook_1_vLLM_Optimization.ipynb'
    },
    {
        'issue': 27,
        'title': 'Agent Observability',
        'youtube_url': 'https://www.youtube.com/watch?v=Ibd0kRTL4oA',
        'notebook_url': 'https://colab.research.google.com/drive/1tcD_U3rTDPBKXQjT8Y90lLnSJ3VJfDg7'
    },
    {
        'issue': 28,
        'title': 'Guardrails',
        'youtube_url': 'https://www.youtube.com/watch?v=p-gpZg1kH7U',
        'notebook_url': 'https://github.com/ruvnet/AI-Makerspace/blob/main/10-2024/Week-3/Notebook_3_Guardrails.ipynb'
    },
    {
        'issue': 29,
        'title': 'Fine-tuning',
        'youtube_url': 'https://www.youtube.com/watch?v=FdBCMJn6NaI',
        'notebook_url': 'https://colab.research.google.com/drive/17xQ6nCgcvC1xq7ER4kZp4HCN3sLLVJoN'
    },
    {
        'issue': 30,
        'title': 'Agent Evaluation',
        'youtube_url': 'https://www.youtube.com/watch?v=2lN0LQ_6WSc',
        'notebook_url': 'https://github.com/ruvnet/AI-Makerspace/blob/main/09-2024/Week-4/Notebook_4_RAGAS_Evaluation.ipynb'
    }
]

def main():
    print(f"\n{'='*60}")
    print(f"Enhanced Overnight Batch Processing")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    print(f"Processing {len(resources)} AI Makerspace resources...")
    print("This will take several hours. Running in background is recommended.\n")
    
    log_file = Path(f"logs/enhanced_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    log_file.parent.mkdir(exist_ok=True)
    
    # Process each resource
    for i, resource in enumerate(resources, 1):
        print(f"[{i}/{len(resources)}] Starting {resource['title']}...")
        
        # Create command to process this resource
        cmd = [
            sys.executable,
            "scripts/enhanced_batch_processor.py"
        ]
        
        # Pass resource data via environment variables
        env = {
            **subprocess.os.environ,
            'RESOURCE_ISSUE': str(resource['issue']),
            'RESOURCE_TITLE': resource['title'],
            'RESOURCE_YOUTUBE': resource.get('youtube_url', ''),
            'RESOURCE_NOTEBOOK': resource.get('notebook_url', '')
        }
        
        # Run processor
        with open(log_file, 'a') as log:
            log.write(f"\n[{i}/{len(resources)}] Processing {resource['title']}...\n")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            log.write(result.stdout)
            if result.stderr:
                log.write(f"ERRORS:\n{result.stderr}\n")
        
        if result.returncode == 0:
            print(f"✅ Completed {resource['title']}")
        else:
            print(f"❌ Failed {resource['title']}")
        
        # Brief pause between resources
        if i < len(resources):
            print("Waiting 10 seconds before next resource...")
            subprocess.run(["sleep", "10"])
    
    print(f"\n{'='*60}")
    print(f"Batch processing complete!")
    print(f"Finished: {datetime.now().isoformat()}")
    print(f"Log file: {log_file}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()