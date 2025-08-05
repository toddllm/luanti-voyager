#!/Users/tdeshane/luanti-voyager/.venv-whisper/bin/python3
"""
Process all AI Makerspace resources for issues #21-#30
"""

from process_ai_makerspace_batch import AIResourceProcessor
import time

# All resources to process
RESOURCES = [
    {
        'issue': 21,
        'title': 'Vector Memory',
        'youtube_url': 'https://youtu.be/XwUD9uXL0eg',
        'notebook_url': 'https://colab.research.google.com/drive/1vy73KW_Kz83nt9Sw8h8LM9GOPaA3gNST'
    },
    {
        'issue': 22,
        'title': 'Planner Executor',
        'youtube_url': 'https://www.youtube.com/watch?v=PsjMHb4nl24',  # What is an Agent?
        'notebook_url': 'https://colab.research.google.com/drive/1p5L8pWzJG4KuopFNoc70OZiNpFkdYVCf'  # LlamaIndex Workflows
    },
    {
        'issue': 23,
        'title': 'Multi Agent Swarm',
        'youtube_url': 'https://www.youtube.com/watch?v=7MBvhqaFYu0',
        'notebook_url': 'https://colab.research.google.com/drive/1GFZ3F2TCWdCEuFXyFf7Ij5V4E3gBKBrZ'
    },
    {
        'issue': 24,
        'title': 'MCP A2A Protocols',
        'youtube_url': 'https://www.youtube.com/watch?v=wDMlaytqcoo',  # MCP
        'notebook_url': None  # Use GitHub repo instead
    },
    {
        'issue': 25,
        'title': 'RAG Production',
        'youtube_url': 'https://www.youtube.com/live/-S6iVvSjVoo',
        'notebook_url': 'https://colab.research.google.com/drive/1YhvxtDO5Av46eUO88AYb7vV2UTf4XBRi'
    },
    {
        'issue': 26,
        'title': 'LLM Optimization',
        'youtube_url': 'https://www.youtube.com/live/bz7u0vQAYFQ',
        'notebook_url': 'https://colab.research.google.com/drive/1JeKo79hzhtE3pQdNy5T60p3gYGxsP3oo'
    },
    {
        'issue': 27,
        'title': 'Agent Observability',
        'youtube_url': 'https://youtube.com/live/eh1_CKLi3jw',  # LangSmith
        'notebook_url': 'https://colab.research.google.com/drive/1TiuuqZvoj4boJbGuOehWKMgrpO-3J9EC'
    },
    {
        'issue': 28,
        'title': 'Guardrails Safety',
        'youtube_url': 'https://www.youtube.com/watch?v=KNdnFqZs5RA',
        'notebook_url': 'https://colab.research.google.com/drive/1s64LdUIJkM0c3NUcSfB-bhcKq0xvOJzH'
    },
    {
        'issue': 29,
        'title': 'Fine Tuning',
        'youtube_url': 'https://www.youtube.com/live/gJy8L7Z9Ai8',
        'notebook_url': 'https://colab.research.google.com/drive/1Wvnj-890XBL3ydGW22I4vHGdDMq-EDeC'
    },
    {
        'issue': 30,
        'title': 'Agent Evaluation',
        'youtube_url': 'https://www.youtube.com/watch?v=HWRr4y6PUQY',
        'notebook_url': 'https://colab.research.google.com/drive/1x4XL4vDlI25efBinhNHdA3F0U31EQGpb'
    }
]

def main():
    processor = AIResourceProcessor()
    
    print(f"Processing {len(RESOURCES)} AI Makerspace resources...")
    print("This will take several hours. Running in background is recommended.")
    print("="*60)
    
    for i, resource in enumerate(RESOURCES):
        print(f"\n[{i+1}/{len(RESOURCES)}] Starting {resource['title']}...")
        
        try:
            processor.process_resource(resource)
            print(f"✅ Completed {resource['title']}")
        except Exception as e:
            print(f"❌ Error processing {resource['title']}: {e}")
            # Continue with next resource
        
        # Small delay between resources
        if i < len(RESOURCES) - 1:
            print("Waiting 10 seconds before next resource...")
            time.sleep(10)
    
    print("\n" + "="*60)
    print("✨ Batch processing complete!")
    print(f"Check results in: docs/ai-makerspace-resources/")

if __name__ == "__main__":
    main()