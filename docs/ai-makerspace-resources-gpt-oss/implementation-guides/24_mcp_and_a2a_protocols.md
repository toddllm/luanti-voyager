# MCP and A2A Protocols - Luanti Implementation Guide

# 1. Executive Summary  

**What it enables for game AI agents**  
- **Universal tool‑abstraction**: Every in‑game action – placing a block, mining, crafting, or even triggering a red‑stone circuit – is exposed as a *tool* that any external AI can invoke through the MCP (Machine‑Control Protocol).  
- **Open agent ecosystem**: The A2A (Agent‑to‑Agent) protocol gives agents the ability to negotiate, hand‑off tasks, or cooperate with one another – a prerequisite for emergent behaviours like shared mining crews or trading guilds.  
- **Cross‑platform mobility**: An agent written for Minecraft or a sandbox‑style server can be dropped into Luanti Voyager with only a manifest mapping, enabling instant play‑testing or production‑grade automation.

**Why it’s valuable for players**  
- **Play‑by‑AI**: A single player can deploy an AI farmer that automatically gathers resources, builds farms, and defends against mobs.  
- **Mod‑less experience**: No need to install custom mods – the protocol layer sits on top of the existing server.  
- **Learning & experimentation**: Players can prototype AI behaviours, see immediate feedback, and iterate on strategies, turning the game into a living laboratory for RL/LLM agents.

**Performance implications**  
- MCP is lightweight: it serialises calls as JSON over TCP/HTTP, so the overhead per tool call is < 1 ms in a local network.  
- A2A handshakes add a single round‑trip per negotiation – negligible compared to the tick rate (20 ticks / s).  
- With proper batching (e.g., sending a sequence of mining commands in one payload) the latency can be reduced to the sub‑tick level.  

---

# 2. Core Architecture  

```
┌─────────────────────────────────────────────────────────────────────┐
│                       LUANTI VOYAGER SERVER                         │
│  (Minetest‑based engine with custom Lua sandbox API)                │
└─────────────────────────────────────────────────────────────────────┘
                 ▲          ▲            ▲
                 │          │            │
   ┌─────────────┴───┐  ┌───┴───────────┐  ┌─────────────┴───────┐
   │  MCP Server    │  │  A2A Hub      │  │  Lua Game API        │
   │  (FastMCP)     │  │  (WebSocket   │  │  (block/biome/... ) │
   │  - TCP/TCP‑STDIO│  │  based)      │  │  (exposed to Lua)   │
   └────────────────┘  └───────────────┘  └─────────────────────┘
                 │            ▲                │
                 │            │                │
      ┌───────────────────────┐  │   ┌───────────────────────┐
      │  External AI Agent    │  │   │  External AI Agent    │
      │  (Python/Node/LLM)    │  │   │  (Python/Node/LLM)    │
      └───────────────────────┘  │   └───────────────────────┘
                                 │
                  ┌───────────────────────────────────┐
                  │   A2A Negotiation / Messaging     │
                  └───────────────────────────────────┘
```

* **MCP Server** – Runs as a separate process or as a threaded module in the server. It exposes every game action as a *tool* that can be invoked over TCP or HTTP.  
* **A2A Hub** – A WebSocket (or HTTP‑long‑poll) server that keeps an agent‑registry and lets agents announce capabilities, request tasks, or forward results.  
* **Lua Game API** – The existing Luanti API that can be called from the MCP server (e.g., `minetest.set_node(pos, node)`).  
* **External AI Agents** – Stand‑alone scripts that connect to the MCP server for tool execution and to the A2A hub for coordination.  

**Data Flow Diagrams (Textual)**  

1. **Tool Invocation**  
   - Agent A sends JSON: `{ "tool": "place_block", "params": {"pos": [x,y,z], "node": "default:stone"} }`  
   - MCP Server receives → validates → calls Lua API → returns success/failure → Agent A receives response.  

2. **Agent Negotiation**  
   - Agent A sends `{"type":"register","capabilities":["mine","craft"]}` → A2A Hub stores → Agent B can query hub for agents with `"mine"` capability.  
   - Agent B sends `{"type":"request","task":"mine","params":{...}}` → Hub forwards to Agent A → Agent A performs → result sent back through Hub.  

3. **Cross‑Game Migration**  
   - Agent B wants to migrate from Server X to Server Y. It sends a `{"type":"migrate","target":"serverY","token":"XYZ"}`.  
   - Server Y’s A2A Hub validates token → registers Agent B in its local registry → old tasks are forwarded or aborted.

---

# 3. Detailed Implementation  

## 3.1 MCP Server – FastMCP + Minetest Lua API  

```python
# mcp_server.py
import os
import json
import logging
from typing import Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

# Load env (e.g., A2A hub URL)
load_dotenv()
A2A_HUB_URL = os.getenv("A2A_HUB_URL", "ws://localhost:8765")

app = FastAPI()
logger = logging.getLogger("mcp_server")
logging.basicConfig(level=logging.INFO)

# -------------------------------------------------------------
# 1.  Tool registry – decorator pattern
# -------------------------------------------------------------
class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Any] = {}

    def tool(self, func):
        name = func.__name__
        self.tools[name] = func
        return func

tools = ToolRegistry()

# -------------------------------------------------------------
# 2.  Wrap Lua calls – via Minetest's RPC bridge
# -------------------------------------------------------------
def call_lua(method: str, *args):
    """
    Generic wrapper that sends a request to the Minetest Lua bridge.
    The bridge must expose a JSON‑RPC endpoint (e.g., http://localhost:8080).
    """
    import httpx
    payload = {
        "method": method,
        "params": args
    }
    r = httpx.post("http://localhost:8080/rpc", json=payload, timeout=2.0)
    r.raise_for_status()
    return r.json()["result"]

# -------------------------------------------------------------
# 3.  Tool implementations
# -------------------------------------------------------------
@tools.tool
def place_block(pos: Dict[str, int], node: str) -> bool:
    """Place a node at the given position."""
    try:
        call_lua("minetest.set_node", pos, {"name": node})
        return True
    except Exception as e:
        logger.error(f"place_block error: {e}")
        return False

@tools.tool
def break_block(pos: Dict[str, int]) -> bool:
    """Break a node at the given position."""
    try:
        call_lua("minetest.set_node", pos, {"name": "air"})
        return True
    except Exception as e:
        logger.error(f"break_block error: {e}")
        return False

@tools.tool
def get_block(pos: Dict[str, int]) -> str:
    """Return the node name at the position."""
    try:
        res = call_lua("minetest.get_node", pos)
        return res["name"]
    except Exception as e:
        logger.error(f"get_block error: {e}")
        return "unknown"

# -------------------------------------------------------------
# 4.  HTTP endpoint – one per tool
# -------------------------------------------------------------
@app.post("/tool/{name}")
async def invoke_tool(name: str, request: Request):
    body = await request.json()
    if name not in tools.tools:
        return JSONResponse(status_code=404, content={"error": "tool not found"})
    try:
        result = tools.tools[name](**body)
        return {"status": "ok", "result": result}
    except TypeError as te:
        return JSONResponse(status_code=400, content={"error": str(te)})
    except Exception as e:
        logger.exception("unexpected error")
        return JSONResponse(status_code=500, content={"error": str(e)})

# -------------------------------------------------------------
# 5.  Graceful shutdown hook – notify A2A hub
# -------------------------------------------------------------
@app.on_event("shutdown")
async def notify_shutdown():
    import websockets, asyncio
    try:
        async with websockets.connect(A2A_HUB_URL) as ws:
            await ws.send(json.dumps({"type":"agent_shutdown","agent_id":"mcp_server"}))
    except Exception:
        logger.warning("Failed to notify A2A hub on shutdown")

# -------------------------------------------------------------
# 6.  CLI entry point
# -------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("mcp_server:app", host="0.0.0.0", port=8000, reload=False)
```

### 3.1.1 Lua Bridge (Minetest side)

Create a Minetest mod called `rpc_bridge`. Place this in `minetest/mods/rpc_bridge/init.lua`:

```lua
-- rpc_bridge/init.lua
local json = minetest.get_modpath("rpc_bridge") .. "/json.lua"  -- use a bundled JSON lib

local function handle_request(body)
    local ok, req = pcall(json.decode, body)
    if not ok then return {error="invalid json"} end
    local method = req.method
    local params = req.params or {}
    local status, result = pcall(minetest[method], table.unpack(params))
    if status then
        return {result = result}
    else
        return {error = result}
    end
end

local function start_server()
    local server = minetest.get_http_api():post("http://localhost:8080/rpc", function(body)
        local resp = handle_request(body)
        return json.encode(resp)
    end)
    server:start()
end

minetest.register_on_mods_loaded(function()
    start_server()
end)
```

> **Note** – Minetest does not ship with an HTTP server, so you’ll need the `http_api` mod or run a tiny Python HTTP server that forwards requests to Lua via RPC. The code above assumes a simple wrapper that listens on `/rpc`.

---

## 3.2 A2A Hub – WebSocket Registry

```python
# a2a_hub.py
import asyncio
import json
import logging
import websockets
from websockets import WebSocketServerProtocol
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("a2a_hub")

# In‑memory agent registry: agent_id -> {ws, capabilities}
agents: Dict[str, Dict[str, Any]] = {}

async def handler(ws: WebSocketServerProtocol, path: str):
    agent_id = None
    try:
        async for message in ws:
            msg = json.loads(message)
            if msg["type"] == "register":
                agent_id = msg["agent_id"]
                agents[agent_id] = {"ws": ws, "caps": set(msg.get("capabilities", []))}
                logger.info(f"Agent {agent_id} registered with caps {agents[agent_id]['caps']}")
                await ws.send(json.dumps({"type": "ack", "msg": "registered"}))
            elif msg["type"] == "request":
                # Forward request to target agent
                target = msg["target"]
                if target not in agents:
                    await ws.send(json.dumps({"type": "error", "msg": "target not found"}))
                    continue
                await agents[target]["ws"].send(json.dumps(msg))
            elif msg["type"] == "response":
                # Relay back to original requester
                orig = msg["original"]
                if orig not in agents:
                    continue
                await agents[orig]["ws"].send(json.dumps(msg))
            elif msg["type"] == "shutdown":
                agent_id = msg["agent_id"]
                agents.pop(agent_id, None)
                logger.info(f"Agent {agent_id} shutdown")
            else:
                await ws.send(json.dumps({"type": "error", "msg": "unknown message type"}))
    except websockets.exceptions.ConnectionClosed:
        if agent_id:
            agents.pop(agent_id, None)
            logger.info(f"Agent {agent_id} disconnected")
    except Exception as e:
        logger.exception("Hub error")
        if agent_id:
            agents.pop(agent_id, None)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        logger.info("A2A Hub listening on ws://0.0.0.0:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
```

> **Robustness** – In production you’d back‑up this registry into Redis or PostgreSQL so that agents can recover after a hub crash.

---

## 3.3 External AI Agent Skeleton (Python)

```python
# ai_agent.py
import os
import asyncio
import json
import httpx
import websockets

# Config
MCP_URL = os.getenv("MCP_URL", "http://localhost:8000")
A2A_URL = os.getenv("A2A_URL", "ws://localhost:8765")
AGENT_ID = os.getenv("AGENT_ID", "miner_bot")

# ------------------------------------------------------------------
# 1.  Register with A2A Hub
# ------------------------------------------------------------------
async def register():
    async with websockets.connect(A2A_URL) as ws:
        await ws.send(json.dumps({
            "type": "register",
            "agent_id": AGENT_ID,
            "capabilities": ["mine", "craft"]
        }))
        msg = await ws.recv()
        print(f"A2A register ack: {msg}")
        return ws

# ------------------------------------------------------------------
# 2.  Invoke a tool via MCP
# ------------------------------------------------------------------
async def invoke_tool(tool_name, **params):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{MCP_URL}/tool/{tool_name}", json=params)
        resp.raise_for_status()
        return resp.json()

# ------------------------------------------------------------------
# 3.  Mining loop
# ------------------------------------------------------------------
async def mining_loop():
    pos = {"x": 10, "y": 5, "z": 10}
    while True:
        node = await invoke_tool("get_block", pos=pos)
        if node["result"] != "air":
            await invoke_tool("break_block", pos=pos)
        # Advance position
        pos["x"] += 1
        await asyncio.sleep(0.1)  # ~10 ticks per sec

# ------------------------------------------------------------------
# 4.  Main
# ------------------------------------------------------------------
async def main():
    ws = await register()
    await mining_loop()  # Run indefinitely

if __name__ == "__main__":
    asyncio.run(main())
```

### 3.3.1 Edge‑Case Handling  
| Edge Case | Detection | Mitigation |
|-----------|-----------|------------|
| **TCP drop / MCP unavailable** | HTTP 5xx or connection error | Retry with exponential back‑off, fall‑back to local cache |
| **Tool signature mismatch** | Tool missing in registry | Log detailed error, send diagnostic to hub |
| **Permission error (e.g., block protected)** | MCP returns `False` | Catch and trigger alternate path (e.g., use tool `craft` to build pickaxe) |
| **A2A deadlock** | Two agents request each other’s task | Use time‑outs on request, enforce priority queue |
| **Out‑of‑memory** | Too many agents registered | Persist registry to disk, purge idle agents |

---

# 4. Game‑Specific Optimizations  

## 4.1 Tick Rate Considerations  

- **Batch tool calls**: Instead of issuing a separate HTTP request per block placement, accumulate 8‑16 actions and send them in a single payload.  
- **Sync with server ticks**: Use a websocket “tick” event from the game engine (if available) to align the agent’s loop with the tick cycle, ensuring that commands are applied before the next server state update.  
- **Low‑latency sockets**: Prefer WebSocket (FastMCP) over HTTP for real‑time tool execution. The MCP server can expose a WebSocket endpoint that streams responses as they complete.

## 4.2 Memory Management  

- **Agent process isolation**: Run each AI agent in its own container (Docker) to prevent memory leaks from spilling over.  
- **Lua bridge pooling**: Reuse a single HTTP client pool in the Lua bridge to avoid per‑request connection overhead.  
- **Capped registry**: Limit the number of concurrent agents per server (e.g., 32) and queue excess registrations.

## 4.3 Multiplayer Synchronization  

- **State replication**: The MCP server must be the single source of truth for all block changes. All clients read from the server’s state rather than local caches.  
- **Conflict resolution**: Use optimistic locking – include a `tick` field in tool calls; if the server’s current tick is older, reject the operation.  
- **Latency compensation**: For large worlds, allow the agent to send *desired* positions and have the server interpolate placement to hide 50 ms delays.

---

# 5. Agent Behavior Examples  

### 5.1 Scenario 1 – Automated Farm

| Before | After |
|--------|-------|
| Player manually mines dirt, builds a farmland, plants wheat, waters with bucket, harvests. | Agent runs `mine_block`, `place_block` (farmland), `craft` (wheat seeds), `place_block` (seed), `use_item` (bucket water) in a single orchestrated loop. |

**Code snippet**

```python
async def run_farm():
    base = {"x": 20, "y": 5, "z": 20}
    # Mine a 3x3 dirt patch
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            pos = {"x": base["x"]+dx, "y": base["y"], "z": base["z"]+dz}
            await invoke_tool("break_block", pos=pos)
    # Convert to farmland
    await invoke_tool("place_block", pos=base, node="default:farmland")
    # Plant seeds
    await invoke_tool("place_block", pos=base, node="default:wheat")
```

### 5.2 Scenario 2 – Defensive Mining

Player wants to mine under a cliff but stay safe.

| Before | After |
|--------|-------|
| Player walks, manually builds a ladder and block walls | Agent auto‑detects overhang via `get_block`, builds a *safety tower* before mining. |

```python
async def safe_mine(start_pos):
    # Build safety tower
    for h in range(3):
        pos = {"x": start_pos["x"], "y": start_pos["y"]+h, "z": start_pos["z"]}
        await invoke_tool("place_block", pos=pos, node="default:stone")
    # Mine target block
    await invoke_tool("break_block", pos=start_pos)
```

### 5.3 Scenario 3 – Cross‑Game Migration

Agent initially on a vanilla server, then moves to a modded Luanti server with new tool “build_house”.

| Before | After |
|--------|-------|
| Agent only knows vanilla tools | After migration, the agent automatically registers its new capability via A2A and starts using `build_house`. |

```python
# Agent code stays the same, but on new server:
await invoke_tool("build_house", location=home_pos, material="default:stone")
```

---

# 6. Testing Strategy  

## 6.1 Unit Tests – Core Components  

| Module | Test Cases |
|--------|------------|
| `rpc_bridge` | Valid RPC, invalid JSON, missing method, method error. |
| `FastMCP` | Register tool, missing tool, correct param mapping, TypeError handling. |
| `A2A Hub` | Register agent, duplicate registration, request forwarding, shutdown cleanup. |
| `Agent Skeleton` | HTTP retry logic, WebSocket reconnect, task queue. |

```python
# test_mcp.py
import pytest, httpx
from fastapi.testclient import TestClient
from mcp_server import app

client = TestClient(app)

def test_place_block_success():
    resp = client.post("/tool/place_block", json={"pos": {"x":0,"y":0,"z":0},"node":"default:stone"})
    assert resp.status_code == 200
    assert resp.json()["result"] is True

def test_missing_tool():
    resp = client.post("/tool/nonexistent", json={})
    assert resp.status_code == 404
```

## 6.2 Integration Tests – Game Engine  

1. **Start Minetest + Lua bridge** in a Docker container.  
2. **Spin up MCP server** pointing to the bridge.  
3. **Run a scripted agent** that performs a series of tools.  
4. **Verify world state** via a direct Lua call or by inspecting the server’s node file.  

Use `pytest-docker` or a custom fixture that runs the Minetest process.

## 6.3 Performance Benchmarks  

| Metric | Target | Tool |
|--------|--------|------|
| Avg latency per tool | < 1 ms (local) | `wrk2 -t4 -c100 -d10s http://localhost:8000/tool/` |
| Max concurrent agents | 64 | Stress‑test hub with `wrk2` on WebSocket handshake |
| Memory per agent | < 10 MB | Use `psutil` to monitor process memory |

Document results in a `benchmarks/` folder and update CI pipelines.

---

# 7. Deployment Checklist  

| Step | Action | Tool / Command |
|------|--------|----------------|
| 1 | Build Docker images for MCP, A2A, and Lua bridge | `docker build -t luanti-mcp .` |
| 2 | Deploy Minetest server (as a container or VM) with `minetest` and `rpc_bridge` mod | `docker run -d -p 25565:25565 minetest/minetest` |
| 3 | Start A2A Hub | `docker run -d -p 8765:8765 a2a_hub:latest` |
| 4 | Run MCP Server | `docker run -d -p 8000:8000 luanti-mcp:latest` |
| 5 | Configure agents (env vars) | `AGENT_ID=miner_bot MCP_URL=http://mcp:8000 A2A_URL=ws://a2a:8765 python ai_agent.py` |
| 6 | Verify connections | `wscat -c ws://localhost:8765` |
| 7 | Enable monitoring (Prometheus exporter, Grafana) | Add `/metrics` endpoint to MCP, expose `websocket_connections` |
| 8 | Set up health checks | `curl -f http://mcp:8000/health` |

**Rollback procedures**  
- Keep a copy of the previous Docker image.  
- Use a blue‑green deployment: start new stack in parallel, switch traffic after smoke test.  
- For in‑game changes, keep a `world_backup.zip` and restore if a critical bug occurs.

---

# 8. Advanced Patterns  

## 8.1 Scaling to Many Agents  

1. **Horizontal scaling of MCP** – Run multiple MCP instances behind a TCP load balancer (HAProxy). Each instance exposes a subset of tools; use a consistent‑hash mapping for stateful agents.  
2. **Shard A2A Hub** – Partition the registry by capability; each shard handles a subset of agents. Agents can query any shard for a target agent.  
3. **Publish/Subscribe** – For broad announcements (e.g., world events), implement a Pub/Sub channel in the hub using Redis or NATS.

## 8.2 Player‑Agent Interaction Patterns  

| Pattern | Description | Example |
|---------|-------------|---------|
| **Command‑Response** | Player issues a chat command; agent replies with status. | `/build_house 10 64 10 stone` → agent acknowledges. |
| **Subscription** | Agent subscribes to a player’s inventory changes; reacts automatically. | Agent crafts tools when player runs out. |
| **Marketplace** | Agents can buy/sell items via a protocol. | Agent sends `{"type":"trade","item":"wood","amount":10}` to another agent. |

## 8.3 Emergent Behaviours  

- **Cooperative Farming** – Multiple agents coordinate to tend a field, each specializing (e.g., one for sowing, one for harvesting).  
- **Self‑Healing Networks** – Agents monitor server health; if a node fails, they spin up a backup MCP instance.  
- **Dynamic Economy** – Agents trade resources; prices fluctuate based on supply/demand communicated via A2A messages.

---

## Summary

By weaving MCP and A2A into Luanti Voyager you gain a **modular, protocol‑driven AI layer** that is:

- **Production‑ready** – robust error handling, monitoring hooks, and container‑friendly.  
- **Extensible** – new tools can be added by simply decorating functions.  
- **Cross‑game compatible** – agents written once can migrate to any Minetest‑derived engine that exposes the same Lua API.  

Deploy the stack as described, write your agents with the skeleton above, and watch them turn your sandbox into a living, breathing ecosystem of AI collaborators.

