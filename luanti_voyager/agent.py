"""
The main Voyager Agent - where the magic happens!
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
import random

logger = logging.getLogger(__name__)


@dataclass
class AgentState:
    """Current state of the agent."""
    pos: Dict[str, float]
    yaw: float
    pitch: float
    hp: int
    inventory: Dict[str, int]
    nearby_blocks: List[Dict[str, Any]]
    last_action: Optional[str] = None
    last_error: Optional[str] = None


class VoyagerAgent:
    """An autonomous agent that explores and learns in Luanti."""
    
    def __init__(self, name: str = "VoyagerBot", world_path: str = None):
        self.name = name
        self.world_path = Path(world_path) if world_path else Path.home() / ".minetest" / "worlds" / "world"
        self.command_file = self.world_path / "voyager_commands.txt"
        self.response_file = self.world_path / "voyager_responses.txt"
        
        # Agent state
        self.state: Optional[AgentState] = None
        self.running = False
        self.spawn_pos = {"x": 0, "y": 10, "z": 0}
        
        # Learning components (to be expanded)
        self.skills = {}  # Learned skills
        self.memory = []  # Short-term memory
        
        # LLM placeholder
        self.llm = None  # We'll add this later
        
    async def start(self):
        """Start the agent."""
        logger.info(f"Starting agent '{self.name}'...")
        
        # Clear response file
        if self.response_file.exists():
            self.response_file.unlink()
            
        # Spawn the bot in game
        await self._send_command(f"spawn {self.name} {self.spawn_pos['x']} {self.spawn_pos['y']} {self.spawn_pos['z']}")
        
        self.running = True
        
        # Start main loop
        await asyncio.gather(
            self._perception_loop(),
            self._action_loop(),
            self._learning_loop()
        )
        
    async def stop(self):
        """Stop the agent."""
        self.running = False
        logger.info("Agent stopped")
        
    async def _send_command(self, command: str) -> Optional[Dict]:
        """Send command to Luanti and get response."""
        # Write command
        with open(self.command_file, 'a') as f:
            f.write(command + '\n')
            
        # Wait for response (with timeout)
        start_time = time.time()
        while time.time() - start_time < 2.0:  # 2 second timeout
            if self.response_file.exists():
                try:
                    with open(self.response_file, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            # Get last response and clear file
                            response = json.loads(lines[-1])
                            self.response_file.unlink()
                            return response
                except Exception as e:
                    logger.error(f"Error reading response: {e}")
                    
            await asyncio.sleep(0.1)
            
        logger.warning(f"Command timeout: {command}")
        return None
        
    async def _update_state(self):
        """Update agent state from game."""
        response = await self._send_command(f"state {self.name}")
        if response and response.get("success") and "state" in response:
            state_data = response["state"]
            self.state = AgentState(
                pos=state_data["pos"],
                yaw=state_data.get("yaw", 0),
                pitch=state_data.get("pitch", 0),
                hp=state_data.get("hp", 20),
                inventory=state_data.get("inventory", {}),
                nearby_blocks=[
                    {"pos": node["pos"], "type": node["name"]}
                    for node in state_data.get("nearby_nodes", [])
                ]
            )
            
    async def _perception_loop(self):
        """Continuously update agent's perception of the world."""
        while self.running:
            await self._update_state()
            await asyncio.sleep(0.5)  # Update every 500ms
            
    async def _action_loop(self):
        """Main action decision loop."""
        await asyncio.sleep(2)  # Wait for initial spawn
        
        while self.running:
            if not self.state:
                await asyncio.sleep(0.1)
                continue
                
            # Simple exploration behavior for POC
            action = await self._decide_action()
            if action:
                await self._execute_action(action)
                
            await asyncio.sleep(1)  # One action per second
            
    async def _decide_action(self) -> Optional[Dict[str, Any]]:
        """Decide what action to take (simple version for POC)."""
        if not self.state:
            return None
            
        # Look for nearby wood blocks
        wood_blocks = [
            block for block in self.state.nearby_blocks
            if "wood" in block["type"] or "tree" in block["type"]
        ]
        
        if wood_blocks:
            # Try to dig wood
            target = wood_blocks[0]
            return {
                "type": "dig",
                "pos": target["pos"],
                "reason": "Found wood to collect"
            }
            
        # Otherwise, explore randomly
        directions = ["forward", "left", "right", "back"]
        return {
            "type": "move",
            "direction": random.choice(directions),
            "distance": random.uniform(1, 3),
            "reason": "Exploring"
        }
        
    async def _execute_action(self, action: Dict[str, Any]):
        """Execute an action."""
        logger.info(f"Executing: {action['type']} - {action.get('reason', 'No reason')}")
        
        if action["type"] == "move":
            response = await self._send_command(
                f"move {self.name} {action['direction']} {action['distance']}"
            )
            if response and not response.get("success"):
                logger.warning(f"Move failed: {response.get('error')}")
                # Try turning instead
                await self._send_command(f"turn {self.name} {random.uniform(-1.57, 1.57)}")
                
        elif action["type"] == "dig":
            pos = action["pos"]
            response = await self._send_command(
                f"dig {self.name} {pos['x']} {pos['y']} {pos['z']}"
            )
            if response and response.get("success"):
                logger.info("Successfully dug block!")
                
        elif action["type"] == "place":
            pos = action["pos"]
            item = action.get("item", "default:wood")
            await self._send_command(
                f"place {self.name} {pos['x']} {pos['y']} {pos['z']} {item}"
            )
            
    async def _learning_loop(self):
        """Learn from experiences (placeholder for now)."""
        while self.running:
            # This is where we'll add skill learning, LLM integration, etc.
            await asyncio.sleep(5)
            
            if self.state and self.state.inventory:
                logger.info(f"Inventory: {self.state.inventory}")
                
    def add_skill(self, name: str, code: str):
        """Add a learned skill."""
        self.skills[name] = code
        logger.info(f"Learned new skill: {name}")
        

# Simple test agent
async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create agent
    agent = VoyagerAgent(name="Pioneer")
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        await agent.stop()
        

if __name__ == "__main__":
    asyncio.run(main())