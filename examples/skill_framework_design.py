"""
Skill Execution Framework Design Example
Shows how agents should generate and execute their own code
"""

from typing import Dict, Any, Callable, List, Optional
from dataclasses import dataclass
import ast
import asyncio
import inspect


@dataclass
class SkillMetadata:
    """Metadata for a skill"""
    name: str
    description: str
    required_items: List[str]
    required_skills: List[str]
    provides: List[str]
    version: int = 1
    success_rate: float = 0.0
    usage_count: int = 0


class SkillExecutor:
    """
    Core skill execution engine - this is what makes agents truly autonomous
    """
    
    def __init__(self):
        self.skills: Dict[str, Callable] = {}
        self.metadata: Dict[str, SkillMetadata] = {}
        self.sandbox_globals = self._create_safe_globals()
    
    def _create_safe_globals(self) -> Dict[str, Any]:
        """Create a safe execution environment"""
        return {
            # Safe built-ins only
            'print': print,
            'len': len,
            'range': range,
            'min': min,
            'max': max,
            'abs': abs,
            # Game-specific functions
            'move_to': self._safe_move_to,
            'place_block': self._safe_place_block,
            'mine_block': self._safe_mine_block,
            'wait': self._safe_wait,
            # Math functions
            'distance': lambda p1, p2: ((p1['x']-p2['x'])**2 + (p1['y']-p2['y'])**2 + (p1['z']-p2['z'])**2)**0.5
        }
    
    async def generate_skill(self, goal: str, world_state: Dict[str, Any]) -> str:
        """
        Use LLM to generate skill code
        This is where the magic happens - agents write their own behaviors
        """
        prompt = f"""Generate a Python function to achieve this goal: {goal}

Available functions:
- move_to(x, y, z): Move agent to position
- place_block(x, y, z, block_type): Place a block
- mine_block(x, y, z): Mine/destroy a block  
- wait(seconds): Wait for specified time
- distance(pos1, pos2): Calculate distance between positions

Current world state:
- Agent position: {world_state.get('agent_position')}
- Inventory: {world_state.get('inventory')}
- Nearby blocks: {len(world_state.get('nearby_blocks', []))} blocks

Generate ONLY the function code, starting with 'async def skill_function(agent, world):'
The function should return True if successful, False otherwise.

Example:
async def skill_function(agent, world):
    # Move to tree  
    tree_x, tree_y, tree_z = 10, 0, 5
    await move_to(tree_x, tree_y, tree_z)
    
    # Mine the tree
    for y in range(0, 5):
        await mine_block(tree_x, tree_y + y, tree_z)
    
    return True
"""
        
        # This would call the LLM
        # For now, return a simple example
        return '''
async def skill_function(agent, world):
    """Auto-generated skill for: {goal}"""
    start_pos = agent.pos
    
    # Example: Build a simple 3x3 platform
    for x in range(-1, 2):
        for z in range(-1, 2):
            await place_block(
                start_pos['x'] + x,
                start_pos['y'] - 1,
                start_pos['z'] + z,
                'default:wood'
            )
    
    return True
'''.format(goal=goal)
    
    def validate_skill_code(self, code: str) -> bool:
        """Validate that generated code is safe to execute"""
        try:
            # Parse the code
            tree = ast.parse(code)
            
            # Check for dangerous operations
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    return False  # No imports allowed
                if isinstance(node, ast.Attribute):
                    if node.attr.startswith('_'):
                        return False  # No private attributes
                        
            # Must have the skill_function
            functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            if not any(f.name == 'skill_function' for f in functions):
                return False
                
            return True
            
        except SyntaxError:
            return False
    
    async def compile_and_register(self, skill_name: str, code: str, metadata: SkillMetadata) -> bool:
        """Compile and register a new skill"""
        if not self.validate_skill_code(code):
            raise ValueError("Invalid or unsafe skill code")
        
        # Compile the code
        namespace = {}
        exec(code, self.sandbox_globals, namespace)
        
        if 'skill_function' not in namespace:
            raise ValueError("skill_function not found in generated code")
        
        # Register the skill
        self.skills[skill_name] = namespace['skill_function']
        self.metadata[skill_name] = metadata
        
        return True
    
    async def execute_skill(self, skill_name: str, agent: Any, world: Any) -> bool:
        """Execute a registered skill"""
        if skill_name not in self.skills:
            raise ValueError(f"Skill '{skill_name}' not found")
        
        skill_func = self.skills[skill_name]
        metadata = self.metadata[skill_name]
        
        # Update usage count
        metadata.usage_count += 1
        
        try:
            # Execute the skill
            result = await skill_func(agent, world)
            
            # Update success rate
            if result:
                metadata.success_rate = (
                    (metadata.success_rate * (metadata.usage_count - 1) + 1.0) 
                    / metadata.usage_count
                )
            else:
                metadata.success_rate = (
                    (metadata.success_rate * (metadata.usage_count - 1)) 
                    / metadata.usage_count
                )
            
            return result
            
        except Exception as e:
            print(f"Skill execution error: {e}")
            return False
    
    # Safe sandbox functions
    async def _safe_move_to(self, x: float, y: float, z: float):
        """Safe movement function"""
        print(f"[SANDBOX] Moving to {x}, {y}, {z}")
        await asyncio.sleep(0.1)  # Simulate movement time
        
    async def _safe_place_block(self, x: float, y: float, z: float, block_type: str):
        """Safe block placement"""
        print(f"[SANDBOX] Placing {block_type} at {x}, {y}, {z}")
        await asyncio.sleep(0.05)
        
    async def _safe_mine_block(self, x: float, y: float, z: float):
        """Safe block mining"""
        print(f"[SANDBOX] Mining block at {x}, {y}, {z}")
        await asyncio.sleep(0.1)
        
    async def _safe_wait(self, seconds: float):
        """Safe wait function"""
        print(f"[SANDBOX] Waiting {seconds} seconds")
        await asyncio.sleep(seconds)


class SkillLibrary:
    """
    Manages the agent's growing library of skills
    """
    
    def __init__(self):
        self.executor = SkillExecutor()
        self.skill_tree: Dict[str, List[str]] = {}  # skill -> dependent skills
    
    async def learn_new_skill(self, goal: str, world_state: Dict[str, Any]) -> Optional[str]:
        """
        Main learning pipeline:
        1. Generate code with LLM
        2. Validate for safety
        3. Test in simulation
        4. Add to library
        """
        print(f"\n🧠 Learning new skill for goal: {goal}")
        
        # Generate skill code
        code = await self.executor.generate_skill(goal, world_state)
        print(f"📝 Generated code:\n{code}")
        
        # Create metadata
        skill_name = goal.lower().replace(' ', '_')
        metadata = SkillMetadata(
            name=skill_name,
            description=goal,
            required_items=[],  # Would be extracted from code analysis
            required_skills=[],  # Would check dependencies
            provides=[skill_name]
        )
        
        # Compile and register
        try:
            await self.executor.compile_and_register(skill_name, code, metadata)
            print(f"✅ Successfully learned skill: {skill_name}")
            return skill_name
        except Exception as e:
            print(f"❌ Failed to learn skill: {e}")
            return None
    
    async def compose_skills(self, goal: str, available_skills: List[str]) -> Optional[str]:
        """
        Compose existing skills to achieve a new goal
        This is how agents build complexity from simple behaviors
        """
        prompt = f"""Create a new skill by combining existing skills to achieve: {goal}

Available skills:
{chr(10).join(f"- {skill}: {self.executor.metadata[skill].description}" for skill in available_skills)}

Generate a function that calls these existing skills in the right order.
"""
        # This would use LLM to compose skills
        # Return the new composite skill name
        pass


# Example usage showing the learning pipeline
async def demonstrate_skill_learning():
    """Show how an agent learns and executes new skills"""
    
    library = SkillLibrary()
    
    # Simulate world state
    world_state = {
        'agent_position': {'x': 0, 'y': 0, 'z': 0},
        'inventory': {'default:wood': 10},
        'nearby_blocks': []
    }
    
    # Learn a new skill
    skill_name = await library.learn_new_skill(
        goal="Build a 3x3 wooden platform",
        world_state=world_state
    )
    
    if skill_name:
        # Execute the learned skill
        print(f"\n🎮 Executing learned skill: {skill_name}")
        
        # Mock agent and world objects
        class MockAgent:
            pos = {'x': 0, 'y': 0, 'z': 0}
        
        success = await library.executor.execute_skill(
            skill_name, 
            MockAgent(), 
            world_state
        )
        
        print(f"\n{'✅ Skill executed successfully!' if success else '❌ Skill execution failed'}")
        
        # Show skill metadata
        metadata = library.executor.metadata[skill_name]
        print(f"\n📊 Skill Statistics:")
        print(f"  - Usage count: {metadata.usage_count}")
        print(f"  - Success rate: {metadata.success_rate:.1%}")


if __name__ == "__main__":
    asyncio.run(demonstrate_skill_learning())