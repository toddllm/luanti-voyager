# Issue: Create Test Framework for Network Protocol

## Summary
There's no test framework for the network protocol implementation, making it difficult to verify correctness and prevent regressions.

## Current Behavior
- No unit tests for packet encoding/decoding
- No integration tests for connection flow
- No mock server for testing
- Manual testing only

## Expected Behavior
Comprehensive test suite including:
- Unit tests for all packet types
- Integration tests for connection scenarios
- Mock server for testing without real Minetest
- Performance/stress tests

## Required Components

### 1. Mock Server
```python
class MockMinetestServer:
    """Mock server for testing"""
    
    async def start(self, port: int):
        """Start mock server on port"""
        
    def expect_packet(self, packet_type: PacketType):
        """Set expectation for packet"""
        
    def send_packet(self, packet: bytes):
        """Send packet to connected clients"""
```

### 2. Packet Tests
```python
def test_init_packet_encoding():
    """Test TOSERVER_INIT packet encoding"""
    packet = encode_init_packet("TestBot", "password")
    assert packet[0:4] == PROTOCOL_ID
    # ... more assertions
    
def test_packet_parsing():
    """Test parsing server packets"""
    data = bytes([...])  # Known good packet
    packet_type, payload = parse_packet(data)
    assert packet_type == PacketType.TOCLIENT_HELLO
```

### 3. Connection Flow Tests
```python
async def test_connection_handshake():
    """Test full connection handshake"""
    server = MockMinetestServer()
    await server.start(40000)
    
    conn = UDPLuantiConnection("localhost", 40000)
    await conn.connect()
    
    assert conn.connected
    assert conn.peer_id != 0
```

### 4. Reliability Tests
```python
async def test_packet_retransmission():
    """Test reliable packet retransmission"""
    # Don't ACK packet, verify retransmit
    
async def test_out_of_order_packets():
    """Test handling out-of-order packets"""
    # Send packets with non-sequential seqnums
```

## Test Categories

1. **Unit Tests**
   - Packet encoding/decoding
   - Sequence number handling
   - Data structure serialization

2. **Integration Tests**
   - Connection establishment
   - Authentication flow
   - Chat messages
   - Movement commands

3. **Stress Tests**
   - Many packets quickly
   - Large packets
   - Packet loss simulation

4. **Compatibility Tests**
   - Different protocol versions
   - Various server configurations

## Implementation Plan
1. Create `tests/` directory structure
2. Add pytest configuration
3. Create mock server
4. Write packet tests
5. Add GitHub Actions CI

## Priority
**MEDIUM** - Important for reliability but not blocking

## Labels
- testing
- infrastructure
- quality