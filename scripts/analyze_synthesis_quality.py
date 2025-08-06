#!/usr/bin/env python3
"""
Analyze and compare synthesis quality between qwen2.5 and GPT-OSS outputs
"""

import re
from pathlib import Path

def analyze_markdown(file_path):
    """Analyze markdown file structure and content"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Count various elements
    lines = content.split('\n')
    
    analysis = {
        'file': file_path.name,
        'total_lines': len(lines),
        'total_chars': len(content),
        'code_blocks': len(re.findall(r'```', content)) // 2,
        'headers': {
            'h1': len(re.findall(r'^# ', content, re.MULTILINE)),
            'h2': len(re.findall(r'^## ', content, re.MULTILINE)),
            'h3': len(re.findall(r'^### ', content, re.MULTILINE)),
            'h4': len(re.findall(r'^#### ', content, re.MULTILINE)),
        },
        'lists': len(re.findall(r'^\s*[-*] ', content, re.MULTILINE)),
        'tables': len(re.findall(r'^\|', content, re.MULTILINE)),
        'links': len(re.findall(r'\[.*?\]\(.*?\)', content)),
        'code_lines': 0,
        'python_specific': {
            'imports': len(re.findall(r'^import |^from ', content, re.MULTILINE)),
            'functions': len(re.findall(r'^def ', content, re.MULTILINE)),
            'classes': len(re.findall(r'^class ', content, re.MULTILINE)),
        }
    }
    
    # Count lines in code blocks
    in_code = False
    for line in lines:
        if '```' in line:
            in_code = not in_code
        elif in_code:
            analysis['code_lines'] += 1
    
    return analysis

def compare_topics():
    """Compare all topics between qwen2.5 and GPT-OSS"""
    qwen_dir = Path("docs/ai-makerspace-resources/synthesis")
    gpt_dir = Path("docs/ai-makerspace-resources-gpt-oss/synthesis")
    
    topics = [
        "21_vector_memory",
        "22_planner_executor", 
        "23_multi-agent_swarm",
        "24_mcp_and_a2a_protocols",
        "25_production_rag",
        "26_llm_optimization",
        "27_guardrails",
        "28_agent_observability",
        "29_fine-tuning",
        "30_agent_evaluation"
    ]
    
    print("# Synthesis Quality Comparison\n")
    print("| Topic | Model | Lines | Chars | Code Blocks | Code Lines | Headers | Lists | Tables |")
    print("|-------|-------|-------|-------|-------------|------------|---------|-------|--------|")
    
    for topic in topics:
        # Check if qwen file exists
        qwen_files = list(qwen_dir.glob(f"{topic}*.md"))
        if qwen_files:
            qwen_analysis = analyze_markdown(qwen_files[0])
            total_headers = sum(qwen_analysis['headers'].values())
            print(f"| {topic} | qwen2.5 | {qwen_analysis['total_lines']} | {qwen_analysis['total_chars']:,} | {qwen_analysis['code_blocks']} | {qwen_analysis['code_lines']} | {total_headers} | {qwen_analysis['lists']} | {qwen_analysis['tables']} |")
        
        # Check GPT-OSS file
        gpt_file = gpt_dir / f"{topic}.md"
        if gpt_file.exists():
            gpt_analysis = analyze_markdown(gpt_file)
            total_headers = sum(gpt_analysis['headers'].values())
            print(f"| {topic} | gpt-oss | {gpt_analysis['total_lines']} | {gpt_analysis['total_chars']:,} | {gpt_analysis['code_blocks']} | {gpt_analysis['code_lines']} | {total_headers} | {gpt_analysis['lists']} | {gpt_analysis['tables']} |")
    
    print("\n## Detailed Analysis for Vector Memory (with transcript)\n")
    
    # Detailed comparison for Vector Memory
    qwen_vm = analyze_markdown(list(qwen_dir.glob("21_vector_memory*.md"))[0])
    gpt_vm = analyze_markdown(gpt_dir / "21_vector_memory.md")
    
    print("### Content Structure")
    print(f"- **Qwen2.5**: {qwen_vm['total_chars']:,} chars, {qwen_vm['code_blocks']} code blocks")
    print(f"- **GPT-OSS**: {gpt_vm['total_chars']:,} chars, {gpt_vm['code_blocks']} code blocks")
    print(f"- **Ratio**: GPT-OSS has {gpt_vm['total_chars']/qwen_vm['total_chars']:.1f}x more content")
    
    print("\n### Code Content")
    print(f"- **Qwen2.5**: {qwen_vm['code_lines']} lines of code")
    print(f"- **GPT-OSS**: {gpt_vm['code_lines']} lines of code")
    print(f"- **Ratio**: GPT-OSS has {gpt_vm['code_lines']/qwen_vm['code_lines']:.1f}x more code")

if __name__ == "__main__":
    compare_topics()