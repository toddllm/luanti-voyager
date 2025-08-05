#!/bin/bash
# Quick start script for Ollama + Luanti Voyager

echo "🚀 Luanti Voyager with Ollama - Quick Start"
echo "=========================================="
echo

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Please install from: https://ollama.ai/"
    exit 1
fi

# Check if Ollama server is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "🔄 Starting Ollama server..."
    ollama serve &
    sleep 3
fi

# Check for available models
echo "📋 Checking available models..."
MODELS=$(ollama list | grep -E "(llama3|qwen|mistral)" | head -1 | awk '{print $1}')

if [ -z "$MODELS" ]; then
    echo "📥 No suitable models found. Downloading llama3.1..."
    ollama pull llama3.1
    MODELS="llama3.1:latest"
fi

echo "✅ Using model: $MODELS"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating .env configuration..."
    cat > .env << EOF
# Luanti Voyager Configuration
OLLAMA_MODEL=$MODELS
OLLAMA_BASE_URL=http://localhost:11434
AGENT_NAME=LocalBot
LOG_LEVEL=INFO
EOF
    echo "✅ Created .env file"
fi

# Check if terrain test server is running
if ! lsof -i :40000 > /dev/null 2>&1; then
    echo "⚠️  Terrain test server not running on port 40000"
    echo "   You can start it with: cd test-server && ./start-test-server.sh"
    echo "   Or use default port 30000"
    PORT_FLAG=""
else
    echo "✅ Terrain test server detected on port 40000"
    PORT_FLAG="--port 40000"
fi

echo
echo "🤖 Starting Luanti Voyager with Ollama..."
echo "   Model: $MODELS"
echo "   Press Ctrl+C to stop"
echo

# Start the agent
exec python -m luanti_voyager --llm ollama --name LocalBot $PORT_FLAG