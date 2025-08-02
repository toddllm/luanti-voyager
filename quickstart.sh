#!/bin/bash
# Quick start script for Luanti Voyager

echo "🚀 Luanti Voyager Quick Start"
echo "============================"
echo

# Check if Luanti is installed
if ! command -v luanti &> /dev/null && ! command -v minetest &> /dev/null; then
    echo "❌ Luanti/Minetest not found!"
    echo "Please install Luanti first: https://www.luanti.org/downloads/"
    exit 1
fi

# Detect Luanti command
if command -v luanti &> /dev/null; then
    LUANTI_CMD="luanti"
else
    LUANTI_CMD="minetest"
fi

echo "✅ Found Luanti at: $(which $LUANTI_CMD)"

# Create Python virtual environment
echo
echo "📦 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -e .

# Create test world if it doesn't exist
echo
echo "🌍 Setting up test world..."
mkdir -p worlds/test_world

# Copy our mod to Luanti mods directory
echo
echo "🔧 Installing Voyager bot mod..."
MODS_DIR="$HOME/.luanti/mods"
if [ ! -d "$MODS_DIR" ]; then
    MODS_DIR="$HOME/.minetest/mods"
fi

mkdir -p "$MODS_DIR"
cp -r mods/voyager_bot "$MODS_DIR/"

echo
echo "✨ Setup complete!"
echo
echo "To start experimenting:"
echo "1. Start Luanti and create a new world with the 'voyager_bot' mod enabled"
echo "2. In another terminal, run: python -m luanti_voyager.main"
echo
echo "Or try the example:"
echo "  python examples/simple_agent.py"
echo
echo "Happy exploring! 🤖"