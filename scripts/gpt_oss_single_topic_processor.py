#!/usr/bin/env python3
"""
Process a single AI Makerspace topic with gpt-oss
"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime

def process_single_topic(issue_num, title):
    """Process one topic with gpt-oss"""
    
    print(f"\n{'='*60}")
    print(f"🚀 Processing Issue #{issue_num}: {title}")
    print(f"{'='*60}")
    
    # Paths
    base_dir = Path("docs/ai-makerspace-resources-gpt-oss")
    synthesis_dir = base_dir / "synthesis"
    synthesis_dir.mkdir(parents=True, exist_ok=True)
    
    # Try to load transcript from original resources
    transcript = None
    original_transcript_path = Path(f"docs/ai-makerspace-resources/transcripts/{issue_num:02d}_{title.lower().replace(' ', '_')}.json")
    if original_transcript_path.exists():
        with open(original_transcript_path) as f:
            transcript = json.load(f)
        print(f"✅ Loaded transcript: {len(transcript.get('text', ''))} characters")
    else:
        print(f"⚠️ No transcript found at {original_transcript_path}")
        # Create minimal transcript
        transcript = {"text": f"This is a placeholder for {title} content."}
    
    # Create a focused prompt
    prompt = f"""You are an expert game developer creating an implementation guide for integrating "{title}" into Luanti Voyager, an open-source Minecraft-like game with AI agents.

Create a practical implementation guide that includes:

1. **Core Concept** - What is {title} and why it matters for game AI (2-3 paragraphs)

2. **Architecture Overview** - How to structure this in a game engine

3. **Implementation Steps** - Concrete steps to implement this feature:
   - Data structures needed
   - Key algorithms
   - Integration points with game engine

4. **Code Example** - A working code example that demonstrates the concept

5. **Game-Specific Applications** - How game agents can use this feature:
   - Specific use cases in a voxel world
   - Performance considerations
   - Scalability notes

6. **Testing Approach** - How to verify it works correctly

Based on this context about {title}:
{transcript.get('text', '')[:3000]}

Keep the guide practical and focused on implementation. Target length: 800-1200 words."""

    print(f"📝 Created prompt: {len(prompt)} characters")
    print(f"🤖 Synthesizing with gpt-oss:20b...")
    print(f"⏳ Expected time: 1-3 minutes...")
    
    # Run synthesis
    cmd = ["ollama", "run", "gpt-oss:20b", prompt]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and result.stdout.strip():
            synthesis = result.stdout.strip()
            print(f"✅ Synthesis complete: {len(synthesis)} characters")
            
            # Save synthesis
            output_path = synthesis_dir / f"{issue_num:02d}_{title.lower().replace(' ', '_')}_gpt_oss.md"
            with open(output_path, 'w') as f:
                f.write(f"# {title} - Implementation Guide (GPT-OSS)\n\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Model: gpt-oss:20b\n")
                f.write(f"Issue: #{issue_num}\n\n")
                f.write(synthesis)
            
            print(f"💾 Saved to: {output_path}")
            return True
        else:
            print(f"❌ Synthesis failed or empty")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️ Timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

# Topics to process
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
    if len(sys.argv) > 1:
        # Process specific topic
        topic_num = int(sys.argv[1])
        topic = next((t for t in topics if t[0] == topic_num), None)
        if topic:
            process_single_topic(topic[0], topic[1])
        else:
            print(f"❌ Topic {topic_num} not found")
    else:
        # Process all topics
        successful = 0
        for issue_num, title in topics:
            if process_single_topic(issue_num, title):
                successful += 1
        
        print(f"\n{'='*60}")
        print(f"✅ Completed: {successful}/{len(topics)} topics")
        print(f"{'='*60}")