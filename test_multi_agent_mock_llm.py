#!/usr/bin/env python3
"""
Multi-agent demo with mock LLM responses.
Shows how different agent personalities lead to different behaviors.
"""

import asyncio
from luanti_voyager.multi_agent import AgentProfile, AgentCommunication, MessagePriority

# Mock LLM responses based on personality
MOCK_RESPONSES = {
    "adventurous_discovery": "WOW! This is AMAZING! We could build an underground crystal palace here!",
    "methodical_discovery": "Interesting find. We should survey for stability before proceeding.",
    "adventurous_danger": "Let's fight it! I'll distract while you attack!",
    "methodical_danger": "Fall back to defensive positions. Activate base defenses."
}

async def mock_llm_generate(prompt: str) -> str:
    """Mock LLM that returns personality-appropriate responses."""
    if "adventurous" in prompt and "discovered" in prompt:
        return MOCK_RESPONSES["adventurous_discovery"]
    elif "methodical" in prompt and "discovered" in prompt:
        return MOCK_RESPONSES["methodical_discovery"]
    elif "adventurous" in prompt and "monster" in prompt:
        return MOCK_RESPONSES["adventurous_danger"]
    elif "methodical" in prompt and "monster" in prompt:
        return MOCK_RESPONSES["methodical_danger"]
    else:
        return "Acknowledged. Proceeding with caution."

async def multi_agent_demo():
    """Demo showing how agent personalities affect responses."""
    print("\n" + "="*60)
    print("🤖 MULTI-AGENT PERSONALITY DEMO")
    print("="*60)
    print("Showing how different personalities lead to different behaviors\n")
    
    # Create agents with distinct personalities
    explorer = AgentProfile(
        name="Scout",
        personality="adventurous and excitable",
        skills=["exploration", "discovery"],
        communication_style="enthusiastic",
        team_role="explorer"
    )
    
    builder = AgentProfile(
        name="Constructor",
        personality="careful and methodical",
        skills=["building", "planning"],
        communication_style="precise",
        team_role="builder"
    )
    
    # Create communication channels
    scout_comm = AgentCommunication("Scout", "alpha")
    constructor_comm = AgentCommunication("Constructor", "alpha")
    
    # Register listeners
    scout_comm.register_listener("Constructor", constructor_comm)
    constructor_comm.register_listener("Scout", scout_comm)
    
    print("📋 Agent Profiles:")
    print(f"  Scout: {explorer.personality}")
    print(f"  Constructor: {builder.personality}")
    print()
    
    # Scenario 1: Discovery
    print("💎 Scenario 1: Major Discovery")
    print("-" * 40)
    discovery = "massive underground cave with glowing crystals"
    
    # Get personality-based responses (simulated)
    explorer_response = await mock_llm_generate(f"adventurous personality discovered {discovery}")
    builder_response = await mock_llm_generate(f"methodical personality discovered {discovery}")
    
    print(f"Scout discovers: {discovery}")
    print(f"  Scout's reaction: \"{explorer_response}\"")
    print(f"  Constructor's response: \"{builder_response}\"")
    print()
    
    # Actually send the messages
    await scout_comm.share_discovery(discovery, importance=9)
    messages = await constructor_comm.process_messages()
    print(f"  (Constructor received {len(messages)} message about the discovery)")
    print()
    
    # Scenario 2: Danger
    print("🚨 Scenario 2: Danger Approaching")
    print("-" * 40)
    threat = "Large monster approaching the base"
    
    # Get personality-based responses
    explorer_danger = await mock_llm_generate("adventurous personality monster approaching")
    builder_danger = await mock_llm_generate("methodical personality monster approaching")
    
    print(f"Alert: {threat}")
    print(f"  Scout's reaction: \"{explorer_danger}\"")
    print(f"  Constructor's reaction: \"{builder_danger}\"")
    print()
    
    # Send urgent messages
    await scout_comm.broadcast(
        "Monster spotted! " + explorer_danger,
        priority=MessagePriority.URGENT
    )
    await constructor_comm.broadcast(
        "Defensive protocol: " + builder_danger,
        priority=MessagePriority.URGENT
    )
    
    # Process urgent messages
    scout_msgs = await scout_comm.process_messages()
    constructor_msgs = await constructor_comm.process_messages()
    
    print(f"  Messages exchanged: {len(scout_msgs) + len(constructor_msgs)}")
    print()
    
    # Scenario 3: Collaboration
    print("🤝 Scenario 3: Task Assignment Based on Skills")
    print("-" * 40)
    
    tasks = [
        ("Scout for new areas", explorer),
        ("Design base layout", builder),
        ("Explore dangerous cave", explorer),
        ("Build defensive walls", builder)
    ]
    
    print("Task assignments based on agent skills:")
    for task, best_agent in tasks:
        suitability = "HIGH" if any(skill in task.lower() for skill in best_agent.skills) else "LOW"
        print(f"  '{task}' → {best_agent.name} (suitability: {suitability})")
    
    print("\n" + "="*60)
    print("✅ KEY INSIGHTS FROM DEMO:")
    print("="*60)
    print("1. Agent personalities affect decision-making")
    print("2. Different roles lead to complementary behaviors")
    print("3. Skill-based task assignment improves efficiency")
    print("4. Communication priority ensures critical info is shared")
    print("\nThis shows how Mindcraft's multi-agent concepts enhance")
    print("Luanti Voyager with realistic team dynamics!\n")

if __name__ == "__main__":
    asyncio.run(multi_agent_demo())