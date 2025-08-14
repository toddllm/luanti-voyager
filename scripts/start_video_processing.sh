#!/bin/bash

# Start full video processing in background
# Video: "Building Production-Ready Multi-Agent Systems"

VIDEO_URL="https://www.youtube.com/watch?v=nyb3TnUkwE8"
VIDEO_TITLE="Building_Production_Ready_Multi_Agent_Systems"
OUTPUT_DIR="docs/video-analysis/multi-agent-systems"
LOG_FILE="docs/video-analysis/processing.log"

echo "🚀 Starting full video processing in background"
echo "================================================"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running. Starting Ollama..."
    ollama serve > /dev/null 2>&1 &
    sleep 5
fi

# Check if gpt-oss:120b model is available
if ! ollama list | grep -q "gpt-oss:120b"; then
    echo "📥 Model gpt-oss:120b not found. Please run:"
    echo "   ollama pull gpt-oss:120b"
    exit 1
fi

# Start processing in background with nohup
echo "📹 Processing video: $VIDEO_URL"
echo "📁 Output directory: $OUTPUT_DIR"
echo "📝 Log file: $LOG_FILE"
echo ""

nohup python3 scripts/process_video_with_code_extraction.py \
    "$VIDEO_URL" \
    --title "$VIDEO_TITLE" \
    --model "gpt-oss:120b" \
    --whisper-model "large-v3" \
    --output-dir "$OUTPUT_DIR" \
    > "$LOG_FILE" 2>&1 &

PID=$!
echo "✅ Processing started with PID: $PID"
echo ""
echo "To check progress, run:"
echo "  ./scripts/check_video_progress.sh"
echo ""
echo "To watch logs in real-time:"
echo "  tail -f $LOG_FILE"
echo ""
echo "To stop processing:"
echo "  kill $PID"

# Save PID for later reference
echo $PID > docs/video-analysis/processing.pid

echo ""
echo "The process will continue running even if you close this terminal."
echo "Estimated time: 15-30 minutes for a 1-hour video"