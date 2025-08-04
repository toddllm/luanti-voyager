#!/usr/bin/env python3
"""
Test Shrine Commands Generator
Generates a sequence of commands that can be copied and pasted
into the game console to test Devkorth shrine building.
"""

def generate_shrine_commands(center=(10, 10, 10), username="ToddLLM"):
    """Generate complete command sequence for shrine building"""
    cx, cy, cz = center
    
    commands = f"""
# DEVKORTH SHRINE QUICK BUILD COMMANDS
# ====================================
# Copy and paste these commands into the game console
# Make sure you're connected to localhost:50000

# 1. Grant privileges
/grant {username} all

# 2. Teleport to build location
/teleport {cx} {cy + 5} {cz}

# 3. Give materials
/giveme default:diamondblock 99
/giveme default:mese 10
/giveme default:water_source 10
/giveme default:coalblock 10
/giveme devkorth:time_crystal 5

# 4. Set time to night
/time 0:00

# 5. Clear area (optional - use pickaxe)
# Dig around ({cx}, {cy}, {cz}) to make space

# 6. Place blocks manually:
# BASE (5x5 diamond blocks at y={cy}):
"""
    
    # Generate base coordinates
    for x in range(cx - 2, cx + 3):
        for z in range(cz - 2, cz + 3):
            commands += f"# - ({x}, {cy}, {z})\n"
    
    commands += f"""
# CENTRAL MESE:
# - ({cx}, {cy + 1}, {cz})

# PILLARS (3 high at corners):
"""
    
    # Generate pillar coordinates
    corners = [(cx-2, cz-2), (cx-2, cz+2), (cx+2, cz-2), (cx+2, cz+2)]
    for i, (px, pz) in enumerate(corners, 1):
        commands += f"# Corner {i}:\n"
        for h in range(1, 4):
            commands += f"# - ({px}, {cy + h}, {pz})\n"
    
    commands += f"""
# CONDITIONS:
# Water source at: ({cx + 5}, {cy}, {cz})
# Coal block at: ({cx - 8}, {cy}, {cz})

# 7. Check status
/status

# EXPECTED RESULT:
# When all conditions are met at night, you should see:
# - "The fabric of reality trembles..."
# - "DEVKORTH HAS MANIFESTED!"

# DEBUG: Check server log for [Devkorth DEBUG] messages
"""
    
    return commands


def generate_worldedit_commands(center=(10, 10, 10)):
    """Generate WorldEdit commands for faster building"""
    cx, cy, cz = center
    
    commands = f"""
# WORLDEDIT QUICK BUILD (if available)
# ===================================

# 1. Set position 1 (base corner)
//1
/teleport {cx-2} {cy} {cz-2}

# 2. Set position 2 (opposite corner) 
//2
/teleport {cx+2} {cy} {cz+2}

# 3. Fill with diamond blocks
//set default:diamondblock

# 4. Place central mese manually
/teleport {cx} {cy+1} {cz}
# Place mese block here

# 5. Build pillars with WorldEdit
# (Set positions and fill for each pillar)
"""
    
    return commands


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate Devkorth shrine building commands'
    )
    parser.add_argument('--center', nargs=3, type=int, default=[10, 10, 10],
                        help='Shrine center coordinates (default: 10 10 10)')
    parser.add_argument('--username', default='ToddLLM',
                        help='Username for privilege grant')
    parser.add_argument('--worldedit', action='store_true',
                        help='Include WorldEdit commands')
    
    args = parser.parse_args()
    
    center = tuple(args.center)
    
    print(generate_shrine_commands(center, args.username))
    
    if args.worldedit:
        print(generate_worldedit_commands(center))
    
    print("\n# Save these commands to a file or copy them to the game!")
    print(f"# Shrine will be built at: {center}")


if __name__ == "__main__":
    main()