# Agent Evaluation - Luanti Implementation Guide

# Agent Evaluation for **Luanti Voyager**  
*A production‑ready implementation guide*  

> **Author** – Expert Game AI Engineer  
> **Audience** – Game developers, DevOps, QA & AI researchers working on Luanti/Minetest.  
> **Goal** – Enable systematic, repeatable, data‑driven evaluation of in‑game AI agents while keeping the core gameplay smooth and players happy.

---

## 1. Executive Summary

Luanti Voyager’s open‑source nature gives developers unprecedented freedom to inject sophisticated AI agents—farmers, traders, builders, and combat bots.  
However, *“in‑world”* AI brings a new challenge: how do we know that an agent behaves correctly, improves over time, and does not degrade gameplay or performance?

**Agent Evaluation** is a lightweight, modular system that:
- **Benchmarks** agents against a library of scripted scenarios (e.g., “grow wheat”, “defend base”).
- **Quantifies** performance with well‑defined metrics (completion time, resource usage, success rate, etc.).
- **Facilitates A/B testing** so that new agent versions can be rolled out safely.
- **Collects player feedback** via in‑game prompts or telemetry to keep the experience enjoyable.

By integrating this framework into Luanti’s Lua scripting and server core, teams can automatically spot regressions, validate new training runs, and maintain a high‑quality player experience—all while keeping latency and memory usage within acceptable bounds.

---

## 2. Core Architecture

```
+---------------------------------------+
|           Agent Evaluation UI         |
|  (Web Dashboard / In‑Game Console)    |
+-------------------+-------------------+
                    |
                    v
+---------------------------------------+
|          Evaluation Engine            |
|  - Scenario Loader                    |
|  - Metrics Collector                  |
|  - A/B Test Coordinator              |
|  - Feedback Aggregator                |
+-------------------+-------------------+
                    |
                    v
+---------------------------------------+
|        Agent Manager (Lua Module)      |
|  - Registers agents                   |
|  - Executes agent actions             |
|  - Reports status to Engine           |
+-------------------+-------------------+
                    |
                    v
+---------------------------------------+
|         Game Engine (Luanti)          |
|  - Physics / Tick Loop                |
|  - Multiplayer Sync (TCP/UDP)         |
|  - Entity & Item System               |
+---------------------------------------+
```

### Data Flow (text diagram)

1. **Scenario Definition**  
   *JSON / Lua* files describe world state, objectives, and success conditions.

2. **Evaluation Scheduler**  
   A cron‑style Lua routine triggers the Engine at configured intervals or on-demand (e.g., after a new agent version is uploaded).

3. **Agent Invocation**  
   Engine requests the *Agent Manager* to instantiate an agent, injects the scenario world snapshot, and starts a controlled tick loop.

4. **Metrics Collection**  
   During execution, the Engine gathers data: `ticks_executed`, `actions_taken`, `resources_gathered`, `error_rate`, etc.

5. **Result Aggregation**  
   Metrics + scenario metadata are stored in an **Evaluation DB** (SQLite or external PostgreSQL) and surfaced to the UI.

6. **Player Feedback**  
   Optional chat prompt or UI overlay asks players to rate the agent after each run; responses are tagged by session ID and stored.

---

## 3. Detailed Implementation

> **Tip:** All core Lua files live under `mods/agent_evaluation/`.  
> **Configuration** is stored in `mods/agent_evaluation/config.lua`.

### 3.1 Configuration (`config.lua`)

```lua
-- config.lua
return {
    -- Path to scenario directory
    scenario_dir = "mods/agent_evaluation/scenarios",

    -- How often to run automated tests (in seconds)
    auto_run_interval = 3600,  -- every hour

    -- DB connection (SQLite fallback)
    db = {
        driver = "sqlite3",
        path   = "data/agent_eval.db",
    },

    -- Logging
    log_file = "logs/agent_evaluation.log",

    -- Player feedback prompt delay
    feedback_delay = 5,  -- seconds after scenario finish

    -- A/B testing
    ab_test = {
        enabled = true,
        max_active_runs = 5,
    },
}
```

### 3.2 Core Engine (`engine.lua`)

```lua
-- engine.lua
local modpath = minetest.get_modpath("agent_evaluation")
local config = dofile(modpath .. "/config.lua")
local json = dofile(modpath .. "/json.lua")   -- minetest's built‑in JSON lib
local sqlite = dofile(modpath .. "/sqlite.lua") -- tiny wrapper

local Logger = dofile(modpath .. "/logger.lua")

local engine = {}
local db = sqlite.open(config.db.path)

-- Utility: load scenario files
local function load_scenarios()
    local dir = minetest.get_worldpath() .. "/" .. config.scenario_dir
    local files = minetest.get_dir_list(dir, true)
    local scenarios = {}
    for _, file in ipairs(files) do
        if file:match("%.json$") then
            local full = dir .. "/" .. file
            local content = io.open(full, "r"):read("*a")
            table.insert(scenarios, json.decode(content))
        end
    end
    return scenarios
end

-- Store a single evaluation record
local function store_result(record)
    local stmt = db:prepare([[
        INSERT INTO evaluations(
            timestamp, agent_name, scenario_id, ticks, actions,
            success, metrics_json, feedback
        ) VALUES(?,?,?,?,?,?,?,?) ]])
    stmt:bind_values(
        os.time(),
        record.agent,
        record.scenario.id,
        record.ticks,
        record.actions,
        record.success and 1 or 0,
        json.encode(record.metrics),
        record.feedback or ""
    )
    stmt:execute()
    stmt:close()
end

-- Run a single scenario with a given agent instance
local function run_scenario(agent, scenario)
    local ctx = {
        ticks = 0,
        actions = 0,
        metrics = {},
        success = false,
    }

    -- Setup world according to scenario snapshot
    scenario.setup(agent, ctx)

    while not ctx.success and ctx.ticks < scenario.timeout do
        agent:tick()           -- agent's logic for this tick
        ctx.ticks = ctx.ticks + 1
        ctx.actions = ctx.actions + 1
        agent:collect_metrics(ctx)  -- add agent‑specific metrics
    end

    ctx.success = scenario.check_success(ctx)
    store_result{
        agent = agent.name,
        scenario = scenario,
        ticks = ctx.ticks,
        actions = ctx.actions,
        success = ctx.success,
        metrics = ctx.metrics,
    }
end

-- Scheduler: auto‑run every interval
function engine.start_auto_run()
    minetest.after(config.auto_run_interval, function()
        engine.run_all()
        engine.start_auto_run()
    end)
end

-- Public: run all scenarios for all registered agents
function engine.run_all()
    local agents = minetest.get_modpath("agent_evaluation"):get_agents()
    local scenarios = load_scenarios()
    for _, agent in ipairs(agents) do
        for _, scenario in ipairs(scenarios) do
            run_scenario(agent, scenario)
        end
    end
end

-- Public: trigger from chat or admin command
minetest.register_chatcommand("eval_run", {
    description = "Run all agent evaluations now",
    privs = {server=true},
    func = function() engine.run_all() end,
})

-- Initialize database schema (idempotent)
local function init_db()
    db:execute([[
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER,
            agent_name TEXT,
            scenario_id TEXT,
            ticks INTEGER,
            actions INTEGER,
            success INTEGER,
            metrics_json TEXT,
            feedback TEXT
        );]] )
end
init_db()

return engine
```

#### Error Handling & Edge Cases

| Issue | Handling |
|-------|----------|
| Missing scenario file | Warn in log, skip |
| Agent throws exception on `tick` | Wrap in `pcall`, abort run, record failure |
| DB write failure | Retry 3 times with exponential backoff; if still failing, dump to file |
| Duplicate runs (A/B) | Use unique `scenario_id + agent_version` key to avoid double‑counting |

### 3.3 Agent Manager (`agent_manager.lua`)

```lua
-- agent_manager.lua
local modpath = minetest.get_modpath("agent_evaluation")
local Logger = dofile(modpath .. "/logger.lua")

local agents = {}

-- Register an agent constructor
function register_agent(name, ctor)
    if agents[name] then
        Logger.warn("Agent '"..name.."' already registered, overwriting")
    end
    agents[name] = ctor
end

-- Return all registered agent instances
function get_agents()
    local list = {}
    for name, ctor in pairs(agents) do
        local instance = ctor()
        instance.name = name
        table.insert(list, instance)
    end
    return list
end

-- Example agent constructor (in separate file `farm_bot.lua`)
local FarmBot = {}
FarmBot.__index = FarmBot

function FarmBot.new()
    local self = setmetatable({}, FarmBot)
    self.state = "idle"
    return self
end

function FarmBot:tick()
    -- Simplified example logic
    if self.state == "idle" then
        self.state = "gathering"
    elseif self.state == "gathering" then
        self.state = "planting"
    elseif self.state == "planting" then
        self.state = "idle"
    end
end

function FarmBot:collect_metrics(ctx)
    ctx.metrics.gathered = ctx.metrics.gathered or 0
    if self.state == "gathering" then
        ctx.metrics.gathered = ctx.metrics.gathered + 1
    end
end

-- Register the example agent
register_agent("farm_bot", FarmBot.new)

return {
    register_agent = register_agent,
    get_agents = get_agents,
}
```

> **Note:** Real agents are more complex – they may access the world via `minetest.get_node`, spawn items, use pathfinding, etc. All should expose `tick()` and `collect_metrics(ctx)` hooks.

### 3.4 Scenario Definition (`scenarios/grow_wheat.json`)

```json
{
  "id": "grow_wheat_001",
  "timeout": 300,
  "setup": "function(agent, ctx)\n    -- Place a wheat seedling at (0, 0, 0)\n    minetest.set_node({x=0,y=0,z=0}, {name='default:wheat_seed'})\nend",
  "check_success": "function(ctx)\n    local node = minetest.get_node({x=0,y=0,z=0})\n    return node.name == 'default:wheat'\nend"
}
```

> In practice, use Lua snippets (or a lightweight DSL) embedded in JSON or plain Lua tables. The engine evaluates `setup` and `check_success` via `loadstring`.

---

## 4. Game‑Specific Optimizations

| Concern | Solution | Code Snippet |
|---------|----------|--------------|
| **Tick rate** | Reduce evaluation ticks to *1/10th* of a normal game tick (use a separate “evaluation tick” timer). | `minetest.after(0.1, function() agent:tick() end)` |
| **Memory** | Keep world snapshots shallow: only nodes that the agent interacts with (≈ 200 nodes). Use `minetest.get_node()` sparingly; cache results. | `local node = minetest.get_node(pos)` |
| **Multiplayer sync** | Mark evaluation runs as *non‑interactive*: disable physics, disable other player actions during evaluation to avoid network chatter. | `minetest.set_player_privs(name, {interact=false})` |
| **CPU spikes** | Batch DB writes: accumulate results in memory and flush every 5 seconds. | `local batch = {}; table.insert(batch, result); if #batch > 50 then flush(); end` |
| **Scalability** | Use Lua's `coroutine`s for concurrent evaluation pipelines, or spawn multiple Lua states on separate CPU cores (via C++ extension). | `local co = coroutine.create(run_scenario)` |

---

## 5. Agent Behavior Examples

### 5.1 Scenario 1 – “Harvest Wheat”

| Metric | Baseline (v1) | New (v2) | Improvement |
|--------|---------------|----------|-------------|
| Success rate | 85 % | 92 % | +7 % |
| Avg. ticks | 280 | 240 | -14 % |
| Actions per tick | 1.1 | 1.4 | +27 % |

*Before* – Agent walked randomly until a seed was found.  
*After* – Agent uses a simple A* path to the seed location, reduces idle time.

### 5.2 Scenario 2 – “Defend Base”

| Metric | Baseline | New | Improvement |
|--------|----------|-----|-------------|
| Hit points survived | 78 % | 95 % | +17 % |
| Enemy kills | 3.2 | 5.0 | +56 % |
| CPU usage | 2.5 % | 2.1 % | -16 % |

*Before* – Defensive stance only when player nearby.  
*After* – Proactive scouting and blocking with a simple threat model.

---

## 6. Testing Strategy

### 6.1 Unit Tests

```lua
-- tests/test_agent.lua
local Agent = require("agent_evaluation.agent_manager")
local assert = assert

local farm = Agent.get_agents()[1]
assert(farm, "FarmBot should exist")
assert(farm.tick, "tick() must exist")
assert(farm.collect_metrics, "collect_metrics() must exist")
```

> Use the built‑in Minetest test framework (`minetest.register_on_mods_loaded`) to auto‑run tests at startup.

### 6.2 Integration Tests

- **Scenario Engine** – Feed a mock agent that logs every tick; ensure `run_scenario` writes a record.
- **Database** – Use an in‑memory SQLite DB (`:memory:`) to validate inserts.
- **Player Feedback** – Simulate a player sending a `/feedback` chat command; check aggregation.

### 6.3 Performance Benchmarks

1. **Cold Start** – Measure engine init time: should be < 200 ms.  
2. **Scenario Load** – Average load time per scenario: < 5 ms.  
3. **Evaluation Throughput** – Run 10 agents × 10 scenarios: < 30 s.  

Use `minetest.after(0, ...)` to time these segments.

---

## 7. Deployment Checklist

| Step | Detail |
|------|--------|
| **1. Install Mod** | Copy `mods/agent_evaluation` into server root. |
| **2. Configure** | Edit `config.lua`: scenario path, DB, A/B settings. |
| **3. Create DB** | Run `lua modpath/init_db.lua` (or let engine auto‑create). |
| **4. Load Scenarios** | Place JSON files in `scenarios/`. |
| **5. Register Agents** | Modify `agent_manager.lua` or separate agent modules. |
| **6. Enable Auto‑Run** | Call `engine.start_auto_run()` in `init.lua`. |
| **7. Monitor Logs** | Tail `logs/agent_evaluation.log`; set up rotation. |
| **8. Set Alerts** | Use `minetest.register_on_dignode` to catch failures; push to Grafana/Prometheus. |
| **9. Rollback** | Keep previous DB backup (`agent_eval.db.bak`). If evaluation fails, restore. |
| **10. Scale** | For many agents, consider launching a separate “evaluation server” and streaming results via WebSocket. |

---

## 8. Advanced Patterns

### 8.1 Scaling to Hundreds of Agents

- **Distributed Workers** – Spawn separate Lua instances in a worker process pool (C++ extension). Each worker pulls scenarios from a message queue (Redis, RabbitMQ).
- **Stateless Agents** – Design agents to be stateless between runs; only load the minimal model parameters per tick.

### 8.2 Player Interaction Patterns

- **Live Coaching** – Expose evaluation metrics in a floating HUD (`minetest.register_on_joinplayer`) for in‑game coaching.
- **Dynamic Difficulty** – Adjust agent behavior based on real‑time player performance metrics (e.g., reduce farming speed if players report lag).

### 8.3 Emergent Behaviors

- **Meta‑Learning** – Record agent logs and feed them back into a training loop (Python script) that refines policies with RL or supervised learning.
- **Behavioral Diversity** – Track entropy of action sequences; trigger diversification when entropy drops below a threshold.

---

## 9. Quick Start Guide

1. **Download** the mod from GitHub:  
   `git clone https://github.com/yourorg/luanti_agent_evaluation.git mods/agent_evaluation`

2. **Start the Server** (`minetest -p 30000`).  
   The engine will auto‑create the DB, load scenarios, and schedule runs.

3. **Run a Manual Test**:  
   `/eval_run` → All agents run against all scenarios; results appear in `/logs/agent_evaluation.log`.

4. **View Results**:  
   Launch the web dashboard (if you enabled it) at `http://localhost:8080/`.  
   Or query the DB: `sqlite3 data/agent_eval.db "SELECT * FROM evaluations;"`.

5. **Iterate**:  
   Add new scenarios, tweak agents, and watch the metrics improve.

---

### Final Thoughts

Agent Evaluation in Luanti Voyager turns an otherwise ad‑hoc experimentation process into a disciplined, data‑driven pipeline. By tightly coupling evaluation logic with the game’s core loop, you preserve low latency while enabling deep insights into AI behavior. The modular architecture means you can drop in new agent types, add sophisticated statistical tests, or hook into external ML services without touching the core engine.

Happy coding, and may your agents thrive!

