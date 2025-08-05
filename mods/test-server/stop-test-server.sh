#!/bin/bash
# Safely stop the test server

echo "🛑 Stopping Luanti Test Server"
echo "============================="
echo

# Check if test server is running
if ! lsof -Pi :40000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "❌ Test server not running on port 40000"
    exit 0
fi

# Get PID of test server
TEST_PID=$(lsof -t -i :40000)

echo "Found test server PID: $TEST_PID"
echo "Sending shutdown signal..."

# Gracefully stop
kill -TERM $TEST_PID

# Wait a moment
sleep 2

# Check if stopped
if ! lsof -Pi :40000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Test server stopped successfully"
else
    echo "⚠️  Server still running, forcing stop..."
    kill -KILL $TEST_PID
    sleep 1
    echo "✅ Test server force stopped"
fi