#!/usr/bin/env python3
"""
Check AI Makerspace's typical resource patterns
"""

# Based on AI Makerspace patterns, they typically use:
# 1. Slides: tinyurl.com links
# 2. Code: Either GitHub repos or Colab notebooks
# 3. Sometimes both are in the Awesome-AIM-Index

missing_resources = [
    {
        'issue': 21,
        'title': 'Vector Memory / LlamaIndex Agent Memory',
        'date': '6/26/25',
        'video': 'https://youtu.be/XwUD9uXL0eg',
        'slides': 'https://tinyurl.com/3rjcymzv',
        'note': 'Listed as "No Code" in index, but might have examples in slides'
    },
    {
        'issue': 22,
        'title': 'Planner Executor',
        'date': 'Unknown',
        'note': 'Need to find in AI Makerspace events - might be part of LangGraph event'
    },
    {
        'issue': 24,
        'title': 'MCP and A2A Protocols',
        'date': '4/9/25 (MCP), 6/4/25 (A2A)',
        'mcp_repo': 'https://github.com/AI-Maker-Space/MCP-Event',
        'a2a_repo': 'https://github.com/AI-Maker-Space/AIM-A2A-Event',
        'note': 'Two separate events, need to check both repos for notebooks'
    },
    {
        'issue': 27,
        'title': 'Agent Observability',
        'date': 'Unknown',
        'possible_repo': 'https://github.com/AI-Maker-Space/Building-with-Autogen-AIM',
        'note': 'Might be covered in Autogen or LangSmith events'
    },
    {
        'issue': 29,
        'title': 'Fine-tuning',
        'date': '9/4/24',
        'slides': 'Check event page',
        'note': 'Had broken Colab link, might have updated link'
    },
    {
        'issue': 30,
        'title': 'Agent Evaluation / RAGAS',
        'date': 'Unknown',
        'possible_repo': 'https://github.com/AI-Maker-Space/Production-RAG-AIM',
        'note': 'RAGAS is usually covered with Production RAG'
    }
]

print("AI Makerspace Resource Patterns")
print("=" * 60)
print("\nBased on their typical format, here's what to check:\n")

for resource in missing_resources:
    print(f"[{resource['issue']}] {resource['title']}")
    if 'slides' in resource:
        print(f"  📊 Slides: {resource['slides']}")
    if 'mcp_repo' in resource:
        print(f"  📁 MCP Repo: {resource['mcp_repo']}")
    if 'a2a_repo' in resource:
        print(f"  📁 A2A Repo: {resource['a2a_repo']}")
    if 'possible_repo' in resource:
        print(f"  📁 Possible: {resource['possible_repo']}")
    print(f"  ℹ️  {resource['note']}")
    print()

print("\nRecommended Actions:")
print("1. Check the slide decks (tinyurl links) - they often contain code")
print("2. Look in GitHub repos for .ipynb files in subdirectories")
print("3. Search AI-Maker-Space org for event-specific repos")
print("4. Check if topics are covered in other events (e.g., RAGAS in Production RAG)")
print("\nManual browser check recommended for:")
print("- YouTube pinned comments")
print("- Slide deck contents")
print("- Private repo access requests")

if __name__ == "__main__":
    pass