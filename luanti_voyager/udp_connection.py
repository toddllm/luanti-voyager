"""
UDP-based connection for Minetest/Luanti protocol.

This implements the actual Minetest network protocol which uses UDP,
replacing the broken TCP implementation.
"""

import asyncio
import struct
import time
import logging
from typing import Optional, Dict, Any, Callable, Tuple
from dataclasses import dataclass
from enum import IntEnum

logger = logging.getLogger(__name__)


class PacketType(IntEnum):
    """Minetest packet types we need"""
    # Client to server
    TOSERVER_INIT = 0x02
    TOSERVER_INIT2 = 0x11
    TOSERVER_PLAYERPOS = 0x23
    TOSERVER_GOTBLOCKS = 0x24
    TOSERVER_DELETEDBLOCKS = 0x25
    TOSERVER_CHAT_MESSAGE = 0x32
    TOSERVER_INTERACT = 0x39
    
    # Server to client
    TOCLIENT_HELLO = 0x02
    TOCLIENT_AUTH_ACCEPT = 0x03
    TOCLIENT_INIT_LEGACY = 0x10
    TOCLIENT_BLOCKDATA = 0x20
    TOCLIENT_TIME_OF_DAY = 0x29
    TOCLIENT_CHAT_MESSAGE = 0x2f
    TOCLIENT_MOVEMENT = 0x45


@dataclass
class PlayerState:
    """Current player state"""
    pos: Dict[str, float]
    yaw: float = 0.0
    pitch: float = 0.0
    keys: int = 0
    fov: float = 72.0


class MineTestUDPProtocol(asyncio.DatagramProtocol):
    """UDP protocol handler for Minetest"""
    
    def __init__(self, connection: 'UDPLuantiConnection'):
        self.connection = connection
        self.transport = None
        
    def connection_made(self, transport):
        self.transport = transport
        self.connection._on_transport_ready(transport)
        
    def datagram_received(self, data, addr):
        self.connection._handle_packet(data)
        
    def error_received(self, exc):
        logger.error(f"UDP error: {exc}")
        
    def connection_lost(self, exc):
        logger.info(f"UDP connection lost: {exc}")
        self.connection._on_connection_lost()


class UDPLuantiConnection:
    """UDP-based connection to Minetest/Luanti server"""
    
    # Protocol constants
    PROTOCOL_VERSION = 42  # Latest Minetest protocol
    MIN_PROTOCOL_VERSION = 37
    MAX_PROTOCOL_VERSION = 42
    
    # Packet structure
    PACKET_HEADER_SIZE = 4
    SEQNUM_INITIAL = 65500
    
    def __init__(self, host: str = "localhost", port: int = 30000,
                 username: str = "VoyagerBot", password: str = ""):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        
        # Connection state
        self.transport: Optional[asyncio.DatagramTransport] = None
        self.protocol: Optional[MineTestUDPProtocol] = None
        self.connected = False
        self.peer_id = 0
        self.auth_complete = False
        
        # Sequence numbers
        self.seqnum = self.SEQNUM_INITIAL
        
        # Player state
        self.player_state = PlayerState(
            pos={"x": 0.0, "y": 0.0, "z": 0.0}
        )
        
        # Packet handlers
        self.handlers: Dict[int, Callable] = {
            PacketType.TOCLIENT_HELLO: self._handle_hello,
            PacketType.TOCLIENT_AUTH_ACCEPT: self._handle_auth_accept,
            PacketType.TOCLIENT_INIT_LEGACY: self._handle_init_legacy,
            PacketType.TOCLIENT_CHAT_MESSAGE: self._handle_chat_message,
        }
        
    async def connect(self):
        """Connect to the server using UDP"""
        try:
            # Create UDP endpoint
            loop = asyncio.get_event_loop()
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: MineTestUDPProtocol(self),
                remote_addr=(self.host, self.port)
            )
            
            self.protocol = protocol
            logger.info(f"UDP endpoint created for {self.host}:{self.port}")
            
            # Send initial handshake
            await self._send_init()
            
            # Wait for connection
            for _ in range(50):  # 5 seconds timeout
                if self.connected:
                    break
                await asyncio.sleep(0.1)
            else:
                raise TimeoutError("Connection timeout")
                
            logger.info("Connected successfully!")
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise
            
    def _on_transport_ready(self, transport):
        """Called when transport is ready"""
        self.transport = transport
        logger.debug("Transport ready")
        
    def _on_connection_lost(self):
        """Called when connection is lost"""
        self.connected = False
        self.transport = None
        
    async def _send_init(self):
        """Send initial connection packet"""
        # Build TOSERVER_INIT packet
        packet_data = bytearray()
        
        # Protocol version range
        packet_data.extend(struct.pack("!B", self.MAX_PROTOCOL_VERSION))
        
        # Player name (wide string)
        name_bytes = self.username.encode('utf-16-be')
        packet_data.extend(struct.pack("!H", len(self.username)))
        packet_data.extend(name_bytes)
        
        # Password (if any)
        pass_bytes = self.password.encode('utf-16-be')
        packet_data.extend(struct.pack("!H", len(self.password)))
        packet_data.extend(pass_bytes)
        
        # Client version info
        packet_data.extend(struct.pack("!HHH", 5, 8, 0))  # Version 5.8.0
        
        await self._send_packet(PacketType.TOSERVER_INIT, packet_data)
        
    async def _send_packet(self, packet_type: int, data: bytes, reliable: bool = True):
        """Send a packet to the server"""
        if not self.transport:
            raise RuntimeError("Not connected")
            
        # Build packet with Minetest protocol format
        packet = bytearray()
        
        # Protocol ID (4 bytes)
        packet.extend(struct.pack("!I", 0x4f457403))  # PROTOCOL_ID
        
        # Peer ID (2 bytes) 
        packet.extend(struct.pack("!H", self.peer_id))
        
        # Channel (1 byte) - 0 for main channel
        packet.append(0)
        
        # Packet type (1 byte) and reliable flag
        if reliable:
            packet.append(packet_type | 0x80)  # Set reliable bit
        else:
            packet.append(packet_type)
            
        # Sequence number (2 bytes) for reliable packets
        if reliable:
            packet.extend(struct.pack("!H", self.seqnum))
            self.seqnum = (self.seqnum + 1) % 65536
        
        # Add data
        packet.extend(data)
        
        # Send
        self.transport.sendto(packet)
        logger.debug(f"Sent packet type {packet_type:#x}, size {len(packet)}")
        
    def _handle_packet(self, data: bytes):
        """Handle incoming packet"""
        if len(data) < 8:  # Minimum packet size
            logger.warning(f"Packet too small: {len(data)}")
            return
            
        # Parse Minetest packet header
        pos = 0
        
        # Protocol ID (4 bytes)
        protocol_id = struct.unpack("!I", data[pos:pos+4])[0]
        pos += 4
        
        if protocol_id != 0x4f457403:
            logger.warning(f"Invalid protocol ID: {protocol_id:#x}")
            return
            
        # Peer ID (2 bytes)
        peer_id = struct.unpack("!H", data[pos:pos+2])[0]
        pos += 2
        
        # Channel (1 byte)
        channel = data[pos]
        pos += 1
        
        # Packet type (1 byte) - mask off reliable bit
        packet_type_byte = data[pos]
        is_reliable = (packet_type_byte & 0x80) != 0
        packet_type = packet_type_byte & 0x7F
        pos += 1
        
        # Sequence number for reliable packets
        if is_reliable and len(data) >= pos + 2:
            seqnum = struct.unpack("!H", data[pos:pos+2])[0]
            pos += 2
        else:
            seqnum = 0
            
        packet_data = data[pos:]
        
        logger.debug(f"Received packet type {packet_type:#x}, reliable={is_reliable}, seq={seqnum}")
        
        # Handle packet
        handler = self.handlers.get(packet_type)
        if handler:
            handler(packet_data)
        else:
            logger.debug(f"Unhandled packet type: {packet_type:#x}")
            
    def _handle_hello(self, data: bytes):
        """Handle TOCLIENT_HELLO packet"""
        logger.info("Received HELLO from server")
        
        # Parse peer_id
        if len(data) >= 2:
            self.peer_id = struct.unpack("!H", data[:2])[0]
            logger.info(f"Assigned peer_id: {self.peer_id}")
            
        self.connected = True
        
        # Send INIT2
        asyncio.create_task(self._send_init2())
        
    def _handle_auth_accept(self, data: bytes):
        """Handle authentication acceptance"""
        logger.info("Authentication accepted!")
        self.auth_complete = True
        self.connected = True  # Mark as connected when auth is accepted
        
    async def _send_init2(self):
        """Send TOSERVER_INIT2 packet"""
        # Empty packet for now
        await self._send_packet(PacketType.TOSERVER_INIT2, b'')
        
    def _handle_auth_accept(self, data: bytes):
        """Handle authentication acceptance"""
        logger.info("Authentication accepted!")
        self.auth_complete = True
        
    def _handle_init_legacy(self, data: bytes):
        """Handle init legacy packet"""
        logger.info("Received init data from server")
        # Parse player position etc
        
    def _handle_chat_message(self, data: bytes):
        """Handle chat message"""
        try:
            # Simple parsing - actual format is more complex
            message = data.decode('utf-8', errors='ignore')
            logger.info(f"Chat: {message}")
        except:
            pass
            
    async def send_chat_message(self, message: str):
        """Send a chat message"""
        if not self.connected:
            raise RuntimeError("Not connected")
            
        # Build chat packet
        msg_bytes = message.encode('utf-16-be')
        packet_data = struct.pack("!H", len(message)) + msg_bytes
        
        await self._send_packet(PacketType.TOSERVER_CHAT_MESSAGE, packet_data)
        logger.info(f"Sent chat: {message}")
        
    async def disconnect(self):
        """Disconnect from server"""
        if self.transport:
            self.transport.close()
            self.transport = None
        self.connected = False
        logger.info("Disconnected")


# Quick test
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    async def test():
        conn = UDPLuantiConnection(port=50000, username="UDPTestBot")
        
        try:
            await conn.connect()
            
            if conn.connected:
                logger.info("Successfully connected via UDP!")
                
                # Try to send a chat message
                await conn.send_chat_message("Hello from UDP bot!")
                
                # Wait a bit to see responses
                await asyncio.sleep(3)
            else:
                logger.error("Failed to establish connection")
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await conn.disconnect()
            
    asyncio.run(test())