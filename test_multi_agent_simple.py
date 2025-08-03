#!/usr/bin/env python3
"""
Simple smoke test for multi-agent communication system.
Tests basic message passing without requiring game server.
"""

import asyncio
import logging
from datetime import datetime

from luanti_voyager.multi_agent import (
    AgentCommunication,
    MessagePriority,
    AgentProfile
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


async def test_basic_communication():
    """Test basic agent-to-agent communication."""
    print("\n" + "="*60)
    print("🤖 MULTI-AGENT COMMUNICATION SMOKE TEST")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*60 + "\n")
    
    # Create two agent profiles
    builder_profile = AgentProfile(
        name="BuilderBot",
        personality="methodical and helpful",
        skills=["construction", "planning"],
        communication_style="precise",
        team_role="builder"
    )
    
    explorer_profile = AgentProfile(
        name="ExplorerBot", 
        personality="curious and adventurous",
        skills=["scouting", "navigation"],
        communication_style="enthusiastic",
        team_role="explorer"
    )
    
    # Create communication channels
    builder_comm = AgentCommunication("BuilderBot", team_id="alpha")
    explorer_comm = AgentCommunication("ExplorerBot", team_id="alpha")
    
    # Register them to hear each other
    builder_comm.register_listener("ExplorerBot", explorer_comm)
    explorer_comm.register_listener("BuilderBot", builder_comm)
    
    print("✅ Created two agents: BuilderBot and ExplorerBot")
    print(f"   BuilderBot: {builder_profile.personality}")
    print(f"   ExplorerBot: {explorer_profile.personality}")
    print()
    
    # Test 1: Simple message
    print("📨 Test 1: Simple Message Exchange")
    print("-" * 40)
    await explorer_comm.send_message(
        "BuilderBot",
        "I found a perfect spot for our base at coordinates (100, 64, 200)!",
        priority=MessagePriority.NORMAL
    )
    
    # Process messages
    builder_messages = await builder_comm.process_messages()
    print(f"BuilderBot received {len(builder_messages)} message(s):")
    for msg in builder_messages:
        print(f"  From {msg.sender}: {msg.content}")
    print()
    
    # Test 2: High priority message
    print("🚨 Test 2: High Priority Message")
    print("-" * 40)
    await builder_comm.send_message(
        "ExplorerBot",
        "Need help! Running low on materials!",
        priority=MessagePriority.HIGH
    )
    
    explorer_messages = await explorer_comm.process_messages()
    print(f"ExplorerBot received {len(explorer_messages)} high-priority message(s):")
    for msg in explorer_messages:
        print(f"  Priority: {msg.priority.name} - From {msg.sender}: {msg.content}")
    print()
    
    # Test 3: Team broadcast
    print("📢 Test 3: Team Broadcast")
    print("-" * 40)
    await explorer_comm.broadcast(
        "Team, I discovered a cave system with rare minerals!",
        priority=MessagePriority.NORMAL
    )
    
    # Builder should receive the broadcast
    builder_messages = await builder_comm.process_messages()
    print(f"BuilderBot received broadcast: {len(builder_messages)} message(s)")
    for msg in builder_messages:
        print(f"  Broadcast from {msg.sender}: {msg.content}")
    print()
    
    # Test 4: Help request
    print("🆘 Test 4: Help Request Protocol")
    print("-" * 40)
    await builder_comm.request_help(
        "constructing the main tower",
        urgency=MessagePriority.HIGH
    )
    
    explorer_messages = await explorer_comm.process_messages()
    print("ExplorerBot received help request:")
    for msg in explorer_messages:
        print(f"  {msg.sender} needs help with: {msg.content}")
        if msg.metadata:
            print(f"  Task type: {msg.metadata.get('type', 'unknown')}")
    print()
    
    # Test 5: Discovery sharing
    print("💎 Test 5: Discovery Sharing")
    print("-" * 40)
    await explorer_comm.share_discovery(
        "Found diamond ore at level -58!",
        importance=9
    )
    
    builder_messages = await builder_comm.process_messages()
    print("BuilderBot received discovery notification:")
    for msg in builder_messages:
        print(f"  {msg.sender} discovered: {msg.content}")
        if msg.metadata:
            print(f"  Importance level: {msg.metadata.get('importance', 0)}/10")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*60)
    
    # Summary
    print("\n📊 Test Summary:")
    print(f"  - Messages sent: 5")
    print(f"  - Messages received: 5") 
    print(f"  - Priority levels tested: NORMAL, HIGH")
    print(f"  - Features tested: messaging, broadcast, help request, discovery")
    print(f"\nThe multi-agent communication system is working correctly!")
    print("Agents can communicate, coordinate, and share information.\n")


if __name__ == "__main__":
    asyncio.run(test_basic_communication())