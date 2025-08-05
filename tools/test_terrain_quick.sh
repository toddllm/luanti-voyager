#!/bin/bash
# Quick test for terrain generation

echo "Testing terrain generation..."
cd /home/tdeshane/luanti/luanti-voyager

# Make sure the server is using our updated mod
echo "Checking mod status..."
ls -la test-server/test_world/worldmods/voyager_bot/

# Run the terrain test
python3 test_terrain_generation.py