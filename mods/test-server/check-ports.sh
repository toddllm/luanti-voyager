#!/bin/bash
# Check which Luanti servers are running

echo "🔍 Checking Luanti server ports..."
echo "================================="
echo

# Check production port (30000)
echo "Production Port (30000):"
if lsof -Pi :30000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ RUNNING - DO NOT DISTURB"
    lsof -Pi :30000 -sTCP:LISTEN
else
    echo "❌ Not running"
fi

echo
echo "Test Port (40000):"
if lsof -Pi :40000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Running"
    lsof -Pi :40000 -sTCP:LISTEN
else
    echo "❌ Not running"
fi

echo
echo "Other Luanti processes:"
ps aux | grep -E "(luanti|minetest)" | grep -v grep || echo "None found"