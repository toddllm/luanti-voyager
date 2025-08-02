// Luanti Voyager Web UI
let ws = null;
let reconnectTimer = null;
let worldView = null;
let agentElement = null;

// Configuration
const WS_PORT = 8765;  // WebSocket port for agent data
const RECONNECT_DELAY = 3000;

// Initialize UI
function init() {
    worldView = document.getElementById('world-view');
    agentElement = document.getElementById('agent');
    
    // Create inventory slots
    const inventoryGrid = document.getElementById('inventory');
    for (let i = 0; i < 32; i++) {
        const slot = document.createElement('div');
        slot.className = 'inventory-slot';
        slot.id = `slot-${i}`;
        inventoryGrid.appendChild(slot);
    }
    
    connectWebSocket();
}

// WebSocket connection
function connectWebSocket() {
    const wsUrl = `ws://${window.location.hostname}:${WS_PORT}`;
    
    try {
        ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
            console.log('Connected to agent');
            updateConnectionStatus(true);
            addLogEntry('Connected to agent', 'action');
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                updateUI(data);
            } catch (e) {
                console.error('Failed to parse message:', e);
            }
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            addLogEntry('Connection error', 'error');
        };
        
        ws.onclose = () => {
            updateConnectionStatus(false);
            addLogEntry('Disconnected from agent', 'error');
            
            // Reconnect after delay
            if (reconnectTimer) clearTimeout(reconnectTimer);
            reconnectTimer = setTimeout(connectWebSocket, RECONNECT_DELAY);
        };
        
    } catch (e) {
        console.error('Failed to create WebSocket:', e);
        
        // Retry connection
        if (reconnectTimer) clearTimeout(reconnectTimer);
        reconnectTimer = setTimeout(connectWebSocket, RECONNECT_DELAY);
    }
}

// Update UI with agent data
function updateUI(data) {
    // Update agent info
    if (data.agent) {
        document.getElementById('agent-name').textContent = data.agent.name || 'Unknown';
        
        if (data.agent.pos) {
            const pos = data.agent.pos;
            document.getElementById('agent-pos').textContent = 
                `${Math.floor(pos.x)}, ${Math.floor(pos.y)}, ${Math.floor(pos.z)}`;
            
            // Update agent position on map
            updateAgentPosition(pos);
        }
        
        if (data.agent.hp !== undefined) {
            document.getElementById('agent-health').textContent = `${data.agent.hp}/20`;
        }
        
        if (data.agent.current_action) {
            document.getElementById('current-action').textContent = data.agent.current_action;
        }
    }
    
    // Update inventory
    if (data.inventory) {
        updateInventory(data.inventory);
    }
    
    // Update world view
    if (data.nearby_blocks) {
        updateWorldView(data.nearby_blocks, data.agent.pos);
    }
    
    // Update nearby block counts
    if (data.block_counts) {
        document.getElementById('nearby-wood').textContent = data.block_counts.wood || 0;
        document.getElementById('nearby-stone').textContent = data.block_counts.stone || 0;
        document.getElementById('nearby-ores').textContent = data.block_counts.ores || 0;
    }
    
    // Add action to log
    if (data.last_action) {
        addLogEntry(data.last_action, 'action');
    }
}

// Update agent position on map
function updateAgentPosition(pos) {
    // Center view on agent
    const centerX = worldView.offsetWidth / 2;
    const centerY = worldView.offsetHeight / 2;
    
    agentElement.style.left = centerX + 'px';
    agentElement.style.top = centerY + 'px';
}

// Update world view with nearby blocks
function updateWorldView(blocks, agentPos) {
    // Clear existing blocks (except agent)
    const existingBlocks = worldView.querySelectorAll('.block');
    existingBlocks.forEach(block => block.remove());
    
    const centerX = worldView.offsetWidth / 2;
    const centerY = worldView.offsetHeight / 2;
    const scale = 20; // pixels per block
    
    blocks.forEach(block => {
        const relX = block.pos.x - agentPos.x;
        const relZ = block.pos.z - agentPos.z;
        
        // Only show blocks within view
        if (Math.abs(relX) > 15 || Math.abs(relZ) > 15) return;
        
        const blockEl = document.createElement('div');
        blockEl.className = `block ${getBlockClass(block.type)}`;
        blockEl.style.left = (centerX + relX * scale) + 'px';
        blockEl.style.top = (centerY + relZ * scale) + 'px';
        blockEl.title = `${block.type} (${block.pos.x}, ${block.pos.y}, ${block.pos.z})`;
        
        worldView.appendChild(blockEl);
    });
}

// Get block CSS class based on type
function getBlockClass(blockType) {
    if (blockType.includes('wood') || blockType.includes('tree')) return 'wood';
    if (blockType.includes('stone')) return 'stone';
    if (blockType.includes('dirt')) return 'dirt';
    if (blockType.includes('air')) return 'air';
    return 'stone'; // default
}

// Update inventory display
function updateInventory(inventory) {
    // Clear all slots first
    for (let i = 0; i < 32; i++) {
        const slot = document.getElementById(`slot-${i}`);
        slot.className = 'inventory-slot';
        slot.textContent = '';
    }
    
    // Fill slots with items
    let slotIndex = 0;
    for (const [item, count] of Object.entries(inventory)) {
        if (slotIndex >= 32) break;
        
        const slot = document.getElementById(`slot-${slotIndex}`);
        slot.className = 'inventory-slot filled';
        slot.textContent = count > 1 ? count : '';
        slot.title = `${item} x${count}`;
        
        slotIndex++;
    }
}

// Update connection status
function updateConnectionStatus(connected) {
    const status = document.getElementById('connection-status');
    status.className = `status ${connected ? 'connected' : 'disconnected'}`;
    status.textContent = connected ? 'Connected' : 'Disconnected';
}

// Add entry to action log
function addLogEntry(message, type = '') {
    const log = document.getElementById('action-log');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    
    const timestamp = new Date().toLocaleTimeString();
    entry.textContent = `[${timestamp}] ${message}`;
    
    log.appendChild(entry);
    
    // Keep only last 50 entries
    while (log.children.length > 50) {
        log.removeChild(log.firstChild);
    }
    
    // Scroll to bottom
    log.scrollTop = log.scrollHeight;
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', init);