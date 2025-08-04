# Issue: Implement Packet Acknowledgment System for Reliable UDP

## Summary
The UDP connection doesn't acknowledge reliable packets from the server, causing the server to repeatedly resend packets and eventually timeout the connection.

## Current Behavior
- Server sends reliable packets with sequence numbers
- Client doesn't send acknowledgments
- Server logs show: "RE-SENDING timed-out RELIABLE"
- Connection eventually times out

## Expected Behavior
- Client should track received reliable packets
- Send acknowledgment packets back to server
- Maintain sliding window of sequence numbers
- Handle out-of-order packets correctly

## Technical Details

### Server Log Evidence
```
VERBOSE[ConnectionSend]: con(4/1)RE-SENDING timed-out RELIABLE to 127.0.0.1(t/o=0.5): count=33, channel=0, seqnum=65500
```

### Required Implementation
1. **Track reliable packets received**
   ```python
   self.received_seqnums: Set[int] = set()
   self.ack_queue: List[int] = []
   ```

2. **Send acknowledgments**
   ```python
   async def _send_ack(self, seqnum: int):
       """Send acknowledgment for reliable packet"""
       # TOCLIENT_CONTROL packet with ACK
       pass
   ```

3. **Handle retransmissions**
   - Detect duplicate packets
   - Maintain sliding window
   - Send cumulative ACKs

## Priority
**HIGH** - Without this, connections timeout and are unusable

## Related
- Depends on #33 (UDP protocol implementation)
- Required for stable connections

## Labels
- bug
- network
- reliability