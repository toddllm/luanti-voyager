"""
Pytest configuration and shared fixtures for Luanti Voyager tests
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil
from typing import Dict, Any, List

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class MockWorld:
    """Mock Luanti world for testing without server"""
    
    def __init__(self, size=(100, 100, 100), terrain="flat"):
        self.size = size
        self.terrain = terrain
        self.blocks = {}  # (x,y,z) -> block_type
        self._generate_terrain()
    
    def _generate_terrain(self):
        """Generate simple terrain for testing"""
        if self.terrain == "flat":
            # Create flat ground at y=0
            for x in range(-50, 50):
                for z in range(-50, 50):
                    self.blocks[(x, 0, z)] = "default:stone"
                    self.blocks[(x, 1, z)] = "default:dirt"
                    self.blocks[(x, 2, z)] = "default:grass"
        elif self.terrain == "void":
            # Empty world for void testing
            pass
    
    def get_block(self, x: int, y: int, z: int) -> str:
        """Get block at position"""
        return self.blocks.get((x, y, z), "air")
    
    def set_block(self, x: int, y: int, z: int, block_type: str):
        """Set block at position"""
        if block_type == "air":
            self.blocks.pop((x, y, z), None)
        else:
            self.blocks[(x, y, z)] = block_type
    
    def get_nearby_blocks(self, pos: Dict[str, float], radius: int = 5) -> List[Dict[str, Any]]:
        """Get blocks near position"""
        blocks = []
        px, py, pz = int(pos['x']), int(pos['y']), int(pos['z'])
        
        for x in range(px - radius, px + radius + 1):
            for y in range(py - radius, py + radius + 1):
                for z in range(pz - radius, pz + radius + 1):
                    block_type = self.get_block(x, y, z)
                    if block_type != "air":
                        blocks.append({
                            "pos": {"x": x, "y": y, "z": z},
                            "type": block_type
                        })
        
        return blocks


class MockAgent:
    """Mock agent for testing behaviors"""
    
    def __init__(self, world: MockWorld, name="TestBot", spawn_pos=(0, 10, 0)):
        self.world = world
        self.name = name
        self.pos = {"x": spawn_pos[0], "y": spawn_pos[1], "z": spawn_pos[2]}
        self.hp = 20
        self.inventory = {}
        self.commands_executed = []
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Track commands for testing"""
        self.commands_executed.append(command)
        
        # Parse and simulate command effects
        parts = command.split()
        cmd_type = parts[0]
        
        if cmd_type == "teleport":
            self.pos = {"x": float(parts[2]), "y": float(parts[3]), "z": float(parts[4])}
            return {"success": True}
        elif cmd_type == "move":
            # Simplified movement
            self.pos = {"x": float(parts[2]), "y": float(parts[3]), "z": float(parts[4])}
            return {"success": True}
        
        return {"success": False, "error": "Unknown command"}
    
    def get_state(self):
        """Get current agent state"""
        return {
            "pos": self.pos,
            "hp": self.hp,
            "inventory": self.inventory,
            "nearby_blocks": self.world.get_nearby_blocks(self.pos)
        }


@pytest.fixture
def mock_world():
    """Provides a mock world for testing"""
    return MockWorld(terrain="flat")


@pytest.fixture
def void_world():
    """Provides an empty void world"""
    return MockWorld(terrain="void")


@pytest.fixture
def test_agent(mock_world):
    """Provides a test agent in mock world"""
    return MockAgent(mock_world)


@pytest.fixture
def temp_dir():
    """Provides temporary directory for file tests"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Test utilities
def place_agent_in_void(agent: MockAgent):
    """Place agent in void area for testing"""
    agent.pos = {"x": 1000, "y": 1000, "z": 1000}
    # Ensure no blocks nearby
    for x in range(990, 1010):
        for y in range(990, 1010):
            for z in range(990, 1010):
                agent.world.blocks.pop((x, y, z), None)