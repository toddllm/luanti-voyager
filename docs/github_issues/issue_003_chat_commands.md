# Issue: Add Chat Message and Command Support

## Summary
The network connection lacks methods to send chat messages or execute commands, which are essential for bot functionality.

## Current Behavior
- No `send_chat_message()` method
- Cannot execute server commands like `/grant`, `/teleport`
- Cannot communicate with other players
- Bots are effectively mute and cannot use commands

## Expected Behavior
- Ability to send chat messages
- Ability to execute server commands
- Proper handling of chat responses
- Support for both public chat and commands

## Use Cases
1. **Admin commands**: `/grant`, `/teleport`, `/time`
2. **Communication**: Responding to players, announcing actions
3. **Coordination**: Multi-bot communication
4. **Debugging**: Status reports, error messages

## Suggested Implementation

### Add to LuantiConnection
```python
async def send_chat_message(self, message: str):
    """Send a chat message or command.
    
    Args:
        message: Chat message or command (starting with /)
    """
    packet = self._create_chat_packet(message)
    await self._send_packet(packet)

def _create_chat_packet(self, message: str) -> bytes:
    """Create a TOSERVER_CHAT_MESSAGE packet."""
    # Implement according to Minetest protocol
    pass
```

### Add chat event handling
```python
async def on_chat_message(self, sender: str, message: str):
    """Handle incoming chat messages."""
    pass
```

## Priority
**HIGH** - Essential for most bot operations

## Labels
- enhancement
- feature
- network