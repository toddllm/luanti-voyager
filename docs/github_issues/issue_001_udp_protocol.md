# Issue: Network Connection Uses Wrong Protocol (TCP instead of UDP)

## Summary
The `LuantiConnection` class attempts to connect using TCP, but Minetest/Luanti servers use UDP for the game protocol. This makes the network connection completely non-functional.

## Current Behavior
- Connection attempts fail with "Connection refused" error
- Uses `asyncio.open_connection()` which creates TCP connections
- Cannot connect to any Minetest/Luanti server

## Expected Behavior
- Should connect using UDP protocol
- Should implement Minetest network protocol correctly
- Should be able to join servers and interact

## Technical Details

### Current Code (connection.py:58)
```python
self.reader, self.writer = await asyncio.open_connection(
    self.host, self.port
)
```

### Required Implementation
- Use `asyncio.create_datagram_endpoint()` for UDP
- Implement Minetest protocol handshake
- Handle reliable/unreliable packet distinction

## Steps to Reproduce
1. Start a Minetest server on port 30000 or 50000
2. Run `python3 test_connection.py`
3. Observe connection refused error

## Priority
**CRITICAL** - Without this fix, no network functionality works

## Suggested Fix
1. Replace TCP connection with UDP
2. Implement proper Minetest protocol:
   - Initial handshake
   - Packet structure (split packets, reliability)
   - Authentication flow
3. Reference Minetest source: `src/network/clientpackethandler.cpp`

## Labels
- bug
- critical
- network
- help wanted