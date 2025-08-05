#!/Users/tdeshane/luanti-voyager/.venv-whisper/bin/python3
"""
Check status of batch processing
"""

import os
import json
from pathlib import Path
from datetime import datetime

def check_status():
    base_dir = Path("docs/ai-makerspace-resources")
    
    resources = [
        "21_vector_memory",
        "22_planner_executor", 
        "23_multi_agent_swarm",
        "24_mcp_a2a_protocols",
        "25_rag_production",
        "26_llm_optimization",
        "27_agent_observability",
        "28_guardrails_safety",
        "29_fine_tuning",
        "30_agent_evaluation"
    ]
    
    print("AI Makerspace Batch Processing Status")
    print("=" * 60)
    print(f"Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    total_steps = len(resources) * 4  # audio, transcript, notebook, synthesis
    completed_steps = 0
    
    for resource in resources:
        issue_num = resource.split('_')[0]
        print(f"\nIssue #{issue_num}: {resource.replace('_', ' ').title()}")
        
        # Check audio
        audio_files = list(base_dir.glob(f"audio/{resource}.*"))
        if audio_files:
            print("  ✅ Audio downloaded")
            completed_steps += 1
        else:
            print("  ⏳ Audio pending")
        
        # Check transcript
        transcript_file = base_dir / "transcripts" / f"{resource}.json"
        if transcript_file.exists():
            print("  ✅ Transcript complete")
            completed_steps += 1
            # Show transcript size
            size_mb = transcript_file.stat().st_size / 1024 / 1024
            print(f"     ({size_mb:.1f} MB)")
        else:
            print("  ⏳ Transcript pending")
        
        # Check notebook
        notebook_file = base_dir / "notebooks" / f"{resource}.ipynb"
        if notebook_file.exists():
            print("  ✅ Notebook downloaded")
            completed_steps += 1
        else:
            print("  ❌ Notebook missing")
        
        # Check synthesis
        synthesis_file = base_dir / "synthesis" / f"{resource}.md"
        if synthesis_file.exists():
            print("  ✅ Synthesis complete")
            completed_steps += 1
            # Show first line of synthesis
            with open(synthesis_file, 'r') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#'):
                    print(f"     {first_line}")
        else:
            print("  ⏳ Synthesis pending")
        
        # Check implementation guide
        guide_file = base_dir / "implementation-guides" / f"{resource}.md"
        if guide_file.exists():
            print("  ✅ Implementation guide created")
        else:
            print("  ⏳ Guide pending")
    
    print("\n" + "=" * 60)
    print(f"Overall Progress: {completed_steps}/{total_steps} steps ({completed_steps/total_steps*100:.1f}%)")
    
    # Check if process is still running
    pid_file = Path("logs/batch_process.pid")
    if pid_file.exists():
        with open(pid_file, 'r') as f:
            pid = f.read().strip()
        
        # Check if process is alive
        try:
            os.kill(int(pid), 0)
            print(f"\n🟢 Process is running (PID: {pid})")
        except ProcessLookupError:
            print(f"\n🔴 Process has stopped (PID: {pid} not found)")
    else:
        print("\n❓ No process PID file found")

if __name__ == "__main__":
    check_status()