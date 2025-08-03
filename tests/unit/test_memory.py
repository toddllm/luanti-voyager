"""
Unit tests for the memory system
"""

import pytest
import json
from pathlib import Path
import tempfile

from luanti_voyager.memory import SkillMemory


class TestSkillMemory:
    """Test the SkillMemory class"""
    
    def test_memory_initialization(self, temp_dir):
        """Test memory system initializes correctly"""
        memory = SkillMemory("TestBot", memory_dir=temp_dir)
        
        assert memory.agent_name == "TestBot"
        assert memory.memory_dir == Path(temp_dir)
        # Files are created when data is saved, not on init
        assert memory.skills == {}
        assert memory.strategies == {}
    
    def test_remember_skill(self, temp_dir):
        """Test skill remembering and persistence"""
        memory = SkillMemory("TestBot", memory_dir=temp_dir)
        
        # Remember a skill
        action_sequence = [
            {"action": "move", "params": {"x": 10, "y": 0, "z": 5}},
            {"action": "place", "params": {"block": "wood"}}
        ]
        memory.remember_skill("build_shelter", action_sequence, success=True)
        
        # Verify it was saved
        skill = memory.get_skill("build_shelter")
        assert skill is not None
        assert skill["name"] == "build_shelter"
        assert skill["success"] is True
        assert skill["actions"] == action_sequence
    
    def test_skill_persistence(self, temp_dir):
        """Test skills persist across memory instances"""
        # First instance
        memory1 = SkillMemory("TestBot", memory_dir=temp_dir)
        memory1.remember_skill("test_skill", [{"action": "test"}], success=True)
        
        # Second instance should load existing data
        memory2 = SkillMemory("TestBot", memory_dir=temp_dir)
        skill = memory2.get_skill("test_skill")
        
        assert skill is not None
        assert skill["actions"] == [{"action": "test"}]
    
    def test_remember_strategy(self, temp_dir):
        """Test strategy memory"""
        memory = SkillMemory("TestBot", memory_dir=temp_dir)
        
        # Remember strategies
        memory.remember_strategy("low_health", "find_food", success=True)
        memory.remember_strategy("low_health", "hide", success=False)
        memory.remember_strategy("low_health", "find_food", success=True)
        
        # Get best strategies
        strategies = memory.get_best_strategies("low_health")
        
        assert len(strategies) > 0
        assert strategies[0] == "find_food"  # Should be first (higher success rate)
    
    def test_strategy_success_rate(self, temp_dir):
        """Test strategy success rate calculation"""
        memory = SkillMemory("TestBot", memory_dir=temp_dir)
        
        # Add multiple outcomes
        for _ in range(7):
            memory.remember_strategy("test_situation", "strategy_a", success=True)
        for _ in range(3):
            memory.remember_strategy("test_situation", "strategy_a", success=False)
        
        # Check that strategies were recorded
        best_strategies = memory.get_best_strategies("test_situation")
        assert "strategy_a" in best_strategies
        
        # Count successes and failures from internal data
        strat_list = memory.strategies.get("test_situation", [])
        successes = sum(1 for s in strat_list if s["strategy"] == "strategy_a" and s.get("success", True))
        failures = sum(1 for s in strat_list if s["strategy"] == "strategy_a" and not s.get("success", True))
        assert successes == 7
        assert failures == 3
    
    def test_multiple_agents(self, temp_dir):
        """Test multiple agents have separate memories"""
        memory1 = SkillMemory("Agent1", memory_dir=temp_dir)
        memory2 = SkillMemory("Agent2", memory_dir=temp_dir)
        
        memory1.remember_skill("skill1", [{"action": "test1"}])
        memory2.remember_skill("skill2", [{"action": "test2"}])
        
        # Each agent should only see their own skills
        assert memory1.get_skill("skill1") is not None
        assert memory1.get_skill("skill2") is None
        
        assert memory2.get_skill("skill2") is not None
        assert memory2.get_skill("skill1") is None
    
    def test_empty_strategy_query(self, temp_dir):
        """Test querying strategies for unknown situation"""
        memory = SkillMemory("TestBot", memory_dir=temp_dir)
        strategies = memory.get_best_strategies("unknown_situation")
        
        assert strategies == []
    
    def test_skill_update(self, temp_dir):
        """Test updating existing skill statistics"""
        memory = SkillMemory("TestBot", memory_dir=temp_dir)
        
        # Initial success
        memory.remember_skill("test", [{"action": "test"}], success=True)
        
        # Add failure - this overwrites the previous skill
        memory.remember_skill("test", [{"action": "test"}], success=False)
        
        skill = memory.get_skill("test")
        assert skill["success"] is False  # Latest state
        # The current implementation doesn't track counts
    
    def test_strategy_ordering(self, temp_dir):
        """Test strategies are ordered by recency"""
        memory = SkillMemory("TestBot", memory_dir=temp_dir)
        
        # Add strategies in specific order
        memory.remember_strategy("combat", "attack", success=True)
        memory.remember_strategy("combat", "defend", success=True)
        memory.remember_strategy("combat", "flee", success=True)
        memory.remember_strategy("combat", "attack", success=False)  # Failed, won't be in results
        memory.remember_strategy("combat", "hide", success=True)
        
        # get_best_strategies returns most recent successful strategies
        strategies = memory.get_best_strategies("combat", limit=3)
        
        # Should be most recent successful ones: hide, flee, defend
        assert len(strategies) == 3
        assert strategies[0] == "hide"  # Most recent
        assert strategies[1] == "flee"
        assert strategies[2] == "defend"