#!/Users/tdeshane/luanti-voyager/.venv-whisper/bin/python3
"""
Fix notebook download URLs and re-download failed notebooks
"""

import os
import sys
import re
import requests
from pathlib import Path

def download_colab_notebook(url, output_path):
    """Download Colab notebook using gdown"""
    # Extract file ID from Colab URL
    match = re.search(r'/drive/([a-zA-Z0-9-_]+)', url)
    if not match:
        print(f"Could not extract file ID from: {url}")
        return False
    
    file_id = match.group(1)
    
    try:
        # Use gdown to download from Google Drive
        gdown.download(f"https://drive.google.com/uc?id={file_id}", output_path, quiet=False)
        return os.path.exists(output_path)
    except Exception as e:
        print(f"Error downloading: {e}")
        return False

# Install gdown if not present
try:
    import gdown
except ImportError:
    print("Installing gdown...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown"])
    import gdown

# Fix notebook downloads for all resources
notebooks = [
    {
        'issue': 21,
        'url': 'https://colab.research.google.com/drive/1vy73KW_Kz83nt9Sw8h8LM9GOPaA3gNST',
        'name': '21_vector_memory'
    },
    {
        'issue': 22,
        'url': 'https://colab.research.google.com/drive/1p5L8pWzJG4KuopFNoc70OZiNpFkdYVCf',
        'name': '22_planner_executor'
    },
    {
        'issue': 23,
        'url': 'https://colab.research.google.com/drive/1GFZ3F2TCWdCEuFXyFf7Ij5V4E3gBKBrZ',
        'name': '23_multi_agent_swarm'
    },
    {
        'issue': 25,
        'url': 'https://colab.research.google.com/drive/1YhvxtDO5Av46eUO88AYb7vV2UTf4XBRi',
        'name': '25_rag_production'
    },
    {
        'issue': 26,
        'url': 'https://colab.research.google.com/drive/1JeKo79hzhtE3pQdNy5T60p3gYGxsP3oo',
        'name': '26_llm_optimization'
    },
    {
        'issue': 27,
        'url': 'https://colab.research.google.com/drive/1TiuuqZvoj4boJbGuOehWKMgrpO-3J9EC',
        'name': '27_agent_observability'
    },
    {
        'issue': 28,
        'url': 'https://colab.research.google.com/drive/1s64LdUIJkM0c3NUcSfB-bhcKq0xvOJzH',
        'name': '28_guardrails_safety'
    },
    {
        'issue': 29,
        'url': 'https://colab.research.google.com/drive/1Wvnj-890XBL3ydGW22I4vHGdDMq-EDeC',
        'name': '29_fine_tuning'
    },
    {
        'issue': 30,
        'url': 'https://colab.research.google.com/drive/1x4XL4vDlI25efBinhNHdA3F0U31EQGpb',
        'name': '30_agent_evaluation'
    }
]

notebook_dir = Path("docs/ai-makerspace-resources/notebooks")
notebook_dir.mkdir(exist_ok=True)

for nb in notebooks:
    output_path = notebook_dir / f"{nb['name']}.ipynb"
    if output_path.exists():
        print(f"✅ Already exists: {output_path}")
    else:
        print(f"\nDownloading notebook for issue #{nb['issue']}...")
        if download_colab_notebook(nb['url'], str(output_path)):
            print(f"✅ Downloaded: {output_path}")
        else:
            print(f"❌ Failed: {output_path}")

print("\nDone!")