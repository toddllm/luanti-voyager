"""
Simple Luanti network protocol client for agent communication.

This is a minimal implementation to get started. We'll expand it as needed!
"""

import asyncio
import struct
import time
from typing import Optional, Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)


class LuantiConnection:
    """Basic connection to a Luanti server."""
    
    # Protocol constants (simplified for POC)
    PROTOCOL_ID = 0x4f457403
    PROTOCOL_VERSION = 42  # Update based on actual Luanti version
    
    # Packet types we care about for POC
    TOSERVER_INIT = 0x02
    TOSERVER_INIT2 = 0x11
    TOSERVER_PLAYERPOS = 0x23
    TOSERVER_INTERACT = 0x39
    
    TOCLIENT_HELLO = 0x02
    TOCLIENT_AUTH_ACCEPT = 0x03
    TOCLIENT_MOVEMENT = 0x2f
    TOCLIENT_BLOCKDATA = 0x20
    TOCLIENT_TIME_OF_DAY = 0x29
    
    def __init__(self, host: str = "localhost", port: int = 30000):
        self.host = host
        self.port = port
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.peer_id = 1  # Will be assigned by server
        self.player_name = "VoyagerBot"
        self.connected = False
        self.auth_complete = False
        
        # Callbacks for different packet types
        self.handlers: Dict[int, Callable] = {}
        
        # Game state
        self.player_pos = {"x": 0, "y": 0, "z": 0}
        self.player_pitch = 0
        self.player_yaw = 0
        self.inventory = {}
        self.world_blocks = {}  # Simple block cache
        
    async def connect(self):
        """Connect to Luanti server."""
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port
            )
            self.connected = True
            logger.info(f"Connected to {self.host}:{self.port}")
            
            # Start packet handler
            asyncio.create_task(self._packet_handler())
            
            # Send initial handshake
            await self._send_init()
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise
            
    async def _packet_handler(self):
        """Handle incoming packets."""
        while self.connected:
            try:
                # Read packet header (simplified)
                header = await self.reader.read(4)
                if not header:
                    break
                    
                packet_type, size = struct.unpack(">HH", header)
                
                # Read packet data
                data = await self.reader.read(size) if size > 0 else b""
                
                # Handle packet
                if packet_type in self.handlers:
                    await self.handlers[packet_type](data)
                else:
                    logger.debug(f"Unhandled packet type: 0x{packet_type:02x}")
                    
            except Exception as e:
                logger.error(f"Packet handler error: {e}")
                break
                
        self.connected = False
        
    async def _send_init(self):
        """Send initial connection packet."""
        # This is a simplified version - real protocol is more complex
        packet = struct.pack(
            ">HH20s",
            self.TOSERVER_INIT,
            24,  # packet size
            self.player_name.encode("utf-8").ljust(20, b'\x00')
        )
        self.writer.write(packet)
        await self.writer.drain()
        
    async def send_player_pos(self, x: float, y: float, z: float, 
                            pitch: float = 0, yaw: float = 0):
        """Send player position update."""
        if not self.auth_complete:
            return
            
        # Update local state
        self.player_pos = {"x": x, "y": y, "z": z}
        self.player_pitch = pitch
        self.player_yaw = yaw
        
        # Pack position data (simplified)
        packet = struct.pack(
            ">HHfffff",
            self.TOSERVER_PLAYERPOS,
            20,  # packet size
            x, y, z, pitch, yaw
        )
        self.writer.write(packet)
        await self.writer.drain()
        
    async def dig_block(self, x: int, y: int, z: int):
        """Attempt to dig a block at position."""
        if not self.auth_complete:
            return
            
        # Send interact packet (simplified)
        packet = struct.pack(
            ">HHBiii",
            self.TOSERVER_INTERACT,
            13,  # packet size
            0,  # action: dig
            x, y, z
        )
        self.writer.write(packet)
        await self.writer.drain()
        
    async def place_block(self, x: int, y: int, z: int, block_type: int = 1):
        """Attempt to place a block at position."""
        if not self.auth_complete:
            return
            
        # Send interact packet (simplified)
        packet = struct.pack(
            ">HHBiiiH",
            self.TOSERVER_INTERACT,
            15,  # packet size
            3,  # action: place
            x, y, z,
            block_type
        )
        self.writer.write(packet)
        await self.writer.drain()
        
    def get_nearby_blocks(self, radius: int = 5) -> Dict[tuple, int]:
        """Get blocks near the player."""
        nearby = {}
        px, py, pz = int(self.player_pos["x"]), int(self.player_pos["y"]), int(self.player_pos["z"])
        
        for x in range(px - radius, px + radius + 1):
            for y in range(py - radius, py + radius + 1):
                for z in range(pz - radius, pz + radius + 1):
                    if (x, y, z) in self.world_blocks:
                        nearby[(x, y, z)] = self.world_blocks[(x, y, z)]
                        
        return nearby
        
    async def disconnect(self):
        """Disconnect from server."""
        self.connected = False
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            
    def register_handler(self, packet_type: int, handler: Callable):
        """Register a packet handler."""
        self.handlers[packet_type] = handler


class SimpleBot:
    """A very simple bot using the connection."""
    
    def __init__(self, connection: LuantiConnection):
        self.conn = connection
        self.running = False
        
    async def start(self):
        """Start the bot."""
        await self.conn.connect()
        self.running = True
        
        # Simple behavior loop
        while self.running:
            # Move forward a bit
            pos = self.conn.player_pos
            await self.conn.send_player_pos(
                pos["x"] + 0.1,
                pos["y"],
                pos["z"]
            )
            
            # Check for nearby blocks
            nearby = self.conn.get_nearby_blocks(radius=3)
            logger.info(f"Nearby blocks: {len(nearby)}")
            
            await asyncio.sleep(1)
            
    async def stop(self):
        """Stop the bot."""
        self.running = False
        await self.conn.disconnect()


# Quick test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        conn = LuantiConnection()
        bot = SimpleBot(conn)
        
        try:
            await bot.start()
        except KeyboardInterrupt:
            await bot.stop()
            
    asyncio.run(main())