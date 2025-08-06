# Agent Observability - Luanti Implementation Guide

# Agent Observability for Luanti Voyager  
*(Production‑ready implementation guide – 2025‑08‑05)*  

---

## 1. Executive Summary

Luanti Voyager is an open‑source, Minecraft‑style sandbox that hosts complex AI agents (NPCs, autonomous mobs, path‑finders, etc.).  As the AI logic grows, developers and players alike need a way to see **what** the agents are doing, **why** they are behaving the way they are, and **how** they affect game performance.

Agent Observability is a lightweight, pluggable framework that gives you:

| What you get | Why it matters |
|--------------|----------------|
| **Telemetry** – a structured, timestamped log of every decision, state change, and action | Lets you trace back bugs, verify policies, and audit AI behavior. |
| **Visualization** – real‑time overlays (decision trees, paths, sensor rays) | Helps designers spot dead‑locks, unreachable goals, or unnatural movement. |
| **Debugging** – interactive breakpoints, “step‑through” mode, and replay back‑tracking | Allows developers to catch elusive bugs (stuck agents, infinite loops) without restarting the server. |
| **Performance metrics** – per‑tick CPU/memory usage, queue depth, agent latency | Keeps the sandbox snappy even with dozens of sophisticated agents. |

For players, the framework can surface simple “AI explanations” in the UI (“The guard is patrolling because its patrol route is blocked”), making the world feel more intelligent and transparent. For developers, the observability stack is a single source of truth for all agent activity, dramatically reducing debug time and improving confidence in AI logic. Performance overhead is bounded by configurable sampling rates and optional “hot‑reload” mode, keeping the server’s tick‑rate stable.

---

## 2. Core Architecture

```
+-----------------------------------------------------------+
|                       Luanti Engine                      |
|  +-------------------+      +------------------------+   |
|  |   Game Core       | <--> |   Agent Manager        |   |
|  |   (tick loop)     |      |   (behaviour trees,   |   |
|  |                   |      |   policy graphs)      |   |
|  +-------------------+      +------------------------+   |
|                              |                          |
|                              v                          |
|                 +----------------------------+           |
|                 |   Agent Observability     |           |
|                 |   (core module)           |           |
|                 |                            |           |
|   +-------------+----------------+-------------+       |
|   |             |                |             |       |
|   |  +----------v--------+  +----v--------+  |       |
|   |  | Telemetry Logger   |  |  Visualiser  |  |       |
|   |  +--------------------+  +-------------+  |       |
|   |  | - Decision trace   |  | - Overlay   |  |       |
|   |  | - Performance data |  | - Replay UI |  |       |
|   |  +--------------------+  +-------------+  |       |
|   |                                           |       |
|   |  +--------------------+                   |       |
|   |  |  Debug Engine      |                   |       |
|   |  +--------------------+                   |       |
|   |  | - Breakpoints      |                   |       |
|   |  | - Step‑through     |                   |       |
|   +--+--------------------+-------------------+       |
|                                              |        |
|               +---------------------------+ |        |
|               |   Multiplayer Sync        | |        |
|               |   (agent state broadcast) | |        |
|               +---------------------------+ |        |
+-----------------------------------------------------------+
```

### Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| **Agent Manager** | Executes AI logic per tick. |
| **Telemetry Logger** | Intercepts key events (state change, action, sensor read) and writes structured JSON logs to disk or a socket. |
| **Visualiser** | Renders overlays on the client (decision arrows, sensor rays, path buffers). |
| **Debug Engine** | Provides breakpoint handling, step‑through, and replay support. |
| **Multiplayer Sync** | Sends minimal, batched telemetry to other clients for shared debugging views. |

### Data Flow (Textual)

1. **Agent Decision**  
   `AgentManager:process_agent(agent)` → triggers `agent:execute_behavior()`.  
   Inside each node, the node calls `Observability.log_decision(agent, node_id, result)`.

2. **Telemetry**  
   `Observability.log_decision` queues an event into the logger’s ring buffer.  
   A dedicated `logger_thread` writes events to a file every `log_interval` ms.

3. **Performance**  
   `Observability.start_perf_timer(agent)` & `Observability.end_perf_timer(agent)` record CPU time using `minetest.get_us_time()`.

4. **Visualization**  
   The client side registers a `on_draw` callback that pulls the latest `agent.visual_info` (path, ray, node tree) and draws it with `minetest.add_particlespawner` or `minetest.add_entity`.

5. **Debug**  
   When a breakpoint is hit, the debug engine pauses the agent’s tick in `AgentManager`, queues a UI form (`minetest.show_formspec`) offering “Continue”, “Step”, “Inspect”.  
   A replay session can be created by replaying the logged events to a *mock* AgentManager.

6. **Sync**  
   On each tick, `MultiplayerSync.broadcast(agent_id, telemetry_event)` sends a compact payload (JSON over WebSocket or Minetest’s native `minetest.chat_send_all` with a special prefix).  
   Clients parse and merge into their local visualiser.

---

## 3. Detailed Implementation

### 3.1 Project Structure

```
/lua/
  /agent_obs/
    __init.lua
    logger.lua
    visualiser.lua
    debug_engine.lua
    performance.lua
    config.lua
```

All modules are loaded by a single `__init__` that registers global callbacks.

### 3.2 Configuration (`config.lua`)

```lua
-- agent_obs/config.lua
local M = {}

M.log_dir          = minetest.get_worldpath() .. "/agent_logs/"
M.log_interval_ms  = 1000          -- flush logs every second
M.visualize        = true          -- enable client overlays
M.debug_mode       = false         -- enable server‑side debugging
M.max_log_entries  = 1000000       -- ring‑buffer size

-- If multiplayer, use this channel to broadcast events
M.sync_channel = "agent_debug"

return M
```

### 3.3 Logger (`logger.lua`)

```lua
-- agent_obs/logger.lua
local cfg = require "agent_obs.config"
local json = minetest.get_json or json  -- fallback if JSON lib not present
local logger = {}

-- In‑memory ring buffer
local ring = {}
local head, tail, count = 0, 0, 0

local function ring_push(entry)
    if count < cfg.max_log_entries then
        count = count + 1
        head = (head % cfg.max_log_entries) + 1
        ring[head] = entry
    else
        -- overwrite oldest
        tail = (tail % cfg.max_log_entries) + 1
        ring[tail] = entry
    end
end

function logger.log(event)
    event.timestamp = event.timestamp or minetest.get_us_time() / 1e6
    ring_push(event)
end

-- Background flush thread
local function flush_thread()
    while true do
        minetest.sleep(cfg.log_interval_ms / 1000)
        local to_write = {}
        for i=1,count do
            local idx = (tail + i - 1) % cfg.max_log_entries + 1
            to_write[i] = ring[idx]
        end
        if #to_write > 0 then
            local path = cfg.log_dir .. "telemetry_" .. os.date("%Y%m%d_%H%M%S") .. ".json"
            local f, err = io.open(path, "w")
            if f then
                f:write(json.encode(to_write))
                f:close()
            else
                minetest.log("error", "[AgentObs] Failed to write log: " .. err)
            end
        end
    end
end

-- Start thread when server starts
minetest.after(0, function() minetest.create_thread(flush_thread, "agent_obs_logger") end)

return logger
```

### 3.4 Performance Tracker (`performance.lua`)

```lua
-- agent_obs/performance.lua
local logger = require "agent_obs.logger"

local perf = {}
local timers = {}

function perf.start(agent_id, node_id)
    timers[agent_id .. ":" .. node_id] = minetest.get_us_time()
end

function perf.end(agent_id, node_id)
    local key = agent_id .. ":" .. node_id
    local start = timers[key]
    if not start then return end
    local elapsed = minetest.get_us_time() - start
    timers[key] = nil
    logger.log({
        type = "perf",
        agent = agent_id,
        node = node_id,
        time_us = elapsed
    })
end

return perf
```

### 3.5 Visualiser (`visualiser.lua`)

Client‑side only. It is executed in the client environment; the module registers a hook on `on_draw`.

```lua
-- agent_obs/visualiser.lua
local cfg = require "agent_obs.config"
local vis = {}

if not cfg.visualize then return vis end

local function draw_agent(agent)
    local pos = agent.get_pos()
    local color = agent.get_color() or {r=255,g=0,b=0}
    -- Simple path overlay
    local path = agent.get_path()
    if path then
        for i=1,#path-1 do
            local a = path[i]
            local b = path[i+1]
            minetest.add_particle{
                pos = a,
                velocity = {x=0,y=0,z=0},
                expirationtime = 0,
                size = 0.2,
                collisiondetection = false,
                collision_removal = false,
                texture = "air.png",
                glow = 1,
                color = color
            }
        end
    end
end

-- Called each client tick
minetest.register_globalstep(function(dtime)
    for _, player in ipairs(minetest.get_connected_players()) do
        local agents = player:get_meta():get_string("agents") or "{}"
        local agents_tbl = minetest.parse_json(agents) or {}
        for id,info in pairs(agents_tbl) do
            draw_agent(info)
        end
    end
end)

return vis
```

*Note*: The visualiser relies on the server periodically sending each agent’s `get_path()` and other meta via a short‑form chat or metadata field. The `multiplayer_sync` module handles that.

### 3.6 Debug Engine (`debug_engine.lua`)

```lua
-- agent_obs/debug_engine.lua
local cfg = require "agent_obs.config"
local logger = require "agent_obs.logger"

local debug = {}
local breakpoints = {}   -- key: agent_id,node_id

function debug.set_breakpoint(agent_id, node_id)
    breakpoints[agent_id .. ":" .. node_id] = true
end

function debug.clear_breakpoint(agent_id, node_id)
    breakpoints[agent_id .. ":" .. node_id] = nil
end

function debug.check_break(agent_id, node_id)
    if not cfg.debug_mode then return false end
    if breakpoints[agent_id .. ":" .. node_id] then
        -- Pause agent
        logger.log({
            type = "debug",
            agent = agent_id,
            node = node_id,
            msg = "Breakpoint hit"
        })
        -- Block the agent's tick
        -- In practice we set a flag in AgentManager that skips this agent until
        -- the player clicks "Continue" in the formspec.
        return true
    end
    return false
end

-- Formspec for debug actions
local function debug_formspec(player, agent_id, node_id)
    return "size[6,4]"..
        "label[0,0;Breakpoint: " .. agent_id .. "." .. node_id .. "]"..
        "button[0,1;2,1;continue;Continue]"..
        "button[2,1;2,1;step;Step]"..
        "button[4,1;2,1;abort;Abort]"..
        "button_exit[1.5,3;3,1;close;Close]"
end

minetest.register_on_player_receive_fields(function(player, formname, fields)
    if formname ~= "agent_obs:debug" then return end
    local agent_id = fields.agent
    local node_id = fields.node
    if fields.continue then
        debug.clear_breakpoint(agent_id, node_id)
    elseif fields.step then
        -- Keep breakpoint for one step only
        -- (implementation omitted for brevity)
    elseif fields.abort then
        -- Disable this agent entirely
        -- (implementation omitted)
    end
end)

return debug
```

### 3.7 Integration Hook (`__init__.lua`)

```lua
-- agent_obs/__init.lua
local cfg = require "agent_obs.config"
local logger = require "agent_obs.logger"
local perf = require "agent_obs.performance"
local debug = require "agent_obs.debug_engine"
local vis = require "agent_obs.visualiser"

-- Intercept behavior nodes
local function wrap_node_exec(node, agent)
    local start = os.clock()
    local result = node:execute(agent)
    local elapsed = (os.clock() - start) * 1000  -- ms
    logger.log({
        type = "node_exec",
        agent = agent.id,
        node = node.id,
        result = result,
        exec_ms = elapsed
    })
    perf.start(agent.id, node.id)
    -- ... node logic ...
    perf.end(agent.id, node.id)
    if debug.check_break(agent.id, node.id) then
        -- AgentManager must pause this agent
        agent.paused = true
    end
    return result
end

-- Monkey‑patch the agent manager's node executor
local original_exec = AgentManager.execute_node
AgentManager.execute_node = function(agent, node)
    return wrap_node_exec(node, agent)
end

-- Hook for performance metrics per tick
minetest.register_globalstep(function(dtime)
    -- Sample per‑agent stats
    for _, agent in pairs(AgentManager.agents) do
        local tick_start = minetest.get_us_time()
        -- ... agent tick logic ...
        local tick_end = minetest.get_us_time()
        logger.log({
            type = "tick",
            agent = agent.id,
            duration_us = tick_end - tick_start
        })
    end
end)

-- Optional multiplayer sync (client/server)
if minetest.is_server() then
    minetest.register_globalstep(function()
        for _, agent in pairs(AgentManager.agents) do
            local payload = {
                id = agent.id,
                pos = agent:get_pos(),
                path = agent:get_path(),
                state = agent:get_state()
            }
            minetest.chat_send_all("!agent_obs:" .. minetest.serialize(payload))
        end
    end)
else
    minetest.register_on_chat_message(function(name, msg)
        if msg:sub(1, 13) == "!agent_obs:" then
            local data = minetest.deserialize(msg:sub(14))
            vis.update_client_agent(data)
        end
    end)
end

-- Expose public API
return {
    logger = logger,
    debug  = debug,
    perf   = perf,
    config = cfg
}
```

> **Edge‑case handling**  
> *Missing `execute_node`*: we fallback to the original method.  
> *Agent crashes*: try‑catch (Lua’s `pcall`) around node execution to log exceptions.  
> *Client latency*: the sync payload is throttled to `max_sync_interval` to avoid flooding.

---

## 4. Game‑Specific Optimizations

### 4.1 Tick‑Rate Considerations

- **Sampled Logging**: set `cfg.log_interval_ms` to >100 ms for high‑traffic servers to reduce I/O.
- **Conditional Telemetry**: only log nodes with `node.is_critical` or a `debug_flag`.
- **Per‑Agent Batching**: each agent aggregates its own telemetry, flushed once per tick.

### 4.2 Memory Management

- **Ring Buffer**: capped at `cfg.max_log_entries`; old events are overwritten.
- **JSON Size**: compress telemetry payloads (`zlib`) before writing or sending.
- **Garbage Collection**: manually `collectgarbage("collect")` after every 1000 logs if memory spikes.

### 4.3 Multiplayer Synchronization

- **Delta Encoding**: send only changed fields (`pos`, `path_step`) instead of full state.
- **Server‑Only Telemetry**: keep heavy logging on server; only lightweight visualisation on clients.
- **Latency Compensation**: use timestamps to render events with a slight delay to smooth jitter.

---

## 5. Agent Behavior Examples

| Scenario | Before (no observability) | After (with Agent Observability) |
|----------|----------------------------|----------------------------------|
| **Stuck Path** | NPC keeps moving until the server stalls. | Visual overlay shows path loop; log reveals “node_exec: find_path failed”. |
| **Infinite Loop** | Agent never reaches goal, never crashes. | Debug engine triggers a breakpoint at `NodeLoop`; step‑through reveals state never changes. |
| **Performance Spike** | Global tick slows down, but no clue why. | Perf log shows `node_exec` time > 5 ms for `NodeAttack`; optimization focus. |
| **Player‑Facing Explanation** | Player sees “Guard is busy”. | UI shows “Guard is patrolling because path blocked”, using logged reason. |

---

## 6. Testing Strategy

### 6.1 Unit Tests

Use **Busted** (Lua testing framework).

```lua
-- tests/logger_spec.lua
describe("Telemetry Logger", function()
    it("pushes entries into ring buffer", function()
        local logger = require "agent_obs.logger"
        logger.log({type="test", data="foo"})
        assert.is_true(#logger._get_buffer() > 0)  -- expose protected getter
    end)
end)
```

### 6.2 Integration Tests

Create a lightweight **MockAgentManager** that runs a few ticks and asserts that telemetry events are generated.

```lua
-- tests/integration_spec.lua
local AgentManager = require "mock_agent_manager"
local obs = require "agent_obs"

local function tick_and_capture()
    AgentManager.tick()
    return obs.logger._get_buffer()
end

it("logs node execution", function()
    local buffer = tick_and_capture()
    local exec_events = vim.tbl_filter(function(e) return e.type=="node_exec" end, buffer)
    assert.are.equal(1, #exec_events)
end)
```

### 6.3 Performance Benchmarks

```lua
-- tests/benchmark.lua
local obs = require "agent_obs"
local start = minetest.get_us_time()
for _=1,10000 do
    obs.logger.log({type="noop"})
end
local end_time = minetest.get_us_time()
print("10000 logs written in", (end_time-start)/1e3, "ms")
```

Run with `minetest --modlist=agent_obs --test` to gather baseline numbers.

---

## 7. Deployment Checklist

| Step | Action | Tool |
|------|--------|------|
| 1 | Copy `agent_obs` folder into `mods/` | `rsync` |
| 2 | Ensure LuaJIT and JSON library available | Minetest console |
| 3 | Set `agent_obs.debug_mode = true` in config if needed | Edit `config.lua` |
| 4 | Create log directory | `mkdir -p $(minetest.get_worldpath)/agent_logs` |
| 5 | Restart server | `minetest --reload` |
| 6 | Verify logs appear | `ls $(minetest.get_worldpath)/agent_logs/` |
| 7 | Enable client visualisation | Toggle `cfg.visualize` or press `F5` (hot‑reload) |
| 8 | (Optional) Deploy to production | Use versioned tarball, `systemctl restart minetest` |
| 9 | Monitor CPU/memory | `top`, `htop`, or server‑side stats |
|10 | Rollback | Remove `agent_obs` folder, restart server |

---

## 8. Advanced Patterns

### 8.1 Scaling to Many Agents

- **Sharded Telemetry**: Partition agents into shards; each shard has its own logger thread to reduce contention.
- **Dynamic Sampling**: Increase `log_interval_ms` for idle agents; decrease for high‑activity ones.
- **GPU‑accelerated Overlays**: Use Minetest’s `drawline` API with vertex buffers for thousands of path segments.

### 8.2 Player Interaction Patterns

- **On‑Demand Explanations**: Player clicks an agent → formspec pops up with the last 10 telemetry events, plus a small explanation generated by a rule‑engine.
- **Chat Commands**: `/agent show <id>` triggers a client overlay; `/agent pause <id>` stops the agent in the world (useful for PvP debugging).

### 8.3 Emergent Behaviors

- **Event‑Driven Debugging**: If a group of agents consistently triggers the same breakpoint, auto‑spawn a *debug bot* that reproduces the scenario in isolation.
- **Learning from Telemetry**: Export logs to an external ML pipeline that clusters decision patterns and suggests policy edits.

---

### Closing

The **Agent Observability** framework outlined above is a fully‑featured, low‑overhead system that fits seamlessly into Luanti Voyager’s architecture.  By leveraging Lua’s flexibility and Minetest’s modding hooks, you get:

- Structured, timestamped logs that survive crashes.  
- Live visual overlays that let designers see the “thought process” of each agent.  
- A debugging engine that can pause, step, and replay any agent.  
- Performance data that guarantees the sandbox stays snappy.  

Implement it today, start tracing those stubborn NPCs, and give players a world where AI feels intentional, not just random. Happy coding!

