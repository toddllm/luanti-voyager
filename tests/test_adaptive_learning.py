"""
Luanti Voyager - Adaptive Learning Tests
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

Tests for the adaptive learning system in Luanti Voyager.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np

from luanti_voyager.learning import (
    AdaptiveLearning,
    ErrorType,
    LearningConfig,
)


class TestAdaptiveLearning(unittest.TestCase):
    """Test cases for the AdaptiveLearning class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.agent_name = "test_agent"
        self.config = LearningConfig(
            learning_rate=0.1,
            exploration_rate=0.1,
            confidence_threshold=0.7,
            memory_decay=0.99,
        )
        self.learning = AdaptiveLearning(
            agent_name=self.agent_name,
            config=self.config,
        )
        # Override the memory file path for testing
        self.memory_file = Path(self.test_dir) / f"{self.agent_name}_learning.json"
        self.learning.memory_file = self.memory_file

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """Test that the learning system initializes correctly."""
        self.assertEqual(self.learning.agent_name, self.agent_name)
        self.assertEqual(self.learning.config.learning_rate, 0.1)
        self.assertEqual(self.learning.config.exploration_rate, 0.1)
        self.assertEqual(self.learning.config.confidence_threshold, 0.7)

    def test_analyze_failure(self):
        """Test failure analysis and learning."""
        action = {"type": "move", "direction": "forward"}
        world_before = {"player": {"position": (0, 0)}, "inventory": [], "nearby_entities": []}
        world_after = {"player": {"position": (0, 0)}, "inventory": [], "nearby_entities": []}
        
        # Analyze a path blocked failure
        analysis = self.learning.analyze_failure(
            action=action,
            world_before=world_before,
            world_after=world_after,
            error_type=ErrorType.PATH_BLOCKED,
        )
        
        # Check that the analysis contains expected fields
        self.assertIn("situation", analysis)
        self.assertIn("error_type", analysis)
        self.assertEqual(analysis["error_type"], "PATH_BLOCKED")
        self.assertIn("suggested_alternatives", analysis)
        
        # Check that the error was recorded in the state
        self.assertEqual(self.learning.state["learning_stats"]["error_counts"]["PATH_BLOCKED"], 1)
        self.assertEqual(self.learning.state["learning_stats"]["total_attempts"], 1)

    def test_track_success(self):
        """Test success tracking and learning."""
        action = {"type": "move", "direction": "forward"}
        world_before = {"player": {"position": (0, 0)}, "inventory": [], "nearby_entities": []}
        world_after = {"player": {"position": (0, 1)}, "inventory": [], "nearby_entities": []}
        
        # Track a successful action
        self.learning.track_success(
            action=action,
            world_before=world_before,
            world_after=world_after,
            efficiency=0.9,
        )
        
        # Check that the success was recorded in the state
        self.assertEqual(self.learning.state["learning_stats"]["successful_attempts"], 1)
        self.assertEqual(self.learning.state["learning_stats"]["total_attempts"], 1)
        
        # Check that the success pattern was recorded
        situation = "day:(0, 0)"
        self.assertIn(situation, self.learning.state["success_patterns"])

    def test_get_best_strategy(self):
        """Test strategy selection logic."""
        world_state = {
            "time_of_day": "day",
            "player": {"position": (0, 0)},
            "inventory": [],
            "nearby_entities": [],
        }
        
        # Get best strategy for the initial state
        strategy = self.learning.get_best_strategy(world_state)
        
        # Check that the strategy contains expected fields
        self.assertIn("strategy", strategy)
        self.assertIn("confidence", strategy)
        self.assertIn("situation", strategy)
        
        # The strategy should be one of the default strategies
        self.assertIn(strategy["strategy"], ["explore", "observe", "interact"])

    def test_persistence(self):
        """Test that learning state is properly saved and loaded."""
        # Record some learning
        action = {"type": "move", "direction": "forward"}
        world_before = {"player": {"position": (0, 0)}, "inventory": [], "nearby_entities": []}
        world_after = {"player": {"position": (0, 1)}, "inventory": [], "nearby_entities": []}
        
        self.learning.track_success(
            action=action,
            world_before=world_before,
            world_after=world_after,
            efficiency=0.9,
        )
        
        # Save the state
        self.learning.save_state()
        
        # Create a new instance that should load the saved state
        new_learning = AdaptiveLearning(agent_name=self.agent_name, config=self.config)
        new_learning.memory_file = self.memory_file
        
        # Check that the state was loaded correctly
        self.assertEqual(new_learning.state["learning_stats"]["successful_attempts"], 1)
        self.assertEqual(new_learning.state["learning_stats"]["total_attempts"], 1)

    def test_strategy_adaptation(self):
        """Test that the system adapts strategies based on success/failure."""
        world_state = {
            "time_of_day": "day",
            "player": {"position": (0, 0)},
            "inventory": [],
            "nearby_entities": [],
        }
        
        # Get initial strategy
        strategy1 = self.learning.get_best_strategy(world_state)
        
        # Simulate success with this strategy
        action = {"type": strategy1["strategy"]}
        self.learning.track_success(
            action=action,
            world_before=world_state,
            world_after=world_state,
            efficiency=1.0,
        )
        
        # Get strategy again - should have higher confidence in the successful strategy
        strategy2 = self.learning.get_best_strategy(world_state)
        
        # The same strategy should now have higher confidence
        if strategy1["strategy"] == strategy2["strategy"]:
            self.assertGreaterEqual(strategy2["confidence"], strategy1["confidence"])


class TestLearningConfig(unittest.TestCase):
    """Test cases for the LearningConfig class."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        config = LearningConfig()
        self.assertEqual(config.learning_rate, 0.1)
        self.assertEqual(config.exploration_rate, 0.2)
        self.assertEqual(config.confidence_threshold, 0.7)
        self.assertEqual(config.max_strategies_per_situation, 5)
        self.assertEqual(config.memory_decay, 0.99)

    def test_custom_values(self):
        """Test that custom values are set correctly."""
        config = LearningConfig(
            learning_rate=0.2,
            exploration_rate=0.3,
            confidence_threshold=0.8,
            max_strategies_per_situation=10,
            memory_decay=0.95,
        )
        self.assertEqual(config.learning_rate, 0.2)
        self.assertEqual(config.exploration_rate, 0.3)
        self.assertEqual(config.confidence_threshold, 0.8)
        self.assertEqual(config.max_strategies_per_situation, 10)
        self.assertEqual(config.memory_decay, 0.95)


class TestErrorType(unittest.TestCase):
    """Test cases for the ErrorType enum."""

    def test_error_types(self):
        """Test that all error types are defined."""
        self.assertEqual(ErrorType.RESOURCE_UNAVAILABLE.name, "RESOURCE_UNAVAILABLE")
        self.assertEqual(ErrorType.INVALID_ACTION.name, "INVALID_ACTION")
        self.assertEqual(ErrorType.PATH_BLOCKED.name, "PATH_BLOCKED")
        self.assertEqual(ErrorType.TARGET_NOT_FOUND.name, "TARGET_NOT_FOUND")
        self.assertEqual(ErrorType.TOOL_FAILURE.name, "TOOL_FAILURE")
        self.assertEqual(ErrorType.TIMEOUT.name, "TIMEOUT")
        self.assertEqual(ErrorType.OTHER.name, "OTHER")


if __name__ == "__main__":
    unittest.main()
