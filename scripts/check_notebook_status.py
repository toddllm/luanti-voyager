#!/usr/bin/env python3
"""
Check status of notebook downloads and provide actionable report
"""

import json
from pathlib import Path

def main():
    notebook_dir = Path("docs/ai-makerspace-resources/notebooks")
    synthesis_dir = Path("docs/ai-makerspace-resources/synthesis")
    
    print("AI Makerspace Notebook Status Report")
    print("=" * 60)
    
    # Check each resource
    notebooks_found = 0
    references_found = 0
    synthesis_found = 0
    
    for i in range(21, 31):
        print(f"\nIssue #{i}:")
        
        # Check for actual notebook
        notebook_path = None
        for file in notebook_dir.glob(f"{i:02d}_*.ipynb"):
            notebook_path = file
            notebooks_found += 1
            print(f"  ✅ Notebook: {file.name} ({file.stat().st_size:,} bytes)")
            break
        
        # Check for reference file
        ref_path = None
        for file in notebook_dir.glob(f"{i:02d}_*.json"):
            ref_path = file
            references_found += 1
            with open(file) as f:
                ref = json.load(f)
            print(f"  📝 Reference: {ref['type']} - {ref['status']}")
            print(f"     URL: {ref['url']}")
            break
            
        # Check synthesis
        for file in synthesis_dir.glob(f"{i:02d}_*.md"):
            synthesis_found += 1
            print(f"  ✅ Synthesis: {file.name} ({file.stat().st_size:,} bytes)")
            break
    
    print(f"\n{'=' * 60}")
    print("Summary:")
    print(f"  Notebooks downloaded: {notebooks_found}/10")
    print(f"  Reference files: {references_found}/10")
    print(f"  Synthesis completed: {synthesis_found}/10")
    print(f"  Using mock content: {10 - notebooks_found}/10")
    
    if notebooks_found == 0:
        print("\n⚠️  All notebooks are currently inaccessible")
        print("   Synthesis was completed using:")
        print("   - Video transcripts from YouTube")
        print("   - Mock notebook content")
        print("   - Context-aware enrichment")
        
    print("\nRecommended Actions:")
    print("1. Try manual download from Colab links in browser")
    print("2. Search AI-Maker-Space organization for public versions")
    print("3. Contact AI Makerspace for access permissions")
    print("4. Re-run synthesis if notebooks become available")

if __name__ == "__main__":
    main()