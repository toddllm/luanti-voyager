#!/usr/bin/env python3
"""
Simple test of notebook processing
"""

import json
from pathlib import Path

def test_notebook_extraction():
    notebook_path = Path("docs/ai-makerspace-resources/notebooks/23_multi-agent_swarm.ipynb")
    
    print(f"Testing notebook: {notebook_path}")
    print(f"Exists: {notebook_path.exists()}")
    print(f"Size: {notebook_path.stat().st_size:,} bytes")
    
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    print(f"\nNotebook structure:")
    print(f"  nbformat: {notebook.get('nbformat')}")
    print(f"  Total cells: {len(notebook.get('cells', []))}")
    
    code_cells = 0
    total_code_length = 0
    
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') == 'code':
            code_cells += 1
            source = cell.get('source', '')
            if isinstance(source, list):
                source = ''.join(source)
            total_code_length += len(source)
    
    print(f"  Code cells: {code_cells}")
    print(f"  Total code length: {total_code_length:,} chars")
    
    # Show first code cell
    print(f"\nFirst code cell preview:")
    for i, cell in enumerate(notebook.get('cells', [])):
        if cell.get('cell_type') == 'code':
            source = cell.get('source', '')
            if isinstance(source, list):
                source = ''.join(source)
            print(source[:200] + "..." if len(source) > 200 else source)
            break

if __name__ == "__main__":
    test_notebook_extraction()