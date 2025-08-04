"""
UDP-based connection for Minetest/Luanti protocol.

This implements the actual Minetest network protocol which uses UDP,
replacing the broken TCP implementation.
"""

import asyncio
import struct
import time
import logging
from typing import Optional, Dict, Any, Callable, Tuple, Set, List
from dataclasses import dataclass
from enum import IntEnum

logger = logging.getLogger(__name__)


class PacketType(IntEnum):
    """Minetest packet types we need"""
    # Control types
    CONTROLTYPE_ACK = 0x00
    CONTROLTYPE_SET_PEER_ID = 0x01
    CONTROLTYPE_PING = 0x02
    CONTROLTYPE_DISCO = 0x03
    
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
        
        # Reliability tracking
        self.received_reliable: Set[int] = set()  # Track received reliable packets
        self.ack_queue: List[Tuple[int, int]] = []  # (seqnum, channel) to acknowledge
        
        # Player state
        self.player_state = PlayerState(
            pos={"x": 0.0, "y": 0.0, "z": 0.0}
        )
        
        # Packet handlers
        self.handlers: Dict[int, Callable] = {
            0x01: self._handle_set_peer_id,  # TOCLIENT_SET_PEER_ID
            PacketType.TOCLIENT_HELLO: self._handle_hello,
            PacketType.TOCLIENT_AUTH_ACCEPT: self._handle_auth_accept,
            0x04: self._handle_auth_mechanism,  # TOCLIENT_AUTH_MECHANISM
            0x0a: self._handle_access_denied,  # TOCLIENT_ACCESS_DENIED  
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
            
            # Send initial packet to establish connection
            # This is a control PING packet with peer_id 0
            ping_packet = bytearray()
            ping_packet.extend(struct.pack("!I", 0x4f457403))  # Protocol ID
            ping_packet.extend(struct.pack("!H", 0))  # Peer ID 0
            ping_packet.append(0)  # Channel 0
            ping_packet.append(0x00)  # TYPE_CONTROL
            ping_packet.append(PacketType.CONTROLTYPE_PING)  # PING
            
            self.transport.sendto(ping_packet)
            logger.debug("Sent initial PING to establish connection")
            
            # Wait for connection and authentication
            for _ in range(50):  # 5 seconds timeout
                if self.auth_complete:
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
        
    async def _send_packet(self, packet_type: int, data: bytes, reliable: bool = True, channel: int = 0):
        """Send a packet to the server"""
        if not self.transport:
            raise RuntimeError("Not connected")
            
        # Build packet with Minetest protocol format
        packet = bytearray()
        
        # Protocol ID (4 bytes)
        packet.extend(struct.pack("!I", 0x4f457403))  # PROTOCOL_ID
        
        # Peer ID (2 bytes) 
        packet.extend(struct.pack("!H", self.peer_id))
        
        # Channel (1 byte)
        packet.append(channel)
        
        if reliable:
            # Reliable packet type indicator
            packet.append(0x03)  # TYPE_RELIABLE
            
            # Sequence number (2 bytes)
            packet.extend(struct.pack("!H", self.seqnum))
            self.seqnum = (self.seqnum + 1) % 65536
            
            # Actual packet type (2 bytes)
            packet.extend(struct.pack("!H", packet_type))
        else:
            # Unreliable (TYPE_ORIGINAL)
            packet.append(0x01)
            
            # Packet type (2 bytes)
            packet.extend(struct.pack("!H", packet_type))
        
        # Add data
        packet.extend(data)
        
        # Send
        self.transport.sendto(packet)
        logger.debug(f"Sent packet type {packet_type:#x}, reliable={reliable}, size {len(packet)}")
        
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
        
        # Packet type indicator (1 byte)
        type_indicator = data[pos]
        pos += 1
        
        is_reliable = False
        seqnum = 0
        packet_type = 0
        
        if type_indicator == 0x00:  # TYPE_CONTROL
            # Control packet - packet type is 1 byte
            control_type = data[pos]
            pos += 1
            packet_data = data[pos:]
            # Handle control packets specially
            self._handle_control_packet(control_type, packet_data, channel)
            return
        elif type_indicator == 0x01:  # TYPE_ORIGINAL (unreliable)
            # Packet type is 2 bytes
            packet_type = struct.unpack("!H", data[pos:pos+2])[0]
            pos += 2
            packet_data = data[pos:]
        elif type_indicator == 0x02:  # TYPE_SPLIT
            # Split packet - not implemented yet
            logger.warning("Split packets not implemented")
            return
        elif type_indicator == 0x03:  # TYPE_RELIABLE
            is_reliable = True
            # Sequence number (2 bytes)
            seqnum = struct.unpack("!H", data[pos:pos+2])[0]
            pos += 2
            # Packet type (2 bytes)
            packet_type = struct.unpack("!H", data[pos:pos+2])[0]
            pos += 2
            packet_data = data[pos:]
        else:
            logger.warning(f"Unknown packet type indicator: {type_indicator:#x}")
            return
        
        logger.debug(f"Received packet type {packet_type:#x}, reliable={is_reliable}, seq={seqnum}")
        
        # If reliable packet, queue acknowledgment
        if is_reliable:
            # Check if we've already seen this packet
            if seqnum not in self.received_reliable:
                self.received_reliable.add(seqnum)
                # Send acknowledgment immediately
                asyncio.create_task(self._send_ack(seqnum, channel))
            else:
                logger.debug(f"Duplicate reliable packet {seqnum}, ignoring")
                return
        
        # Handle packet
        handler = self.handlers.get(packet_type)
        if handler:
            handler(packet_data)
        else:
            logger.debug(f"Unhandled packet type: {packet_type:#x}")
            
    def _handle_control_packet(self, control_type: int, data: bytes, channel: int):
        """Handle control packets"""
        logger.debug(f"Received control packet type {control_type:#x}")
        
        if control_type == PacketType.CONTROLTYPE_ACK:
            # Server acknowledging our packet
            if len(data) >= 2:
                acked_seqnum = struct.unpack("!H", data[:2])[0]
                logger.debug(f"Server acknowledged seqnum {acked_seqnum}")
        elif control_type == PacketType.CONTROLTYPE_PING:
            # Server ping - we should pong back
            logger.debug("Received PING from server")
            # TODO: Send PONG response
            
    def _handle_set_peer_id(self, data: bytes):
        """Handle TOCLIENT_SET_PEER_ID packet"""
        if len(data) >= 2:
            self.peer_id = struct.unpack("!H", data[:2])[0]
            logger.info(f"Assigned peer_id: {self.peer_id}")
            # After getting peer ID, send INIT packet
            asyncio.create_task(self._send_init())
            
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
        
    def _handle_auth_mechanism(self, data: bytes):
        """Handle auth mechanism packet"""
        logger.info("Received AUTH_MECHANISM from server")
        # For now, we'll just respond with legacy password auth
        # In the future, we could implement SRP
        asyncio.create_task(self._send_legacy_auth())
        
    def _handle_access_denied(self, data: bytes):
        """Handle access denied packet"""
        logger.error("Access denied by server!")
        # Try to parse reason
        try:
            if len(data) >= 1:
                reason_code = data[0]
                logger.error(f"Reason code: {reason_code}")
        except:
            pass
            
    async def _send_legacy_auth(self):
        """Send legacy password authentication"""
        # For servers that don't require auth, sending empty response
        packet_data = bytearray()
        
        # Legacy password (empty)
        packet_data.extend(struct.pack("!H", 0))  # Empty password
        
        await self._send_packet(0x54, packet_data)  # TOSERVER_LEGACY_PASSWORD
        logger.debug("Sent legacy auth response")
        
    async def _send_init2(self):
        """Send TOSERVER_INIT2 packet"""
        # Empty packet for now
        await self._send_packet(PacketType.TOSERVER_INIT2, b'')
        
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
            
    async def _send_ack(self, seqnum: int, channel: int):
        """Send acknowledgment for reliable packet"""
        logger.debug(f"Sending ACK for seqnum {seqnum} on channel {channel}")
        
        # Build control packet for ACK
        packet = bytearray()
        
        # Protocol ID (4 bytes)
        packet.extend(struct.pack("!I", 0x4f457403))
        
        # Peer ID (2 bytes) 
        packet.extend(struct.pack("!H", self.peer_id))
        
        # Channel (1 byte)
        packet.append(channel)
        
        # Control packet type indicator
        packet.append(0x00)  # TYPE_CONTROL
        
        # Control type (1 byte)
        packet.append(PacketType.CONTROLTYPE_ACK)
        
        # Sequence number being acknowledged (2 bytes)
        packet.extend(struct.pack("!H", seqnum))
        
        # Send
        if self.transport:
            self.transport.sendto(packet)
            
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
                await asyncio.sleep(10)
            else:
                logger.error("Failed to establish connection")
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await conn.disconnect()
            
    asyncio.run(test())