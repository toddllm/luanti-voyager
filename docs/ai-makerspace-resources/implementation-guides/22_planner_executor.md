# Planner Executor - Luanti Implementation Guide

# Implementation Guide: Integrating Planner Executor into Luanti Voyager

## Executive Summary

The Planner-Executor architecture separates high-level planning from low-level execution in game AI agents, leading to more robust and adaptive behaviors. This separation allows for complex goal achievement, multi-step crafting sequences, coordinated team actions, and dynamic replanning when obstacles are encountered. For players, this means more engaging and intelligent NPC interactions, enhancing the overall gaming experience. Performance-wise, while there is an initial overhead in setting up abstract plans and monitoring execution, the long-term benefits of reduced computational complexity during runtime ensure efficient gameplay.

## Core Architecture

### System Design with Clear Components

1. **LuantiPlanner**: Handles high-level planning by creating abstract tasks based on game goals.
2. **LuantiExecutor**: Executes concrete actions derived from planner's tasks.
3. **TaskMonitor**: Monitors execution progress and triggers replanning if necessary.

### Data Flow Diagrams (Described in Text)

1. **Planning Phase**:
   - Game environment sends high-level objectives to `LuantiPlanner`.
   - `LuantiPlanner` decomposes these objectives into a sequence of abstract tasks.
   
2. **Execution Phase**:
   - Abstract tasks are handed over to `LuantiExecutor`.
   - `LuantiExecutor` translates abstract tasks into concrete actions and executes them in the game world.
   
3. **Monitoring Phase**:
   - `TaskMonitor` tracks execution progress.
   - If any task fails or conditions change, `TaskMonitor` triggers replanning by sending new objectives to `LuantiPlanner`.

### Integration Points with Game Engine

- **Game Interface**: Abstracts interactions between the game engine and Planner/Executor components.
- **World State API**: Provides real-time data about the game world (e.g., resource availability, obstacles).
- **Event System**: Handles asynchronous events like task completion or failure.

## Detailed Implementation

### Complete, Runnable Code Examples

#### LuantiPlanner
```python
class LuantiPlanner:
    """High-level planning for game agents"""
    
    def __init__(self):
        self.tasks = []

    def plan(self, objectives: List[Dict]) -> List[GameTask]:
        """Create abstract tasks based on high-level objectives"""
        planned_tasks = []
        
        for obj in objectives:
            if obj['goal'] == "build":
                task = GameTask(
                    task_id=str(len(self.tasks) + 1),
                    description=f"Build {obj['target_type']} at {obj['location']}",
                    task_type="build",
                    priority=obj.get('priority', 50),
                    prerequisites=["gather_materials"],
                    required_items=obj['required_items'],
                    target_location=obj['location']
                )
            elif obj['goal'] == "explore":
                task = GameTask(
                    task_id=str(len(self.tasks) + 1),
                    description=f"Explore area around {obj['location']}",
                    task_type="explore",
                    priority=obj.get('priority', 30),
                    prerequisites=[],
                    target_location=obj['location']
                )
            planned_tasks.append(task)
        return planned_tasks
```

#### LuantiExecutor
```python
class LuantiExecutor:
    """Low-level task execution for game agents"""
    
    def __init__(self, agent_controller, world_interface):
        self.agent = agent_controller
        self.world = world_interface
        self.current_task = None
        self.execution_history = []

    async def execute_task(self, task: GameTask) -> TaskResult:
        """Execute a single task with monitoring"""
        self.current_task = task
        start_time = datetime.now()

        try:
            if not self._check_prerequisites(task):
                return TaskResult(task.task_id, False, None, "Prerequisites not met")

            result_data = await self._execute_action(task)

            duration = (datetime.now() - start_time).total_seconds()
            task_result = TaskResult(
                task_id=task.task_id,
                success=True,
                result_data=result_data,
                items_used=task.required_items,
                items_gained=self.agent.inventory.get_gained_items()
            )
        except Exception as e:
            task_result = TaskResult(task.task_id, False, None, str(e))

        self.execution_history.append(task_result)
        return task_result

    def _check_prerequisites(self, task):
        """Check if all prerequisites for the task are met"""
        return not task.prerequisites or all(p in self.agent.completed_tasks for p in task.prerequisites)

    async def _execute_action(self, task):
        """Execute the actual action based on task type"""
        if task.task_type == "gather":
            items = await self.world.gather_items(task.required_items)
            self.agent.inventory.add_items(items)
            return {"items_gathered": items}
        elif task.task_type == "build":
            construction_time = 10  # Simulated time to build
            await asyncio.sleep(construction_time)  # Simulate building process
            return {"building_status": "completed"}
        elif task.task_type == "explore":
            explored_area = self.world.explore_area(task.target_location)
            return {"explored_area": explored_area}
```

### Error Handling and Edge Cases

- **Prerequisite Checks**: Ensure all necessary prerequisites are met before executing a task.
- **Exception Handling**: Catch exceptions during execution and log errors appropriately.
- **Resource Management**: Handle resource constraints (e.g., insufficient items) gracefully.

### Configuration Options

- **Task Priorities**: Configure the priority of tasks based on game logic or player preferences.
- **Replanning Thresholds**: Set thresholds for triggering replanning when conditions change.

## Game-Specific Optimizations

### Tick Rate Considerations

- Adjust the tick rate to balance between planning and execution. Higher rates ensure faster reaction times but can increase computational load.

### Memory Management

- Use efficient data structures (e.g., dictionaries) for storing tasks and their results.
- Implement garbage collection mechanisms to free up memory when tasks are completed or abandoned.

### Multiplayer Synchronization

- Ensure that all agents' actions are synchronized across the network to maintain consistency in multiplayer games.
- Use distributed task queues or shared databases to coordinate tasks among agents.

## Agent Behavior Examples

### Scenarios

1. **Building a House**:
   - Before: Agents randomly gather resources without a plan.
   - After: Agents follow a structured plan, gathering required materials first before construction.

2. **Exploring an Area**:
   - Before: Agents wander aimlessly.
   - After: Agents systematically explore designated areas based on a predefined route.

3. **Multi-Step Crafting Sequences**:
   - Before: Agents fail to complete crafting due to missing prerequisites.
   - After: Agents follow a sequence of tasks, ensuring all materials are gathered before starting the craft.

4. **Dynamic Replanning**:
   - Before: Agents get stuck when encountering obstacles.
   - After: Agents dynamically adjust their plans to overcome obstacles and continue execution.

## Testing Strategy

### Unit Tests for Core Components

- Test `LuantiPlanner`'s ability to generate correct task sequences.
- Test `LuantiExecutor`'s handling of various task types (gather, build, explore).

### Integration Tests with Game Engine

- Simulate game scenarios and verify that Planner-Executor components work together seamlessly.
- Validate the robustness of error handling mechanisms.

### Performance Benchmarks

- Measure the computational overhead introduced by the Planner-Executor architecture.
- Conduct stress tests to ensure stability under high loads (e.g., many agents).

## Deployment Checklist

### Configuration Steps

1. Define task priorities and replanning thresholds in configuration files.
2. Integrate game-specific interfaces for world state access and event handling.

### Monitoring Setup

- Set up logging mechanisms to track task progress and execution times.
- Implement alerts for unexpected errors or performance issues.

### Rollback Procedures

- Maintain version control of all components.
- Document rollback procedures to revert to previous stable states in case of deployment failures.

## Advanced Patterns

### Scaling to Many Agents

- Use distributed computing techniques (e.g., cloud services) to handle large numbers of agents.
- Implement load balancing strategies to distribute tasks evenly across available resources.

### Player Interaction Patterns

- Allow players to assign specific tasks to agents or set general objectives.
- Enable real-time communication between players and AI agents for coordinated actions.

### Emergent Behaviors

- Encourage emergent behaviors by designing flexible task decomposition and adaptation mechanisms.
- Monitor and refine planner algorithms based on observed agent behavior patterns.

This guide provides a comprehensive implementation plan for integrating Planner Executor into Luanti Voyager, ensuring robust and intelligent AI behaviors in your game.

