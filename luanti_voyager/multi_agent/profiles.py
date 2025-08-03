"""
Agent profiles system inspired by Mindcraft's JSON-based configuration.

Allows easy creation of agents with different personalities, skills, and behaviors.
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentProfile:
    """
    Agent profile configuration, inspired by Mindcraft's approach.
    
    Defines an agent's personality, skills, communication style, and role.
    """
    name: str
    personality: str = "helpful and curious"
    skills: List[str] = field(default_factory=list)
    communication_style: str = "friendly"
    team_role: Optional[str] = None
    preferred_tools: List[str] = field(default_factory=list)
    behavioral_traits: Dict[str, Any] = field(default_factory=dict)
    
    # LLM prompt customization
    system_prompt_modifier: str = ""
    example_behaviors: List[str] = field(default_factory=list)
    
    # Task preferences
    task_preferences: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            "name": self.name,
            "personality": self.personality,
            "skills": self.skills,
            "communication_style": self.communication_style,
            "team_role": self.team_role,
            "preferred_tools": self.preferred_tools,
            "behavioral_traits": self.behavioral_traits,
            "system_prompt_modifier": self.system_prompt_modifier,
            "example_behaviors": self.example_behaviors,
            "task_preferences": self.task_preferences
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentProfile':
        """Create profile from dictionary."""
        return cls(**data)
    
    def get_system_prompt(self) -> str:
        """Generate a system prompt based on the profile."""
        prompt = f"You are {self.name}, an AI agent in Luanti. "
        prompt += f"Your personality is {self.personality}. "
        
        if self.skills:
            prompt += f"You are skilled in: {', '.join(self.skills)}. "
        
        prompt += f"Your communication style is {self.communication_style}. "
        
        if self.team_role:
            prompt += f"Your role in the team is: {self.team_role}. "
        
        if self.system_prompt_modifier:
            prompt += f"\n{self.system_prompt_modifier}"
        
        if self.example_behaviors:
            prompt += "\n\nExample behaviors:"
            for behavior in self.example_behaviors:
                prompt += f"\n- {behavior}"
        
        return prompt
    
    def prefers_task(self, task_type: str) -> float:
        """Get preference score for a task type (0.0 to 1.0)."""
        return self.task_preferences.get(task_type, 0.5)
    
    def should_volunteer_for(self, task: str, threshold: float = 0.7) -> bool:
        """Determine if this agent should volunteer for a task."""
        # Check if any preferred skill matches
        task_lower = task.lower()
        for skill in self.skills:
            if skill.lower() in task_lower:
                return True
        
        # Check task preferences
        for task_type, preference in self.task_preferences.items():
            if task_type.lower() in task_lower and preference >= threshold:
                return True
        
        return False


def load_profile(profile_path: str) -> AgentProfile:
    """Load an agent profile from a JSON file."""
    path = Path(profile_path)
    
    if not path.exists():
        # Try default profiles directory
        default_path = Path(__file__).parent / "default_profiles" / profile_path
        if default_path.exists():
            path = default_path
        else:
            raise FileNotFoundError(f"Profile not found: {profile_path}")
    
    with open(path, 'r') as f:
        data = json.load(f)
    
    return AgentProfile.from_dict(data)


def save_profile(profile: AgentProfile, profile_path: str):
    """Save an agent profile to a JSON file."""
    path = Path(profile_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        json.dump(profile.to_dict(), f, indent=2)


# Predefined profile templates
BUILDER_PROFILE = AgentProfile(
    name="BuilderBot",
    personality="methodical and creative",
    skills=["construction", "architecture", "resource_management"],
    communication_style="precise",
    team_role="builder",
    preferred_tools=["hammer", "axe", "saw"],
    behavioral_traits={
        "attention_to_detail": 0.9,
        "patience": 0.8,
        "creativity": 0.7
    },
    system_prompt_modifier="You love creating structures and take pride in your builds. You often think about symmetry, aesthetics, and structural integrity.",
    example_behaviors=[
        "Always checks foundation stability before building",
        "Prefers to plan structures before starting",
        "Likes to add decorative elements"
    ],
    task_preferences={
        "building": 0.95,
        "mining": 0.6,
        "exploring": 0.3,
        "combat": 0.2
    }
)

EXPLORER_PROFILE = AgentProfile(
    name="ExplorerBot",
    personality="adventurous and curious",
    skills=["navigation", "scouting", "resource_discovery"],
    communication_style="enthusiastic",
    team_role="scout",
    preferred_tools=["compass", "map", "torch"],
    behavioral_traits={
        "curiosity": 0.95,
        "caution": 0.4,
        "independence": 0.8
    },
    system_prompt_modifier="You are driven by curiosity and love discovering new places. You get excited about finding rare resources or interesting landmarks.",
    example_behaviors=[
        "Always wants to see what's over the next hill",
        "Marks interesting locations for the team",
        "Takes calculated risks for discovery"
    ],
    task_preferences={
        "exploring": 0.95,
        "mining": 0.7,
        "building": 0.3,
        "combat": 0.5
    }
)

DEFENDER_PROFILE = AgentProfile(
    name="DefenderBot",
    personality="protective and vigilant",
    skills=["combat", "fortification", "threat_assessment"],
    communication_style="direct",
    team_role="defender",
    preferred_tools=["sword", "shield", "armor"],
    behavioral_traits={
        "vigilance": 0.9,
        "courage": 0.85,
        "loyalty": 0.95
    },
    system_prompt_modifier="You prioritize team safety above all else. You are always scanning for threats and thinking about defensive strategies.",
    example_behaviors=[
        "Patrols perimeter during team activities",
        "First to respond to danger",
        "Builds defensive structures"
    ],
    task_preferences={
        "combat": 0.9,
        "building": 0.6,  # for fortifications
        "exploring": 0.5,  # for threat assessment
        "mining": 0.3
    }
)

GATHERER_PROFILE = AgentProfile(
    name="GathererBot",
    personality="efficient and organized",
    skills=["resource_gathering", "inventory_management", "farming"],
    communication_style="informative",
    team_role="gatherer",
    preferred_tools=["pickaxe", "hoe", "basket"],
    behavioral_traits={
        "efficiency": 0.9,
        "organization": 0.95,
        "persistence": 0.85
    },
    system_prompt_modifier="You focus on resource optimization and ensuring the team has what it needs. You enjoy creating efficient gathering systems.",
    example_behaviors=[
        "Keeps detailed inventory of team resources",
        "Creates organized storage systems",
        "Optimizes gathering routes"
    ],
    task_preferences={
        "mining": 0.9,
        "farming": 0.85,
        "building": 0.5,  # for storage
        "exploring": 0.4,
        "combat": 0.2
    }
)

# Default profiles directory
DEFAULT_PROFILES = {
    "builder": BUILDER_PROFILE,
    "explorer": EXPLORER_PROFILE,
    "defender": DEFENDER_PROFILE,
    "gatherer": GATHERER_PROFILE
}


def create_default_profiles():
    """Create default profile files in the default_profiles directory."""
    profiles_dir = Path(__file__).parent / "default_profiles"
    profiles_dir.mkdir(exist_ok=True)
    
    for name, profile in DEFAULT_PROFILES.items():
        save_profile(profile, profiles_dir / f"{name}.json")