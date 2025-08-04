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
            
            # Send initial INIT packet to start handshake
            await self._send_init()
            logger.debug("Sent initial INIT packet")
            
            # Wait for connection and authentication
            for i in range(100):  # 10 seconds timeout
                if self.auth_complete:
                    break
                if i % 10 == 0:
                    logger.debug(f"Waiting for auth... connected={self.connected}, auth={self.auth_complete}, peer_id={self.peer_id}")
                await asyncio.sleep(0.1)
            else:
                logger.error(f"Timeout: connected={self.connected}, auth={self.auth_complete}, peer_id={self.peer_id}")
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
        
        # Use unreliable for initial INIT (peer_id will be 0)
        await self._send_packet(PacketType.TOSERVER_INIT, packet_data, reliable=False)
        
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
        
        logger.debug(f"Received packet type {packet_type:#x}, reliable={is_reliable}, seq={seqnum}, data_len={len(packet_data)}")
        
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
            logger.debug(f"Calling handler for packet type {packet_type:#x}")
            handler(packet_data)
        else:
            logger.warning(f"Unhandled packet type: {packet_type:#x} - this might be important!")
            
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
            # Don't send INIT here - it's already been sent
            # The server should send HELLO next
            
    def _handle_hello(self, data: bytes):
        """Handle TOCLIENT_HELLO packet"""
        logger.info("Received HELLO from server")
        
        # HELLO packet format varies by protocol version
        # For now, just mark as connected and send INIT2
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
        except (IndexError, struct.error) as e:
            logger.debug(f"Could not parse disconnect reason: {e}")
            
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
        except (UnicodeDecodeError, AttributeError) as e:
            logger.debug(f"Could not decode chat message: {e}")
            
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
        
    async def move_to(self, x: float, y: float, z: float, yaw: float = 0.0, pitch: float = 0.0):
        """Move the bot to a specific position"""
        if not self.connected:
            raise RuntimeError("Not connected")
            
        # Update internal state
        self.player_state.pos = {"x": x, "y": y, "z": z}
        self.player_state.yaw = yaw
        self.player_state.pitch = pitch
        
        # Build TOSERVER_PLAYERPOS packet
        packet_data = bytearray()
        
        # Position * 1000 (fixed point)
        packet_data.extend(struct.pack("!iii", 
            int(x * 1000), 
            int(y * 1000), 
            int(z * 1000)
        ))
        
        # Speed * 1000 (fixed point) - for now, 0
        packet_data.extend(struct.pack("!iii", 0, 0, 0))
        
        # Pitch and yaw * 1000
        packet_data.extend(struct.pack("!ii",
            int(pitch * 1000),
            int(yaw * 1000)
        ))
        
        # Key states (32 bits) - for now, 0
        packet_data.extend(struct.pack("!I", 0))
        
        # FOV (80) 
        packet_data.append(80)
        
        # Wanted range (0 = default)
        packet_data.append(0)
        
        await self._send_packet(PacketType.TOSERVER_PLAYERPOS, packet_data)
        logger.debug(f"Sent position update: ({x}, {y}, {z})")
        
    async def look_at(self, x: float, y: float, z: float):
        """Make the bot look at a specific position"""
        if not self.connected:
            raise RuntimeError("Not connected")
            
        # Calculate yaw and pitch to look at target
        dx = x - self.player_state.pos["x"]
        dy = y - self.player_state.pos["y"]
        dz = z - self.player_state.pos["z"]
        
        import math
        # Calculate yaw (horizontal angle)
        yaw = math.atan2(dx, dz)
        
        # Calculate pitch (vertical angle)
        horizontal_dist = math.sqrt(dx*dx + dz*dz)
        pitch = -math.atan2(dy, horizontal_dist)
        
        # Update position with new look direction
        await self.move_to(
            self.player_state.pos["x"],
            self.player_state.pos["y"], 
            self.player_state.pos["z"],
            yaw,
            pitch
        )
        
    async def jump(self):
        """Make the bot jump"""
        if not self.connected:
            raise RuntimeError("Not connected")
            
        # Set jump key bit
        key_states = 0x200  # Jump key
        
        # Send position with jump key pressed
        packet_data = bytearray()
        
        # Current position * 1000
        packet_data.extend(struct.pack("!iii", 
            int(self.player_state.pos["x"] * 1000), 
            int(self.player_state.pos["y"] * 1000), 
            int(self.player_state.pos["z"] * 1000)
        ))
        
        # Speed * 1000
        packet_data.extend(struct.pack("!iii", 0, 0, 0))
        
        # Pitch and yaw * 1000
        packet_data.extend(struct.pack("!ii",
            int(self.player_state.pitch * 1000),
            int(self.player_state.yaw * 1000)
        ))
        
        # Key states with jump
        packet_data.extend(struct.pack("!I", key_states))
        
        # FOV and range
        packet_data.append(80)
        packet_data.append(0)
        
        await self._send_packet(PacketType.TOSERVER_PLAYERPOS, packet_data)
        
        # Release jump key after short delay
        await asyncio.sleep(0.1)
        
        # Send without jump key
        packet_data[-6:-2] = struct.pack("!I", 0)
        await self._send_packet(PacketType.TOSERVER_PLAYERPOS, packet_data)
        
        logger.debug("Jumped")
        
    async def dig_block(self, x: int, y: int, z: int) -> bool:
        """Dig/break a block at the specified position"""
        if not self.connected:
            raise RuntimeError("Not connected")
            
        # Build TOSERVER_INTERACT packet for digging
        packet_data = bytearray()
        
        # Action: 0 = start digging
        packet_data.append(0)
        
        # Item index (0 = first item)
        packet_data.extend(struct.pack("!H", 0))
        
        # Pointed thing type: 1 = node
        packet_data.append(1)
        
        # Node position
        packet_data.extend(struct.pack("!iii", x, y, z))
        
        # Face (0-5, we'll use top)
        packet_data.append(1)
        
        await self._send_packet(PacketType.TOSERVER_INTERACT, packet_data)
        logger.info(f"Started digging block at ({x}, {y}, {z})")
        
        # Send "digging completed" after a short delay
        await asyncio.sleep(0.5)
        
        # Action: 2 = digging completed
        packet_data = bytearray()
        packet_data.append(2)
        packet_data.extend(struct.pack("!H", 0))
        packet_data.append(1)
        packet_data.extend(struct.pack("!iii", x, y, z))
        packet_data.append(1)
        
        await self._send_packet(PacketType.TOSERVER_INTERACT, packet_data)
        logger.info(f"Completed digging block at ({x}, {y}, {z})")
        
        return True
        
    async def place_block(self, x: int, y: int, z: int, item_index: int = 0) -> bool:
        """Place a block at the specified position"""
        if not self.connected:
            raise RuntimeError("Not connected")
            
        # Build TOSERVER_INTERACT packet for placing
        packet_data = bytearray()
        
        # Action: 3 = place
        packet_data.append(3)
        
        # Item index
        packet_data.extend(struct.pack("!H", item_index))
        
        # Pointed thing type: 1 = node
        packet_data.append(1)
        
        # Node position (place next to this)
        packet_data.extend(struct.pack("!iii", x, y-1, z))
        
        # Face (1 = top)
        packet_data.append(1)
        
        await self._send_packet(PacketType.TOSERVER_INTERACT, packet_data)
        logger.info(f"Placed block at ({x}, {y}, {z})")
        
        return True
        
    async def disconnect(self):
        """Disconnect from server"""
        if self.transport:
            self.transport.close()
            self.transport = None
        self.connected = False
        logger.info("Disconnected")


async def test_with_simple_auth():
    """Test connection with simple authentication flow"""
    logging.basicConfig(level=logging.DEBUG)
    
    conn = UDPLuantiConnection(
        host="localhost",
        port=50000, 
        username="TestBot",
        password=""
    )
    
    try:
        # Just establish UDP endpoint first
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: MineTestUDPProtocol(conn),
            remote_addr=(conn.host, conn.port)
        )
        
        conn.protocol = protocol
        logger.info("UDP endpoint created")
        
        # Send simple INIT without peer ID first
        packet = bytearray()
        packet.extend(struct.pack("!I", 0x4f457403))  # Protocol ID
        packet.extend(struct.pack("!H", 0))  # Peer ID 0
        packet.append(0)  # Channel 0
        packet.append(0x01)  # TYPE_ORIGINAL (unreliable)
        packet.extend(struct.pack("!H", PacketType.TOSERVER_INIT))  # Packet type
        
        # Protocol version
        packet.append(42)  # MAX_PROTOCOL_VERSION
        
        # Player name (wide string)
        name_bytes = conn.username.encode('utf-16-be')
        packet.extend(struct.pack("!H", len(conn.username)))
        packet.extend(name_bytes)
        
        # Password (empty)
        packet.extend(struct.pack("!H", 0))
        
        # Client version
        packet.extend(struct.pack("!HHH", 5, 8, 0))
        
        transport.sendto(packet)
        logger.info("Sent INIT packet")
        
        # Wait for responses
        await asyncio.sleep(5)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if transport:
            transport.close()


# Quick test
if __name__ == "__main__":
    asyncio.run(test_with_simple_auth())