# Multi-Agent Swarm - Implementation Guide (GPT-OSS)

Generated: 2025-08-05T18:17:25.601456
Model: gpt-oss:20b

---

## Multi‑Agent Swarm in Luanti Voyager  
*(≈350 words – stay under 500)*  

### 1. What is Multi‑Agent Swarm?  
A Multi‑Agent Swarm is a collective of simple AI agents that cooperate through local interactions, producing emergent global behavior (flocking, hunting, mining, etc.). Each agent only knows its immediate neighbors, but together they move cohesively without a central controller.  

### 2. How to implement it for game AI agents  
- **Create a base `SwarmAgent` entity** that holds position, velocity, and a unique ID.  
- **Define perception radius** (`viewDist`) and weight parameters for the three classic Reynolds rules:  
  - *Alignment*: match average velocity of nearby agents.  
  - *Cohesion*: move toward the average position of neighbors.  
  - *Separation*: avoid collisions.  
- **Implement neighbor lookup** using the world’s spatial index (e.g., a quad‑tree or simple grid).  
- **Update loop**: every tick,  
  1. Gather neighbors within `viewDist`.  
  2. Compute steering vectors for alignment, cohesion, and separation.  
  3. Combine with weighting factors, clamp to max speed.  
  4. Update velocity and position.  
- **Add environmental interactions** (e.g., obstacle avoidance, goal seeking) by blending additional steering forces.  
- **Spawn the swarm** by creating N `SwarmAgent`s at a start position or random locations.  
- **Optional: Visual debugging** – draw lines to neighbors or show velocity arrows.  

### 3. One simple code example  
```lua
-- SwarmAgent.lua
SwarmAgent = {}
SwarmAgent.__index = SwarmAgent

function SwarmAgent:new(id, pos)
  local o = setmetatable({}, SwarmAgent)
  o.id      = id
  o.pos     = pos          -- {x, y, z}
  o.vel     = {x=0, y=0, z=0}
  o.maxSpeed = 5
  o.viewDist = 10
  return o
end

function SwarmAgent:update(neighbors)
  local align, cohesion, separation = {x=0,y=0,z=0}, {x=0,y=0,z=0}, {x=0,y=0,z=0}
  local count = 0

  for _, n in ipairs(neighbors) do
    count = count + 1
    -- Alignment: average velocity
    align.x, align.y, align.z = align.x + n.vel.x, align.y + n.vel.y, align.z + n.vel.z
    -- Cohesion: average position
    cohesion.x, cohesion.y, cohesion.z = cohesion.x + n.pos.x, cohesion.y + n.pos.y, cohesion.z + n.pos.z
    -- Separation: inverse distance
    local d = math.sqrt((n.pos.x-o.pos.x)^2 + (n.pos.y-o.pos.y)^2 + (n.pos.z-o.pos.z)^2)
    local diff = {x=o.pos.x-n.pos.x, y=o.pos.y-n.pos.y, z=o.pos.z-n.pos.z}
    separation.x, separation.y, separation.z = separation.x + diff.x/d,
                                               separation.y + diff.y/d,
                                               separation.z + diff.z/d
  end

  if count > 0 then
    align.x, align.y, align.z = align.x/count, align.y/count, align.z/count
    cohesion.x, cohesion.y, cohesion.z = (cohesion.x/count - o.pos.x),
                                         (cohesion.y/count - o.pos.y),
                                         (cohesion.z/count - o.pos.z)
    separation.x, separation.y, separation.z = separation.x/count, separation.y/count, separation.z/count

    -- Apply weights
    local steer = {
      x = align.x*1.5 + cohesion.x*1.0 + separation.x*2.0,
      y = align.y*1.5 + cohesion.y*1.0 + separation.y*2.0,
      z = align.z*1.5 + cohesion.z*1.0 + separation.z*2.0
    }

    -- Update velocity
    o.vel.x, o.vel.y, o.vel.z = o.vel.x + steer.x,
                                 o.vel.y + steer.y,
                                 o.vel.z + steer.z
    -- Clamp speed
    local speed = math.sqrt(o.vel.x^2 + o.vel.y^2 + o.vel.z^2)
    if speed > o.maxSpeed then
      local scale = o.maxSpeed / speed
      o.vel.x, o.vel.y, o.vel.z = o.vel.x*scale, o.vel.y*scale, o.vel.z*scale
    end
  end

  -- Update position
  o.pos.x, o.pos.y, o.pos.z = o.pos.x + o.vel.x,
                               o.pos.y + o.vel.y,
                               o.pos.z + o.vel.z
end
```
*The main game loop would call `SwarmAgent:update(neighborList)` each tick.*

### 4. Game‑specific use case  
**Mining Swarm** – A group of “mining bots” patrol a cavern. Each bot uses the swarm rules to stay together while evenly spreading out to mine ore veins. The swarm’s cohesion keeps the group intact if a bot falls into a pit; alignment makes the group head toward the nearest ore deposit; separation prevents bots from smashing into each other. A single “target” entity (the ore vein) can be added as an extra steering force so the swarm collectively moves toward the resource, resulting in fast, coordinated mining without a single AI orchestrating every action.