#!/bin/bash
# Live monitoring script for Devkorth debug messages

echo "🔍 Monitoring Devkorth Debug Messages"
echo "===================================="
echo "Watching: /home/tdeshane/luanti/devkorth_test.log"
echo "Press Ctrl+C to stop"
echo

# Show initial status
echo "📊 Current Status:"
if lsof -Pi :50000 -t >/dev/null 2>&1; then
    echo "✅ Test server running on port 50000"
else
    echo "❌ Test server not running"
fi

echo
echo "📋 Starting live monitoring..."
echo "Looking for:"
echo "  - [Devkorth DEBUG] messages"
echo "  - Shrine detection"
echo "  - Manifestation events"
echo

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Monitor log with highlighting
tail -f /home/tdeshane/luanti/devkorth_test.log | while read line; do
    if echo "$line" | grep -q "\[Devkorth DEBUG\]"; then
        echo -e "${GREEN}$line${NC}"
    elif echo "$line" | grep -q "ERROR.*devkorth"; then
        echo -e "${RED}$line${NC}"
    elif echo "$line" | grep -q "shrine"; then
        echo -e "${BLUE}$line${NC}"
    elif echo "$line" | grep -q "MANIFEST"; then
        echo -e "${PURPLE}$line${NC}"
    elif echo "$line" | grep -q "check_"; then
        echo -e "${YELLOW}$line${NC}"
    elif echo "$line" | grep -q "devkorth" -i; then
        echo "$line"
    fi
done