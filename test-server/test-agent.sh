#!/bin/bash
# Test agent connection to test server

echo "🤖 Testing Voyager Agent on Test Server"
echo "======================================"
echo

# Check if test server is running
if ! lsof -Pi :40000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "❌ Test server not running on port 40000!"
    echo "Please run ./start-test-server.sh first"
    exit 1
fi

echo "✅ Test server detected on port 40000"
echo

# Activate virtual environment if it exists
if [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# Run agent pointing to test world
cd ..
python -m luanti_voyager.main \
    --name "TestBot" \
    --world-path "./test-server/test_world" \
    --port 40000 \
    --verbose