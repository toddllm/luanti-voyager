#!/usr/bin/env python3
"""
Simple synthesis using gpt-oss with existing resources
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

def synthesize_topic(issue_num, title, use_transcript=True):
    """Synthesize a single topic"""
    
    print(f"\n{'='*60}")
    print(f"🚀 Processing Issue #{issue_num}: {title}")
    print(f"{'='*60}")
    
    # Load existing resources
    transcript_text = ""
    if use_transcript:
        # Try original location
        transcript_paths = [
            Path(f"docs/ai-makerspace-resources/transcripts/{issue_num:02d}_{title.lower().replace(' ', '_')}.json"),
            Path(f"docs/ai-makerspace-resources/transcripts/{issue_num}_vector_memory.json"),
            Path(f"docs/ai-makerspace-resources/transcripts/21_vector_memory.json")  # Use this as fallback
        ]
        
        for path in transcript_paths:
            if path.exists():
                with open(path) as f:
                    data = json.load(f)
                    transcript_text = data.get('text', '')[:2000]  # First 2000 chars
                    print(f"✅ Using transcript from {path.name}")
                    break
    
    if not transcript_text:
        print("⚠️ No transcript found, using generic prompt")
    
    # Simple, focused prompt
    prompt = f"""Create a concise implementation guide for "{title}" in Luanti Voyager (a Minecraft-like game).

Include:
1. What is {title}? (2-3 sentences)
2. How to implement it for game AI agents (bullet points)
3. One simple code example
4. Game-specific use case

{f'Context: {transcript_text}' if transcript_text else ''}

Keep it under 500 words. Be practical and code-focused."""
    
    print(f"📝 Prompt length: {len(prompt)} characters")
    print("🤖 Synthesizing with gpt-oss:20b...")
    
    output_dir = Path("docs/ai-makerspace-resources-gpt-oss/synthesis")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Use echo to pipe prompt to ollama
        cmd = f'echo {json.dumps(prompt)} | ollama run gpt-oss:20b'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0 and result.stdout.strip():
            synthesis = result.stdout.strip()
            print(f"✅ Success! Generated {len(synthesis)} characters")
            
            # Save output
            output_file = output_dir / f"{issue_num:02d}_{title.lower().replace(' ', '_')}_gpt_oss.md"
            with open(output_file, 'w') as f:
                f.write(f"# {title} - Implementation Guide (GPT-OSS)\n\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Model: gpt-oss:20b\n\n")
                f.write("---\n\n")
                f.write(synthesis)
            
            print(f"💾 Saved to: {output_file}")
            return True
        else:
            print(f"❌ Failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️ Timed out after 3 minutes")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# Process all topics
topics = [
    (21, "Vector Memory"),
    (22, "Planner Executor"),
    (23, "Multi-Agent Swarm"),
    (24, "MCP and A2A Protocols"),
    (25, "Production RAG"),
    (26, "LLM Optimization"),
    (27, "Agent Observability"),
    (28, "Guardrails"),
    (29, "Fine-tuning"),
    (30, "Agent Evaluation")
]

if __name__ == "__main__":
    successful = 0
    for issue_num, title in topics:
        if synthesize_topic(issue_num, title):
            successful += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Completed: {successful}/{len(topics)} topics")
    print(f"{'='*60}")