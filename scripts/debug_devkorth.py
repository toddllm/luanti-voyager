#!/usr/bin/env python3
"""
Debug script for Devkorth mod
Part of the luanti-voyager project
"""

import os
import sys
import subprocess
import time
import re
from pathlib import Path

class DevkorthDebugger:
    def __init__(self, server_log_path="/var/log/minetest/minetest.log"):
        self.log_path = server_log_path
        self.devkorth_mod_path = "/var/games/minetest-server/.minetest/mods/devkorth_mod"
        
    def check_mod_installed(self):
        """Check if Devkorth mod is properly installed"""
        print("🔍 Checking Devkorth mod installation...")
        
        if not os.path.exists(self.devkorth_mod_path):
            print(f"❌ Devkorth mod not found at {self.devkorth_mod_path}")
            return False
            
        required_files = ["init.lua", "mod.conf", "entity.lua", "shrine.lua", "api.lua", "items.lua", "powers.lua"]
        for file in required_files:
            path = os.path.join(self.devkorth_mod_path, file)
            if not os.path.exists(path):
                print(f"❌ Missing required file: {file}")
                return False
                
        print("✅ All required files present")
        return True
        
    def check_mod_enabled(self, world_path="/var/games/minetest-server/.minetest/worlds/world"):
        """Check if mod is enabled in world.mt"""
        print("\n🔍 Checking if mod is enabled...")
        
        world_mt = os.path.join(world_path, "world.mt")
        if not os.path.exists(world_mt):
            print(f"❌ world.mt not found at {world_mt}")
            return False
            
        with open(world_mt, 'r') as f:
            content = f.read()
            
        if "load_mod_devkorth_mod = true" in content:
            print("✅ Devkorth mod is enabled")
            return True
        elif "load_mod_devkorth_mod = false" in content:
            print("❌ Devkorth mod is disabled in world.mt")
            return False
        else:
            print("⚠️  Devkorth mod not mentioned in world.mt")
            return False
            
    def tail_log_for_devkorth(self, duration=30):
        """Tail the server log looking for Devkorth messages"""
        print(f"\n📋 Monitoring log for {duration} seconds...")
        print("Looking for Devkorth DEBUG messages...\n")
        
        start_time = time.time()
        devkorth_pattern = re.compile(r'\[Devkorth.*?\].*')
        error_pattern = re.compile(r'ERROR.*devkorth', re.IGNORECASE)
        
        try:
            # Use tail -f to follow the log
            process = subprocess.Popen(
                ['tail', '-f', self.log_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            while time.time() - start_time < duration:
                line = process.stdout.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                    
                # Check for Devkorth messages
                if devkorth_pattern.search(line):
                    print(f"🔷 {line.strip()}")
                elif error_pattern.search(line):
                    print(f"❌ {line.strip()}")
                elif "shrine" in line.lower() or "manifest" in line.lower():
                    print(f"🏛️ {line.strip()}")
                    
        except KeyboardInterrupt:
            print("\n\nStopped monitoring.")
        finally:
            process.terminate()
            
    def analyze_recent_errors(self):
        """Analyze recent log entries for Devkorth errors"""
        print("\n🔍 Analyzing recent log entries for errors...")
        
        try:
            # Get last 200 lines of log
            result = subprocess.run(
                ['tail', '-n', '200', self.log_path],
                capture_output=True,
                text=True
            )
            
            lines = result.stdout.split('\n')
            errors = []
            devkorth_msgs = []
            
            for line in lines:
                if 'ERROR' in line and 'devkorth' in line.lower():
                    errors.append(line)
                elif '[Devkorth' in line:
                    devkorth_msgs.append(line)
                    
            if errors:
                print(f"\n❌ Found {len(errors)} Devkorth-related errors:")
                for error in errors[-5:]:  # Show last 5 errors
                    print(f"  {error}")
            else:
                print("✅ No recent Devkorth errors found")
                
            if devkorth_msgs:
                print(f"\n📋 Last {min(10, len(devkorth_msgs))} Devkorth messages:")
                for msg in devkorth_msgs[-10:]:
                    print(f"  {msg}")
                    
        except Exception as e:
            print(f"❌ Error reading log: {e}")
            
    def test_shrine_coordinates(self):
        """Provide test coordinates for shrine building"""
        print("\n🏛️ Shrine Building Guide:")
        print("Build at coordinates around spawn (0, 0, 0)")
        print("\nStructure (5x5 base + 4 pillars):")
        print("  - Base: 5x5 diamond blocks at ground level")
        print("  - Center: 1 mese block on top of center diamond block")
        print("  - Pillars: 3-high diamond blocks at each corner")
        print("\nConditions needed:")
        print("  - Night time (use time_crystal if needed)")
        print("  - Water within 10 blocks")
        print("  - Coal block or bones within 15 blocks")
        print("  - Open sky above (no blocks 10+ blocks up)")
        
    def check_server_port(self, port=50000):
        """Check if server is running on correct port"""
        print(f"\n🔍 Checking if server is running on port {port}...")
        
        try:
            result = subprocess.run(
                ['lsof', '-i', f':{port}'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Server is running on port {port}")
                return True
            else:
                print(f"❌ No server found on port {port}")
                return False
        except:
            # Try netstat as fallback
            try:
                result = subprocess.run(
                    ['netstat', '-tuln'],
                    capture_output=True,
                    text=True
                )
                if f':{port}' in result.stdout:
                    print(f"✅ Server is listening on port {port}")
                    return True
                else:
                    print(f"❌ No server found on port {port}")
                    return False
            except:
                print("⚠️  Could not check port status")
                return None

def main():
    print("🎮 Devkorth Mod Debugger")
    print("========================\n")
    
    # Allow custom log path
    log_path = "/var/log/minetest/minetest.log"
    if len(sys.argv) > 1:
        log_path = sys.argv[1]
        
    debugger = DevkorthDebugger(log_path)
    
    # Run all checks
    debugger.check_mod_installed()
    debugger.check_mod_enabled()
    debugger.check_server_port(50000)
    debugger.analyze_recent_errors()
    debugger.test_shrine_coordinates()
    
    print("\n📋 Starting live log monitoring...")
    print("Build a shrine and watch for debug messages!")
    print("Press Ctrl+C to stop monitoring.\n")
    
    debugger.tail_log_for_devkorth(duration=300)  # Monitor for 5 minutes

if __name__ == "__main__":
    main()