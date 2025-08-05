#!/bin/bash
# Process AI Makerspace videos with proper virtual environment

# Ensure we're in the project directory
cd "$(dirname "$0")/.."

# Activate the virtual environment
source .venv-whisper/bin/activate

# Process each video
echo "Processing AI Makerspace videos..."

# Vector Memory (Issue #21)
echo "1. Processing Vector Memory video..."
python scripts/process_ai_makerspace_video.py \
    "https://youtu.be/XwUD9uXL0eg" \
    "LlamaIndex Agent Memory" \
    "21" &

# Let's process one at a time for now to avoid overload
wait

echo "Video processing complete!"