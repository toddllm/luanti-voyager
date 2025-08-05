#!/usr/bin/env python3
"""
Simple reprocessing of synthesis using real notebooks
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

# Resources with notebooks
notebooks_available = {
    23: "Multi-Agent Swarm",
    25: "Production RAG", 
    26: "LLM Optimization",
    28: "Guardrails"
}

def extract_notebook_code(notebook_path):
    """Extract code from notebook"""
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    code_cells = []
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = cell.get('source', '')
            if isinstance(source, list):
                source = ''.join(source)
            if source.strip():
                code_cells.append(source)
    
    return code_cells

def create_synthesis_prompt(issue_num, title, notebook_code, transcript_path=None):
    """Create synthesis prompt with real notebook code"""
    
    # Load transcript if available
    transcript_text = ""
    if transcript_path and transcript_path.exists():
        with open(transcript_path, 'r') as f:
            transcript = json.load(f)
            transcript_text = transcript.get('text', '')[:5000]
    
    prompt = f"""You are an expert developer creating a production-ready implementation guide for integrating "{title}" into Luanti Voyager, an open-source Minecraft-like game with AI agents.

Based on the ACTUAL notebook code from AI Makerspace, create a comprehensive implementation guide.

NOTEBOOK CODE ({len(notebook_code)} cells):
{chr(10).join(f"```python\n{code[:500]}\n```" for i, code in enumerate(notebook_code[:8]))}

{f"TRANSCRIPT EXCERPT:\n{transcript_text}\n" if transcript_text else ""}

Create a COMPREHENSIVE implementation guide that includes:

1. **Executive Summary** - What this enables for game AI agents (2-3 paragraphs)
2. **Core Architecture** - How to adapt the notebook's approach to Luanti
3. **Detailed Implementation** - Adapt the notebook code for the game context
4. **Game-Specific Adaptations** - How to modify for Minecraft-like environment
5. **Integration Points** - Where this fits in the game architecture
6. **Performance Considerations** - Game-specific optimizations
7. **Testing Strategy** - How to validate in the game environment
8. **Example Use Cases** - 3-4 specific game scenarios

Focus on adapting the ACTUAL notebook patterns to the game context. Make it production-ready."""
    
    return prompt

def synthesize_with_ollama(prompt, output_path):
    """Call Ollama to synthesize"""
    print(f"  🤖 Synthesizing with Ollama...")
    
    cmd = ["ollama", "run", "qwen2.5-coder:32b", prompt]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            with open(output_path, 'w') as f:
                f.write(f"# {output_path.stem} - Real Notebook Synthesis\n\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Type: Based on ACTUAL AI Makerspace notebook\n\n")
                f.write(result.stdout)
            return True
        else:
            print(f"  ❌ Ollama error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  ⏱️ Synthesis timed out")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print("Reprocessing with Real Notebooks")
    print("=" * 60)
    
    synthesis_dir = Path("docs/ai-makerspace-resources/synthesis")
    notebook_dir = Path("docs/ai-makerspace-resources/notebooks")
    transcript_dir = Path("docs/ai-makerspace-resources/transcripts")
    
    success_count = 0
    
    for issue_num, title in notebooks_available.items():
        print(f"\n[{issue_num}] {title}")
        
        # Find notebook
        notebook_path = notebook_dir / f"{issue_num:02d}_{title.lower().replace(' ', '_')}.ipynb"
        if not notebook_path.exists():
            print(f"  ❌ Notebook not found")
            continue
            
        print(f"  📓 Found notebook: {notebook_path.name}")
        
        # Extract code
        notebook_code = extract_notebook_code(notebook_path)
        print(f"  ✅ Extracted {len(notebook_code)} code cells")
        
        # Find transcript (optional)
        transcript_path = transcript_dir / f"{issue_num:02d}_{title.lower().replace(' ', '_')}.json"
        
        # Create prompt
        prompt = create_synthesis_prompt(issue_num, title, notebook_code, transcript_path)
        
        # Synthesize
        output_path = synthesis_dir / f"{issue_num:02d}_{title.lower().replace(' ', '_')}_real_notebook.md"
        
        if synthesize_with_ollama(prompt, output_path):
            print(f"  ✅ Saved: {output_path}")
            success_count += 1
        else:
            print(f"  ❌ Failed to synthesize")
    
    print(f"\n{'=' * 60}")
    print(f"Completed: {success_count}/{len(notebooks_available)}")
    
    print("\nNext steps:")
    print("1. Review the new synthesis files")
    print("2. Compare with mock notebook versions")
    print("3. Update GitHub issues with the improved content")

if __name__ == "__main__":
    main()