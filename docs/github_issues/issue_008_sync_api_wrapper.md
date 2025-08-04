# Issue: Add Synchronous API Wrapper for Easier Usage

## Summary
All network methods are async, which makes simple scripts more complex. A synchronous wrapper would make the library more accessible for beginners and simple use cases.

## Current Behavior
```python
# Current async-only approach
import asyncio

async def main():
    conn = UDPLuantiConnection()
    await conn.connect()
    await conn.send_chat_message("Hello")
    await conn.disconnect()

asyncio.run(main())
```

## Expected Behavior
```python
# Simpler sync approach
from luanti_voyager import SyncConnection

conn = SyncConnection()
conn.connect()
conn.send_chat_message("Hello")
conn.disconnect()
```

## Suggested Implementation

### Sync Wrapper Class
```python
class SyncConnection:
    """Synchronous wrapper around async connection"""
    
    def __init__(self, host="localhost", port=30000):
        self._conn = UDPLuantiConnection(host, port)
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop)
        self._thread.start()
        
    def connect(self):
        """Synchronous connect"""
        future = asyncio.run_coroutine_threadsafe(
            self._conn.connect(), self._loop
        )
        return future.result()
        
    def send_chat_message(self, message: str):
        """Synchronous chat"""
        future = asyncio.run_coroutine_threadsafe(
            self._conn.send_chat_message(message), self._loop
        )
        return future.result()
```

### Alternative: Dual API
```python
class Connection:
    """Connection with both sync and async methods"""
    
    async def connect_async(self):
        """Async version"""
        pass
        
    def connect(self):
        """Sync version"""
        return asyncio.run(self.connect_async())
```

## Use Cases
1. **Simple scripts**: Quick automation without async complexity
2. **REPL/Interactive**: Testing in Python shell
3. **Beginners**: Lower barrier to entry
4. **Integration**: Easier to integrate with sync codebases

## Considerations
- Thread safety for event loop
- Performance overhead of sync wrapper
- Clear documentation on when to use each
- Consistent API between sync/async

## Priority
**MEDIUM** - Quality of life improvement

## Labels
- enhancement
- usability
- api