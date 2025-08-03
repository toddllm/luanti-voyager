"""
Agent communication system inspired by Mindcraft's approach.

Implements message passing, priority handling, and emergent communication
protocols between Luanti agents.
"""

import asyncio
import time
from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, List, Optional, Any
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class MessagePriority(IntEnum):
    """Message priority levels, inspired by Mindcraft's interrupt system."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3  # Interrupts current task
    CRITICAL = 4  # Emergency (e.g., "help I'm dying!")


@dataclass
class Message:
    """A message between agents."""
    sender: str
    recipient: str
    content: str
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: float = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}
    
    def __lt__(self, other):
        """For priority queue ordering - higher priority first."""
        return self.priority > other.priority


class AgentCommunication:
    """
    Handles inter-agent communication, inspired by Mindcraft's messaging system.
    
    Features:
    - Priority-based message queue
    - Natural language and structured protocols
    - Broadcast capabilities
    - Message history tracking
    """
    
    def __init__(self, agent_name: str, team_id: Optional[str] = None):
        self.agent_name = agent_name
        self.team_id = team_id
        self.message_queue = asyncio.PriorityQueue()
        self.message_history: List[Message] = []
        self.listeners = {}
        self.running = False
        
    async def send_message(self, recipient: str, content: str, 
                          priority: MessagePriority = MessagePriority.NORMAL,
                          metadata: Dict[str, Any] = None):
        """Send a message to another agent."""
        message = Message(
            sender=self.agent_name,
            recipient=recipient,
            content=content,
            priority=priority,
            metadata=metadata or {}
        )
        
        # In real implementation, this would use the game's chat or a dedicated channel
        logger.info(f"{self.agent_name} -> {recipient}: {content} (priority: {priority.name})")
        
        # For now, simulate by adding to recipient's queue if they're listening
        if recipient in self.listeners:
            await self.listeners[recipient].receive_message(message)
        
        self.message_history.append(message)
        
    async def broadcast(self, content: str, priority: MessagePriority = MessagePriority.NORMAL,
                       metadata: Dict[str, Any] = None):
        """Broadcast a message to all team members."""
        if not self.team_id:
            logger.warning(f"{self.agent_name} tried to broadcast without a team")
            return
            
        message = Message(
            sender=self.agent_name,
            recipient=f"team:{self.team_id}",
            content=content,
            priority=priority,
            metadata=metadata or {}
        )
        
        logger.info(f"{self.agent_name} broadcasts to team: {content}")
        
        # Simulate team broadcast
        for agent_name, agent_comm in self.listeners.items():
            if agent_comm.team_id == self.team_id and agent_name != self.agent_name:
                await agent_comm.receive_message(message)
        
        self.message_history.append(message)
    
    async def receive_message(self, message: Message):
        """Receive a message from another agent."""
        await self.message_queue.put(message)
        
        # Handle urgent messages immediately
        if message.priority >= MessagePriority.URGENT:
            logger.warning(f"URGENT message for {self.agent_name}: {message.content}")
            # In real implementation, this would interrupt current task
    
    async def process_messages(self) -> List[Message]:
        """Process pending messages, returning them in priority order."""
        messages = []
        
        while not self.message_queue.empty():
            try:
                message = self.message_queue.get_nowait()
                messages.append(message)
                
                # Log for debugging
                logger.debug(f"{self.agent_name} processing: {message.content} from {message.sender}")
                
            except:
                break
                
        return messages
    
    def register_listener(self, agent_name: str, agent_comm: 'AgentCommunication'):
        """Register another agent's communication interface (for simulation)."""
        self.listeners[agent_name] = agent_comm
    
    async def request_help(self, task: str, urgency: MessagePriority = MessagePriority.HIGH):
        """Request help from team members for a specific task."""
        help_request = {
            "type": "help_request",
            "task": task,
            "position": None,  # Would include agent position in real implementation
            "urgency": urgency.name
        }
        
        await self.broadcast(
            f"Need help with: {task}",
            priority=urgency,
            metadata=help_request
        )
    
    async def share_discovery(self, discovery: str, importance: int = 5):
        """Share an important discovery with the team."""
        discovery_data = {
            "type": "discovery",
            "importance": importance,
            "timestamp": time.time()
        }
        
        priority = MessagePriority.HIGH if importance >= 7 else MessagePriority.NORMAL
        
        await self.broadcast(
            f"Discovery: {discovery}",
            priority=priority,
            metadata=discovery_data
        )
    
    async def coordinate_action(self, action: str, participants: List[str]):
        """Coordinate a group action with specific agents."""
        coordination_data = {
            "type": "coordination",
            "action": action,
            "participants": participants,
            "coordinator": self.agent_name
        }
        
        for participant in participants:
            await self.send_message(
                participant,
                f"Coordinating action: {action}. Please confirm readiness.",
                priority=MessagePriority.HIGH,
                metadata=coordination_data
            )
    
    def get_conversation_history(self, with_agent: Optional[str] = None) -> List[Message]:
        """Get conversation history, optionally filtered by agent."""
        if with_agent:
            return [msg for msg in self.message_history 
                    if msg.sender == with_agent or msg.recipient == with_agent]
        return self.message_history.copy()


class EmergentProtocol:
    """
    Tracks and analyzes emerging communication patterns between agents.
    
    This allows agents to develop their own "language" or shortcuts
    over time, similar to Mindcraft's emergent behavior tracking.
    """
    
    def __init__(self):
        self.pattern_counts: Dict[str, int] = {}
        self.abbreviations: Dict[str, str] = {}
        self.common_sequences: List[List[str]] = []
        
    def analyze_message(self, message: Message):
        """Analyze a message for patterns."""
        words = message.content.lower().split()
        
        # Track word frequencies
        for word in words:
            self.pattern_counts[word] = self.pattern_counts.get(word, 0) + 1
        
        # Detect potential abbreviations
        if len(words) == 1 and len(words[0]) <= 3:
            # Might be an abbreviation emerging
            context = message.metadata.get('context', '')
            if context:
                self.abbreviations[words[0]] = context
    
    def get_common_patterns(self, threshold: int = 10) -> List[str]:
        """Get commonly used patterns/words."""
        return [word for word, count in self.pattern_counts.items() 
                if count >= threshold]
    
    def suggest_abbreviation(self, phrase: str) -> Optional[str]:
        """Suggest an abbreviation based on observed patterns."""
        words = phrase.lower().split()
        if len(words) > 1:
            # Use first letters
            abbrev = ''.join(word[0] for word in words)
            if len(abbrev) <= 3:
                return abbrev
        return None