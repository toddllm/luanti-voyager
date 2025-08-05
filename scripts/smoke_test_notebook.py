#!/Users/tdeshane/luanti-voyager/.venv-whisper/bin/python3
"""
Smoke test for notebook download
"""

import os
import sys
import re
from pathlib import Path

# Import gdown after installation
try:
    import gdown
except ImportError:
    print("Installing gdown...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown"])
    import gdown

def test_notebook_download():
    """Test downloading a single notebook"""
    # Test with Vector Memory notebook
    test_url = 'https://colab.research.google.com/drive/1vy73KW_Kz83nt9Sw8h8LM9GOPaA3gNST'
    test_output = Path("/tmp/test_notebook.ipynb")
    
    print(f"Testing notebook download...")
    print(f"URL: {test_url}")
    print(f"Output: {test_output}")
    
    # Extract file ID
    match = re.search(r'/drive/([a-zA-Z0-9-_]+)', test_url)
    if not match:
        print("❌ Failed to extract file ID")
        return False
    
    file_id = match.group(1)
    print(f"File ID: {file_id}")
    
    # Download
    try:
        gdown.download(f"https://drive.google.com/uc?id={file_id}", str(test_output), quiet=False)
        
        if test_output.exists():
            size_kb = test_output.stat().st_size / 1024
            print(f"✅ Download successful! Size: {size_kb:.1f} KB")
            
            # Check if it's valid JSON (notebooks are JSON)
            import json
            with open(test_output, 'r') as f:
                notebook = json.load(f)
            
            cells = notebook.get('cells', [])
            print(f"✅ Valid notebook with {len(cells)} cells")
            
            # Clean up
            test_output.unlink()
            return True
        else:
            print("❌ Download failed - file not created")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_notebook_download()
    sys.exit(0 if success else 1)