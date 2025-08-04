#!/usr/bin/env python3
"""
Voyager Shrine Builder for Devkorth - UDP Version
Automated shrine construction using the luanti-voyager UDP connection

This script connects a bot to the server and builds a complete
Devkorth shrine with all required conditions.
"""

import asyncio
import time
import logging
from typing import Tuple, List, Dict, Any
import math
import sys
import os

# Add parent directory to path to import luanti_voyager
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from luanti_voyager import UDPLuantiConnection

# Configuration
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 50000
DEFAULT_USERNAME = "VoyagerBuilder"
SHRINE_CENTER = (10, 10, 10)  # Default shrine location

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ShrineBuilder')


class DevkorthShrineBuilder:
    """Automated shrine builder for Devkorth testing using UDP connection"""
    
    def __init__(self, connection: UDPLuantiConnection):
        self.connection = connection
        self.shrine_center = SHRINE_CENTER
        self.commands_log = []  # Log all commands for debugging
        
    async def send_chat(self, message: str):
        """Send chat message/command"""
        self.commands_log.append(message)
        logger.debug(f"Chat: {message}")
        await self.connection.send_chat_message(message)
        await asyncio.sleep(0.5)  # Small delay between commands
            
    async def place_block(self, pos: Tuple[int, int, int], item_index: int = 0):
        """Place a block at position"""
        x, y, z = pos
        logger.debug(f"Placing block at {pos}")
        await self.connection.place_block(x, y, z, item_index)
        await asyncio.sleep(0.1)  # Small delay to avoid overwhelming
            
    async def dig_block(self, pos: Tuple[int, int, int]):
        """Dig/remove block at position"""
        x, y, z = pos
        logger.debug(f"Digging at {pos}")
        await self.connection.dig_block(x, y, z)
        await asyncio.sleep(0.1)
            
    async def clear_area(self, center: Tuple[int, int, int], radius: int = 10, height: int = 20):
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
                await self.dig_block(pos)
            await asyncio.sleep(1)  # Delay between batches
            
        logger.info(f"Cleared {len(positions)} blocks")
        
    async def teleport_to_shrine(self, center: Tuple[int, int, int]):
        """Teleport bot to shrine location"""
        cx, cy, cz = center
        await self.send_chat(f"/teleport {cx} {cy + 5} {cz}")
        # Also update bot's internal position
        await self.connection.move_to(float(cx), float(cy + 5), float(cz))
        
    async def get_materials(self):
        """Give bot necessary materials"""
        logger.info("Getting materials")
        materials = [
            "/giveme default:diamondblock 99",
            "/giveme default:mese 10",
            "/giveme default:water_source 10",
            "/giveme default:coalblock 10"
        ]
        for cmd in materials:
            await self.send_chat(cmd)
            
    async def build_shrine_base(self, center: Tuple[int, int, int]):
        """Build 5x5 diamond block base"""
        logger.info("Building shrine base (5x5 diamond blocks)")
        cx, cy, cz = center
        
        # First, select diamond blocks in inventory (slot 0)
        await self.send_chat("/giveme default:diamondblock 30")
        
        base_positions = []
        for x in range(cx - 2, cx + 3):
            for z in range(cz - 2, cz + 3):
                base_positions.append((x, cy, z))
                
        for pos in base_positions:
            await self.place_block(pos, 0)  # Assuming diamond blocks in slot 0
            
        logger.info(f"Placed {len(base_positions)} diamond blocks for base")
        
    async def build_central_mese(self, center: Tuple[int, int, int]):
        """Place central mese block"""
        logger.info("Placing central mese block")
        cx, cy, cz = center
        
        # Give mese block
        await self.send_chat("/giveme default:mese 1")
        await self.place_block((cx, cy + 1, cz), 1)  # Assuming mese in slot 1
        
    async def build_pillars(self, center: Tuple[int, int, int]):
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
                await self.place_block((corner_x, cy + height, corner_z), 0)  # Diamond blocks
                pillar_count += 1
                
        logger.info(f"Placed {pillar_count} blocks for pillars")
        
    async def create_water_source(self, center: Tuple[int, int, int]):
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
            await self.dig_block(pos)
            
        # Give water and place it
        await self.send_chat("/giveme default:water_source 1")
        await self.place_block(water_pos, 2)  # Assuming water in slot 2
        logger.info(f"Placed water source at {water_pos}")
        
    async def place_fossil(self, center: Tuple[int, int, int]):
        """Place coal block as fossil"""
        logger.info("Placing fossil (coal block)")
        cx, cy, cz = center
        
        # Give coal block
        await self.send_chat("/giveme default:coalblock 1")
        
        # Place coal block 8 blocks west
        fossil_pos = (cx - 8, cy, cz)
        await self.place_block(fossil_pos, 3)  # Assuming coal in slot 3
        logger.info(f"Placed coal block at {fossil_pos}")
        
    async def set_night_time(self):
        """Set time to night"""
        logger.info("Setting time to night")
        await self.send_chat("/time 0:00")
        
    async def grant_privileges(self):
        """Grant necessary privileges to bot"""
        logger.info("Requesting privileges")
        await self.send_chat(f"/grant {self.connection.username} all")
        
    async def build_complete_shrine(self, center: Tuple[int, int, int] = None):
        """Build complete Devkorth shrine with all conditions"""
        if center is None:
            center = self.shrine_center
            
        logger.info(f"=== BUILDING DEVKORTH SHRINE AT {center} ===")
        
        # Phase 1: Preparation
        logger.info("Phase 1: Preparation")
        await self.grant_privileges()
        await asyncio.sleep(2)
        
        await self.teleport_to_shrine(center)
        await asyncio.sleep(2)
        
        # Get all materials first
        await self.get_materials()
        await asyncio.sleep(2)
        
        # Phase 2: Clear area
        logger.info("Phase 2: Clearing area")
        await self.clear_area(center, radius=10, height=15)
        await asyncio.sleep(2)
        
        # Phase 3: Build structure
        logger.info("Phase 3: Building structure")
        await self.build_shrine_base(center)
        await self.build_central_mese(center)
        await self.build_pillars(center)
        await asyncio.sleep(1)
        
        # Phase 4: Create conditions
        logger.info("Phase 4: Creating manifestation conditions")
        await self.create_water_source(center)
        await self.place_fossil(center)
        await self.set_night_time()
        
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
        
        # Announce completion
        await self.send_chat("Shrine complete! Devkorth should manifest soon...")
        
    async def monitor_manifestation(self, duration: int = 30):
        """Monitor for Devkorth manifestation"""
        logger.info(f"Monitoring for {duration} seconds...")
        
        start_time = time.time()
        check_interval = 5
        
        while time.time() - start_time < duration:
            elapsed = int(time.time() - start_time)
            logger.info(f"Monitoring... ({elapsed}/{duration}s)")
            
            # Check for manifestation messages
            await self.send_chat("/status")
            
            await asyncio.sleep(check_interval)
            
        logger.info("Monitoring complete")


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Automated Devkorth shrine builder using UDP connection'
    )
    parser.add_argument('--host', default=DEFAULT_HOST, help='Server host')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='Server port')
    parser.add_argument('--username', default=DEFAULT_USERNAME, help='Bot username')
    parser.add_argument('--password', help='Bot password (or use MINETEST_PASSWORD env var)')
    parser.add_argument('--center', nargs=3, type=int, metavar=('X', 'Y', 'Z'),
                        help='Shrine center coordinates (default: 10 10 10)')
    
    args = parser.parse_args()
    
    # Set shrine center
    shrine_center = tuple(args.center) if args.center else SHRINE_CENTER
    
    # Create UDP connection
    logger.info(f"Connecting to {args.host}:{args.port} as {args.username}")
    # Load password from environment or args
    password = os.environ.get('MINETEST_PASSWORD', '')
    if hasattr(args, 'password') and args.password:
        password = args.password
    
    connection = UDPLuantiConnection(
        host=args.host,
        port=args.port,
        username=args.username,
        password=password
    )
    
    try:
        # Connect to server - be lenient for test servers
        try:
            await connection.connect()
        except TimeoutError:
            # Check if we at least got HELLO
            if connection.connected:
                logger.warning("Auth timeout but connected via HELLO - continuing anyway")
                connection.auth_complete = True  # Force it for test server
            else:
                logger.error("Failed to connect to server!")
                return
            
        logger.info(f"Connected! Peer ID: {connection.peer_id}")
        
        # Create builder and build shrine
        builder = DevkorthShrineBuilder(connection)
        builder.shrine_center = shrine_center
        
        # Build the shrine
        await builder.build_complete_shrine()
        
        # Monitor for manifestation
        await builder.monitor_manifestation(duration=60)
        
        # Save command log
        log_file = "shrine_builder_commands.log"
        with open(log_file, 'w') as f:
            f.write("\n".join(builder.commands_log))
        logger.info(f"Command log saved to {log_file}")
        
    except Exception as e:
        logger.error(f"Error during shrine building: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await connection.disconnect()
        
    logger.info("Shrine builder complete!")


if __name__ == "__main__":
    asyncio.run(main())