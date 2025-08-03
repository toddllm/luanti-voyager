-- Voyager Bot Mod for Luanti
-- This mod creates a bot player and provides an API for external control

voyager = {}
voyager.bots = {}
voyager.actions_queue = {}

-- Configuration
local UPDATE_INTERVAL = 0.1  -- How often to process commands
local BOT_SPEED = 4.0
local BOT_JUMP = 6.5

-- Create a bot player
function voyager.spawn_bot(name, pos)
    -- Check if bot already exists
    if voyager.bots[name] then
        return false, "Bot already exists"
    end
    
    -- Create a simple bot entity
    local bot = {
        name = name,
        pos = pos or {x=0, y=0, z=0},
        yaw = 0,
        pitch = 0,
        hp = 20,
        inventory = {},
        attached_to = nil
    }
    
    voyager.bots[name] = bot
    voyager.actions_queue[name] = {}
    
    minetest.log("action", "Voyager bot '" .. name .. "' spawned at " .. minetest.pos_to_string(pos))
    return true
end

-- Bot action functions
function voyager.move_bot(name, direction, distance)
    local bot = voyager.bots[name]
    if not bot then return false end
    
    local new_pos = vector.new(bot.pos)
    
    if direction == "forward" then
        new_pos.x = new_pos.x + math.cos(bot.yaw) * distance
        new_pos.z = new_pos.z + math.sin(bot.yaw) * distance
    elseif direction == "back" then
        new_pos.x = new_pos.x - math.cos(bot.yaw) * distance
        new_pos.z = new_pos.z - math.sin(bot.yaw) * distance
    elseif direction == "left" then
        new_pos.x = new_pos.x + math.cos(bot.yaw - math.pi/2) * distance
        new_pos.z = new_pos.z + math.sin(bot.yaw - math.pi/2) * distance
    elseif direction == "right" then
        new_pos.x = new_pos.x + math.cos(bot.yaw + math.pi/2) * distance
        new_pos.z = new_pos.z + math.sin(bot.yaw + math.pi/2) * distance
    elseif direction == "up" then
        new_pos.y = new_pos.y + distance
    elseif direction == "down" then
        new_pos.y = new_pos.y - distance
    end
    
    -- Check if position is valid (not inside solid block)
    local node = minetest.get_node(new_pos)
    if node.name == "air" or minetest.registered_nodes[node.name].walkable == false then
        bot.pos = new_pos
        return true
    end
    
    return false, "Blocked by " .. node.name
end

function voyager.turn_bot(name, angle)
    local bot = voyager.bots[name]
    if not bot then return false end
    
    bot.yaw = (bot.yaw + angle) % (2 * math.pi)
    return true
end

function voyager.dig_block(name, pos)
    local bot = voyager.bots[name]
    if not bot then return false end
    
    -- Check if block is within reach (5 blocks)
    if vector.distance(bot.pos, pos) > 5 then
        return false, "Too far away"
    end
    
    local node = minetest.get_node(pos)
    if node.name == "air" then
        return false, "Nothing to dig"
    end
    
    -- Dig the node
    minetest.dig_node(pos)
    
    -- Add to bot inventory (simplified)
    local drops = minetest.get_node_drops(node.name)
    for _, item in ipairs(drops) do
        bot.inventory[item] = (bot.inventory[item] or 0) + 1
    end
    
    return true
end

function voyager.place_block(name, pos, item)
    local bot = voyager.bots[name]
    if not bot then return false end
    
    -- Check if block is within reach
    if vector.distance(bot.pos, pos) > 5 then
        return false, "Too far away"
    end
    
    -- Check inventory
    if not bot.inventory[item] or bot.inventory[item] <= 0 then
        return false, "Don't have " .. item
    end
    
    -- Place the node
    minetest.set_node(pos, {name = item})
    bot.inventory[item] = bot.inventory[item] - 1
    
    return true
end

-- Get bot state
function voyager.get_bot_state(name)
    local bot = voyager.bots[name]
    if not bot then return nil end
    
    local state = {
        pos = bot.pos,
        yaw = bot.yaw,
        pitch = bot.pitch,
        hp = bot.hp,
        inventory = bot.inventory,
        nearby_nodes = {}
    }
    
    -- Get nearby nodes
    local radius = 5
    for x = -radius, radius do
        for y = -radius, radius do
            for z = -radius, radius do
                local check_pos = vector.add(bot.pos, {x=x, y=y, z=z})
                local node = minetest.get_node(check_pos)
                if node.name ~= "air" then
                    table.insert(state.nearby_nodes, {
                        pos = check_pos,
                        name = node.name
                    })
                end
            end
        end
    end
    
    return state
end

-- File-based API for external control (simpler and more reliable for POC)

-- Command file interface (simpler for POC)
local command_file = minetest.get_worldpath() .. "/voyager_commands.txt"
local response_file = minetest.get_worldpath() .. "/voyager_responses.txt"

local timer = 0
minetest.register_globalstep(function(dtime)
    timer = timer + dtime
    if timer < UPDATE_INTERVAL then return end
    timer = 0
    
    -- Read commands from file
    local file = io.open(command_file, "r")
    if file then
        local content = file:read("*all")
        file:close()
        
        -- Clear the command file
        file = io.open(command_file, "w")
        file:close()
        
        -- Parse and execute commands
        for line in content:gmatch("[^\r\n]+") do
            local parts = {}
            for part in line:gmatch("%S+") do
                table.insert(parts, part)
            end
            
            if #parts > 0 then
                local cmd = parts[1]
                local bot_name = parts[2]
                
                minetest.log("action", "Voyager: Processing command: " .. line)
                
                local result = {success = false, error = "Unknown command"}
                
                if cmd == "spawn" and bot_name then
                    local x = tonumber(parts[3]) or 0
                    local y = tonumber(parts[4]) or 0
                    local z = tonumber(parts[5]) or 0
                    result.success = voyager.spawn_bot(bot_name, {x=x, y=y, z=z})
                    
                elseif cmd == "move" and bot_name then
                    local direction = parts[3]
                    local distance = tonumber(parts[4]) or 1
                    result.success = voyager.move_bot(bot_name, direction, distance)
                    
                elseif cmd == "turn" and bot_name then
                    local angle = tonumber(parts[3]) or 0
                    result.success = voyager.turn_bot(bot_name, angle)
                    
                elseif cmd == "dig" and bot_name then
                    local x = tonumber(parts[3])
                    local y = tonumber(parts[4])
                    local z = tonumber(parts[5])
                    if x and y and z then
                        result.success = voyager.dig_block(bot_name, {x=x, y=y, z=z})
                    end
                    
                elseif cmd == "place" and bot_name then
                    local x = tonumber(parts[3])
                    local y = tonumber(parts[4])
                    local z = tonumber(parts[5])
                    local item = parts[6]
                    if x and y and z and item then
                        result.success = voyager.place_block(bot_name, {x=x, y=y, z=z}, item)
                    end
                    
                elseif cmd == "state" and bot_name then
                    local state = voyager.get_bot_state(bot_name)
                    if state then
                        result.success = true
                        result.state = state
                    end
                end
                
                -- Write response
                local resp_file = io.open(response_file, "a")
                if resp_file then
                    resp_file:write(minetest.write_json(result) .. "\n")
                    resp_file:close()
                    minetest.log("action", "Voyager: Wrote response for command: " .. cmd .. " " .. bot_name)
                else
                    minetest.log("error", "Voyager: Failed to open response file: " .. response_file)
                end
            end
        end
    end
end)

-- Chat commands for testing
minetest.register_chatcommand("vbot", {
    params = "<spawn|move|turn|dig|place|state> <name> [params...]",
    description = "Control Voyager bots",
    func = function(name, param)
        local parts = {}
        for part in param:gmatch("%S+") do
            table.insert(parts, part)
        end
        
        if #parts < 2 then
            return false, "Usage: /vbot <command> <bot_name> [params...]"
        end
        
        local cmd = parts[1]
        local bot_name = parts[2]
        
        if cmd == "spawn" then
            local player = minetest.get_player_by_name(name)
            local pos = player:get_pos()
            local success = voyager.spawn_bot(bot_name, pos)
            return success, success and "Bot spawned" or "Failed to spawn bot"
            
        elseif cmd == "state" then
            local state = voyager.get_bot_state(bot_name)
            if state then
                return true, minetest.write_json(state)
            else
                return false, "Bot not found"
            end
        end
        
        return false, "Unknown command"
    end
})

minetest.log("action", "Voyager Bot mod loaded!")