# Issue: Network Connection Classes Not Exposed in Public API

## Summary
The `LuantiConnection` class and related network functionality are not exposed in the package's public API (`__init__.py`), making it difficult to use network features.

## Current Behavior
- Must import directly: `from luanti_voyager.connection import LuantiConnection`
- No network-based agent class exposed
- Examples use non-public APIs

## Expected Behavior
- `from luanti_voyager import LuantiConnection, NetworkAgent`
- Clear public API for network functionality
- Proper documentation of available classes

## Technical Details

### Current __init__.py
```python
from .agent import VoyagerAgent

__all__ = ["VoyagerAgent"]
```

### Suggested __init__.py
```python
from .agent import VoyagerAgent
from .connection import LuantiConnection, SimpleBot
from .network_agent import NetworkAgent  # New class

__all__ = [
    "VoyagerAgent",
    "LuantiConnection", 
    "SimpleBot",
    "NetworkAgent"
]
```

## Impact
- Users cannot easily discover network functionality
- Confusion about which classes are public API
- Examples may break if internal structure changes

## Suggested Fix
1. Add connection classes to `__all__`
2. Create a `NetworkAgent` base class that uses `LuantiConnection`
3. Update documentation to show both file-based and network-based agents
4. Add docstrings explaining when to use each

## Labels
- enhancement
- api
- documentation