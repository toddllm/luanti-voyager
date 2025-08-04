#!/bin/bash
# Quick status check for Devkorth mod and servers

echo "🔍 Devkorth Status Check"
echo "========================"
echo

# Check production server (30000)
echo "📌 Production Server (Port 30000):"
if lsof -Pi :30000 -t >/dev/null 2>&1; then
    echo "   ✅ Running"
else
    echo "   ❌ Not running"
fi

# Check test server (50000)
echo
echo "🧪 Test Server (Port 50000):"
if lsof -Pi :50000 -t >/dev/null 2>&1; then
    echo "   ✅ Running"
    echo "   📋 Log: /home/tdeshane/luanti/devkorth_test.log"
else
    echo "   ❌ Not running"
    echo "   💡 Start with: ./scripts/launch_devkorth_test_server.sh"
fi

# Check mod installation
echo
echo "📦 Devkorth Mod Status:"
MOD_PATH="/var/games/minetest-server/.minetest/mods/devkorth_mod"
if [ -d "$MOD_PATH" ]; then
    echo "   ✅ Installed at: $MOD_PATH"
    if [ -f "$MOD_PATH/init.lua" ]; then
        echo "   ✅ init.lua present"
    fi
    if grep -q "devkorth.debug = true" "$MOD_PATH/init.lua" 2>/dev/null; then
        echo "   ✅ Debug mode enabled"
    fi
else
    echo "   ❌ Not found at expected location"
fi

# Check world configuration
echo
echo "🌍 World Configuration:"
PROD_WORLD="/var/games/minetest-server/.minetest/worlds/world/world.mt"
if [ -f "$PROD_WORLD" ]; then
    if grep -q "load_mod_devkorth" "$PROD_WORLD" 2>/dev/null && grep -q "= true" "$PROD_WORLD" 2>/dev/null; then
        echo "   ✅ Enabled in production world"
    else
        echo "   ❌ Not enabled in production world"
    fi
fi

TEST_WORLD="/home/tdeshane/luanti/devkorth_test_world/world.mt"
if [ -f "$TEST_WORLD" ]; then
    if grep -q "load_mod_devkorth_mod = true" "$TEST_WORLD" 2>/dev/null; then
        echo "   ✅ Enabled in test world"
    else
        echo "   ❌ Not enabled in test world"
    fi
fi

# Recent errors
echo
echo "📋 Recent Devkorth Log Entries:"
LOG_FILE="/home/tdeshane/luanti/devkorth_test.log"
if [ -f "$LOG_FILE" ]; then
    echo "   Last 5 Devkorth messages:"
    grep -i "devkorth" "$LOG_FILE" 2>/dev/null | tail -5 | sed 's/^/   /'
else
    echo "   No log file found"
fi

echo
echo "🚀 Quick Actions:"
echo "   - Start test server: ./scripts/launch_devkorth_test_server.sh"
echo "   - Test manually: python3 scripts/manual_devkorth_test.py"
echo "   - Debug logs: python3 scripts/debug_devkorth.py"
echo "   - Full guide: docs/devkorth_testing_guide.md"
echo