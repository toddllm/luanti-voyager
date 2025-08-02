"""
Web server for Luanti Voyager visualization.

Serves the web UI and provides WebSocket connection for real-time agent data.
"""

import asyncio
import json
import logging
from pathlib import Path
import websockets
from aiohttp import web
import weakref

logger = logging.getLogger(__name__)

class VoyagerWebServer:
    """Web server for agent visualization."""
    
    def __init__(self, host='0.0.0.0', http_port=8090, ws_port=8765):
        self.host = host
        self.http_port = http_port
        self.ws_port = ws_port
        self.web_ui_path = Path(__file__).parent.parent / 'web_ui'
        
        # WebSocket clients
        self.clients = weakref.WeakSet()
        
        # Latest agent state
        self.agent_state = {
            "agent": {
                "name": "VoyagerBot",
                "pos": {"x": 0, "y": 0, "z": 0},
                "hp": 20,
                "current_action": "Initializing..."
            },
            "inventory": {},
            "nearby_blocks": [],
            "block_counts": {"wood": 0, "stone": 0, "ores": 0},
            "last_action": "Starting up..."
        }
        
    async def start(self):
        """Start both HTTP and WebSocket servers."""
        # Start WebSocket server
        ws_server = await websockets.serve(
            self.handle_websocket,
            self.host,
            self.ws_port
        )
        logger.info(f"WebSocket server started on ws://{self.host}:{self.ws_port}")
        
        # Start HTTP server
        app = web.Application()
        app.router.add_static('/', path=self.web_ui_path, name='static')
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.http_port)
        await site.start()
        
        logger.info(f"Web UI available at http://{self.host}:{self.http_port}")
        
        # Return servers for cleanup
        return ws_server, runner
        
    async def handle_websocket(self, websocket, path):
        """Handle WebSocket connections."""
        self.clients.add(websocket)
        logger.info(f"Client connected from {websocket.remote_address}")
        
        try:
            # Send current state to new client
            await websocket.send(json.dumps(self.agent_state))
            
            # Keep connection alive
            await websocket.wait_closed()
            
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            logger.info(f"Client disconnected")
            
    async def update_state(self, state_update):
        """Update agent state and broadcast to all clients."""
        # Merge update into current state
        for key, value in state_update.items():
            if isinstance(value, dict) and key in self.agent_state:
                self.agent_state[key].update(value)
            else:
                self.agent_state[key] = value
                
        # Broadcast to all connected clients
        if self.clients:
            message = json.dumps(self.agent_state)
            disconnected = []
            
            for client in self.clients:
                try:
                    await client.send(message)
                except:
                    disconnected.append(client)
                    
            # Clean up disconnected clients
            for client in disconnected:
                self.clients.discard(client)
                
    def update_agent_position(self, x, y, z):
        """Update agent position."""
        asyncio.create_task(self.update_state({
            "agent": {
                "pos": {"x": x, "y": y, "z": z}
            }
        }))
        
    def update_inventory(self, inventory):
        """Update agent inventory."""
        asyncio.create_task(self.update_state({
            "inventory": inventory
        }))
        
    def update_nearby_blocks(self, blocks):
        """Update nearby blocks for visualization."""
        # Process blocks for visualization
        block_list = []
        block_counts = {"wood": 0, "stone": 0, "ores": 0}
        
        for block in blocks:
            block_list.append({
                "pos": block["pos"],
                "type": block["type"]
            })
            
            # Count block types
            block_type = block["type"].lower()
            if "wood" in block_type or "tree" in block_type:
                block_counts["wood"] += 1
            elif "stone" in block_type:
                block_counts["stone"] += 1
            elif "ore" in block_type:
                block_counts["ores"] += 1
                
        asyncio.create_task(self.update_state({
            "nearby_blocks": block_list[:100],  # Limit to 100 blocks for performance
            "block_counts": block_counts
        }))
        
    def log_action(self, action):
        """Log an agent action."""
        asyncio.create_task(self.update_state({
            "last_action": action,
            "agent": {"current_action": action}
        }))


# Standalone server for testing
async def main():
    logging.basicConfig(level=logging.INFO)
    
    server = VoyagerWebServer(host='0.0.0.0')
    ws_server, runner = await server.start()
    
    print(f"\n🌐 Luanti Voyager Web UI")
    print(f"=======================")
    print(f"Web Interface: http://192.168.68.145:{server.http_port}")
    print(f"WebSocket: ws://192.168.68.145:{server.ws_port}")
    print(f"\nPress Ctrl+C to stop\n")
    
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        pass
    finally:
        ws_server.close()
        await ws_server.wait_closed()
        await runner.cleanup()
        

if __name__ == "__main__":
    asyncio.run(main())