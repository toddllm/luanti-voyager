"""
Luanti Voyager - Adaptive Learning System
Copyright (C) 2025 Luanti Voyager Team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Adaptive learning system for Luanti Voyager agents.
Implements mechanisms for learning from experience, adapting behavior,
and optimizing performance over time.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Categories of errors that can occur during agent operation."""

    RESOURCE_UNAVAILABLE = auto()
    INVALID_ACTION = auto()
    PATH_BLOCKED = auto()
    TARGET_NOT_FOUND = auto()
    TOOL_FAILURE = auto()
    TIMEOUT = auto()
    OTHER = auto()


@dataclass
class LearningConfig:
    """Configuration parameters for the learning system."""

    learning_rate: float = 0.1  # How quickly to update strategy weights
    exploration_rate: float = 0.2  # Probability of trying a random strategy
    confidence_threshold: float = 0.7  # Minimum confidence to use learned behavior
    max_strategies_per_situation: int = 5  # Maximum strategies to maintain per situation
    memory_decay: float = 0.99  # How quickly to forget old experiences


class AdaptiveLearning:
    """
    Implements adaptive learning mechanisms for agents to improve from experience.
    """

    def __init__(self, agent_name: str, config: Optional[LearningConfig] = None):
        self.agent_name = agent_name
        self.config = config or LearningConfig()
        self.memory_file = Path(f"agent_memory/{agent_name}_learning.json")
        self.memory_file.parent.mkdir(exist_ok=True)

        # Load or initialize learning state
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load learning state from disk."""
        default_state = {
            "strategy_weights": {},
            "error_patterns": {},
            "success_patterns": {},
            "learning_stats": {
                "total_attempts": 0,
                "successful_attempts": 0,
                "error_counts": {e.name: 0 for e in ErrorType},
                "last_updated": datetime.now().isoformat(),
            },
        }

        try:
            if self.memory_file.exists():
                with open(self.memory_file, "r") as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key, value in default_state.items():
                        if key not in loaded:
                            loaded[key] = value
                    return loaded
        except Exception as e:
            logger.error(f"Failed to load learning state: {e}")

        return default_state

    def save_state(self):
        """Save learning state to disk."""
        try:
            with open(self.memory_file, "w") as f:
                json.dump(self.state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save learning state: {e}")

    def analyze_failure(
        self,
        action: Dict[str, Any],
        world_before: Dict[str, Any],
        world_after: Dict[str, Any],
        error_type: ErrorType,
    ) -> Dict[str, Any]:
        """
        Analyze a failed action and update learning state.

        Args:
            action: The action that was attempted
            world_before: World state before the action
            world_after: World state after the action
            error_type: Type of error that occurred

        Returns:
            Analysis of the failure and suggested improvements
        """
        # Update error statistics
        self.state["learning_stats"]["total_attempts"] += 1
        self.state["learning_stats"]["error_counts"][error_type.name] += 1

        # Extract relevant context
        context = self._extract_context(world_before, action)
        situation = self._identify_situation(context)

        # Update error patterns
        error_key = f"{situation}:{error_type.name}"
        self.state["error_patterns"][error_key] = (
            self.state["error_patterns"].get(error_key, 0) + 1
        )

        # Generate analysis
        analysis = {
            "situation": situation,
            "error_type": error_type.name,
            "context": context,
            "suggested_alternatives": self._generate_alternatives(action, error_type),
            "timestamp": datetime.now().isoformat(),
        }

        # Update strategy weights to avoid this failure
        self._update_strategy_weights(situation, success=False)

        self.save_state()
        return analysis

    def track_success(
        self,
        action: Dict[str, Any],
        world_before: Dict[str, Any],
        world_after: Dict[str, Any],
        efficiency: float = 1.0,
    ):
        """
        Track a successful action and update learning state.

        Args:
            action: The action that succeeded
            world_before: World state before the action
            world_after: World state after the action
            efficiency: Measure of how efficient the action was (0.0-1.0)
        """
        # Update success statistics
        self.state["learning_stats"]["total_attempts"] += 1
        self.state["learning_stats"]["successful_attempts"] += 1

        # Extract relevant context
        context = self._extract_context(world_before, action)
        situation = self._identify_situation(context)

        # Update success patterns
        success_key = f"{situation}:success"
        self.state["success_patterns"][success_key] = (
            self.state["success_patterns"].get(success_key, 0) + 1
        )

        # Update strategy weights to reinforce this success
        self._update_strategy_weights(situation, success=True, efficiency=efficiency)

        self.save_state()

    def get_best_strategy(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the best strategy for the current situation.

        Args:
            world_state: Current world state

        Returns:
            Dictionary containing the recommended strategy and confidence
        """
        context = self._extract_context(world_state, None)
        situation = self._identify_situation(context)

        # Get all strategies for this situation
        strategies = self._get_available_strategies(situation)

        if not strategies:
            return {
                "strategy": "explore",
                "confidence": 0.0,
                "situation": situation,
            }

        # Sort strategies by weight (descending)
        sorted_strategies = sorted(
            strategies.items(),
            key=lambda x: x[1]["weight"],
            reverse=True,
        )

        # Get best strategy
        best_strategy, stats = sorted_strategies[0]
        confidence = self._calculate_confidence(stats)

        # Sometimes explore randomly
        if np.random.random() < self.config.exploration_rate:
            best_strategy = np.random.choice(list(strategies.keys()))
            confidence = 0.5  # Lower confidence for exploration

        return {
            "strategy": best_strategy,
            "confidence": confidence,
            "situation": situation,
        }

    def _extract_context(
        self, world_state: Dict[str, Any], action: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract relevant context from world state and action."""
        # This is a simplified version - should be customized based on actual state structure
        context = {
            "time_of_day": world_state.get("time_of_day", "unknown"),
            "location": world_state.get("player", {}).get("position", "unknown"),
            "inventory": world_state.get("inventory", []),
            "nearby_entities": world_state.get("nearby_entities", []),
            "action_type": action.get("type", "none") if action else "none",
        }
        return context

    def _identify_situation(self, context: Dict[str, Any]) -> str:
        """Identify the current situation from context."""
        time_of_day = str(context.get("time_of_day", "unknown"))
        location = str(context.get("location", "unknown"))

        # Handle nearby entities
        nearby = []
        for entity in context.get("nearby_entities", []):
            if isinstance(entity, dict):
                nearby.append(entity.get("type", "unknown"))
            else:
                nearby.append(str(entity))

        nearby_str = "with_" + "_".join(sorted(nearby)) if nearby else ""

        # Join non-empty parts
        parts = [time_of_day, location]
        if nearby_str:
            parts.append(nearby_str)

        return ":".join(parts)

    def _get_available_strategies(self, situation: str) -> Dict[str, Dict[str, float]]:
        """Get available strategies for a situation with their weights."""
        if situation not in self.state["strategy_weights"]:
            # Initialize with default strategies if none exist
            self.state["strategy_weights"][situation] = {
                "explore": {"weight": 1.0, "successes": 0, "attempts": 0},
                "observe": {"weight": 1.0, "successes": 0, "attempts": 0},
                "interact": {"weight": 1.0, "successes": 0, "attempts": 0},
            }
        return self.state["strategy_weights"][situation]

    def _update_strategy_weights(
        self, situation: str, success: bool, efficiency: float = 1.0
    ):
        """Update strategy weights based on success/failure."""
        if situation not in self.state["strategy_weights"]:
            return

        for strategy, stats in self.state["strategy_weights"][situation].items():
            # Apply memory decay
            stats["weight"] *= self.config.memory_decay

            # Update statistics
            stats["attempts"] += 1
            if success:
                stats["successes"] += 1
                # Increase weight more for more efficient strategies
                stats["weight"] += self.config.learning_rate * efficiency
            else:
                # Decrease weight for failures
                stats["weight"] *= 0.9  # 10% reduction for failure

            # Ensure weight stays in reasonable bounds
            stats["weight"] = max(0.1, min(10.0, stats["weight"]))

    def _calculate_confidence(self, stats: Dict[str, float]) -> float:
        """Calculate confidence in a strategy based on its statistics."""
        if stats["attempts"] == 0:
            return 0.0

        success_rate = stats["successes"] / stats["attempts"]
        # Confidence increases with more evidence
        evidence_factor = 1 - np.exp(-stats["attempts"] / 10)
        return success_rate * evidence_factor

    def _generate_alternatives(
        self, action: Dict[str, Any], error_type: ErrorType
    ) -> List[Dict[str, Any]]:
        """Generate alternative actions to try when one fails."""
        alternatives = []
        action_type = action.get("type", "")

        if error_type == ErrorType.PATH_BLOCKED:
            alternatives.extend(
                [
                    {"type": "move", "direction": "left", "reason": "Path blocked, trying left"},
                    {"type": "move", "direction": "right", "reason": "Path blocked, trying right"},
                    {"type": "jump", "reason": "Attempting to jump over obstacle"},
                ]
            )
        elif error_type == ErrorType.TARGET_NOT_FOUND:
            alternatives.extend(
                [
                    {"type": "search", "radius": 5, "reason": "Searching nearby area"},
                    {
                        "type": "ask",
                        "question": "Where can I find this?",
                        "reason": "Asking for help",
                    },
                ]
            )

        # Add a generic retry with different parameters
        if action_type:
            alt_action = action.copy()
            alt_action["retry_attempt"] = alt_action.get("retry_attempt", 0) + 1
            alternatives.append(
                {
                    **alt_action,
                    "reason": f"Retrying {action_type} with attempt #{alt_action['retry_attempt']}",
                }
            )

        return alternatives

    def get_learning_metrics(self) -> Dict[str, Any]:
        """Get learning performance metrics."""
        stats = self.state["learning_stats"]
        total = stats["total_attempts"]
        success = stats["successful_attempts"]

        return {
            "success_rate": success / total if total > 0 else 0.0,
            "total_attempts": total,
            "successful_attempts": success,
            "error_counts": stats["error_counts"],
            "strategy_diversity": len(self.state["strategy_weights"]),
            "last_updated": stats["last_updated"],
        }
