"""
Multi-agent support for Luanti Voyager, inspired by Mindcraft's approach.

This module implements multi-agent coordination, communication, and 
profile-based behaviors adapted from the Minecraft agent framework Mindcraft.
"""

from .communication import AgentCommunication, Message, MessagePriority
from .coordinator import MultiAgentCoordinator, Team
from .profiles import AgentProfile, load_profile

__all__ = [
    'AgentCommunication',
    'Message', 
    'MessagePriority',
    'MultiAgentCoordinator',
    'Team',
    'AgentProfile',
    'load_profile'
]