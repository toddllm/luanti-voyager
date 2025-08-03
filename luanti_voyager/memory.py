"""
Simple skill memory system for Luanti Voyager agents.
Stores and retrieves learned behaviors and successful strategies.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SkillMemory:
    """Simple file-based skill memory for agents."""
    
    def __init__(self, agent_name: str = "VoyagerBot", memory_dir: str = "agent_memory"):
        self.agent_name = agent_name
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        # Memory files
        self.skills_file = self.memory_dir / f"{agent_name}_skills.json"
        self.locations_file = self.memory_dir / f"{agent_name}_locations.json"
        self.strategies_file = self.memory_dir / f"{agent_name}_strategies.json"
        
        # Load existing memory
        self.skills = self._load_json(self.skills_file, {})
        self.locations = self._load_json(self.locations_file, {})
        self.strategies = self._load_json(self.strategies_file, {})
        
        logger.info(f"🧠 Memory initialized for {agent_name}: {len(self.skills)} skills, {len(self.locations)} locations, {len(self.strategies)} strategies")
    
    def _load_json(self, file_path: Path, default: Any) -> Any:
        """Load JSON file with error handling."""
        try:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load {file_path}: {e}")
        return default
    
    def _save_json(self, file_path: Path, data: Any):
        """Save JSON file with error handling."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save {file_path}: {e}")
    
    def remember_skill(self, skill_name: str, action_sequence: List[Dict[str, Any]], success: bool = True):
        """Remember a skill (sequence of actions that achieved a goal)."""
        skill_data = {
            "name": skill_name,
            "actions": action_sequence,
            "success": success,
            "learned_at": datetime.now().isoformat(),
            "usage_count": self.skills.get(skill_name, {}).get("usage_count", 0)
        }
        
        self.skills[skill_name] = skill_data
        self._save_json(self.skills_file, self.skills)
        logger.info(f"💡 Learned skill: {skill_name} ({'successful' if success else 'failed'})")
    
    def remember_location(self, location_name: str, pos: Dict[str, float], description: str = ""):
        """Remember an interesting location."""
        location_data = {
            "name": location_name,
            "position": pos,
            "description": description,
            "discovered_at": datetime.now().isoformat(),
            "visit_count": self.locations.get(location_name, {}).get("visit_count", 0) + 1
        }
        
        self.locations[location_name] = location_data
        self._save_json(self.locations_file, self.locations)
        logger.info(f"📍 Remembered location: {location_name} at {pos}")
    
    def remember_strategy(self, situation: str, strategy: str, success: bool = True):
        """Remember a successful strategy for a given situation."""
        if situation not in self.strategies:
            self.strategies[situation] = []
        
        strategy_data = {
            "strategy": strategy,
            "success": success,
            "used_at": datetime.now().isoformat()
        }
        
        self.strategies[situation].append(strategy_data)
        self._save_json(self.strategies_file, self.strategies)
        logger.info(f"🎯 Remembered strategy for '{situation}': {strategy}")
    
    def get_skill(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a learned skill."""
        return self.skills.get(skill_name)
    
    def get_best_strategies(self, situation: str, limit: int = 3) -> List[str]:
        """Get the best strategies for a situation (most recent successful ones)."""
        if situation not in self.strategies:
            return []
        
        # Filter successful strategies and sort by recency
        successful = [s for s in self.strategies[situation] if s.get("success", True)]
        successful.sort(key=lambda x: x.get("used_at", ""), reverse=True)
        
        return [s["strategy"] for s in successful[:limit]]
    
    def get_nearby_locations(self, current_pos: Dict[str, float], radius: float = 100) -> List[Dict[str, Any]]:
        """Get remembered locations near current position."""
        nearby = []
        for name, location in self.locations.items():
            pos = location["position"]
            distance = ((pos["x"] - current_pos["x"])**2 + 
                       (pos["z"] - current_pos["z"])**2)**0.5
            
            if distance <= radius:
                location_copy = location.copy()
                location_copy["distance"] = distance
                nearby.append(location_copy)
        
        return sorted(nearby, key=lambda x: x["distance"])
    
    def get_memory_summary(self) -> str:
        """Get a summary of what the agent remembers."""
        return f"""🧠 Memory Summary for {self.agent_name}:
- 💡 Skills: {len(self.skills)} learned
- 📍 Locations: {len(self.locations)} discovered  
- 🎯 Strategies: {sum(len(strats) for strats in self.strategies.values())} recorded
- 📁 Memory saved in: {self.memory_dir}"""
    
    def suggest_action_from_memory(self, current_state: Dict[str, Any]) -> Optional[str]:
        """Suggest an action based on remembered experiences."""
        pos = current_state.get("agent_position", {})
        hp = current_state.get("hp", 20)
        
        # Health-based suggestions
        if hp <= 5:
            strategies = self.get_best_strategies("low_health")
            if strategies:
                return f"💡 Memory suggests: {strategies[0]}"
        
        # Location-based suggestions
        nearby = self.get_nearby_locations(pos, radius=50)
        if nearby:
            closest = nearby[0]
            return f"📍 Memory: {closest['name']} nearby ({closest['distance']:.1f}m) - {closest['description']}"
        
        # General exploration strategies
        void_strategies = self.get_best_strategies("void_exploration")
        if void_strategies:
            return f"🎯 Memory suggests: {void_strategies[0]}"
        
        return None