"""
Advanced LLM reasoning module with multi-step planning, reflection, and goal decomposition.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

from .llm import VoyagerLLM

logger = logging.getLogger(__name__)


@dataclass
class Goal:
    """Represents a high-level goal that can be decomposed into steps."""
    description: str
    priority: int = 1
    steps: List[str] = field(default_factory=list)
    completed_steps: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, failed
    created_at: datetime = field(default_factory=datetime.now)
    
    def progress(self) -> float:
        """Calculate progress percentage."""
        if not self.steps:
            return 0.0
        return len(self.completed_steps) / len(self.steps) * 100


@dataclass 
class ActionPlan:
    """A plan consisting of multiple actions to achieve a goal."""
    goal: str
    steps: List[Dict[str, Any]]
    current_step: int = 0
    success_criteria: Optional[str] = None
    
    def get_current_action(self) -> Optional[Dict[str, Any]]:
        """Get the current action to execute."""
        if self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None
    
    def advance(self):
        """Move to next step."""
        self.current_step += 1
    
    def is_complete(self) -> bool:
        """Check if plan is complete."""
        return self.current_step >= len(self.steps)


class AdvancedLLM:
    """Enhanced LLM with advanced reasoning capabilities."""
    
    def __init__(self, base_llm: VoyagerLLM):
        self.llm = base_llm
        self.current_plan: Optional[ActionPlan] = None
        self.goals: List[Goal] = []
        self.action_history: List[Dict[str, Any]] = []
        self.failure_memory: List[Dict[str, Any]] = []
        self.max_history = 50
        
    async def plan_sequence(self, goal: str, world_state: Dict[str, Any]) -> ActionPlan:
        """Break down a goal into a sequence of actions using chain-of-thought reasoning."""
        if not self.llm.llm:
            return ActionPlan(goal=goal, steps=[])
            
        prompt = f"""You are planning actions for an AI agent in a Luanti voxel world.

GOAL: {goal}

CURRENT STATE:
- Position: {world_state.get('agent_position', {})}
- Health: {world_state.get('hp', 20)}/20 HP
- Inventory: {world_state.get('inventory', {})}
- Nearby blocks: {self._summarize_environment(world_state)}

Think step-by-step about how to achieve this goal:
1. What is the current situation?
2. What resources or conditions are needed?
3. What obstacles might we face?
4. What is the optimal sequence of actions?

Provide a detailed plan as a JSON object:
{{
    "analysis": "Your step-by-step thinking",
    "steps": [
        {{"action": "move_to", "params": {{"x": 0, "y": 0, "z": 0}}, "purpose": "Get to starting position"}},
        {{"action": "dig", "params": {{"x": 1, "y": 0, "z": 0}}, "purpose": "Mine wood block"}}
    ],
    "success_criteria": "What indicates success",
    "potential_failures": ["What could go wrong"]
}}"""

        try:
            response = await self.llm.llm.generate(prompt, max_tokens=800, temperature=0.2)
            plan_data = self._parse_json_response(response)
            
            if plan_data and "steps" in plan_data:
                logger.info(f"🧠 Chain-of-thought: {plan_data.get('analysis', 'No analysis')}")
                return ActionPlan(
                    goal=goal,
                    steps=plan_data["steps"],
                    success_criteria=plan_data.get("success_criteria")
                )
        except Exception as e:
            logger.error(f"Failed to create plan: {e}")
            
        # Fallback to simple plan
        return ActionPlan(goal=goal, steps=[{"action": "explore", "purpose": "Basic exploration"}])
    
    async def decompose_goal(self, high_level_goal: str, world_state: Dict[str, Any]) -> Goal:
        """Decompose a high-level goal into smaller sub-goals."""
        if not self.llm.llm:
            return Goal(description=high_level_goal)
            
        prompt = f"""Break down this high-level goal into smaller, achievable sub-goals:

HIGH-LEVEL GOAL: {high_level_goal}

CONTEXT:
- Current position: {world_state.get('agent_position', {})}
- Available resources: {world_state.get('inventory', {})}
- Environment: {self._summarize_environment(world_state)}

Provide a JSON response:
{{
    "sub_goals": [
        "First specific sub-goal",
        "Second specific sub-goal",
        ...
    ],
    "priority": 1-5 (5 is highest),
    "estimated_steps": 10
}}"""

        try:
            response = await self.llm.llm.generate(prompt, max_tokens=400, temperature=0.3)
            goal_data = self._parse_json_response(response)
            
            if goal_data and "sub_goals" in goal_data:
                return Goal(
                    description=high_level_goal,
                    priority=goal_data.get("priority", 1),
                    steps=goal_data["sub_goals"]
                )
        except Exception as e:
            logger.error(f"Failed to decompose goal: {e}")
            
        return Goal(description=high_level_goal)
    
    async def reflect_on_failure(self, failed_action: Dict[str, Any], 
                                world_state: Dict[str, Any], 
                                error: Optional[str] = None) -> Dict[str, Any]:
        """Analyze why an action failed and suggest alternatives."""
        if not self.llm.llm:
            return {"suggestion": "Try a different approach"}
            
        # Add to failure memory
        self.failure_memory.append({
            "action": failed_action,
            "error": error,
            "state": world_state,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep failure memory bounded
        if len(self.failure_memory) > 20:
            self.failure_memory = self.failure_memory[-20:]
        
        prompt = f"""An action failed. Analyze why and suggest alternatives.

FAILED ACTION: {json.dumps(failed_action, indent=2)}
ERROR: {error or "Unknown error"}

CURRENT STATE:
- Position: {world_state.get('agent_position', {})}
- Health: {world_state.get('hp', 20)}/20 HP
- Nearby blocks: {self._summarize_environment(world_state)}

RECENT FAILURES:
{self._summarize_failures()}

Think about:
1. Why did this action fail?
2. What assumptions were wrong?
3. What alternative approaches could work?
4. Should we try again or do something different?

Respond with JSON:
{{
    "failure_analysis": "Why it failed",
    "lesson_learned": "What to remember",
    "alternative_action": {{"action": "...", "params": {{...}}, "reason": "Why this might work better"}},
    "retry_original": true/false
}}"""

        try:
            response = await self.llm.llm.generate(prompt, max_tokens=600, temperature=0.4)
            reflection = self._parse_json_response(response)
            
            if reflection:
                logger.info(f"💭 Reflection: {reflection.get('failure_analysis', 'No analysis')}")
                logger.info(f"📚 Lesson: {reflection.get('lesson_learned', 'No lesson')}")
                return reflection
        except Exception as e:
            logger.error(f"Failed to reflect on failure: {e}")
            
        return {"suggestion": "Try exploring in a different direction"}
    
    async def decide_with_context(self, world_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make decisions considering history, goals, and current plan."""
        # If we have an active plan, execute next step
        if self.current_plan and not self.current_plan.is_complete():
            action = self.current_plan.get_current_action()
            if action:
                logger.info(f"📋 Executing plan step {self.current_plan.current_step + 1}/{len(self.current_plan.steps)}")
                self.current_plan.advance()
                return self._convert_plan_action(action)
        
        # Otherwise, use enhanced decision making
        if not self.llm.llm:
            return None
            
        prompt = self._build_contextual_prompt(world_state)
        
        try:
            response = await self.llm.llm.generate(prompt, max_tokens=600, temperature=0.3)
            action = self._parse_action_response(response)
            
            if action:
                # Record in history
                self.action_history.append({
                    "action": action,
                    "state": world_state,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Maintain history size
                if len(self.action_history) > self.max_history:
                    self.action_history = self.action_history[-self.max_history:]
                
                return action
        except Exception as e:
            logger.error(f"Context-aware decision failed: {e}")
            
        return None
    
    def _build_contextual_prompt(self, world_state: Dict[str, Any]) -> str:
        """Build a prompt that includes context from history and goals."""
        agent_pos = world_state.get("agent_position", {})
        
        prompt = f"""You are an intelligent agent exploring a Luanti world. Make decisions based on context.

CURRENT SITUATION:
- Position: x={agent_pos.get('x', 0):.1f}, y={agent_pos.get('y', 0):.1f}, z={agent_pos.get('z', 0):.1f}
- Health: {world_state.get('hp', 20)}/20 HP
- Inventory: {json.dumps(world_state.get('inventory', {}))}
- Environment: {self._summarize_environment(world_state)}

RECENT ACTIONS:
{self._summarize_history()}

ACTIVE GOALS:
{self._summarize_goals()}

MEMORY OF FAILURES:
{self._summarize_failures()}

AVAILABLE ACTIONS:
- move_to <x> <y> <z>: Walk to position
- teleport <x> <y> <z>: Instant travel
- dig <x> <y> <z>: Mine block
- place <block> <x> <y> <z>: Place block
- generate <radius>: Generate terrain
- explore: Random exploration
- wait: Observe surroundings

Consider:
1. Past successes and failures
2. Current goals and priorities
3. Environmental opportunities
4. Safety (health level)

Choose the best action. Respond with JSON:
{{"action": "...", "params": {{...}}, "reason": "Detailed reasoning"}}"""
        
        return prompt
    
    def _summarize_environment(self, world_state: Dict[str, Any]) -> str:
        """Create a summary of the environment."""
        blocks = world_state.get("nearby_blocks", [])
        if not blocks:
            return "No blocks detected"
            
        block_types = {}
        for block in blocks:
            btype = block.get("type", "unknown")
            block_types[btype] = block_types.get(btype, 0) + 1
            
        summary = []
        for btype, count in sorted(block_types.items(), key=lambda x: x[1], reverse=True)[:5]:
            if btype != "ignore":
                summary.append(f"{count}x {btype}")
                
        return ", ".join(summary) if summary else "Mostly void"
    
    def _summarize_history(self) -> str:
        """Summarize recent action history."""
        if not self.action_history:
            return "No recent actions"
            
        summary = []
        for item in self.action_history[-5:]:
            action = item["action"]
            summary.append(f"- {action.get('type', 'unknown')}: {action.get('reason', 'no reason')}")
            
        return "\n".join(summary)
    
    def _summarize_goals(self) -> str:
        """Summarize active goals."""
        if not self.goals:
            return "No specific goals"
            
        active_goals = [g for g in self.goals if g.status != "completed"][:3]
        if not active_goals:
            return "All goals completed"
            
        summary = []
        for goal in active_goals:
            summary.append(f"- {goal.description} ({goal.progress():.0f}% complete)")
            
        return "\n".join(summary)
    
    def _summarize_failures(self) -> str:
        """Summarize recent failures."""
        if not self.failure_memory:
            return "No recent failures"
            
        summary = []
        for failure in self.failure_memory[-3:]:
            action = failure["action"]
            error = failure.get("error", "unknown error")
            summary.append(f"- {action.get('type', 'unknown')} failed: {error}")
            
        return "\n".join(summary)
    
    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from LLM response."""
        try:
            # Clean up response
            response = response.strip()
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.rfind("```")
                if end > start:
                    response = response[start:end]
            elif "```" in response:
                start = response.find("```") + 3
                end = response.rfind("```")
                if end > start:
                    response = response[start:end]
                    
            return json.loads(response.strip())
        except Exception as e:
            logger.warning(f"Failed to parse JSON: {e}")
            logger.debug(f"Response was: {response[:200]}...")
            return None
    
    def _parse_action_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse action from LLM response."""
        data = self._parse_json_response(response)
        if not data or "action" not in data:
            return None
            
        return self._convert_plan_action(data)
    
    def _convert_plan_action(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert plan action format to agent action format."""
        action_type = action_data.get("action", "")
        params = action_data.get("params", {})
        reason = action_data.get("reason", action_data.get("purpose", "LLM decision"))
        
        if action_type == "move_to":
            return {"type": "move", "pos": params, "reason": reason}
        elif action_type == "teleport":
            return {"type": "teleport", "pos": params, "reason": reason}
        elif action_type == "dig":
            return {"type": "dig", "pos": params, "reason": reason}
        elif action_type == "place":
            return {
                "type": "place",
                "pos": params,
                "block": params.get("block", "basenodes:dirt"),
                "reason": reason
            }
        elif action_type == "generate":
            return {
                "type": "generate",
                "radius": params.get("radius", 20),
                "reason": reason
            }
        elif action_type == "explore":
            return {"type": "explore", "reason": reason}
        elif action_type == "wait":
            return {"type": "wait", "reason": reason}
        else:
            logger.warning(f"Unknown action type: {action_type}")
            return None