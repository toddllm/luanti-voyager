#!/bin/bash
# Monitor Devkorth shrine activity in real-time

echo "🔮 Devkorth Shrine Activity Monitor"
echo "==================================="
echo "Watching for shrine checks and manifestations..."
echo

# Check if server is running
if ! lsof -Pi :50000 -t >/dev/null 2>&1; then
    echo "❌ Test server not running on port 50000"
    echo "💡 Start with: ./scripts/launch_devkorth_test_server.sh"
    exit 1
fi

echo "✅ Server running on port 50000"
echo "📋 Monitoring /home/tdeshane/luanti/devkorth_test.log"
echo
echo "Key events to watch for:"
echo "  🟢 [Devkorth DEBUG] - Debug messages"
echo "  🔵 'shrine' - Shrine detection"
echo "  🟣 'manifest' - Manifestation events"
echo "  🔴 'ERROR' - Errors"
echo "  🟡 Player actions"
echo

# Monitor with grep highlighting
tail -f /home/tdeshane/luanti/devkorth_test.log | grep --line-buffered -E "(Devkorth|shrine|manifest|ToddLLM|Toby|water|coal|diamond|mese|night)" | while IFS= read -r line; do
    # Color based on content
    if [[ $line == *"[Devkorth DEBUG]"* ]]; then
        echo -e "\033[0;32m$line\033[0m"  # Green
    elif [[ $line == *"check_shrine"* ]] || [[ $line == *"shrine detected"* ]]; then
        echo -e "\033[0;34m$line\033[0m"  # Blue
    elif [[ $line == *"MANIFEST"* ]] || [[ $line == *"trembles"* ]]; then
        echo -e "\033[0;35m$line\033[0m"  # Purple
    elif [[ $line == *"ERROR"* ]]; then
        echo -e "\033[0;31m$line\033[0m"  # Red
    elif [[ $line == *"ToddLLM"* ]] || [[ $line == *"Toby"* ]]; then
        echo -e "\033[1;33m$line\033[0m"  # Yellow
    elif [[ $line == *"conditions"* ]]; then
        echo -e "\033[0;36m$line\033[0m"  # Cyan
    else
        echo "$line"
    fi
done