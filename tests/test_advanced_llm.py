#!/usr/bin/env python3
"""Test advanced LLM features including multi-step reasoning, goal decomposition, and failure reflection."""

import asyncio
import logging
from luanti_voyager.agent import VoyagerAgent
from luanti_voyager.advanced_llm import Goal, ActionPlan

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_goal_decomposition():
    """Test goal decomposition feature."""
    logger.info("=== Testing Goal Decomposition ===")
    
    # Create agent with LLM
    agent = VoyagerAgent(name="GoalBot", llm_provider="ollama")
    
    # Set a high-level goal
    await agent.set_goal("Build a simple wooden house with a door and windows")
    
    # Check goal progress
    progress = await agent.get_goal_progress()
    logger.info(f"Goal progress:\n{progress}")
    
    await agent.llm.close()


async def test_multi_step_planning():
    """Test multi-step planning feature."""
    logger.info("\n=== Testing Multi-Step Planning ===")
    
    # Create agent with LLM
    agent = VoyagerAgent(name="PlannerBot", llm_provider="ollama")
    
    # Create a plan for collecting wood
    await agent.create_plan("Collect 10 pieces of wood")
    
    # Show the plan
    if agent.advanced_llm and agent.advanced_llm.current_plan:
        plan = agent.advanced_llm.current_plan
        logger.info(f"Plan has {len(plan.steps)} steps")
        logger.info(f"Success criteria: {plan.success_criteria}")
    
    await agent.llm.close()


async def test_failure_reflection():
    """Test failure reflection feature."""
    logger.info("\n=== Testing Failure Reflection ===")
    
    # Create agent with LLM
    agent = VoyagerAgent(name="LearnerBot", llm_provider="ollama")
    
    # Simulate a failed action
    failed_action = {
        "type": "dig",
        "pos": {"x": 10, "y": 5, "z": 10},
        "reason": "Mine iron ore"
    }
    
    world_state = {
        "agent_position": {"x": 10, "y": 5, "z": 10},
        "hp": 15,
        "inventory": {"wood": 5},
        "nearby_blocks": [
            {"type": "stone", "pos": {"x": 10, "y": 4, "z": 10}},
            {"type": "bedrock", "pos": {"x": 10, "y": 5, "z": 10}}
        ]
    }
    
    # Get reflection on failure
    if agent.advanced_llm:
        reflection = await agent.advanced_llm.reflect_on_failure(
            failed_action, 
            world_state,
            "Cannot dig bedrock - unbreakable block"
        )
        
        logger.info(f"Failure analysis: {reflection.get('failure_analysis', 'No analysis')}")
        logger.info(f"Lesson learned: {reflection.get('lesson_learned', 'No lesson')}")
        
        alt_action = reflection.get('alternative_action')
        if alt_action:
            logger.info(f"Alternative action suggested: {alt_action}")
    
    await agent.llm.close()


async def test_contextual_decision_making():
    """Test context-aware decision making."""
    logger.info("\n=== Testing Contextual Decision Making ===")
    
    # Create agent with LLM
    agent = VoyagerAgent(name="ContextBot", llm_provider="ollama")
    
    # Simulate some history
    if agent.advanced_llm:
        # Add some action history
        agent.advanced_llm.action_history = [
            {
                "action": {"type": "move", "pos": {"x": 0, "y": 10, "z": 0}},
                "state": {"hp": 20},
                "timestamp": "2025-01-01T10:00:00"
            },
            {
                "action": {"type": "dig", "pos": {"x": 1, "y": 10, "z": 0}},
                "state": {"hp": 20},
                "timestamp": "2025-01-01T10:01:00"
            }
        ]
        
        # Add a goal
        test_goal = Goal(
            description="Explore the underground cave system",
            steps=["Find cave entrance", "Gather torches", "Explore safely"],
            completed_steps=["Find cave entrance"]
        )
        agent.advanced_llm.goals.append(test_goal)
        
        # Make a contextual decision
        world_state = {
            "agent_position": {"x": 5, "y": 10, "z": 5},
            "hp": 18,
            "inventory": {"wood": 3, "stone": 10},
            "nearby_blocks": [
                {"type": "stone", "pos": {"x": 5, "y": 9, "z": 5}},
                {"type": "air", "pos": {"x": 5, "y": 8, "z": 5}},  # Cave entrance
                {"type": "coal_ore", "pos": {"x": 6, "y": 9, "z": 5}}
            ]
        }
        
        decision = await agent.advanced_llm.decide_with_context(world_state)
        if decision:
            logger.info(f"Contextual decision: {decision.get('type')} - {decision.get('reason')}")
    
    await agent.llm.close()


async def main():
    """Run all tests."""
    logger.info("Testing Advanced LLM Features")
    logger.info("=" * 50)
    
    # Run tests one by one
    await test_goal_decomposition()
    await asyncio.sleep(2)
    
    await test_multi_step_planning()
    await asyncio.sleep(2)
    
    await test_failure_reflection()
    await asyncio.sleep(2)
    
    await test_contextual_decision_making()
    
    logger.info("\n" + "=" * 50)
    logger.info("All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())