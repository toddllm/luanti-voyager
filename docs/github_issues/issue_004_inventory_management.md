# Issue: Add Inventory Management Support

## Summary
There are no methods to interact with the bot's inventory, making it impossible to manage items, use tools, or check what the bot is carrying.

## Current Behavior
- No way to query inventory contents
- Cannot select items in hotbar
- Cannot use/activate items
- Cannot drop or pick up items

## Expected Behavior
- Query inventory contents
- Select active item
- Use items (right-click functionality)
- Drop/pick up items
- Move items between inventory slots

## Use Cases
1. **Building**: Select and place different block types
2. **Tools**: Use pickaxe, shovel, etc.
3. **Items**: Use food, potions, special items
4. **Trading**: Exchange items with other players
5. **Crafting**: Access crafting grid

## Suggested Implementation

### Core Methods
```python
async def get_inventory(self) -> Dict[int, ItemStack]:
    """Get current inventory contents."""
    pass

async def select_item(self, slot: int):
    """Select item in hotbar (0-8)."""
    pass

async def use_item(self, target_pos: Optional[Vec3] = None):
    """Use currently selected item."""
    pass

async def drop_item(self, slot: int, count: int = 1):
    """Drop items from inventory."""
    pass

async def move_item(self, from_slot: int, to_slot: int, count: int):
    """Move items between inventory slots."""
    pass
```

### Data Structures
```python
@dataclass
class ItemStack:
    name: str  # e.g., "default:stone"
    count: int
    wear: float
    metadata: Dict[str, Any]
```

## Technical Notes
- Requires TOSERVER_INVENTORY_ACTION packets
- Need to track inventory state from TOCLIENT_INVENTORY
- Handle inventory formspecs

## Priority
**MEDIUM** - Important for advanced functionality

## Labels
- enhancement
- feature
- inventory