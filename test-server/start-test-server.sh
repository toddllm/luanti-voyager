#!/bin/bash
# Start script for Luanti Voyager test server
# This runs our custom Luanti fork on port 40000

set -e

echo "🧪 Luanti Voyager Test Server Launcher"
echo "====================================="
echo "⚠️  This runs on PORT 40000 (not the default 30000)"
echo "⚠️  This is for TESTING ONLY - not production!"
echo

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Paths
LUANTI_BIN="$PROJECT_ROOT/luanti-source-voyager-fork/bin/luanti"
LUANTI_SRC="$PROJECT_ROOT/luanti-source-voyager-fork"
TEST_WORLD="$SCRIPT_DIR/test_world"
CONFIG_FILE="$SCRIPT_DIR/luanti-test.conf"
MODS_DIR="$TEST_WORLD/worldmods"

# Check if we need to build Luanti
if [ ! -f "$LUANTI_BIN" ]; then
    echo "⚙️  Luanti binary not found. Building from source..."
    echo "This may take a few minutes on first run..."
    
    cd "$LUANTI_SRC"
    
    # Create build directory
    mkdir -p build
    cd build
    
    # Configure with minimal dependencies for faster build
    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_CLIENT=ON \
        -DBUILD_SERVER=ON \
        -DENABLE_GETTEXT=OFF \
        -DENABLE_CURSES=OFF \
        -DENABLE_SOUND=OFF
    
    # Build (use available cores)
    make -j$(nproc)
    
    echo "✅ Build complete!"
    cd "$SCRIPT_DIR"
else
    echo "✅ Found Luanti binary at: $LUANTI_BIN"
fi

# Create test world if it doesn't exist
if [ ! -d "$TEST_WORLD" ]; then
    echo "🌍 Creating test world..."
    mkdir -p "$TEST_WORLD"
    
    # Create world.mt file
    cat > "$TEST_WORLD/world.mt" <<EOF
enable_damage = false
creative_mode = true
gameid = devtest
backend = sqlite3
player_backend = sqlite3
auth_backend = sqlite3
load_mod_voyager_bot = true
server_announce = false
EOF
fi

# Copy our mod to the world
echo "📦 Installing voyager_bot mod..."
mkdir -p "$MODS_DIR"
cp -r "$PROJECT_ROOT/mods/voyager_bot" "$MODS_DIR/"

# Create a marker file to identify this as test server
touch "$TEST_WORLD/.voyager_test_world"

# Check if server is already running on port 40000
if lsof -Pi :40000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "❌ Port 40000 is already in use!"
    echo "Is the test server already running?"
    exit 1
fi

# Start the server
echo
echo "🚀 Starting test server on port 40000..."
echo "Press Ctrl+C to stop"
echo
echo "Connect with: luanti --address 127.0.0.1 --port 40000"
echo "Or run agent: python -m luanti_voyager.main --port 40000"
echo

# Run server with our config
exec "$LUANTI_BIN" \
    --server \
    --world "$TEST_WORLD" \
    --config "$CONFIG_FILE" \
    --port 40000 \
    --logfile "$SCRIPT_DIR/test-server.log"