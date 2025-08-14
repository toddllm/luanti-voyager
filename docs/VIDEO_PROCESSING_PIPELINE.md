# Advanced Video Processing Pipeline with Code Extraction

## Overview
This pipeline processes programming tutorial videos to extract:
1. **Full transcripts** using Whisper Large v3
2. **Code snippets** from video frames using computer vision
3. **Comprehensive analysis** using local LLMs (gpt-oss:120b via Ollama)

## Features
- 🎬 Downloads YouTube videos in optimal quality
- 🎤 Transcribes audio with word-level timestamps
- 📸 Detects frames containing code using CV heuristics
- 🤖 Extracts code from frames using vision-capable LLMs
- 🧠 Analyzes content for key concepts and patterns
- 📝 Generates structured reports in JSON and Markdown

## Installation

### Prerequisites
```bash
# System dependencies
brew install ffmpeg
pip install yt-dlp

# Python packages
pip install -r scripts/requirements_video_processing.txt

# Ollama (for LLM processing)
# Download from: https://ollama.ai/download
ollama serve  # Start the service
ollama pull gpt-oss:120b  # Pull the model (120GB)
```

### Quick Setup Check
```bash
# Test all dependencies
python scripts/test_video_pipeline.py
```

## Usage

### Process the Target Video
```bash
# Process "Building Production-Ready Multi-Agent Systems"
./scripts/process_target_video.sh
```

### Process Any Video
```bash
python scripts/process_video_with_code_extraction.py \
    "https://www.youtube.com/watch?v=VIDEO_ID" \
    --title "Video_Title" \
    --model "gpt-oss:120b" \
    --output-dir "docs/video-analysis/custom"
```

## Pipeline Architecture

### 1. Video Download
- Uses yt-dlp to download video (limited to 1080p for processing efficiency)
- Extracts audio track separately for transcription

### 2. Transcription
- Whisper Large v3 for high-quality transcription
- Generates word-level timestamps for precise alignment
- Outputs both JSON (with timestamps) and plain text

### 3. Code Frame Detection
- Samples video every 5 seconds
- Uses computer vision heuristics to detect code:
  - High contrast detection (dark/light themes)
  - Horizontal line detection (code lines)
  - Text density analysis
- Saves detected frames as PNG images

### 4. Code Extraction
- Uses gpt-oss:120b vision capabilities via Ollama
- Extracts and formats code from each frame
- Handles multiple code blocks per frame

### 5. Comprehensive Analysis
- Combines transcript and extracted code
- Generates structured analysis:
  - Main topics and objectives
  - Key concepts
  - Implementation steps
  - Code patterns and techniques
  - Best practices
  - Common pitfalls
  - Dependencies and tools

### 6. Output Generation
- JSON: Complete structured data
- Markdown: Human-readable report
- Frame images: Saved for reference

## Output Structure

```
docs/video-analysis/
├── videos/          # Downloaded videos
├── audio/           # Extracted audio files
├── transcripts/     # Whisper transcriptions
├── frames/          # Extracted code frames
├── extracted-code/  # Code snippets
└── analysis/        # Final reports
    ├── *_complete.json  # Full analysis data
    └── *_report.md      # Markdown report
```

## Code Frame Detection Algorithm

The pipeline uses several heuristics to identify frames containing code:

1. **Contrast Analysis**: Detects dark or light theme editors
2. **Edge Detection**: Finds horizontal lines typical of code
3. **Text Pattern Recognition**: Identifies text-like density patterns

## LLM Integration

### Using gpt-oss:120b
- Vision-capable model for code extraction
- 120B parameters for high-quality analysis
- Runs locally via Ollama for privacy and control

### Alternative Models
You can use other Ollama models:
```bash
# Smaller models (faster but less accurate)
ollama pull llama3.2-vision:11b
ollama pull qwen2-vl:7b

# Use in script
python scripts/process_video_with_code_extraction.py \
    URL --model "llama3.2-vision:11b"
```

## Performance Considerations

- **Processing Time**: ~30-60 minutes for a 1-hour video
- **Disk Space**: ~5-10GB per video (including frames)
- **Memory**: 16GB+ recommended for Whisper Large
- **GPU**: Optional but speeds up Whisper transcription

## Troubleshooting

### Ollama Not Running
```bash
# Start Ollama service
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

### Model Not Available
```bash
# Pull the model (120GB download)
ollama pull gpt-oss:120b

# List available models
ollama list
```

### FFmpeg Issues
```bash
# Install/update FFmpeg
brew install ffmpeg
# or
brew upgrade ffmpeg
```

### Python Package Issues
```bash
# Create virtual environment
python -m venv .venv-video
source .venv-video/bin/activate

# Install packages
pip install -r scripts/requirements_video_processing.txt
```

## Example Output

### Extracted Code Sample
```python
# Code at 05:42
class MultiAgentCoordinator:
    def __init__(self, agents):
        self.agents = agents
        self.message_queue = []
    
    def coordinate(self, task):
        # Distribute task among agents
        subtasks = self.decompose_task(task)
        results = []
        for agent, subtask in zip(self.agents, subtasks):
            result = agent.execute(subtask)
            results.append(result)
        return self.synthesize_results(results)
```

### Analysis Sample
```markdown
## Main Topic and Objectives
Building production-ready multi-agent systems with emphasis on:
- Scalable agent coordination
- Robust error handling
- Inter-agent communication protocols

## Key Concepts Explained
1. Agent orchestration patterns
2. Message passing architectures
3. Consensus mechanisms
4. Failure recovery strategies
...
```

## Future Enhancements

- [ ] Real-time processing during video playback
- [ ] Interactive code extraction UI
- [ ] Support for multiple programming languages
- [ ] Integration with IDE for direct code import
- [ ] Batch processing for video playlists
- [ ] Cloud deployment for distributed processing

## License
MIT License - See LICENSE file for details