#!/usr/bin/env python3
"""
Manual Devkorth Testing Helper
Generates commands to paste into the game console for testing Devkorth

Run this script and copy/paste the commands into the Luanti client
connected to localhost:50000
"""

import sys


def generate_test_commands():
    """Generate all commands needed to test Devkorth shrine"""
    
    commands = []
    
    # Header
    commands.append("# DEVKORTH SHRINE TEST COMMANDS")
    commands.append("# Copy and paste these into the game console")
    commands.append("#" + "="*50)
    commands.append("")
    
    # Grant privileges
    commands.append("# 1. Grant yourself privileges (replace YOUR_NAME)")
    commands.append("/grant YOUR_NAME all")
    commands.append("")
    
    # Teleport to test location
    commands.append("# 2. Teleport to build location")
    commands.append("/teleport 10 10 10")
    commands.append("")
    
    # Give materials
    commands.append("# 3. Give yourself building materials")
    commands.append("/giveme default:diamondblock 99")
    commands.append("/giveme default:mese 10")
    commands.append("/giveme default:water_source 10")
    commands.append("/giveme default:coalblock 10")
    commands.append("/giveme devkorth:time_crystal 5")
    commands.append("")
    
    # Time commands
    commands.append("# 4. Set time to night (for moonlight)")
    commands.append("/time 0:00")
    commands.append("")
    
    # Building instructions
    commands.append("# 5. BUILD THE SHRINE MANUALLY:")
    commands.append("#    a) Place 5x5 diamond blocks as base (at ground level)")
    commands.append("#    b) Place 1 mese block in center (1 block above base)")
    commands.append("#    c) Build 3-high diamond pillars at 4 corners")
    commands.append("#    d) Place water source within 10 blocks")
    commands.append("#    e) Place coal block within 15 blocks")
    commands.append("#    f) Ensure open sky above (no blocks 10+ up)")
    commands.append("")
    
    # Debug commands
    commands.append("# 6. Debug commands to check status")
    commands.append("/status")
    commands.append("")
    
    # Coordinates helper
    commands.append("# SHRINE STRUCTURE COORDINATES (center at 10,10,10):")
    commands.append("# Base layer (y=10):")
    for x in range(8, 13):
        for z in range(8, 13):
            commands.append(f"#   ({x}, 10, {z}) - diamond block")
    
    commands.append("# Center mese (y=11):")
    commands.append("#   (10, 11, 10) - mese block")
    
    commands.append("# Pillars (y=11,12,13):")
    corners = [(8, 8), (8, 12), (12, 8), (12, 12)]
    for x, z in corners:
        for y in range(11, 14):
            commands.append(f"#   ({x}, {y}, {z}) - diamond block")
    
    commands.append("")
    commands.append("# Water: place at (15, 10, 10)")
    commands.append("# Coal: place at (2, 10, 10)")
    
    return commands


def generate_worldedit_commands():
    """Generate WorldEdit commands for faster building"""
    
    commands = []
    
    commands.append("\n# WORLDEDIT QUICK BUILD (if available):")
    commands.append("//1")
    commands.append("//2")
    commands.append("//set default:diamondblock")
    
    return commands


def main():
    print("DEVKORTH SHRINE TESTING GUIDE")
    print("="*60)
    print()
    print("This script generates commands for manually testing Devkorth.")
    print("Connect to the test server at localhost:50000")
    print()
    
    # Generate commands
    manual_commands = generate_test_commands()
    we_commands = generate_worldedit_commands()
    
    # Print all commands
    for cmd in manual_commands:
        print(cmd)
    
    for cmd in we_commands:
        print(cmd)
    
    print("\n" + "="*60)
    print("WHAT TO EXPECT:")
    print("1. When all conditions are met, you should see:")
    print("   - 'The fabric of reality trembles...'")
    print("   - 'DEVKORTH HAS MANIFESTED!'")
    print("   - Particle effects around the shrine")
    print()
    print("2. If nothing happens, check server logs for:")
    print("   - [Devkorth DEBUG] messages")
    print("   - Shrine detection status")
    print("   - Condition check results")
    print()
    print("3. Common issues:")
    print("   - Not night time (use /time 0:00)")
    print("   - No water nearby (place water_source)")
    print("   - No fossils (place coalblock)")
    print("   - Sky blocked (remove blocks above)")
    print("="*60)
    

if __name__ == "__main__":
    main()