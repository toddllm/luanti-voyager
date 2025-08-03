"""
Multi-agent demonstration for Luanti Voyager.

Shows how to create a team of agents with different roles,
inspired by Mindcraft's multi-agent approach.
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from luanti_voyager.agent import VoyagerAgent
from luanti_voyager.multi_agent import (
    AgentCommunication, 
    MultiAgentCoordinator,
    AgentProfile,
    DEFAULT_PROFILES
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiAgentVoyager(VoyagerAgent):
    """Extended VoyagerAgent with multi-agent capabilities."""
    
    def __init__(self, name: str, profile: AgentProfile, *args, **kwargs):
        super().__init__(name=name, *args, **kwargs)
        self.profile = profile
        self.communication = AgentCommunication(name)
        self.team_coordinator = None
        
        # Override system prompt with profile
        self.system_prompt = profile.get_system_prompt()
        
    async def process_team_messages(self):
        """Process messages from team members."""
        messages = await self.communication.process_messages()
        
        for message in messages:
            logger.info(f"{self.name} received: {message.content} from {message.sender}")
            
            # Handle different message types
            metadata = message.metadata
            if metadata.get("type") == "help_request":
                await self.respond_to_help_request(message)
            elif metadata.get("type") == "discovery":
                await self.process_discovery(message)
            elif metadata.get("type") == "coordination":
                await self.join_coordinated_action(message)
    
    async def respond_to_help_request(self, message):
        """Respond to a help request from a team member."""
        task = message.metadata.get("task", "unknown task")
        
        # Check if we can help based on our profile
        if self.profile.should_volunteer_for(task):
            await self.communication.send_message(
                message.sender,
                f"I can help with {task}! I have skills in {', '.join(self.profile.skills)}",
                priority=message.priority
            )
    
    async def process_discovery(self, message):
        """Process a discovery shared by team member."""
        discovery = message.content
        importance = message.metadata.get("importance", 5)
        
        if importance >= 7:
            # High importance - might change our current task
            logger.info(f"{self.name}: Important discovery noted - {discovery}")
            # In real implementation, might interrupt current task
    
    async def join_coordinated_action(self, message):
        """Join a coordinated team action."""
        action = message.metadata.get("action")
        role = message.metadata.get("role", "supporter")
        
        logger.info(f"{self.name} joining coordinated action: {action} as {role}")
        
        # Confirm readiness
        await self.communication.send_message(
            message.sender,
            f"Ready for {action}!",
            priority=message.priority
        )
    
    async def share_discovery(self, discovery: str, importance: int = 5):
        """Share a discovery with the team."""
        await self.communication.share_discovery(discovery, importance)
    
    async def request_help(self, task: str):
        """Request help from team members."""
        await self.communication.request_help(task)


async def create_castle_building_team():
    """
    Create a team of agents to build a castle together.
    
    Demonstrates Mindcraft-inspired multi-agent coordination.
    """
    # Create coordinator
    coordinator = MultiAgentCoordinator()
    
    # Create team
    castle_team = coordinator.create_team("Castle Builders")
    
    # Create agents with different profiles
    agents = []
    
    # Builder - leads construction
    builder = MultiAgentVoyager(
        name="MasterBuilder",
        profile=DEFAULT_PROFILES["builder"],
        llm_provider="ollama"  # Use local LLM for demo
    )
    castle_team.add_member(builder.name, builder.profile, builder.communication)
    agents.append(builder)
    
    # Explorer - scouts location
    explorer = MultiAgentVoyager(
        name="PathFinder",
        profile=DEFAULT_PROFILES["explorer"],
        llm_provider="ollama"
    )
    castle_team.add_member(explorer.name, explorer.profile, explorer.communication)
    agents.append(explorer)
    
    # Gatherer - collects resources
    gatherer = MultiAgentVoyager(
        name="ResourceHawk",
        profile=DEFAULT_PROFILES["gatherer"],
        llm_provider="ollama"
    )
    castle_team.add_member(gatherer.name, gatherer.profile, gatherer.communication)
    agents.append(gatherer)
    
    # Defender - protects during construction
    defender = MultiAgentVoyager(
        name="Guardian",
        profile=DEFAULT_PROFILES["defender"],
        llm_provider="ollama"
    )
    castle_team.add_member(defender.name, defender.profile, defender.communication)
    agents.append(defender)
    
    # Set coordinator for all agents
    for agent in agents:
        agent.team_coordinator = coordinator
    
    return coordinator, castle_team, agents


async def demonstrate_multi_agent_coordination():
    """Run a multi-agent coordination demonstration."""
    logger.info("=== Luanti Voyager Multi-Agent Demo ===")
    logger.info("Inspired by Mindcraft's multi-agent approach")
    logger.info("=====================================\n")
    
    # Create the team
    coordinator, team, agents = await create_castle_building_team()
    
    # Display team composition
    logger.info(f"Team '{team.name}' created with {len(agents)} agents:")
    for agent in agents:
        logger.info(f"  - {agent.name}: {agent.profile.team_role} "
                   f"(skills: {', '.join(agent.profile.skills)})")
    
    logger.info("\n--- Starting Castle Building Mission ---\n")
    
    # Simulate agent interactions
    
    # 1. Explorer scouts location
    logger.info("Phase 1: Location Scouting")
    explorer = agents[1]  # PathFinder
    await explorer.share_discovery(
        "Found flat area at coordinates (100, 65, 200) perfect for castle!",
        importance=8
    )
    await asyncio.sleep(1)
    
    # 2. Team responds to discovery
    logger.info("\nPhase 2: Team Response")
    for agent in agents:
        await agent.process_team_messages()
    await asyncio.sleep(1)
    
    # 3. Gatherer needs help
    logger.info("\nPhase 3: Resource Gathering")
    gatherer = agents[2]  # ResourceHawk
    await gatherer.request_help("gathering stone for castle walls")
    await asyncio.sleep(1)
    
    # 4. Agents volunteer to help
    for agent in agents:
        await agent.process_team_messages()
    await asyncio.sleep(1)
    
    # 5. Coordinate construction
    logger.info("\nPhase 4: Coordinated Construction")
    builder = agents[0]  # MasterBuilder
    await builder.communication.coordinate_action(
        "building castle foundation",
        participants=["ResourceHawk", "Guardian"]
    )
    await asyncio.sleep(1)
    
    # 6. Process coordination
    for agent in agents:
        await agent.process_team_messages()
    
    # 7. Start team task through coordinator
    logger.info("\nPhase 5: Team Task Assignment")
    await coordinator.coordinate_team_task(team, "Build a defensive castle")
    
    # Show final team status
    logger.info("\n--- Team Status ---")
    status = coordinator.get_team_status(team.team_id)
    logger.info(f"Team: {status['team_name']}")
    logger.info(f"Active tasks: {len(status['active_tasks'])}")
    for task in status['active_tasks']:
        logger.info(f"  - {task['description']} ({task['status']})")
        logger.info(f"    Assigned to: {', '.join(task['assigned_to'])}")
    
    logger.info("\n=== Demo Complete ===")
    logger.info("This demonstrates how Mindcraft's multi-agent concepts")
    logger.info("can enhance Luanti Voyager with team coordination!")


async def simple_communication_demo():
    """Simple demo of agent communication."""
    logger.info("=== Simple Communication Demo ===\n")
    
    # Create two agents
    alice = MultiAgentVoyager("Alice", DEFAULT_PROFILES["builder"], llm_provider="ollama")
    bob = MultiAgentVoyager("Bob", DEFAULT_PROFILES["explorer"], llm_provider="ollama")
    
    # Register them to hear each other
    alice.communication.register_listener("Bob", bob.communication)
    bob.communication.register_listener("Alice", alice.communication)
    
    # Alice sends a message
    await alice.communication.send_message("Bob", "Found some diamonds!")
    
    # Bob processes messages
    await bob.process_team_messages()
    
    # Bob responds
    await bob.communication.send_message("Alice", "Great find! Mark the location!")
    
    # Alice processes messages
    await alice.process_team_messages()
    
    logger.info("\n=== Communication Demo Complete ===")


if __name__ == "__main__":
    # Run the demonstrations
    
    print("\nWhich demo would you like to run?")
    print("1. Simple communication demo")
    print("2. Full castle-building team demo")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(simple_communication_demo())
    elif choice == "2":
        asyncio.run(demonstrate_multi_agent_coordination())
    else:
        print("Invalid choice. Running simple demo...")
        asyncio.run(simple_communication_demo())