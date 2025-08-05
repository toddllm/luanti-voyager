#!/bin/bash
# Test the web UI standalone

echo "🌐 Starting Luanti Voyager Web UI"
echo "================================="
echo

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install dependencies if needed
pip install aiohttp websockets > /dev/null 2>&1

echo "Starting web server..."
echo
echo "📱 LAN Access URLs:"
echo "   Web UI: http://192.168.68.145:8080"
echo "   WebSocket: ws://192.168.68.145:8765"
echo
echo "💻 Local Access URLs:"
echo "   Web UI: http://localhost:8080"
echo "   WebSocket: ws://localhost:8765"
echo
echo "Press Ctrl+C to stop"
echo

python -m luanti_voyager.web_server