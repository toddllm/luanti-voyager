#!/usr/bin/env python3
"""
Voyager Shrine Builder for Devkorth
Automated shrine construction using the luanti-voyager framework

This script connects a bot to the server and builds a complete
Devkorth shrine with all required conditions.
"""

import asyncio
import time
import logging
from typing import Tuple, List, Dict, Any
import math

# Configuration
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 50000
DEFAULT_USERNAME = "VoyagerTestBot"
SHRINE_CENTER = (10, 10, 10)  # Default shrine location

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ShrineBuilder')


class MockConnection:
    """Mock connection for testing without real server"""
    def __init__(self, host, port, username):
        self.host = host
        self.port = port
        self.username = username
        self.connected = False
        
    def connect(self):
        logger.info(f"Mock connecting to {self.host}:{self.port} as {self.username}")
        self.connected = True
        
    def disconnect(self):
        logger.info("Mock disconnecting")
        self.connected = False
        
    def send_command(self, cmd):
        logger.debug(f"Mock sending: {cmd}")
        
    def place_node(self, x, y, z, node_type):
        logger.debug(f"Mock placing {node_type} at ({x}, {y}, {z})")
        
    def dig_node(self, x, y, z):
        logger.debug(f"Mock digging at ({x}, {y}, {z})")


class DevkorthShrineBuilder:
    """Automated shrine builder for Devkorth testing"""
    
    def __init__(self, connection=None):
        self.connection = connection
        self.shrine_center = SHRINE_CENTER
        self.commands_log = []  # Log all commands for debugging
        
    def log_command(self, cmd: str):
        """Log command for debugging"""
        self.commands_log.append(cmd)
        logger.debug(f"Command: {cmd}")
        
    def send_chat(self, message: str):
        """Send chat message/command"""
        self.log_command(f"chat: {message}")
        if self.connection:
            self.connection.send_command(message)
            
    def place_block(self, pos: Tuple[int, int, int], block_type: str):
        """Place a block at position"""
        x, y, z = pos
        self.log_command(f"place: {block_type} at {pos}")
        if self.connection:
            self.connection.place_node(x, y, z, block_type)
            
    def dig_block(self, pos: Tuple[int, int, int]):
        """Dig/remove block at position"""
        x, y, z = pos
        self.log_command(f"dig: at {pos}")
        if self.connection:
            self.connection.dig_node(x, y, z)
            
    def clear_area(self, center: Tuple[int, int, int], radius: int = 10, height: int = 20):
        """Clear area for shrine construction"""
        logger.info(f"Clearing area around {center} (radius={radius}, height={height})")
        cx, cy, cz = center
        
        positions = []
        for y in range(cy - 2, cy + height):
            for x in range(cx - radius, cx + radius + 1):
                for z in range(cz - radius, cz + radius + 1):
                    positions.append((x, y, z))
                    
        # Clear in batches to avoid overwhelming
        for i in range(0, len(positions), 50):
            batch = positions[i:i+50]
            for pos in batch:
                self.dig_block(pos)
            time.sleep(0.1)  # Small delay between batches
            
        logger.info(f"Cleared {len(positions)} blocks")
        
    def build_shrine_base(self, center: Tuple[int, int, int]):
        """Build 5x5 diamond block base"""
        logger.info("Building shrine base (5x5 diamond blocks)")
        cx, cy, cz = center
        
        base_positions = []
        for x in range(cx - 2, cx + 3):
            for z in range(cz - 2, cz + 3):
                base_positions.append((x, cy, z))
                
        for pos in base_positions:
            self.place_block(pos, "default:diamondblock")
            time.sleep(0.05)  # Small delay to avoid overwhelming
            
        logger.info(f"Placed {len(base_positions)} diamond blocks for base")
        
    def build_central_mese(self, center: Tuple[int, int, int]):
        """Place central mese block"""
        logger.info("Placing central mese block")
        cx, cy, cz = center
        self.place_block((cx, cy + 1, cz), "default:mese")
        
    def build_pillars(self, center: Tuple[int, int, int]):
        """Build 4 corner pillars (3 blocks high each)"""
        logger.info("Building corner pillars")
        cx, cy, cz = center
        
        # Corner positions
        corners = [
            (cx - 2, cz - 2),  # NW
            (cx - 2, cz + 2),  # NE
            (cx + 2, cz - 2),  # SW
            (cx + 2, cz + 2),  # SE
        ]
        
        pillar_count = 0
        for corner_x, corner_z in corners:
            for height in range(1, 4):
                self.place_block((corner_x, cy + height, corner_z), "default:diamondblock")
                pillar_count += 1
                time.sleep(0.05)
                
        logger.info(f"Placed {pillar_count} blocks for pillars")
        
    def create_water_source(self, center: Tuple[int, int, int]):
        """Create water source near shrine"""
        logger.info("Creating water source")
        cx, cy, cz = center
        
        # Place water 5 blocks east of center
        water_pos = (cx + 5, cy, cz)
        
        # Dig a small pool
        pool_positions = [
            (cx + 5, cy - 1, cz),
            (cx + 4, cy - 1, cz),
            (cx + 6, cy - 1, cz),
            (cx + 5, cy - 1, cz - 1),
            (cx + 5, cy - 1, cz + 1),
        ]
        
        for pos in pool_positions:
            self.dig_block(pos)
            
        # Place water source
        self.place_block(water_pos, "default:water_source")
        logger.info(f"Placed water source at {water_pos}")
        
    def place_fossil(self, center: Tuple[int, int, int]):
        """Place coal block as fossil"""
        logger.info("Placing fossil (coal block)")
        cx, cy, cz = center
        
        # Place coal block 8 blocks west
        fossil_pos = (cx - 8, cy, cz)
        self.place_block(fossil_pos, "default:coalblock")
        logger.info(f"Placed coal block at {fossil_pos}")
        
    def set_night_time(self):
        """Set time to night"""
        logger.info("Setting time to night")
        self.send_chat("/time 0:00")
        
    def grant_privileges(self):
        """Grant necessary privileges to bot"""
        logger.info("Requesting privileges")
        self.send_chat(f"/grant {self.connection.username if self.connection else 'VoyagerTestBot'} all")
        
    def build_complete_shrine(self, center: Tuple[int, int, int] = None):
        """Build complete Devkorth shrine with all conditions"""
        if center is None:
            center = self.shrine_center
            
        logger.info(f"=== BUILDING DEVKORTH SHRINE AT {center} ===")
        
        # Phase 1: Preparation
        logger.info("Phase 1: Preparation")
        self.grant_privileges()
        time.sleep(1)
        
        # Teleport to location
        cx, cy, cz = center
        self.send_chat(f"/teleport {cx} {cy + 5} {cz}")
        time.sleep(1)
        
        # Phase 2: Clear area
        logger.info("Phase 2: Clearing area")
        self.clear_area(center, radius=10, height=15)
        time.sleep(2)
        
        # Phase 3: Build structure
        logger.info("Phase 3: Building structure")
        self.build_shrine_base(center)
        self.build_central_mese(center)
        self.build_pillars(center)
        time.sleep(1)
        
        # Phase 4: Create conditions
        logger.info("Phase 4: Creating manifestation conditions")
        self.create_water_source(center)
        self.place_fossil(center)
        self.set_night_time()
        
        logger.info("=== SHRINE CONSTRUCTION COMPLETE ===")
        logger.info(f"Shrine built at: {center}")
        logger.info("Conditions:")
        logger.info("  ✓ 5x5 diamond base")
        logger.info("  ✓ Central mese block")
        logger.info("  ✓ 4 corner pillars")
        logger.info("  ✓ Water source nearby")
        logger.info("  ✓ Coal block (fossil)")
        logger.info("  ✓ Night time set")
        logger.info("")
        logger.info("Waiting for Devkorth manifestation...")
        
    def monitor_manifestation(self, duration: int = 30):
        """Monitor for Devkorth manifestation"""
        logger.info(f"Monitoring for {duration} seconds...")
        
        start_time = time.time()
        check_interval = 5
        
        while time.time() - start_time < duration:
            elapsed = int(time.time() - start_time)
            logger.info(f"Monitoring... ({elapsed}/{duration}s)")
            
            # In real implementation, check for manifestation messages
            self.send_chat("/status")
            
            time.sleep(check_interval)
            
        logger.info("Monitoring complete")
        
    def generate_command_list(self) -> List[str]:
        """Generate list of commands for manual execution"""
        commands = [
            "# Devkorth Shrine Building Commands",
            "# Generated by voyager_shrine_builder.py",
            "#" + "=" * 50,
            "",
            "# 1. Grant privileges",
            "/grant VoyagerTestBot all",
            "",
            "# 2. Teleport to build location",
            f"/teleport {self.shrine_center[0]} {self.shrine_center[1] + 5} {self.shrine_center[2]}",
            "",
            "# 3. Give materials",
            "/giveme default:diamondblock 99",
            "/giveme default:mese 10",
            "/giveme default:water_source 10",
            "/giveme default:coalblock 10",
            "",
            "# 4. Set night time",
            "/time 0:00",
            "",
            "# 5. Build shrine manually at coordinates:",
            f"#    Center: {self.shrine_center}",
            "#    - Base: 5x5 diamond blocks",
            "#    - Center mese: 1 block above center",
            "#    - Pillars: 3-high at corners",
            "#    - Water: 5 blocks east",
            "#    - Coal: 8 blocks west",
        ]
        
        return commands


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Automated Devkorth shrine builder using Voyager framework'
    )
    parser.add_argument('--host', default=DEFAULT_HOST, help='Server host')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='Server port')
    parser.add_argument('--username', default=DEFAULT_USERNAME, help='Bot username')
    parser.add_argument('--mock', action='store_true', help='Use mock connection for testing')
    parser.add_argument('--center', nargs=3, type=int, metavar=('X', 'Y', 'Z'),
                        help='Shrine center coordinates (default: 10 10 10)')
    parser.add_argument('--commands-only', action='store_true', 
                        help='Only print commands without connecting')
    
    args = parser.parse_args()
    
    # Set shrine center
    shrine_center = tuple(args.center) if args.center else SHRINE_CENTER
    
    # Commands only mode
    if args.commands_only:
        builder = DevkorthShrineBuilder(None)
        builder.shrine_center = shrine_center
        commands = builder.generate_command_list()
        print("\n".join(commands))
        return
    
    # Create connection (mock or real)
    if args.mock:
        logger.info("Using mock connection for testing")
        connection = MockConnection(args.host, args.port, args.username)
    else:
        logger.warning("Real voyager connection not implemented in this example")
        logger.info("Using mock connection instead")
        connection = MockConnection(args.host, args.port, args.username)
    
    # Connect
    connection.connect()
    
    try:
        # Create builder and build shrine
        builder = DevkorthShrineBuilder(connection)
        builder.shrine_center = shrine_center
        
        # Build the shrine
        builder.build_complete_shrine()
        
        # Monitor for manifestation
        builder.monitor_manifestation(duration=60)
        
        # Save command log
        log_file = "shrine_builder_commands.log"
        with open(log_file, 'w') as f:
            f.write("\n".join(builder.commands_log))
        logger.info(f"Command log saved to {log_file}")
        
    except Exception as e:
        logger.error(f"Error during shrine building: {e}")
        raise
    finally:
        connection.disconnect()
        
    logger.info("Shrine builder complete!")


if __name__ == "__main__":
    main()