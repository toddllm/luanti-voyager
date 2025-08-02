#!/bin/bash
# Build vanilla Luanti from our fork to establish baseline
# This builds WITHOUT any modifications to prove the fork works

set -e

echo "🏗️  Building Vanilla Luanti Fork"
echo "================================"
echo "This builds the unmodified fork to establish a working baseline"
echo

# Get directories
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
LUANTI_SRC="$PROJECT_ROOT/luanti-source-voyager-fork"
BUILD_DIR="$LUANTI_SRC/build"

# Check dependencies
echo "📋 Checking build dependencies..."
MISSING_DEPS=""

# Check for essential build tools
for cmd in cmake make g++ git; do
    if ! command -v $cmd &> /dev/null; then
        MISSING_DEPS="$MISSING_DEPS $cmd"
    fi
done

if [ ! -z "$MISSING_DEPS" ]; then
    echo "❌ Missing dependencies:$MISSING_DEPS"
    echo
    echo "Install with:"
    echo "sudo apt-get update"
    echo "sudo apt-get install build-essential cmake git"
    exit 1
fi

echo "✅ Build tools found"

# Check for Luanti dependencies
echo
echo "📦 Checking library dependencies..."
echo "Note: This is a minimal build for testing"

# Record current state
cd "$LUANTI_SRC"
echo
echo "📊 Source information:"
echo "Path: $LUANTI_SRC"
if [ -d .git ]; then
    echo "Git commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
    echo "Git branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"
else
    echo "Git info: Not a git repository (copied source)"
fi

# Clean previous build if exists
if [ -d "$BUILD_DIR" ]; then
    echo
    echo "🧹 Cleaning previous build..."
    rm -rf "$BUILD_DIR"
fi

# Create build directory
echo
echo "🔨 Starting build..."
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Configure with minimal dependencies for faster build
echo "Configuring..."
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_CLIENT=ON \
    -DBUILD_SERVER=ON \
    -DENABLE_GETTEXT=OFF \
    -DENABLE_CURSES=OFF \
    -DENABLE_SOUND=OFF \
    -DENABLE_POSTGRESQL=OFF \
    -DENABLE_LEVELDB=OFF \
    -DENABLE_REDIS=OFF \
    -DENABLE_PROMETHEUS=OFF \
    -DENABLE_SPATIAL=OFF \
    -DRUN_IN_PLACE=TRUE

# Build
echo
echo "Building (this may take a few minutes)..."
CORES=$(nproc)
echo "Using $CORES CPU cores"
make -j$CORES

# Check if build succeeded
if [ -f "$LUANTI_SRC/bin/luanti" ]; then
    echo
    echo "✅ BUILD SUCCESSFUL!"
    echo
    echo "Binary location: $LUANTI_SRC/bin/luanti"
    echo "Version info:"
    "$LUANTI_SRC/bin/luanti" --version
    
    # Create build info file
    cat > "$SCRIPT_DIR/build-info.txt" <<EOF
Luanti Fork Build Information
============================
Build Date: $(date)
Build Type: Vanilla (unmodified)
Source Path: $LUANTI_SRC
Binary Path: $LUANTI_SRC/bin/luanti
Build Configuration:
- Client: ON
- Server: ON
- Sound: OFF (minimal build)
- Internationalization: OFF (minimal build)
- Run in place: TRUE

Version Output:
$("$LUANTI_SRC/bin/luanti" --version 2>&1)
EOF
    
    echo
    echo "Build info saved to: $SCRIPT_DIR/build-info.txt"
    echo
    echo "Next steps:"
    echo "1. Run ./start-test-server.sh to test the server"
    echo "2. Check ./test-server.log for any issues"
    
else
    echo
    echo "❌ BUILD FAILED!"
    echo "Check the output above for errors"
    exit 1
fi