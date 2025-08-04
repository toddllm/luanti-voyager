# Issue: Support Block Names Instead of Numeric IDs

## Summary
The `place_block()` method only accepts numeric block IDs, but users expect to use block names like "default:stone" or "default:diamondblock".

## Current Behavior
```python
# Must use numeric ID
await conn.place_block(x, y, z, block_type=42)
```

## Expected Behavior
```python
# Use meaningful names
await conn.place_block(x, y, z, "default:diamondblock")
await conn.place_block(x, y, z, "default:stone")
```

## Use Cases
1. **Readable code**: Names are self-documenting
2. **Mod compatibility**: Different mods use different IDs
3. **Portability**: IDs can change between servers

## Suggested Implementation

### Option 1: Client-side mapping
```python
# Built-in mappings for common blocks
BLOCK_IDS = {
    "air": 0,
    "default:stone": 1,
    "default:dirt": 2,
    "default:dirt_with_grass": 3,
    # ... etc
}

async def place_block(self, x: int, y: int, z: int, 
                     block: Union[str, int]):
    """Place a block at position.
    
    Args:
        block: Block name (str) or ID (int)
    """
    if isinstance(block, str):
        block_id = BLOCK_IDS.get(block)
        if block_id is None:
            raise ValueError(f"Unknown block: {block}")
    else:
        block_id = block
```

### Option 2: Server query
```python
async def get_block_id(self, name: str) -> int:
    """Query server for block ID by name."""
    # Request from server
    pass

# Cache results
self._block_cache: Dict[str, int] = {}
```

## Technical Considerations
- Block IDs are not standardized across servers
- Mods add new blocks with dynamic IDs
- Need to handle unknown blocks gracefully

## Priority
**MEDIUM** - Quality of life improvement

## Labels
- enhancement
- usability
- api