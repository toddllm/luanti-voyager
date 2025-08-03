"""
Integration tests for agent-LLM interaction
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import json

from luanti_voyager.agent import VoyagerAgent
from luanti_voyager.llm import VoyagerLLM


class TestAgentLLMIntegration:
    """Test agent and LLM working together"""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM for testing"""
        llm = AsyncMock()
        llm.generate = AsyncMock()
        return llm
    
    @pytest.fixture
    def mock_world_state(self):
        """Create mock world state"""
        return {
            "agent": {
                "name": "TestBot",
                "pos": {"x": 0, "y": 10, "z": 0},
                "hp": 20,
                "breath": 10,
                "inventory": {"default:wood": 5}
            },
            "nearby_blocks": [
                {"pos": {"x": 0, "y": 9, "z": 0}, "type": "default:stone"}
            ],
            "entities": [],
            "time_of_day": 12000
        }
    
    async def test_agent_makes_decisions(self, mock_llm, mock_world_state, temp_dir):
        """Test agent uses LLM to make decisions"""
        # Setup mock response
        mock_llm.generate.return_value = json.dumps({
            "action": "move",
            "parameters": {"target": {"x": 10, "y": 10, "z": 5}},
            "reason": "Exploring new area"
        })
        
        # Create agent with mock LLM
        agent = VoyagerAgent(
            agent_name="TestBot",
            llm=mock_llm,
            command_file=f"{temp_dir}/commands.txt"
        )
        
        # Make decision
        action = await agent._decide_action(mock_world_state)
        
        # Verify LLM was called
        mock_llm.generate.assert_called_once()
        prompt = mock_llm.generate.call_args[0][0]
        
        # Check prompt contains world state info
        assert "TestBot" in prompt
        assert "hp: 20" in prompt
        assert "default:wood" in prompt
        
        # Check action was parsed correctly
        assert action["action"] == "move"
        assert action["parameters"]["target"]["x"] == 10
    
    async def test_agent_handles_complex_decisions(self, mock_llm, temp_dir):
        """Test agent handles multi-step planning"""
        # Mock complex response
        mock_llm.generate.return_value = json.dumps({
            "action": "sequence",
            "steps": [
                {"action": "move", "parameters": {"target": {"x": 5, "y": 10, "z": 5}}},
                {"action": "place", "parameters": {"item": "default:wood", "pos": {"x": 5, "y": 10, "z": 5}}}
            ],
            "reason": "Building a shelter"
        })
        
        agent = VoyagerAgent(
            agent_name="TestBot",
            llm=mock_llm,
            command_file=f"{temp_dir}/commands.txt"
        )
        
        world_state = {"agent": {"pos": {"x": 0, "y": 10, "z": 0}}}
        action = await agent._decide_action(world_state)
        
        assert action["action"] == "sequence"
        assert len(action["steps"]) == 2
        assert action["steps"][0]["action"] == "move"
        assert action["steps"][1]["action"] == "place"
    
    async def test_agent_memory_influences_decisions(self, mock_llm, mock_world_state, temp_dir):
        """Test agent uses memory to inform decisions"""
        # Setup agent with memory
        agent = VoyagerAgent(
            agent_name="TestBot", 
            llm=mock_llm,
            command_file=f"{temp_dir}/commands.txt"
        )
        
        # Add memory of successful strategy
        agent.memory.remember_strategy("low_health", "find_food", success=True)
        agent.memory.remember_strategy("low_health", "find_food", success=True)
        
        # Update world state to low health
        mock_world_state["agent"]["hp"] = 5
        
        # Mock LLM to return food-finding action
        mock_llm.generate.return_value = json.dumps({
            "action": "move",
            "parameters": {"target": {"x": 20, "y": 10, "z": 0}},
            "reason": "Moving to find food based on past success"
        })
        
        action = await agent._decide_action(mock_world_state)
        
        # Verify prompt includes memory info
        prompt = mock_llm.generate.call_args[0][0]
        assert "find_food" in prompt or "strategies" in prompt.lower()
    
    async def test_agent_handles_llm_errors(self, mock_world_state, temp_dir):
        """Test agent handles LLM failures gracefully"""
        # Create LLM that fails
        failing_llm = AsyncMock()
        failing_llm.generate = AsyncMock(side_effect=Exception("LLM API error"))
        
        agent = VoyagerAgent(
            agent_name="TestBot",
            llm=failing_llm,
            command_file=f"{temp_dir}/commands.txt"
        )
        
        # Should return safe default action
        action = await agent._decide_action(mock_world_state)
        
        assert action is not None
        assert "action" in action
        # Default action might be wait or explore
        assert action["action"] in ["wait", "explore", "move"]
    
    async def test_agent_parses_invalid_llm_response(self, mock_llm, mock_world_state, temp_dir):
        """Test agent handles malformed LLM responses"""
        # Mock invalid JSON response
        mock_llm.generate.return_value = "This is not valid JSON"
        
        agent = VoyagerAgent(
            agent_name="TestBot",
            llm=mock_llm,
            command_file=f"{temp_dir}/commands.txt"
        )
        
        # Should handle gracefully
        action = await agent._decide_action(mock_world_state)
        
        assert action is not None
        assert "action" in action
    
    @patch("luanti_voyager.llm.VoyagerLLM")
    async def test_agent_with_real_ollama_format(self, mock_voyager_llm_class, mock_world_state, temp_dir):
        """Test agent with Ollama-style responses"""
        # Mock Ollama-style LLM
        mock_llm_instance = AsyncMock()
        mock_llm_instance.generate = AsyncMock(return_value=json.dumps({
            "action": "teleport",
            "parameters": {"x": 0, "y": 100, "z": 0},
            "reason": "Stuck in void, teleporting to safety"
        }))
        mock_voyager_llm_class.return_value = mock_llm_instance
        
        # Create agent
        agent = VoyagerAgent(
            agent_name="TestBot",
            llm_provider="ollama",
            command_file=f"{temp_dir}/commands.txt"
        )
        
        # Simulate void situation
        mock_world_state["agent"]["pos"] = {"x": 1000, "y": -100, "z": 1000}
        mock_world_state["nearby_blocks"] = []  # No blocks = void
        
        action = await agent._decide_action(mock_world_state)
        
        assert action["action"] == "teleport"
        assert action["reason"] == "Stuck in void, teleporting to safety"
    
    async def test_context_window_management(self, mock_llm, temp_dir):
        """Test agent manages conversation context"""
        agent = VoyagerAgent(
            agent_name="TestBot",
            llm=mock_llm,
            command_file=f"{temp_dir}/commands.txt"
        )
        
        # Simulate multiple interactions
        responses = [
            json.dumps({"action": "move", "parameters": {"target": {"x": i, "y": 10, "z": 0}}})
            for i in range(10)
        ]
        mock_llm.generate = AsyncMock(side_effect=responses)
        
        # Make multiple decisions
        for i in range(10):
            world_state = {"agent": {"pos": {"x": i, "y": 10, "z": 0}}}
            await agent._decide_action(world_state)
        
        # Verify context doesn't grow unbounded
        # (This would be checking internal state if agent tracks history)
        assert mock_llm.generate.call_count == 10
    
    async def test_agent_action_validation(self, mock_llm, mock_world_state, temp_dir):
        """Test agent validates actions before execution"""
        # Mock response with invalid action
        mock_llm.generate.return_value = json.dumps({
            "action": "invalid_action",
            "parameters": {},
            "reason": "Testing"
        })
        
        agent = VoyagerAgent(
            agent_name="TestBot",
            llm=mock_llm,
            command_file=f"{temp_dir}/commands.txt"
        )
        
        # Should either reject or convert to valid action
        action = await agent._decide_action(mock_world_state)
        
        # Agent should handle invalid actions gracefully
        assert action["action"] in ["move", "teleport", "place", "mine", "wait", "explore", "sequence"]