"""
Simple example of running a Luanti Voyager agent.

This shows the most basic usage - an agent that explores and gathers wood.
"""

import asyncio
import logging
from pathlib import Path

# Add parent directory to path so we can import luanti_voyager
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from luanti_voyager import VoyagerAgent


async def run_simple_agent():
    """Run a simple exploring agent."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s'
    )
    
    # Create agent
    agent = VoyagerAgent(
        name="Explorer",
        world_path="./worlds/test_world"  # Adjust this to your world path
    )
    
    print("🤖 Starting Explorer agent!")
    print("The agent will:")
    print("  - Spawn in the world")
    print("  - Look for wood/trees")
    print("  - Try to collect them")
    print("  - Explore randomly")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        print("\n👋 Stopping agent...")
        await agent.stop()
        
        # Show what the agent collected
        if agent.state and agent.state.inventory:
            print("\n📦 Agent inventory:")
            for item, count in agent.state.inventory.items():
                print(f"  - {item}: {count}")
        else:
            print("\n📦 Agent didn't collect anything yet")
            

if __name__ == "__main__":
    asyncio.run(run_simple_agent())