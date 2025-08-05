# Planner Executor - Implementation Guide (GPT-OSS)

Generated: 2025-08-05T18:16:51.155967
Model: gpt-oss:20b

---

**Planner Executor – Luanti Voyager Implementation Guide**  
*(≤ 500 words, code‑focused)*

---

### 1. What is a Planner Executor?

A Planner Executor is a runtime component that takes a high‑level plan (a list of atomic actions with preconditions) and turns it into concrete, time‑stepped commands for an in‑game AI agent. It handles sequencing, re‑planning on failure, and low‑level physics interactions, acting as the bridge between an agent’s decision‑making layer and the game engine.

---

### 2. How to implement it for game AI agents

| Step | What to do | Why it matters |
|------|------------|----------------|
| **Define an Action Interface** | `Action{name, preconditions, effect, cost}` | Keeps actions interchangeable and testable. |
| **Create a Planner** | Use a lightweight planner (e.g., A* over abstract state space) to generate a list of actions from current state to goal state. | Produces the plan the executor will run. |
| **Wrap Actions in a Scheduler** | `Scheduler:queue(action)` → `Scheduler:tick(dt)` | Allows actions to be executed over time and interleaved with other systems. |
| **Implement a State Monitor** | `StateMachine:getState()` → feeds into precondition checks. | Detects when a precondition has changed or an action failed. |
| **Add Re‑planning Hook** | On action failure → re‑plan from current state. | Keeps the agent adaptive to dynamic environments. |
| **Expose Execute API** | `PlannerExecutor:run(plan)` → runs until completion or error. | Gives higher‑level AI modules a single call to launch a plan. |
| **Integrate with Game Loop** | In the `update(dt)` tick, call `PlannerExecutor:tick(dt)`. | Keeps the executor in sync with physics and rendering. |

**Implementation Tips**

- Keep the planner lightweight; use heuristics that are cheap to compute (distance to goal, block counts).
- Store actions as simple tables; no need for heavy OOP if you’re using Lua.
- Use coroutines to model blocking actions (e.g., mining a block takes several seconds).

---

### 3. One simple code example (Lua)

```lua
-- Action definition
local function buildBlock(pos, blockType)
  return {
    name = "Build "..blockType,
    preconditions = function(state)
      return state.canPlaceBlock(pos)
    end,
    effect = function(state)
      state.placeBlock(pos, blockType)
    end,
    cost = 1
  }
end

-- PlannerExecutor
local PlannerExecutor = {}
PlannerExecutor.__index = PlannerExecutor

function PlannerExecutor.new()
  return setmetatable({queue = {}, current = nil}, PlannerExecutor)
end

function PlannerExecutor:run(plan)
  self.queue = plan
  self.current = table.remove(self.queue, 1)
end

function PlannerExecutor:tick(dt, state)
  if not self.current then return end

  if not self.current.preconditions(state) then
    -- precondition failed, replan
    self:run(planner:plan(state, self.goal))
    return
  end

  -- execute effect immediately (simplified)
  self.current.effect(state)
  self.current = table.remove(self.queue, 1)
end

-- Example usage
local state = GameState:new()
local plan = {
  buildBlock({x=10,y=64,z=10}, "stone"),
  buildBlock({x=11,y=64,z=10}, "stone")
}
local executor = PlannerExecutor.new()
executor:run(plan)

-- In game loop
function update(dt)
  executor:tick(dt, state)
end
```

---

### 4. Game‑specific use case

**“Automatic Farm Builder”**

*Goal:* An NPC farmer should construct a 5×5 stone farm, plant wheat, and harvest it automatically.

1. **Planner** generates actions:
   - Build stone perimeter (9 blocks)
   - Dig a 3×3 square
   - Plant wheat seeds in each cell
   - Wait until wheat grows
   - Harvest each cell

2. **Planner Executor** runs the plan:
   - Checks if a stone block can be placed before each build action.
   - Waits (`sleep`) during the growth phase, yielding control to other agents.
   - On failure (e.g., path blocked), it re‑plans to find an alternate spot.

3. **Outcome:** The farmer autonomously constructs the farm, plants, and harvests without player intervention, demonstrating a clear, reusable Planner‑Executor pattern.

---