#!/usr/bin/env python3
"""
Devkorth Shrine Testing Script
Part of the luanti-voyager project

This script connects to the test server on port 50000 and builds
a complete Devkorth shrine with all required conditions.
"""

import sys
import time
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from luanti_voyager.connection import LuantiConnection
from luanti_voyager.agent import Agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DevkorthTest')


class DevkorthShrineTester:
    """Test agent that builds and validates Devkorth shrines"""
    
    def __init__(self, host='localhost', port=50000, username='VoyagerTestBot'):
        self.host = host
        self.port = port
        self.username = username
        self.agent = None
        
    def connect(self):
        """Connect to the test server"""
        logger.info(f"Connecting to {self.host}:{self.port} as {self.username}")
        
        # Create connection
        conn = LuantiConnection(
            server_host=self.host,
            server_port=self.port,
            username=self.username,
            password=""  # No password for test server
        )
        
        # Create agent
        self.agent = Agent(conn, self.username)
        
        # Connect
        self.agent.connect()
        logger.info("Connected successfully!")
        
        # Wait for spawn
        time.sleep(3)
        
    def prepare_shrine_location(self):
        """Find a suitable location and prepare the area"""
        logger.info("Preparing shrine location...")
        
        # Get current position
        pos = self.agent.get_position()
        logger.info(f"Current position: {pos}")
        
        # Move to a clear area near spawn
        shrine_x = 10
        shrine_z = 10
        
        # Find ground level
        self.agent.send_chat_message("/teleport {} 20 {}".format(shrine_x, shrine_z))
        time.sleep(1)
        
        # Clear the area (7x7 to be safe)
        logger.info("Clearing area for shrine...")
        for x in range(-3, 4):
            for z in range(-3, 4):
                for y in range(-1, 10):
                    self.agent.dig_node(shrine_x + x, y, shrine_z + z)
                    
        return shrine_x, 0, shrine_z
        
    def build_shrine_base(self, center_x, base_y, center_z):
        """Build the 5x5 diamond block base"""
        logger.info("Building shrine base (5x5 diamond blocks)...")
        
        for x in range(-2, 3):
            for z in range(-2, 3):
                self.agent.place_node(
                    center_x + x, 
                    base_y, 
                    center_z + z,
                    "default:diamondblock"
                )
                time.sleep(0.1)  # Small delay to avoid overwhelming server
                
        logger.info("Base complete!")
        
    def build_central_mese(self, center_x, base_y, center_z):
        """Place the central mese block"""
        logger.info("Placing central mese block...")
        
        self.agent.place_node(
            center_x,
            base_y + 1,
            center_z,
            "default:mese"
        )
        
        logger.info("Central mese placed!")
        
    def build_pillars(self, center_x, base_y, center_z):
        """Build the 4 corner pillars (3 blocks high)"""
        logger.info("Building corner pillars...")
        
        corners = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        
        for corner_x, corner_z in corners:
            for height in range(1, 4):
                self.agent.place_node(
                    center_x + corner_x,
                    base_y + height,
                    center_z + corner_z,
                    "default:diamondblock"
                )
                time.sleep(0.1)
                
        logger.info("Pillars complete!")
        
    def create_water_source(self, center_x, base_y, center_z):
        """Create water source nearby"""
        logger.info("Creating water source...")
        
        # Place water 5 blocks away
        water_pos = (center_x + 5, base_y, center_z)
        
        # Dig a small pool
        for x in range(-1, 2):
            for z in range(-1, 2):
                self.agent.dig_node(
                    water_pos[0] + x,
                    water_pos[1] - 1,
                    water_pos[2] + z
                )
                
        # Place water source
        self.agent.place_node(
            water_pos[0],
            water_pos[1],
            water_pos[2],
            "default:water_source"
        )
        
        logger.info("Water source created!")
        
    def place_fossil(self, center_x, base_y, center_z):
        """Place coal block as fossil substitute"""
        logger.info("Placing fossil (coal block)...")
        
        # Place coal block 8 blocks away
        self.agent.place_node(
            center_x - 8,
            base_y,
            center_z,
            "default:coalblock"
        )
        
        logger.info("Fossil placed!")
        
    def set_night_time(self):
        """Set time to night using time crystal or command"""
        logger.info("Setting time to night...")
        
        # Try using admin command first
        self.agent.send_chat_message("/time 0:00")
        time.sleep(1)
        
        # Alternative: use time_crystal if available
        # self.agent.use_item("devkorth:time_crystal")
        
        logger.info("Time set to night!")
        
    def grant_privileges(self):
        """Grant necessary privileges to test bot"""
        logger.info("Requesting privileges...")
        
        # Request basic privileges
        self.agent.send_chat_message("/grant {} all".format(self.username))
        time.sleep(1)
        
    def build_complete_shrine(self):
        """Build a complete Devkorth shrine with all conditions"""
        logger.info("=== STARTING DEVKORTH SHRINE TEST ===")
        
        # Grant privileges
        self.grant_privileges()
        
        # Prepare location
        center_x, base_y, center_z = self.prepare_shrine_location()
        
        # Build shrine structure
        self.build_shrine_base(center_x, base_y, center_z)
        self.build_central_mese(center_x, base_y, center_z)
        self.build_pillars(center_x, base_y, center_z)
        
        # Create required conditions
        self.create_water_source(center_x, base_y, center_z)
        self.place_fossil(center_x, base_y, center_z)
        self.set_night_time()
        
        logger.info("=== SHRINE CONSTRUCTION COMPLETE ===")
        logger.info(f"Shrine location: ({center_x}, {base_y}, {center_z})")
        logger.info("Waiting for Devkorth manifestation...")
        
        # Monitor chat for manifestation messages
        self.monitor_manifestation()
        
    def monitor_manifestation(self, duration=30):
        """Monitor for Devkorth manifestation messages"""
        logger.info(f"Monitoring for {duration} seconds...")
        
        start_time = time.time()
        manifestation_detected = False
        
        while time.time() - start_time < duration:
            # Check for chat messages
            # In a real implementation, we'd parse server messages
            self.agent.send_chat_message("/status")
            
            if "DEVKORTH HAS MANIFESTED" in str(self.agent.connection.last_message):
                manifestation_detected = True
                logger.info("🎉 DEVKORTH MANIFESTATION DETECTED!")
                break
                
            time.sleep(1)
            
        if not manifestation_detected:
            logger.warning("No manifestation detected. Checking conditions...")
            self.debug_conditions()
            
    def debug_conditions(self):
        """Send debug commands to check why manifestation failed"""
        logger.info("Debugging shrine conditions...")
        
        debug_commands = [
            "/time",  # Check current time
            "/status",  # General status
            "/list",  # List entities
        ]
        
        for cmd in debug_commands:
            self.agent.send_chat_message(cmd)
            time.sleep(0.5)
            
    def run_test(self):
        """Run the complete test sequence"""
        try:
            # Connect to server
            self.connect()
            
            # Build and test shrine
            self.build_complete_shrine()
            
            # Keep connection alive for observation
            logger.info("Test complete. Keeping connection alive for 60 seconds...")
            time.sleep(60)
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            raise
        finally:
            if self.agent:
                logger.info("Disconnecting...")
                self.agent.disconnect()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Devkorth shrine manifestation')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=50000, help='Server port')
    parser.add_argument('--username', default='DevkorthTester', help='Bot username')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run tester
    tester = DevkorthShrineTester(
        host=args.host,
        port=args.port,
        username=args.username
    )
    
    logger.info("Starting Devkorth shrine test...")
    logger.info(f"Target: {args.host}:{args.port}")
    
    tester.run_test()
    

if __name__ == "__main__":
    main()