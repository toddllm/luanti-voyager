# Issue: Add Essential Bot Interaction Methods

## Summary
The connection classes lack essential methods for bot interaction with the world, such as digging blocks, placing blocks, moving, and interacting with objects.

## Current Behavior
- UDP connection only has basic packet sending
- No high-level methods for world interaction
- File-based VoyagerAgent has limited functionality

## Expected Behavior
Complete set of interaction methods for bots:
- Movement and navigation
- Block manipulation (dig, place)
- Entity interaction
- Item usage

## Required Methods

### Movement
```python
async def move_to(self, x: float, y: float, z: float):
    """Move bot to position"""
    
async def look_at(self, x: float, y: float, z: float):
    """Point bot's view at position"""
    
async def jump(self):
    """Make bot jump"""
    
async def sneak(self, enable: bool = True):
    """Toggle sneak mode"""
```

### Block Interaction
```python
async def dig_block(self, x: int, y: int, z: int) -> bool:
    """Dig block at position"""
    
async def place_block(self, x: int, y: int, z: int, 
                      block: Union[str, int], face: int = 1):
    """Place block at position"""
    
async def get_block(self, x: int, y: int, z: int) -> BlockInfo:
    """Get information about block at position"""
```

### Entity Interaction
```python
async def interact_with_entity(self, entity_id: int, 
                               action: InteractionType):
    """Interact with an entity (right-click, attack, etc)"""
    
async def get_nearby_entities(self, radius: float = 10) -> List[Entity]:
    """Get list of nearby entities"""
```

### Item/Tool Usage
```python
async def use_item(self, target: Optional[Vec3] = None):
    """Use currently held item"""
    
async def attack(self, target: Optional[Vec3] = None):
    """Perform attack/dig with current tool"""
```

## Implementation Notes
- Should work with both UDP and future protocols
- Need to handle server responses
- Should provide feedback on success/failure
- Consider rate limiting to avoid spam

## Priority
**HIGH** - Core functionality needed for any useful bot

## Labels
- enhancement
- feature
- api