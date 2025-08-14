#!/bin/bash

# Process the specific video with code extraction
# Video: "Building Production-Ready Multi-Agent Systems"

VIDEO_URL="https://www.youtube.com/watch?v=nyb3TnUkwE8"
VIDEO_TITLE="Building_Production_Ready_Multi_Agent_Systems"
OUTPUT_DIR="docs/video-analysis/multi-agent-systems"

echo "🎬 Processing Multi-Agent Systems Video"
echo "========================================"
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running. Starting Ollama..."
    ollama serve &
    sleep 5
fi

# Check if gpt-oss:120b model is available
if ! ollama list | grep -q "gpt-oss:120b"; then
    echo "📥 Pulling gpt-oss:120b model (this may take a while)..."
    ollama pull gpt-oss:120b
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Process the video
echo "🚀 Starting video processing..."
echo ""

python3 scripts/process_video_with_code_extraction.py \
    "$VIDEO_URL" \
    --title "$VIDEO_TITLE" \
    --model "gpt-oss:120b" \
    --whisper-model "large-v3" \
    --output-dir "$OUTPUT_DIR"

echo ""
echo "✅ Processing complete!"
echo "📁 Results saved in: $OUTPUT_DIR"