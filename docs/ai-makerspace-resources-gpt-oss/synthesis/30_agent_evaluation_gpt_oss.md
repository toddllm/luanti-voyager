# Agent Evaluation - Implementation Guide (GPT-OSS)

Generated: 2025-08-05T18:21:57.591492
Model: gpt-oss:20b

---

## Agent Evaluation in Luanti Voyager  
**What is Agent Evaluation?**  
Agent Evaluation is a systematic way to measure how well an AI agent achieves its objectives in the game world. It tracks key metrics (success rate, time to goal, resource usage, etc.), logs them per episode, and surfaces actionable feedback for designers and developers.

---

### 1. How to Implement Agent Evaluation

* **Create an Evaluation Manager** – a singleton component that lives in the game loop and collects metrics for every agent episode.  
* **Define Evaluation Criteria** – for each task type (e.g., “mine diamond”, “build shelter”), list the observable outcomes you care about.  
* **Hook Into Agent Lifecycle**  
  * `onEpisodeStart(agent)` – reset counters, note start time.  
  * `onStep(agent, action, observation)` – update running stats (distance walked, blocks broken, etc.).  
  * `onEpisodeEnd(agent, success)` – compute final scores, log to file or dashboard.  
* **Persist & Visualise** – write JSON/CSV logs or push to a lightweight DB; use a simple web UI or built‑in console to view trends.  
* **Automated Tests** – run a batch of episodes with the same seed and assert that metrics stay above a threshold.  
* **Iterate** – feed the evaluation data back into training or hand‑tune agent parameters.

---

### 2. One Simple Code Example (Lua)

```lua
-- evaluation_manager.lua
local EvalMgr = {}

function EvalMgr:startEpisode(agentId)
  self[agentId] = {
    startTime = os.clock(),
    blocksBroken = 0,
    distanceTraveled = 0,
    success = false
  }
end

function EvalMgr:step(agentId, action, obs)
  local state = self[agentId]
  -- Count blocks broken
  if action.type == "BREAK_BLOCK" then
    state.blocksBroken = state.blocksBroken + 1
  end
  -- Accumulate distance
  state.distanceTraveled = state.distanceTraveled + obs.deltaPos
end

function EvalMgr:endEpisode(agentId, success)
  local state = self[agentId]
  state.success = success
  state.duration = os.clock() - state.startTime
  self:logResult(agentId, state)
end

function EvalMgr:logResult(agentId, state)
  local log = string.format(
    "[Agent %s] Success:%s | Blocks:%d | Dist:%.2f | Time:%.2fs\n",
    agentId, tostring(state.success), state.blocksBroken,
    state.distanceTraveled, state.duration)
  io.write(log)          -- or append to a file
end

return EvalMgr
```

**Usage in the agent loop**

```lua
local EvalMgr = require "evaluation_manager"

function onEpisodeStart(agentId)
  EvalMgr:startEpisode(agentId)
end

function onStep(agentId, action, observation)
  EvalMgr:step(agentId, action, observation)
end

function onEpisodeEnd(agentId, success)
  EvalMgr:endEpisode(agentId, success)
end
```

---

### 3. Game‑Specific Use Case: “Mining Bot”

* **Task**: Mine a target block (diamond) inside a cave.  
* **Metrics**  
  * **Blocks Mined** – must include at least one diamond.  
  * **Time to Target** – ≤ 30 s.  
  * **Distance Traveled** – ≤ 200 m.  
  * **Collision Penalties** – each hit on a wall reduces score.  
* **Evaluation Flow**  
  1. At episode start, set a timer and reset counters.  
  2. Every step, increment distance and block‑break counts.  
  3. If a diamond is broken, set `success=true`.  
  4. At episode end, compute a composite score:  
     ```
     score = 1000 * success
           - 5 * (distance - 200 > 0 ? distance-200 : 0)
           - 10 * (time - 30 > 0 ? time-30 : 0)
           - 20 * collisions
     ```  
  5. Log the score and flag any failures for designer review.

* **Why It Matters** – Designers can quickly see whether a mining bot is wandering too far, taking too long, or ignoring the goal. The log feeds directly into training reward shaping or into an A/B test between two navigation policies.

---

**Bottom line**:  
By giving every AI agent a lightweight, plug‑and‑play Evaluation Manager you turn raw gameplay into measurable data, enabling faster iteration, clearer debugging, and ultimately higher‑quality NPCs in Luanti Voyager.