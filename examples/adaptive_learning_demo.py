"""
Luanti Voyager - Adaptive Learning Demo
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

Demo of the AdaptiveLearning system for Luanti Voyager agents.
Shows how agents can learn from failures and optimize their strategies over time.
"""

import random
import time
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path to import luanti_voyager
import sys
sys.path.append(str(Path(__file__).parent.parent))

from luanti_voyager.learning import AdaptiveLearning, ErrorType, LearningConfig

class MockWorld:
    """A simple mock world for demonstration purposes."""
    
    def __init__(self):
        self.time_of_day = 'day'
        self.agent_position = (0, 0)
        self.entities = []
        self.inventory = []
        self.obstacles = [(1, 0), (0, 1), (1, 1)]  # Block some positions
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current world state."""
        return {
            'time_of_day': self.time_of_day,
            'player': {
                'position': self.agent_position,
                'inventory': self.inventory
            },
            'nearby_entities': self.entities.copy(),
        }
    
    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action and return the result."""
        action_type = action.get('type', '')
        result = {'success': False, 'message': 'Unknown action'}
        
        if action_type == 'move':
            direction = action.get('direction', 'forward')
            new_pos = list(self.agent_position)
            
            if direction == 'forward':
                new_pos[1] += 1
            elif direction == 'backward':
                new_pos[1] -= 1
            elif direction == 'left':
                new_pos[0] -= 1
            elif direction == 'right':
                new_pos[0] += 1
            
            new_pos = tuple(new_pos)
            if new_pos in self.obstacles:
                result.update({
                    'success': False,
                    'message': f'Path blocked at {new_pos}',
                    'error_type': ErrorType.PATH_BLOCKED
                })
            else:
                self.agent_position = new_pos
                result.update({
                    'success': True,
                    'message': f'Moved {direction} to {new_pos}'
                })
        
        elif action_type == 'interact':
            target = action.get('target', '')
            if target:
                result.update({
                    'success': random.random() > 0.3,  # 70% success rate
                    'message': f'Interacted with {target}'
                })
        
        elif action_type == 'search':
            # Simulate finding items sometimes
            if random.random() > 0.7:  # 30% chance to find something
                item = random.choice(['apple', 'stick', 'stone', 'flower'])
                self.inventory.append(item)
                result.update({
                    'success': True,
                    'message': f'Found {item}'
                })
            else:
                result.update({
                    'success': False,
                    'message': 'Found nothing',
                    'error_type': ErrorType.TARGET_NOT_FOUND
                })
        
        return result

def run_demo():
    """Run a demonstration of the adaptive learning system."""
    print("=== Luanti Voyager Adaptive Learning Demo ===\n")
    
    # Initialize the learning system with custom config
    config = LearningConfig(
        learning_rate=0.2,
        exploration_rate=0.3,  # Higher exploration for demo
        confidence_threshold=0.6
    )
    learning = AdaptiveLearning("demo_agent", config)
    world = MockWorld()
    
    # Define some possible actions
    possible_actions = [
        {'type': 'move', 'direction': 'forward'},
        {'type': 'move', 'direction': 'left'},
        {'type': 'move', 'direction': 'right'},
        {'type': 'search'},
        {'type': 'interact', 'target': 'object'}
    ]
    
    # Run the simulation
    num_episodes = 10
    steps_per_episode = 5
    
    for episode in range(1, num_episodes + 1):
        print(f"\n=== Episode {episode} ===")
        print(f"Agent position: {world.agent_position}")
        
        for step in range(steps_per_episode):
            # Get current world state
            state = world.get_state()
            
            # Get best strategy based on current state
            strategy = learning.get_best_strategy(state)
            
            # Choose an action based on the strategy
            if strategy['strategy'] == 'explore':
                action = random.choice(possible_actions)
                action['reason'] = 'Exploring randomly'
            elif strategy['strategy'] == 'observe':
                action = {'type': 'search'}
                action['reason'] = 'Observing surroundings'
            else:  # 'interact' or other strategies
                action = random.choice([a for a in possible_actions if a['type'] in ['interact', 'search']])
                action['reason'] = f'Interacting using {strategy["strategy"]} strategy'
            
            print(f"\nStep {step + 1}: Trying {action}")
            
            # Execute the action
            result = world.execute_action(action)
            print(f"Result: {result['message']}")
            
            # Learn from the result
            if result.get('success', False):
                learning.track_success(
                    action=action,
                    world_before=state,
                    world_after=world.get_state(),
                    efficiency=random.uniform(0.5, 1.0)  # Random efficiency for demo
                )
                print("✅ Learned from success")
            else:
                error_type = result.get('error_type', ErrorType.OTHER)
                analysis = learning.analyze_failure(
                    action=action,
                    world_before=state,
                    world_after=world.get_state(),
                    error_type=error_type
                )
                print(f"❌ Learned from failure (error: {error_type.name})")
                if analysis['suggested_alternatives']:
                    print(f"Suggested alternatives: {analysis['suggested_alternatives']}")
            
            # Small delay for readability
            time.sleep(0.5)
    
    # Print final learning metrics
    print("\n=== Learning Metrics ===")
    metrics = learning.get_learning_metrics()
    print(f"Success rate: {metrics['success_rate']:.1%}")
    print(f"Total attempts: {metrics['total_attempts']}")
    print(f"Successful attempts: {metrics['successful_attempts']}")
    print("\nError counts:")
    for error, count in metrics['error_counts'].items():
        if count > 0:
            print(f"- {error}: {count}")

if __name__ == "__main__":
    run_demo()
