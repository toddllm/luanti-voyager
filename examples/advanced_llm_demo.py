#!/usr/bin/env python3
"""
Demonstration of advanced LLM features for Luanti Voyager.

This example shows:
- Multi-step reasoning with chain-of-thought
- Goal decomposition 
- Learning from failures
- Context-aware decision making
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from luanti_voyager.agent import VoyagerAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def demo_advanced_features():
    """Demonstrate advanced LLM capabilities."""
    
    # Create agent with Ollama (or change to "openai"/"anthropic" if you have API keys)
    agent = VoyagerAgent(
        name="AdvancedBot",
        llm_provider="ollama",  # Change this based on your setup
        world_path="test-server/test_world"  # Adjust path as needed
    )
    
    try:
        logger.info("🚀 Starting Advanced LLM Demo")
        logger.info("=" * 60)
        
        # Start the agent
        agent_task = asyncio.create_task(agent.start())
        
        # Wait a bit for initialization
        await asyncio.sleep(3)
        
        # Demo 1: Set a high-level goal
        logger.info("\n📌 Demo 1: Goal Decomposition")
        logger.info("-" * 40)
        await agent.set_goal("Build a shelter before nightfall")
        await asyncio.sleep(2)
        
        # Demo 2: Create a specific plan
        logger.info("\n📌 Demo 2: Multi-Step Planning")
        logger.info("-" * 40)
        await agent.create_plan("Gather wood from nearby trees")
        await asyncio.sleep(2)
        
        # Demo 3: Check goal progress
        logger.info("\n📌 Demo 3: Goal Progress Tracking")
        logger.info("-" * 40)
        progress = await agent.get_goal_progress()
        logger.info(f"Current progress:\n{progress}")
        
        # Let the agent run with advanced features for a while
        logger.info("\n🤖 Agent running with advanced reasoning...")
        logger.info("Watch for:")
        logger.info("- Chain-of-thought reasoning in decisions")
        logger.info("- Reflection when actions fail")
        logger.info("- Context-aware choices based on history")
        logger.info("- Progress on goals and plans")
        
        # Run for 30 seconds to see advanced features in action
        await asyncio.sleep(30)
        
        # Final progress check
        logger.info("\n📊 Final Progress Report")
        logger.info("-" * 40)
        final_progress = await agent.get_goal_progress()
        logger.info(f"Final progress:\n{final_progress}")
        
    except KeyboardInterrupt:
        logger.info("\n⏹️ Demo interrupted by user")
    finally:
        await agent.stop()
        logger.info("\n✅ Demo completed!")


async def main():
    """Run the demonstration."""
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║        Advanced LLM Features Demo for Luanti Voyager   ║
    ╠═══════════════════════════════════════════════════════╣
    ║ This demo showcases:                                   ║
    ║ • Multi-step reasoning and planning                    ║
    ║ • Goal decomposition into sub-tasks                    ║
    ║ • Learning from failures                               ║
    ║ • Context-aware decision making                        ║
    ╚═══════════════════════════════════════════════════════╝
    
    Prerequisites:
    1. Luanti server running with voyager_bot mod
    2. Ollama installed and running (or OpenAI/Anthropic API key)
    3. Python packages installed (pip install -r requirements.txt)
    
    Press Ctrl+C to stop the demo at any time.
    """)
    
    input("Press Enter to start the demo...")
    
    await demo_advanced_features()


if __name__ == "__main__":
    asyncio.run(main())