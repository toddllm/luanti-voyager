#!/usr/bin/env python3
"""
Devkorth Shrine Demo
Example of using luanti-voyager to build a Devkorth shrine

This demonstrates how to use the voyager framework to:
1. Connect to a server
2. Execute commands
3. Build structures programmatically
"""

import sys
import time
import logging
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Since connection module is not exposed in the package API,
# we need to import it directly
try:
    # First try the public API
    from luanti_voyager import VoyagerAgent
    # For network connection, we need to import directly from the module
    import luanti_voyager.connection as connection_module
    LuantiConnection = connection_module.LuantiConnection
except ImportError:
    print("Error: Could not import luanti_voyager modules")
    print("Make sure you're running from the luanti-voyager directory")
    print("Try: cd /home/tdeshane/luanti/luanti-voyager && python3 examples/devkorth_shrine_demo.py")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DevkorthShrineAgent:
    """Extended agent for building Devkorth shrines"""
    
    def __init__(self, connection, username="ShrineBuilder"):
        self.connection = connection
        self.username = username
        self.shrine_center = (10, 10, 10)
        self.connected = False
        
    def execute_command(self, command):
        """Execute a chat command"""
        logger.info(f"Executing: {command}")
        self.send_chat_message(command)
        time.sleep(0.5)  # Give server time to process
        
    def give_materials(self):
        """Give ourselves building materials"""
        logger.info("Getting building materials...")
        materials = [
            "default:diamondblock 99",
            "default:mese 10", 
            "default:water_source 10",
            "default:coalblock 10",
            "devkorth:time_crystal 5"
        ]
        
        for material in materials:
            self.execute_command(f"/giveme {material}")
            
    def clear_build_area(self):
        """Clear area for shrine"""
        logger.info("Clearing build area...")
        cx, cy, cz = self.shrine_center
        
        # Clear a 10x10x10 area
        for y in range(cy - 2, cy + 8):
            for x in range(cx - 5, cx + 6):
                for z in range(cz - 5, cz + 6):
                    try:
                        self.dig_node(x, y, z)
                    except:
                        pass  # Node might not exist
                        
    def build_shrine_structure(self):
        """Build the shrine structure"""
        cx, cy, cz = self.shrine_center
        
        logger.info("Building shrine base...")
        # Build 5x5 diamond base
        for x in range(cx - 2, cx + 3):
            for z in range(cz - 2, cz + 3):
                self.place_node(x, cy, z, "default:diamondblock")
                time.sleep(0.05)
                
        logger.info("Placing central mese...")
        # Central mese block
        self.place_node(cx, cy + 1, cz, "default:mese")
        
        logger.info("Building pillars...")
        # Build 4 corner pillars
        corners = [(cx-2, cz-2), (cx-2, cz+2), (cx+2, cz-2), (cx+2, cz+2)]
        for corner_x, corner_z in corners:
            for height in range(1, 4):
                self.place_node(corner_x, cy + height, corner_z, "default:diamondblock")
                time.sleep(0.05)
                
    def create_conditions(self):
        """Create required conditions for manifestation"""
        cx, cy, cz = self.shrine_center
        
        logger.info("Creating water source...")
        # Water source
        self.dig_node(cx + 5, cy - 1, cz)  # Dig hole for water
        self.place_node(cx + 5, cy, cz, "default:water_source")
        
        logger.info("Placing fossil (coal block)...")
        # Coal block as fossil
        self.place_node(cx - 8, cy, cz, "default:coalblock")
        
        logger.info("Setting night time...")
        # Set night time
        self.execute_command("/time 0:00")
        
    def build_devkorth_shrine(self):
        """Complete shrine building process"""
        logger.info("=== DEVKORTH SHRINE BUILDING STARTED ===")
        
        # Teleport to build location
        cx, cy, cz = self.shrine_center
        self.execute_command(f"/teleport {cx} {cy + 5} {cz}")
        time.sleep(2)
        
        # Get materials
        self.give_materials()
        time.sleep(2)
        
        # Clear area
        self.clear_build_area()
        time.sleep(2)
        
        # Build structure
        self.build_shrine_structure()
        time.sleep(1)
        
        # Create conditions
        self.create_conditions()
        
        logger.info("=== SHRINE COMPLETE ===")
        logger.info(f"Location: {self.shrine_center}")
        logger.info("Now monitoring for Devkorth manifestation...")
        
        # Monitor for manifestation
        self.monitor_manifestation()
        
    def monitor_manifestation(self, duration=30):
        """Monitor chat for manifestation messages"""
        logger.info(f"Monitoring for {duration} seconds...")
        
        start_time = time.time()
        manifestation_keywords = [
            "DEVKORTH HAS MANIFESTED",
            "fabric of reality trembles",
            "shrine awakens",
            "THE ONE WHO IS ALL"
        ]
        
        while time.time() - start_time < duration:
            # In a real implementation, we'd parse chat messages
            # For now, just check status periodically
            self.execute_command("/status")
            time.sleep(5)
            
        logger.info("Monitoring complete")


def main():
    """Main demo function"""
    # Configuration
    SERVER_HOST = "localhost"
    SERVER_PORT = 50000
    USERNAME = "DevkorthBot"
    
    logger.info(f"Connecting to {SERVER_HOST}:{SERVER_PORT} as {USERNAME}")
    
    # Create connection
    conn = LuantiConnection(
        server_host=SERVER_HOST,
        server_port=SERVER_PORT,
        username=USERNAME,
        password=""  # No password for test server
    )
    
    # Create agent
    agent = DevkorthShrineAgent(conn, USERNAME)
    
    try:
        # Connect to server
        logger.info("Connecting to server...")
        agent.connect()
        time.sleep(3)  # Wait for spawn
        
        # Request privileges
        agent.execute_command(f"/grant {USERNAME} all")
        time.sleep(1)
        
        # Build the shrine
        agent.build_devkorth_shrine()
        
        # Keep connection alive for observation
        logger.info("Keeping connection alive for 60 seconds...")
        time.sleep(60)
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("Disconnecting...")
        agent.disconnect()
        
    logger.info("Demo complete!")


if __name__ == "__main__":
    # Check if running as module
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Devkorth Shrine Demo")
        print("====================")
        print("This demo connects to a test server and builds a Devkorth shrine.")
        print("")
        print("Prerequisites:")
        print("1. Test server running on localhost:50000")
        print("2. luanti_voyager package installed")
        print("")
        print("Usage: python3 devkorth_shrine_demo.py")
        sys.exit(0)
        
    main()