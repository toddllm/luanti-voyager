# Agent Observability - Implementation Guide (GPT-OSS)

Generated: 2025-08-05T18:20:05.730073
Model: gpt-oss:20b

---

**Agent Observability in Luanti Voyager – Quick‑Start Guide**  
*(≤ 500 words, practical & code‑focused)*  

---

### 1. What is Agent Observability?  
Agent Observability is the systematic exposure of an AI agent’s internal state, decision‑making process, and runtime metrics so that developers can monitor, debug, and optimize the agent in‑game. Think of it as “telemetry + introspection” for NPCs.

---

### 2. How to implement it for game AI agents  
- **Define an `observe()` interface** on every agent class that returns a JSON‑serialisable table of the data you want to expose (health, target, current goal, memory flags, etc.).  
- **Hook the game’s global update loop** to collect and publish this data. Use `minetest.get_modpath("agent_observability")` to register a callback that runs every tick.  
- **Persist or stream the data**:  
  - *In‑game console*: `minetest.chat_send_player("dev", dump(obs))`  
  - *File*: append to a CSV or JSON log (`io.open("agent_log.json", "a")`).  
  - *External*: push to a WebSocket or HTTP endpoint for live dashboards.  
- **Add diagnostic hooks**:  
  - Wrap core decision functions (`select_action`, `plan_path`) with timers (`os.clock()`) and error‑capturing (`pcall`).  
  - Emit events (`minetest.after(0, function() minetest.log("info", "Agent X moved to "..pos) end)`).  
- **Expose visual aids**:  
  - Use `minetest.add_particle()` or `minetest.add_entity()` to draw lines/boxes around the agent’s perceived area.  
  - Toggle with a dev flag (`minetest.settings:get_bool("agent_debug", false)`).  
- **Granular control**: Allow the developer to request a snapshot on demand (e.g., chat command `/agent_snap <id>`).  
- **Version your observability schema** so that log consumers can evolve without breaking compatibility.

---

### 3. One simple code example  
```lua
-- agent_observability/init.lua
local OBS_DIR = minetest.get_worldpath() .. "/agent_obs/"

-- Utility to ensure dir exists
local function ensure_dir()
  local f = io.open(OBS_DIR, "r")
  if not f then
    minetest.mkdir(OBS_DIR)
  end
end

-- Hook into the agent class
local function wrap_agent(cls)
  local orig_select = cls.select_action
  function cls:select_action(...)
    local start = os.clock()
    local action = orig_select(self, ...)
    local elapsed = os.clock() - start

    -- Build observability payload
    local payload = {
      id          = self.id,
      type        = self.type,
      health      = self.health,
      position    = self.object:get_pos(),
      action      = action,
      action_time = elapsed,
      memory      = self.memory,
      timestamp   = os.time()
    }

    -- Persist to file
    local f = io.open(OBS_DIR .. self.id .. ".json", "a")
    f:write(minetest.write_json(payload) .. "\n")
    f:close()

    return action
  end
end

-- Apply to all registered agents on load
minetest.register_on_mods_loaded(function()
  ensure_dir()
  for _, cls in pairs(minetest.registered_entities) do
    if cls.name:match("^agent:") then
      wrap_agent(cls)
    end
  end
end)
```

*Result:* Every time an agent chooses an action, a JSON line is appended to a file named after the agent. A lightweight script can tail these logs and plot behavior over time.

---

### 4. Game‑specific use case  
**Debugging “wandering” guard NPCs**  
- **Problem:** Guards wander aimlessly, sometimes glitching into blocks or getting stuck.  
- **Observability solution:**  
  1. Log `current_goal` and `target_pos` each tick.  
  2. Emit a diagnostic line whenever the guard’s path‑finder returns `nil`.  
  3. Visualize the guard’s perception radius with a semi‑transparent sphere.  
- **Outcome:** By inspecting the log, you’ll see that guards often target the same point repeatedly because of a stale memory flag. Fixing the memory reset logic dramatically reduces wandering, and the visual aid lets designers see the effective field of view in the world.  

With this observability framework in place, you can iterate on AI behavior quickly, spot regressions early, and deliver more predictable, engaging NPCs in Luanti Voyager.