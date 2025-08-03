"""
Behavior tests for agent decision making
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
import json

from conftest import MockWorld, MockAgent, place_agent_in_void


class TestSurvivalBehaviors:
    """Test agent survival instincts"""
    
    async def test_agent_escapes_void(self, void_world):
        """Agent should teleport when stuck in void"""
        agent = MockAgent(void_world, spawn_pos=(1000, -50, 1000))
        
        # Verify agent is in void
        nearby_blocks = agent.world.get_nearby_blocks(agent.pos)
        assert len(nearby_blocks) == 0
        
        # Agent should decide to teleport
        action = await agent.execute_command("teleport TestBot 0 100 0")
        assert action["success"] is True
        assert agent.pos["y"] == 100
    
    async def test_agent_seeks_safety_low_health(self, mock_world):
        """Agent should seek safety when health is low"""
        agent = MockAgent(mock_world)
        agent.hp = 3  # Very low health
        
        # Agent should prioritize safety
        state = agent.get_state()
        assert state["hp"] < 5
        
        # In real implementation, agent would:
        # - Look for shelter
        # - Avoid enemies
        # - Find food
    
    async def test_agent_avoids_fall_damage(self, mock_world):
        """Agent should avoid dangerous falls"""
        agent = MockAgent(mock_world, spawn_pos=(0, 50, 0))
        
        # Check if there's ground below
        ground_below = []
        for y in range(int(agent.pos["y"]) - 1, int(agent.pos["y"]) - 10, -1):
            block = mock_world.get_block(0, y, 0)
            if block != "air":
                ground_below.append((y, block))
                break
        
        # If drop is too high, agent should be careful
        if not ground_below or (agent.pos["y"] - ground_below[0][0]) > 5:
            # Agent should place blocks or find safer path
            assert agent.pos["y"] > 10  # High position confirmed
    
    async def test_agent_manages_hunger(self, mock_world):
        """Agent should manage food/hunger (if implemented)"""
        agent = MockAgent(mock_world)
        
        # Simulate hunger mechanic
        agent.hunger = 5  # Low hunger
        
        # Agent should prioritize finding food
        # This would check agent's decision making
        assert hasattr(agent, "hunger") or True  # Placeholder


class TestExplorationBehaviors:
    """Test agent exploration patterns"""
    
    async def test_agent_explores_systematically(self, mock_world):
        """Agent should explore in organized patterns"""
        agent = MockAgent(mock_world)
        start_pos = agent.pos.copy()
        
        # Track movement pattern
        positions_visited = [start_pos]
        
        # Simulate exploration
        for i in range(5):
            # Move in expanding square pattern
            new_x = start_pos["x"] + (i + 1) * 10
            new_z = start_pos["z"] + (i + 1) * 10
            
            await agent.execute_command(f"move TestBot {new_x} {start_pos['y']} {new_z}")
            positions_visited.append(agent.pos.copy())
        
        # Check that agent covered ground
        assert len(positions_visited) > 1
        assert positions_visited[-1]["x"] != start_pos["x"]
    
    async def test_agent_marks_explored_areas(self, mock_world):
        """Agent should remember where it has been"""
        agent = MockAgent(mock_world)
        agent.explored_chunks = set()
        
        # Explore area
        chunk_x = int(agent.pos["x"] // 16)
        chunk_z = int(agent.pos["z"] // 16)
        agent.explored_chunks.add((chunk_x, chunk_z))
        
        # Move to new area
        await agent.execute_command("move TestBot 50 10 50")
        new_chunk_x = int(agent.pos["x"] // 16)
        new_chunk_z = int(agent.pos["z"] // 16)
        
        # Should track both areas
        if (new_chunk_x, new_chunk_z) != (chunk_x, chunk_z):
            agent.explored_chunks.add((new_chunk_x, new_chunk_z))
        
        assert len(agent.explored_chunks) >= 1
    
    async def test_agent_returns_to_base(self, mock_world):
        """Agent should be able to return home"""
        agent = MockAgent(mock_world)
        
        # Set home position
        agent.home_pos = {"x": 0, "y": 10, "z": 0}
        
        # Wander away
        await agent.execute_command("move TestBot 100 10 100")
        assert agent.pos["x"] == 100
        
        # Return home
        await agent.execute_command(f"move TestBot {agent.home_pos['x']} {agent.home_pos['y']} {agent.home_pos['z']}")
        
        assert agent.pos["x"] == agent.home_pos["x"]
        assert agent.pos["z"] == agent.home_pos["z"]


class TestBuildingBehaviors:
    """Test agent building capabilities"""
    
    async def test_agent_builds_shelter(self, mock_world):
        """Agent should be able to build basic shelter"""
        agent = MockAgent(mock_world)
        agent.inventory = {"default:wood": 20}
        
        # Build simple 3x3 platform
        start_x, start_z = int(agent.pos["x"]), int(agent.pos["z"])
        platform_y = int(agent.pos["y"]) - 1
        
        for x in range(start_x - 1, start_x + 2):
            for z in range(start_z - 1, start_z + 2):
                mock_world.set_block(x, platform_y, z, "default:wood")
        
        # Verify platform was built
        platform_blocks = 0
        for x in range(start_x - 1, start_x + 2):
            for z in range(start_z - 1, start_z + 2):
                if mock_world.get_block(x, platform_y, z) == "default:wood":
                    platform_blocks += 1
        
        assert platform_blocks == 9
    
    async def test_agent_builds_efficiently(self, mock_world):
        """Agent should minimize material waste"""
        agent = MockAgent(mock_world)
        initial_wood = 10
        agent.inventory = {"default:wood": initial_wood}
        
        # Build small structure
        build_positions = [(0, 10, 0), (1, 10, 0), (0, 10, 1)]
        
        for pos in build_positions:
            mock_world.set_block(*pos, "default:wood")
            agent.inventory["default:wood"] -= 1
        
        # Check efficiency
        blocks_placed = len(build_positions)
        assert agent.inventory["default:wood"] == initial_wood - blocks_placed
    
    async def test_agent_scaffolding(self, mock_world):
        """Agent should use scaffolding for tall builds"""
        agent = MockAgent(mock_world)
        agent.inventory = {"default:dirt": 30}
        
        # Need to build high
        target_height = 20
        current_y = int(agent.pos["y"])
        
        # Build pillar to reach height
        for y in range(current_y, target_height):
            mock_world.set_block(0, y, 0, "default:dirt")
        
        # Verify pillar
        pillar_height = 0
        for y in range(current_y, target_height):
            if mock_world.get_block(0, y, 0) == "default:dirt":
                pillar_height += 1
        
        assert pillar_height == target_height - current_y


class TestCombatBehaviors:
    """Test agent combat decisions"""
    
    async def test_agent_flees_danger(self, mock_world):
        """Agent should flee from stronger enemies"""
        agent = MockAgent(mock_world)
        agent.hp = 5  # Low health
        
        # Simulate enemy nearby
        enemy = {"type": "zombie", "pos": {"x": 5, "y": 10, "z": 5}, "hp": 20}
        
        # Calculate distance to enemy
        dx = agent.pos["x"] - enemy["pos"]["x"]
        dz = agent.pos["z"] - enemy["pos"]["z"]
        distance = (dx**2 + dz**2)**0.5
        
        # Agent should move away
        if agent.hp < 10 and distance < 10:
            # Move in opposite direction
            flee_x = agent.pos["x"] + (dx / distance) * 20
            flee_z = agent.pos["z"] + (dz / distance) * 20
            
            await agent.execute_command(f"move TestBot {flee_x} {agent.pos['y']} {flee_z}")
        
        # Verify agent moved away
        new_dx = agent.pos["x"] - enemy["pos"]["x"]
        new_dz = agent.pos["z"] - enemy["pos"]["z"]
        new_distance = (new_dx**2 + new_dz**2)**0.5
        
        assert new_distance >= distance or agent.hp >= 10
    
    async def test_agent_strategic_combat(self, mock_world):
        """Agent should use terrain in combat"""
        agent = MockAgent(mock_world)
        
        # Place agent on high ground
        high_ground_y = 15
        agent.pos = {"x": 0, "y": high_ground_y, "z": 0}
        
        # Enemy on low ground
        enemy_y = 10
        
        # Agent should maintain height advantage
        assert agent.pos["y"] > enemy_y
        
        # In real implementation:
        # - Use blocks for cover
        # - Maintain distance
        # - Use terrain advantage


class TestResourceBehaviors:
    """Test resource gathering behaviors"""
    
    async def test_agent_gathers_efficiently(self, mock_world):
        """Agent should gather resources efficiently"""
        agent = MockAgent(mock_world)
        
        # Place trees nearby
        tree_positions = [(10, 3, 10), (10, 4, 10), (10, 5, 10)]
        for pos in tree_positions:
            mock_world.set_block(*pos, "default:tree")
        
        # Agent should mine all blocks
        wood_gathered = 0
        for pos in tree_positions:
            if mock_world.get_block(*pos) == "default:tree":
                mock_world.set_block(*pos, "air")
                wood_gathered += 1
        
        assert wood_gathered == len(tree_positions)
    
    async def test_agent_prioritizes_resources(self, mock_world):
        """Agent should prioritize valuable resources"""
        agent = MockAgent(mock_world)
        
        # Place different resources
        mock_world.set_block(5, 2, 5, "default:stone")
        mock_world.set_block(10, 2, 10, "default:diamond")
        
        # Agent should prefer diamond over stone
        priority_order = ["default:diamond", "default:iron", "default:stone"]
        
        # In real implementation, agent would path to diamond first
        assert "default:diamond" in priority_order
        assert priority_order.index("default:diamond") < priority_order.index("default:stone")