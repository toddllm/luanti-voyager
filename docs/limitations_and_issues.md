# Luanti Voyager Limitations and Issues

This document tracks current limitations and issues found during testing.

## CRITICAL ISSUE: Network Connection Not Functional

### TCP vs UDP Protocol Mismatch
**Issue**: `LuantiConnection` uses TCP but Minetest server uses UDP
- **Current code**: Uses `asyncio.open_connection()` (TCP)
- **Required**: UDP socket connection for Minetest protocol
- **Impact**: Cannot connect to any Minetest/Luanti server
- **Status**: Connection will always fail with "Connection refused"
- **Fix needed**: Complete rewrite using UDP sockets

## Import/API Issues

### 1. Connection Module Not Exposed in Public API
**Issue**: The `LuantiConnection` class is not exposed in the package's `__init__.py`
- **Location**: `luanti_voyager/__init__.py` only exports `VoyagerAgent`
- **Impact**: Cannot use network connection without direct module import
- **Workaround**: Import directly: `from luanti_voyager.connection import LuantiConnection`
- **Fix needed**: Add connection classes to `__all__` in `__init__.py`

### 2. No Network-Based Agent Class
**Issue**: No public agent class that uses `LuantiConnection` for network communication
- **Current state**: `VoyagerAgent` uses file-based communication
- **Example exists**: `SimpleBot` in `connection.py` but not exposed
- **Impact**: Must create custom agent classes for network-based bots
- **Fix needed**: Create and expose a `NetworkAgent` class

## API Limitations

### 1. Limited Methods in LuantiConnection
**Current methods**:
- `connect()` - Async connection
- `disconnect()` - Async disconnection  
- `send_player_pos(x, y, z)` - Send position updates
- `dig_block(x, y, z)` - Dig at position
- `place_block(x, y, z, block_type)` - Place block (only numeric IDs)
- `get_nearby_blocks(radius)` - Get nearby blocks

**Missing methods**:
- `send_chat_message()` - Cannot send chat/commands
- `get_player_info()` - Cannot get player state
- `use_item()` - Cannot use items
- `get_inventory()` - Cannot access inventory

### 2. Block Type Limitations
**Issue**: `place_block()` only accepts numeric block type IDs
- No string-to-ID mapping (e.g., "default:diamondblock" → ID)
- Must know numeric IDs for all blocks
- **Fix needed**: Add block name resolution

### 3. No Synchronous API
**Issue**: All connection methods are async
- Requires asyncio for all operations
- More complex for simple scripts
- **Consider**: Add sync wrapper methods

## Functional Limitations

### 1. No Chat/Command Support
**Issue**: Cannot send chat messages or commands through the connection
- Cannot execute `/grant`, `/teleport`, etc.
- Cannot communicate with other players
- **Critical for**: Admin commands, teleportation, giving items

### 2. No Inventory Management
**Issue**: No methods to manage inventory
- Cannot give items to bot
- Cannot check what bot is holding
- Cannot select/use items

### 3. Limited World Interaction
**Issue**: Can only dig and place blocks
- Cannot interact with entities
- Cannot right-click blocks/items
- Cannot pick up items

## Testing Issues

### 1. No Mock/Test Framework
**Issue**: No built-in testing utilities
- Must create mock connections manually
- No test server configuration
- **Fix needed**: Add testing utilities

### 2. Examples Use Non-Existent APIs
**Issue**: Some examples reference APIs that don't exist
- `Agent` class doesn't exist (should be `VoyagerAgent`)
- Methods like `send_chat_message()` not implemented
- **Fix needed**: Update examples to match actual API

## Recommended GitHub Issues

1. **Enhancement: Expose network connection in public API**
   - Add `LuantiConnection` to `__all__`
   - Create `NetworkAgent` base class
   - Update documentation

2. **Feature: Add chat/command support**
   - Implement `send_chat_message()` method
   - Add command parsing utilities
   - Critical for bot functionality

3. **Feature: Block name resolution**
   - Add string-to-ID mapping for common blocks
   - Support "modname:blockname" format
   - Include default mappings

4. **Feature: Inventory management**
   - Add inventory query methods
   - Add item selection/use methods
   - Support for giving items

5. **Enhancement: Synchronous API wrapper**
   - Add sync versions of async methods
   - Simplify usage for basic scripts
   - Maintain async for advanced usage

6. **Documentation: Update examples**
   - Fix incorrect API usage
   - Add working network examples
   - Include troubleshooting guide

## Workarounds

For immediate use:
1. Use file-based `VoyagerAgent` for most tasks
2. Generate manual commands with helper scripts
3. Use mock connections for testing
4. Import modules directly when needed