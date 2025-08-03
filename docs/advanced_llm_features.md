# Advanced LLM Features

The Luanti Voyager agent now includes sophisticated reasoning capabilities that enable more intelligent and adaptive behavior.

## Features

### 1. Multi-Step Reasoning with Chain-of-Thought

The agent can break down complex tasks into logical steps and reason through them:

```python
# Create a plan for a complex objective
await agent.create_plan("Build a shelter with a door and windows")

# The agent will:
# 1. Analyze what resources are needed
# 2. Consider current inventory and surroundings
# 3. Create a step-by-step plan
# 4. Execute each step with purpose
```

### 2. Goal Decomposition

High-level goals are automatically broken down into achievable sub-goals:

```python
# Set a high-level goal
await agent.set_goal("Explore the underground cave system safely")

# Automatically decomposes into:
# - Find cave entrance
# - Gather torches for light
# - Ensure adequate food/health
# - Map the cave systematically
# - Mark exit routes
```

### 3. Learning from Failures

When actions fail, the agent reflects and adapts:

```python
# If an action fails (e.g., trying to mine bedrock)
# The agent will:
# 1. Analyze why it failed
# 2. Remember the lesson learned
# 3. Suggest alternative approaches
# 4. Avoid similar mistakes in the future
```

### 4. Context-Aware Decision Making

Decisions consider history, current goals, and past failures:

```python
# The agent maintains:
# - Action history (last 50 actions)
# - Active goals and progress
# - Memory of failures and lessons learned
# - Environmental context

# All decisions factor in this context for smarter choices
```

## Usage

### Basic Setup

```python
from luanti_voyager.agent import VoyagerAgent

# Create agent with advanced LLM
agent = VoyagerAgent(
    name="SmartBot",
    llm_provider="ollama",  # or "openai", "anthropic"
    model="llama3"  # optional: specify model
)

# Start the agent
await agent.start()
```

### Setting Goals

```python
# Set a high-level goal
await agent.set_goal("Build a house")

# Check progress
progress = await agent.get_goal_progress()
print(progress)
# Output: 🎯 Build a house: 25% complete
```

### Creating Plans

```python
# Create a specific plan
await agent.create_plan("Collect 20 wood blocks")

# The agent will execute the plan step by step
# Each step has a clear purpose and expected outcome
```

### Monitoring Reasoning

Watch the logs for reasoning insights:

```
🧠 Chain-of-thought: To build a shelter, I need walls and a roof...
💭 Reflection: Mining bedrock failed because it's unbreakable
📚 Lesson: Avoid bedrock, look for alternative materials
🎯 Goal progress: Build shelter: 40% complete
```

## Configuration

### Token Optimization

Advanced features use more tokens. Optimize with:

```python
# Reduce context window
agent = VoyagerAgent(
    name="EfficientBot",
    llm_provider="openai",
    max_history=20,  # Reduce from default 50
    temperature=0.3  # Lower temperature for more focused responses
)
```

### Model Selection

Different models excel at different tasks:

- **GPT-4**: Best for complex reasoning and planning
- **Claude**: Excellent for detailed analysis and reflection
- **Llama 3**: Good balance of performance and cost
- **Mixtral**: Fast local option for basic reasoning

## Examples

See `examples/advanced_llm_demo.py` for a complete demonstration.

### Quick Example: Mining with Intelligence

```python
# The agent encounters iron ore but has no pickaxe
# 
# Without advanced LLM:
# - Tries to mine with hands (fails)
# - Moves on without learning
#
# With advanced LLM:
# 1. Recognizes it needs a pickaxe
# 2. Creates plan: gather wood → craft sticks → find stone → craft pickaxe
# 3. Executes plan step by step
# 4. Returns to mine iron successfully
# 5. Remembers: "Iron requires stone pickaxe or better"
```

## Performance Considerations

1. **Token Usage**: Advanced features use 2-3x more tokens
2. **Latency**: Chain-of-thought adds 1-2s per decision
3. **Memory**: Maintains history of 50 actions by default
4. **Caching**: Similar situations reuse previous reasoning

## Troubleshooting

### Agent not showing advanced reasoning?
- Check LLM provider is configured correctly
- Ensure `advanced_llm` is initialized (not using "none" provider)
- Look for 🧠 and 💭 symbols in logs

### Plans not executing?
- Verify world state is being updated
- Check for conflicting goals
- Ensure agent has necessary capabilities

### High token usage?
- Reduce `max_history` setting
- Use more efficient models
- Enable response caching

## Future Enhancements

Planned improvements:
- Multi-agent coordination with shared goals
- Skill learning and code generation
- Long-term memory persistence
- Custom reasoning strategies