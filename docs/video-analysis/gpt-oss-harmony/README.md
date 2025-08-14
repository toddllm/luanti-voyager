# GPT-OSS and Harmony Response Format Analysis

This directory contains the analysis of the AI Makerspace video about OpenAI's GPT-OSS model and the Harmony Response Format.

## Video Information
- **URL**: https://www.youtube.com/watch?v=nyb3TnUkwE8
- **Duration**: ~63 minutes
- **Speakers**: Dr. Greg and Wiz from AI Makerspace
- **Topics**: GPT-OSS, Harmony Response Format, Channels, Open Weight Models

## Key Files

### Analysis Results
- [`analysis/GPT_OSS_Analysis_Report.md`](analysis/GPT_OSS_Analysis_Report.md) - **Main technical documentation** (450+ lines)
- [`analysis/nyb3TnUkwE8_GPT_OSS_Harmony_Response_Format_llm_analysis.json`](analysis/nyb3TnUkwE8_GPT_OSS_Harmony_Response_Format_llm_analysis.json) - Complete analysis data

### Transcripts
- [`transcripts/nyb3TnUkwE8_GPT_OSS_Harmony_Response_Format.json`](transcripts/nyb3TnUkwE8_GPT_OSS_Harmony_Response_Format.json) - Full transcript with timestamps
- [`transcripts/nyb3TnUkwE8_GPT_OSS_Harmony_Response_Format.txt`](transcripts/nyb3TnUkwE8_GPT_OSS_Harmony_Response_Format.txt) - Plain text transcript

### Media Files (Not in Git)
- `videos/` - Original video (335MB)
- `audio/` - Extracted audio (86MB)  
- `frames/` - 657 detected frames (756MB)

*Note: Large media files are excluded from Git via .gitignore*

## Key Technical Findings

### Harmony Response Format (HRF)
A new structured chat schema extending system/user/assistant with:
- **Channels**: `analysis`, `commentary`, `final`
- **Recipients**: `user`, `assistant`, `tool`
- **Formats**: `plain`, `json`, `typescript`

### Code Example from Analysis
```python
from openai_harmony import Chat, Role, Channel, HarmonyTemplate

system_msg = HarmonyTemplate.system()
system_msg.set_valid_channels([Channel.ANALYSIS, Channel.COMMENTARY, Channel.FINAL])

chat = Chat()
chat.add_user("What is the weather in Tokyo?")
response = chat.complete(model="gpt-oss-120b")
print(response.final_content)
```

### GPT-OSS Specifications
- **Sizes**: 20B and 120B parameters (MoE architecture)
- **License**: Apache 2.0 / OpenRAIL-2.0
- **Deployment**: On-premise capable
- **Training**: "Deep fried" (extensive post-training and safety fine-tuning)

## Processing Pipeline Used

1. **Video Download**: yt-dlp (1080p)
2. **Transcription**: Whisper Large v3
3. **Frame Detection**: OpenCV (657 frames identified)
4. **Analysis**: gpt-oss:120b via Ollama

Total processing time: ~45 minutes

## View the Full Report

The main technical documentation is in [`analysis/GPT_OSS_Analysis_Report.md`](analysis/GPT_OSS_Analysis_Report.md)