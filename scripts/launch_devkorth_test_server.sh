#!/bin/bash
# Launch script for Devkorth test server
# Part of luanti-voyager project

set -e

echo "🎮 Devkorth Test Server Launcher"
echo "================================"
echo "Port: 50000 (test server)"
echo

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Check if port 50000 is in use
if lsof -Pi :50000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "❌ Port 50000 is already in use!"
    echo "Stop the existing server first."
    exit 1
fi

# Paths
WORLD_DIR="/home/tdeshane/luanti/devkorth_test_world"
LOG_FILE="/home/tdeshane/luanti/devkorth_test.log"
DEVKORTH_MOD="/var/games/minetest-server/.minetest/mods/devkorth_mod"

# Find minetest/luanti binary
if command -v minetest &> /dev/null; then
    MINETEST_BIN="minetest"
elif command -v minetestserver &> /dev/null; then
    MINETEST_BIN="minetestserver"
elif command -v luanti &> /dev/null; then
    MINETEST_BIN="luanti"
elif [ -x "$PROJECT_ROOT/luanti-source-voyager-fork/bin/luanti" ]; then
    MINETEST_BIN="$PROJECT_ROOT/luanti-source-voyager-fork/bin/luanti"
else
    echo "❌ No minetest/luanti binary found!"
    echo "Options:"
    echo "1. Install minetest: sudo apt-get install minetest-server"
    echo "2. Build from source: cd $PROJECT_ROOT && ./test-server/build-vanilla.sh"
    exit 1
fi

echo "✅ Using binary: $MINETEST_BIN"

# Create world directory
mkdir -p "$WORLD_DIR"
mkdir -p "$WORLD_DIR/worldmods"

# Copy Devkorth mod to world
if [ -d "$DEVKORTH_MOD" ]; then
    echo "📦 Installing Devkorth mod..."
    mkdir -p "$WORLD_DIR/worldmods/devkorth_mod"
    # Copy only necessary files, excluding .git
    cp -r "$DEVKORTH_MOD"/*.lua "$WORLD_DIR/worldmods/devkorth_mod/" 2>/dev/null || true
    cp -r "$DEVKORTH_MOD"/*.txt "$WORLD_DIR/worldmods/devkorth_mod/" 2>/dev/null || true
    cp -r "$DEVKORTH_MOD"/*.md "$WORLD_DIR/worldmods/devkorth_mod/" 2>/dev/null || true
    cp -r "$DEVKORTH_MOD"/*.conf "$WORLD_DIR/worldmods/devkorth_mod/" 2>/dev/null || true
    cp -r "$DEVKORTH_MOD"/textures "$WORLD_DIR/worldmods/devkorth_mod/" 2>/dev/null || true
else
    echo "❌ Devkorth mod not found at $DEVKORTH_MOD"
    exit 1
fi

# Also copy dependencies
echo "📦 Installing dependencies..."
cp -r /var/games/minetest-server/.minetest/mods/kitz "$WORLD_DIR/worldmods/" 2>/dev/null || true
cp -r /var/games/minetest-server/.minetest/mods/petz "$WORLD_DIR/worldmods/" 2>/dev/null || true

# Create world.mt configuration
cat > "$WORLD_DIR/world.mt" <<EOF
enable_damage = true
creative_mode = false
gameid = minetest_game
backend = sqlite3
auth_backend = sqlite3
player_backend = sqlite3

# Core mods
load_mod_default = true
load_mod_bones = true
load_mod_fire = true
load_mod_tnt = true

# Devkorth and dependencies
load_mod_devkorth_mod = true
load_mod_kitz = false
load_mod_petz = false

# Server settings
server_announce = false
EOF

# Create server configuration
cat > "$WORLD_DIR/minetest.conf" <<EOF
# Devkorth Test Server Configuration
port = 50000
name = DevkorthTestServer
server_name = Devkorth Test Realm
server_description = Testing the Legend of Devkorth
motd = Welcome to the Devkorth test server on port 50000!

# Enable debug logging
debug_log_level = verbose
enable_debug_logging = true

# World settings
creative_mode = false
enable_damage = true
enable_pvp = true
give_initial_items = default:torch 99,default:pickaxe_diamond,default:shovel_diamond

# Performance
dedicated_server_step = 0.05
active_block_range = 3
max_block_send_distance = 10

# Security
enable_rollback = true
disallow_empty_password = false
default_privs = interact,shout

# Devkorth specific
time_speed = 72
viewing_range = 1000
EOF

echo
echo "🚀 Starting Devkorth test server..."
echo "Server: localhost:50000"
echo "Log: $LOG_FILE"
echo
echo "To connect:"
echo "  minetest --address localhost --port 50000"
echo
echo "To test Devkorth:"
echo "  python3 $SCRIPT_DIR/manual_devkorth_test.py"
echo
echo "Press Ctrl+C to stop the server"
echo

# Launch server
if [ "$MINETEST_BIN" = "minetestserver" ]; then
    # minetestserver doesn't need --server flag
    exec $MINETEST_BIN \
        --world "$WORLD_DIR" \
        --config "$WORLD_DIR/minetest.conf" \
        --port 50000 \
        --logfile "$LOG_FILE"
else
    # minetest client needs --server flag
    exec $MINETEST_BIN \
        --server \
        --world "$WORLD_DIR" \
        --config "$WORLD_DIR/minetest.conf" \
        --port 50000 \
        --logfile "$LOG_FILE"
fi