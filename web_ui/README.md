# Luanti Voyager Web UI

A real-time visualization interface for the Luanti Voyager agent, inspired by Minecraft Voyager's web interface.

## Features

- **Live World View**: See blocks around the agent in real-time
- **Agent Status**: Position, health, current action
- **Inventory Display**: What the agent has collected
- **Action Log**: Timeline of agent actions
- **Nearby Blocks Counter**: Wood, stone, and ore counts

## Access URLs

### 📱 From Your LAN (Default)
- **Web Interface**: http://192.168.68.145:8090
- **WebSocket**: ws://192.168.68.145:8765

### 💻 Local Only
- **Web Interface**: http://localhost:8090
- **WebSocket**: ws://localhost:8765

## How to Use

1. **Start the Luanti test server** (port 40000):
   ```bash
   ./test-server/start-test-server.sh
   ```

2. **Run the agent with web UI**:
   ```bash
   python -m luanti_voyager.main --port 40000
   ```
   
   The web UI starts automatically. Open your browser to the URL shown.

3. **For localhost-only access**:
   ```bash
   python -m luanti_voyager.main --port 40000 --no-lan-access
   ```

## Architecture

- **HTTP Server** (port 8090): Serves the static web interface
- **WebSocket Server** (port 8765): Real-time data stream from agent
- **Agent Integration**: Updates sent automatically during perception loop

## Customization

- Edit `web_ui/index.html` for UI layout
- Edit `web_ui/app.js` for behavior
- Modify `luanti_voyager/web_server.py` to add new data streams

## Troubleshooting

**Can't connect from LAN:**
- Check firewall settings
- Ensure `--lan-access` is used (default)
- Verify you're on the same network

**Port already in use:**
- Change with `--web-port 8091`
- Check what's using ports: `lsof -i :8090`

**No data showing:**
- Check agent is running
- Look for WebSocket connection in browser console
- Verify agent has spawned in game