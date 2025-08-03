"""
Multi-agent coordination system inspired by Mindcraft.

Manages teams of agents, task distribution, and collaborative behaviors.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import logging
import time
from enum import Enum

from .communication import AgentCommunication, MessagePriority
from .profiles import AgentProfile

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of a team task."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TeamTask:
    """A task that can be assigned to team members."""
    task_id: str
    description: str
    required_skills: List[str] = field(default_factory=list)
    required_agents: int = 1
    priority: int = 1
    status: TaskStatus = TaskStatus.PENDING
    assigned_agents: List[str] = field(default_factory=list)
    subtasks: List['TeamTask'] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # task_ids
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def can_start(self, completed_tasks: List[str]) -> bool:
        """Check if all dependencies are satisfied."""
        return all(dep in completed_tasks for dep in self.dependencies)
    
    def is_suitable_for(self, profile: AgentProfile) -> float:
        """Calculate suitability score for an agent (0.0 to 1.0)."""
        if not self.required_skills:
            return 0.5  # Neutral if no specific skills required
        
        # Check skill overlap
        agent_skills = set(skill.lower() for skill in profile.skills)
        required_skills = set(skill.lower() for skill in self.required_skills)
        
        overlap = len(agent_skills.intersection(required_skills))
        if overlap == 0:
            return 0.1  # Low but not zero - agent might still help
        
        return overlap / len(required_skills)


class Team:
    """A team of cooperating agents."""
    
    def __init__(self, name: str, team_id: str):
        self.name = name
        self.team_id = team_id
        self.members: Dict[str, AgentProfile] = {}
        self.communication_channels: Dict[str, AgentCommunication] = {}
        self.active = True
        
    def add_member(self, agent_name: str, profile: AgentProfile, 
                   communication: AgentCommunication):
        """Add a member to the team."""
        self.members[agent_name] = profile
        self.communication_channels[agent_name] = communication
        communication.team_id = self.team_id
        
        # Register all team members with each other
        for other_name, other_comm in self.communication_channels.items():
            if other_name != agent_name:
                communication.register_listener(other_name, other_comm)
                other_comm.register_listener(agent_name, communication)
        
        logger.info(f"Added {agent_name} to team {self.name}")
    
    def remove_member(self, agent_name: str):
        """Remove a member from the team."""
        if agent_name in self.members:
            del self.members[agent_name]
            del self.communication_channels[agent_name]
            logger.info(f"Removed {agent_name} from team {self.name}")
    
    def get_members_by_role(self, role: str) -> List[str]:
        """Get all members with a specific role."""
        return [name for name, profile in self.members.items() 
                if profile.team_role == role]
    
    def get_members_with_skill(self, skill: str) -> List[str]:
        """Get all members with a specific skill."""
        skill_lower = skill.lower()
        return [name for name, profile in self.members.items()
                if any(s.lower() == skill_lower for s in profile.skills)]


class MultiAgentCoordinator:
    """
    Coordinates multiple agents in teams, inspired by Mindcraft's approach.
    
    Handles task assignment, team formation, and collaborative behaviors.
    """
    
    def __init__(self):
        self.teams: Dict[str, Team] = {}
        self.tasks: Dict[str, TeamTask] = {}
        self.completed_tasks: List[str] = []
        self.task_counter = 0
        self.running = False
        
    def create_team(self, name: str) -> Team:
        """Create a new team."""
        team_id = f"team_{len(self.teams)}"
        team = Team(name, team_id)
        self.teams[team_id] = team
        logger.info(f"Created team: {name} ({team_id})")
        return team
    
    def add_task(self, description: str, required_skills: List[str] = None,
                 required_agents: int = 1, priority: int = 1,
                 dependencies: List[str] = None) -> TeamTask:
        """Add a task to be completed by teams."""
        task_id = f"task_{self.task_counter}"
        self.task_counter += 1
        
        task = TeamTask(
            task_id=task_id,
            description=description,
            required_skills=required_skills or [],
            required_agents=required_agents,
            priority=priority,
            dependencies=dependencies or []
        )
        
        self.tasks[task_id] = task
        logger.info(f"Added task: {description} ({task_id})")
        return task
    
    def decompose_task(self, task: TeamTask, subtask_descriptions: List[str]) -> List[TeamTask]:
        """Decompose a task into subtasks."""
        subtasks = []
        
        for i, desc in enumerate(subtask_descriptions):
            subtask = self.add_task(
                description=desc,
                required_skills=task.required_skills,  # Inherit parent skills
                priority=task.priority
            )
            subtask.dependencies = [task.task_id]  # Depend on parent
            task.subtasks.append(subtask)
            subtasks.append(subtask)
        
        return subtasks
    
    async def assign_task(self, task: TeamTask, team: Team) -> List[str]:
        """
        Assign a task to the most suitable agents in a team.
        
        Returns list of assigned agent names.
        """
        if task.status != TaskStatus.PENDING:
            logger.warning(f"Task {task.task_id} is not pending")
            return []
        
        if not task.can_start(self.completed_tasks):
            logger.warning(f"Task {task.task_id} dependencies not met")
            return []
        
        # Score all team members
        agent_scores: List[Tuple[str, float]] = []
        for agent_name, profile in team.members.items():
            score = task.is_suitable_for(profile)
            # Boost score if agent volunteers
            if profile.should_volunteer_for(task.description):
                score = min(1.0, score + 0.3)
            agent_scores.append((agent_name, score))
        
        # Sort by score and assign top agents
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        assigned = []
        
        for agent_name, score in agent_scores[:task.required_agents]:
            if score > 0.3:  # Minimum threshold
                assigned.append(agent_name)
                task.assigned_agents.append(agent_name)
                
                # Notify agent
                comm = team.communication_channels[agent_name]
                await comm.send_message(
                    agent_name,
                    f"You have been assigned task: {task.description}",
                    priority=MessagePriority.HIGH,
                    metadata={"task_id": task.task_id, "task": task.to_dict()}
                )
        
        if assigned:
            task.status = TaskStatus.ASSIGNED
            logger.info(f"Assigned task {task.task_id} to: {assigned}")
        else:
            logger.warning(f"Could not find suitable agents for task {task.task_id}")
        
        return assigned
    
    async def coordinate_team_task(self, team: Team, goal: str):
        """
        Coordinate a team to achieve a complex goal.
        
        This is the main entry point for team coordination.
        """
        logger.info(f"Team {team.name} starting goal: {goal}")
        
        # Create main task
        main_task = self.add_task(
            description=goal,
            required_agents=len(team.members),
            priority=10
        )
        
        # Have team leader (or first member) decompose the task
        leader = list(team.members.keys())[0]
        leader_comm = team.communication_channels[leader]
        
        # Request task decomposition
        await leader_comm.send_message(
            leader,
            f"Please decompose this goal into subtasks: {goal}",
            priority=MessagePriority.HIGH,
            metadata={"request_type": "task_decomposition"}
        )
        
        # In a real implementation, we'd wait for LLM response
        # For now, simulate with example decomposition
        if "build" in goal.lower() and "castle" in goal.lower():
            subtask_descriptions = [
                "Scout for suitable building location",
                "Gather stone and wood materials",
                "Build castle foundation",
                "Construct castle walls",
                "Add castle towers and defenses",
                "Build interior structures"
            ]
        else:
            subtask_descriptions = [f"Step {i+1} of {goal}" for i in range(3)]
        
        # Create subtasks
        subtasks = self.decompose_task(main_task, subtask_descriptions)
        
        # Assign subtasks to team members
        for subtask in subtasks:
            assigned = await self.assign_task(subtask, team)
            
            if assigned and len(assigned) > 1:
                # Coordinate multi-agent subtasks
                await self.coordinate_agents(team, subtask, assigned)
        
        # Monitor progress
        await self.monitor_team_progress(team, main_task)
    
    async def coordinate_agents(self, team: Team, task: TeamTask, agents: List[str]):
        """Coordinate multiple agents on the same task."""
        # Designate a task leader
        leader = agents[0]
        leader_comm = team.communication_channels[leader]
        
        # Inform all agents
        coordination_data = {
            "task_id": task.task_id,
            "task_description": task.description,
            "team_members": agents,
            "leader": leader
        }
        
        for agent in agents:
            role = "leader" if agent == leader else "supporter"
            await team.communication_channels[agent].send_message(
                agent,
                f"Coordinating on task: {task.description}. Your role: {role}",
                priority=MessagePriority.HIGH,
                metadata=coordination_data
            )
    
    async def monitor_team_progress(self, team: Team, task: TeamTask):
        """Monitor team progress on a task."""
        logger.info(f"Monitoring progress on task: {task.description}")
        
        # In real implementation, this would:
        # 1. Periodically check subtask status
        # 2. Handle failures and reassignments
        # 3. Facilitate inter-agent communication
        # 4. Report overall progress
        
        # For now, just log
        while task.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            await asyncio.sleep(5)  # Check every 5 seconds
            
            # Check subtask progress
            completed_subtasks = sum(1 for st in task.subtasks 
                                   if st.status == TaskStatus.COMPLETED)
            total_subtasks = len(task.subtasks)
            
            if total_subtasks > 0:
                progress = completed_subtasks / total_subtasks
                logger.info(f"Task progress: {progress*100:.1f}% ({completed_subtasks}/{total_subtasks})")
                
                if completed_subtasks == total_subtasks:
                    task.status = TaskStatus.COMPLETED
                    self.completed_tasks.append(task.task_id)
                    logger.info(f"Task completed: {task.description}")
    
    def get_team_status(self, team_id: str) -> Dict[str, Any]:
        """Get current status of a team."""
        if team_id not in self.teams:
            return {"error": "Team not found"}
        
        team = self.teams[team_id]
        
        # Get task assignments
        team_tasks = []
        for task_id, task in self.tasks.items():
            if any(agent in team.members for agent in task.assigned_agents):
                team_tasks.append({
                    "task_id": task_id,
                    "description": task.description,
                    "status": task.status.value,
                    "assigned_to": task.assigned_agents
                })
        
        return {
            "team_name": team.name,
            "team_id": team_id,
            "members": list(team.members.keys()),
            "active_tasks": team_tasks,
            "completed_tasks": [t for t in self.completed_tasks 
                              if any(agent in team.members 
                                    for agent in self.tasks[t].assigned_agents)]
        }