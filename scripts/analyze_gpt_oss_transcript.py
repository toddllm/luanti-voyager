#!/usr/bin/env python3
"""
Analyze the GPT-OSS video transcript with proper context
"""

import json
import requests
import time
from pathlib import Path
import shutil

def rename_files():
    """Rename files to reflect actual content"""
    base_dir = Path("docs/video-analysis/multi-agent-systems")
    old_name = "nyb3TnUkwE8_Building_Production_Ready_Multi_Agent_Systems"
    new_name = "nyb3TnUkwE8_GPT_OSS_Harmony_Response_Format"
    
    print("📝 Renaming files to reflect actual content...")
    
    renamed_count = 0
    for subdir in ["videos", "audio", "transcripts", "analysis"]:
        dir_path = base_dir / subdir
        if dir_path.exists():
            for file_path in dir_path.glob(f"{old_name}*"):
                new_file_path = file_path.parent / file_path.name.replace(old_name, new_name)
                shutil.move(str(file_path), str(new_file_path))
                print(f"  Renamed: {file_path.name} -> {new_file_path.name}")
                renamed_count += 1
    
    print(f"✅ Renamed {renamed_count} files\n")
    return new_name

def analyze_transcript_with_llm():
    """Perform deep analysis of the transcript focusing on technical content"""
    
    base_dir = Path("docs/video-analysis/multi-agent-systems")
    new_name = "nyb3TnUkwE8_GPT_OSS_Harmony_Response_Format"
    
    # Load transcript
    transcript_path = base_dir / "transcripts" / f"{new_name}.json"
    with open(transcript_path, 'r') as f:
        transcript_data = json.load(f)
    
    full_text = transcript_data.get('text', '')
    
    print("🧠 Analyzing transcript with GPT-OSS:120b...")
    print(f"   Transcript length: {len(full_text)} characters")
    print("   This will take several minutes...\n")
    
    # Split transcript into chunks for better analysis
    chunk_size = 15000
    chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]
    
    # Analyze first few chunks in detail
    prompt = f"""You are analyzing a technical video transcript about GPT-OSS (OpenAI's open source model) and the Harmony Response Format.

FULL TRANSCRIPT:
{full_text[:30000]}

[Transcript continues for {len(full_text)-30000} more characters discussing implementation details, code examples, and technical specifications]

Please provide a comprehensive technical analysis including:

1. **Main Technical Concepts**
   - What is GPT-OSS and how does it differ from GPT-4/GPT-5?
   - What is the Harmony Response Format?
   - What are "channels" in this context?
   - What does "deep fried" model mean?

2. **Code and Implementation Details**
   - Any code structures or formats mentioned
   - API patterns or response formats discussed
   - System/User/Assistant prompting evolution
   - The "5 options with sub-options" mentioned

3. **Technical Architecture**
   - Training paradigms discussed (pre-training to post-training)
   - Model deployment considerations (on-prem vs API)
   - Open weight model characteristics

4. **Practical Applications**
   - Use cases for GPT-OSS vs cloud models
   - When to use Harmony Response Format
   - Implementation recommendations

5. **Key Technical Insights**
   - Novel contributions (or lack thereof)
   - Comparison with existing approaches
   - Future implications for developers

6. **Code Examples or Patterns**
   - Extract any code-like structures mentioned
   - Document any JSON formats, schemas, or templates discussed
   - Note any pseudo-code or algorithmic descriptions

Format your response as a detailed technical document that developers can use as a reference for understanding and implementing GPT-OSS and the Harmony Response Format."""
    
    ollama_url = "http://localhost:11434/api/generate"
    payload = {
        "model": "gpt-oss:120b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 8000,  # Allow longer response
            "top_p": 0.9
        }
    }
    
    try:
        print("⏳ Sending request to Ollama (this may take 5-10 minutes)...")
        response = requests.post(ollama_url, json=payload, timeout=600)
        
        if response.status_code == 200:
            result = response.json()
            analysis = result.get('response', '')
            
            # Save analysis
            analysis_data = {
                'url': 'https://www.youtube.com/watch?v=nyb3TnUkwE8',
                'title': 'GPT-OSS and Harmony Response Format - AI Makerspace',
                'transcript_length': len(full_text),
                'analysis': {
                    'content': analysis,
                    'model': 'gpt-oss:120b',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'prompt_tokens': len(prompt),
                    'analysis_tokens': len(analysis)
                },
                'key_topics': [
                    'GPT-OSS (OpenAI Open Source Model)',
                    'Harmony Response Format',
                    'Channels in Response Formatting',
                    'Open Weight Reasoning Models',
                    'On-Premise vs API Deployment',
                    'Model Training Paradigms'
                ]
            }
            
            # Save to JSON
            output_path = base_dir / "analysis" / f"{new_name}_llm_analysis.json"
            with open(output_path, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            print(f"\n✅ Analysis complete! Saved to {output_path}")
            
            # Create markdown report
            create_detailed_report(analysis_data, base_dir / "analysis")
            
            return analysis_data
            
        else:
            print(f"❌ Error: Ollama returned status {response.status_code}")
            return None
            
    except requests.Timeout:
        print("❌ Request timed out after 10 minutes")
        return None
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return None

def create_detailed_report(analysis_data, output_dir):
    """Create a detailed markdown report"""
    
    report_path = output_dir / "GPT_OSS_Analysis_Report.md"
    
    with open(report_path, 'w') as f:
        f.write("# GPT-OSS and Harmony Response Format - Technical Analysis\n\n")
        f.write("## Video Information\n\n")
        f.write(f"- **URL**: {analysis_data['url']}\n")
        f.write(f"- **Title**: {analysis_data['title']}\n")
        f.write(f"- **Transcript Length**: {analysis_data['transcript_length']:,} characters\n")
        f.write(f"- **Analysis Date**: {analysis_data['analysis']['timestamp']}\n\n")
        
        f.write("## Key Topics Covered\n\n")
        for topic in analysis_data['key_topics']:
            f.write(f"- {topic}\n")
        f.write("\n")
        
        f.write("## Detailed Technical Analysis\n\n")
        f.write(analysis_data['analysis']['content'])
        f.write("\n\n")
        
        f.write("## Processing Metadata\n\n")
        f.write(f"- Model Used: {analysis_data['analysis']['model']}\n")
        f.write(f"- Prompt Tokens: {analysis_data['analysis']['prompt_tokens']:,}\n")
        f.write(f"- Analysis Tokens: {analysis_data['analysis']['analysis_tokens']:,}\n")
    
    print(f"📄 Report created: {report_path}")

def main():
    print("=" * 60)
    print("🚀 GPT-OSS Video Transcript Analysis")
    print("=" * 60)
    print()
    
    # Step 1: Rename files
    rename_files()
    
    # Step 2: Analyze transcript
    print("Starting deep analysis of transcript...")
    print("This will run in the background and may take 5-10 minutes.\n")
    
    analysis = analyze_transcript_with_llm()
    
    if analysis:
        print("\n✨ Analysis complete!")
        print("View the report at: docs/video-analysis/multi-agent-systems/analysis/GPT_OSS_Analysis_Report.md")
    else:
        print("\n⚠️ Analysis failed or timed out")

if __name__ == "__main__":
    main()