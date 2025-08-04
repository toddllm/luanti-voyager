# Network API Documentation

The luanti-voyager library provides a UDP-based connection to Minetest/Luanti servers, implementing the native protocol for reliable communication.

## Quick Start

```python
from luanti_voyager import UDPLuantiConnection
import asyncio

async def connect_to_server():
    conn = UDPLuantiConnection(host="localhost", port=30000)
    await conn.connect()
    await conn.send_chat_message("Hello world!")
    await conn.disconnect()

asyncio.run(connect_to_server())
```

## UDPLuantiConnection

The main class for connecting to Minetest/Luanti servers using the UDP protocol.

### Constructor

```python
UDPLuantiConnection(
    host: str = "localhost",
    port: int = 30000, 
    username: str = "VoyagerBot",
    password: str = ""
)
```

**Parameters:**
- `host`: Server hostname or IP address
- `port`: Server port (default Minetest port is 30000)
- `username`: Player name to connect as
- `password`: Player password (empty for servers that allow it)

### Methods

#### Connection Management

##### `async connect()`
Establishes connection to the server. Handles the full handshake including:
- Initial connection establishment
- Peer ID assignment
- Authentication
- Protocol initialization

**Raises:**
- `TimeoutError`: If connection times out
- `RuntimeError`: If connection fails

##### `async disconnect()`
Cleanly disconnects from the server.

#### Communication

##### `async send_chat_message(message: str)`
Sends a chat message to the server.

**Parameters:**
- `message`: The chat message to send

**Raises:**
- `RuntimeError`: If not connected

#### Movement

##### `async move_to(x: float, y: float, z: float, yaw: float = 0.0, pitch: float = 0.0)`
Move the bot to a specific position with optional view direction.

**Parameters:**
- `x`, `y`, `z`: Target coordinates
- `yaw`: Horizontal rotation (radians, optional)
- `pitch`: Vertical rotation (radians, optional)

##### `async look_at(x: float, y: float, z: float)`
Make the bot look at a specific position.

**Parameters:**
- `x`, `y`, `z`: Position to look at

##### `async jump()`
Make the bot jump once.

#### World Interaction

##### `async dig_block(x: int, y: int, z: int) -> bool`
Dig/break a block at the specified position.

**Parameters:**
- `x`, `y`, `z`: Block coordinates

**Returns:**
- `bool`: True if successful

##### `async place_block(x: int, y: int, z: int, item_index: int = 0) -> bool`
Place a block at the specified position.

**Parameters:**
- `x`, `y`, `z`: Position to place block
- `item_index`: Inventory slot to use (default: 0)

**Returns:**
- `bool`: True if successful

### Properties

- `connected`: Boolean indicating if currently connected
- `peer_id`: The peer ID assigned by the server
- `auth_complete`: Boolean indicating if authentication is complete

## Protocol Details

The implementation uses the Minetest UDP protocol which includes:
- Packet acknowledgment for reliable delivery
- Sequence number tracking
- Control packets (ACK, PING, etc.)
- Support for both reliable and unreliable packets

## Example: Connection with Error Handling

```python
import asyncio
import logging
from luanti_voyager import UDPLuantiConnection

logging.basicConfig(level=logging.INFO)

async def robust_connection():
    conn = UDPLuantiConnection(
        host="your-server.com",
        port=30000,
        username="BotPlayer"
    )
    
    try:
        await conn.connect()
        print(f"Connected with peer ID: {conn.peer_id}")
        
        # Your bot logic here
        await conn.send_chat_message("Bot online!")
        
        # Keep alive
        while conn.connected:
            await asyncio.sleep(1)
            
    except TimeoutError:
        print("Connection timed out")
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        await conn.disconnect()

asyncio.run(robust_connection())
```

## Future Enhancements

The following features are planned or in development:
- Movement and navigation methods
- Block interaction (dig, place)
- Entity interaction
- Inventory management
- World state queries
- Event callbacks

See the [GitHub issues](https://github.com/toddllm/luanti-voyager/issues) for the current roadmap.