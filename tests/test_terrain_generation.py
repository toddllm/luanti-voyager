#!/usr/bin/env python3
"""Test terrain generation for the voyager bot mod"""

import os
import time
import json

def send_command(world_path, command):
    """Send a command to the voyager bot mod"""
    command_file = os.path.join(world_path, "voyager_commands.txt")
    response_file = os.path.join(world_path, "voyager_responses.txt")
    
    # Clear response file
    if os.path.exists(response_file):
        os.remove(response_file)
    
    # Write command
    with open(command_file, 'w') as f:
        f.write(command + '\n')
    
    # Wait for response
    time.sleep(0.5)
    
    # Read response
    if os.path.exists(response_file):
        with open(response_file, 'r') as f:
            lines = f.readlines()
            if lines:
                return json.loads(lines[-1])
    
    return None

def test_terrain_generation():
    """Test the terrain generation commands"""
    world_path = "/home/tdeshane/luanti/luanti-voyager/test-server/test_world"
    
    print("Testing terrain generation...")
    
    # First spawn a bot
    print("\n1. Spawning bot...")
    response = send_command(world_path, "spawn TestBot 0 10 0")
    print(f"Response: {response}")
    
    # Test generate with bot name
    print("\n2. Testing generate with bot name...")
    response = send_command(world_path, "generate TestBot 10")
    print(f"Response: {response}")
    
    # Get bot state to see if terrain was generated
    print("\n3. Getting bot state to check for terrain...")
    response = send_command(world_path, "state TestBot")
    if response and 'state' in response:
        nodes = response['state'].get('nearby_nodes', [])
        print(f"Found {len(nodes)} nearby nodes")
        # Show first few nodes
        for node in nodes[:5]:
            print(f"  - {node['name']} at {node['pos']}")
    
    # Test generate with coordinates
    print("\n4. Testing generate with coordinates...")
    response = send_command(world_path, "generate 20 10 20 15")
    print(f"Response: {response}")
    
    # Teleport bot to new terrain
    print("\n5. Teleporting bot to new terrain...")
    response = send_command(world_path, "teleport TestBot 20 11 20")
    print(f"Response: {response}")
    
    # Check state again
    print("\n6. Getting bot state at new location...")
    response = send_command(world_path, "state TestBot")
    if response and 'state' in response:
        nodes = response['state'].get('nearby_nodes', [])
        print(f"Found {len(nodes)} nearby nodes")
        # Show first few nodes
        for node in nodes[:5]:
            print(f"  - {node['name']} at {node['pos']}")

if __name__ == "__main__":
    test_terrain_generation()