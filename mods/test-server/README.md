# Test Server Setup - IMPORTANT! ⚠️

This directory contains scripts to run a **TEST** Luanti server on **PORT 40000**.

## ⚠️ SAFETY FIRST

**NEVER** run these scripts on the production server port (30000)!

Always check ports before starting:
```bash
./check-ports.sh
```

## Quick Start

1. **Check if production is safe:**
   ```bash
   ./check-ports.sh
   # Make sure port 30000 shows your production server
   # Make sure port 40000 is free
   ```

2. **Start test server:**
   ```bash
   ./start-test-server.sh
   # This will:
   # - Build Luanti from our fork if needed
   # - Create a test world
   # - Start server on port 40000
   ```

3. **In another terminal, run test agent:**
   ```bash
   ./test-agent.sh
   ```

## Port Configuration

| Server | Port | Purpose |
|--------|------|---------|
| Production | 30000 | DO NOT TOUCH - Live server |
| Test | 40000 | Safe for experiments |
| Web UI | 8080 | Agent visualization interface |
| WebSocket | 8081 | Real-time agent data |

## Network Access Settings

By default, servers allow LAN access (bind to 0.0.0.0). This is useful for:
- Testing from other devices on your network
- Sharing demos with teammates
- Mobile device testing

**For localhost-only development:**
- Edit `luanti-test.conf` and set `bind_address = 127.0.0.1`
- Run agent with `--no-lan-access` flag

## What's Different

The test server:
- Runs on port **40000** (not 30000!)
- Uses our forked Luanti source
- Has creative mode enabled
- No damage or PvP
- Isolated test world
- Local connections only (127.0.0.1)

## File Structure

```
test-server/
├── luanti-test.conf      # Server config (PORT 40000!)
├── start-test-server.sh   # Launch test server
├── test-agent.sh         # Run agent on test server
├── check-ports.sh        # Safety check script
├── test_world/           # Isolated test world
└── test-server.log       # Server logs
```

## Testing Workflow

1. Make changes to Luanti source or mods
2. Run `./check-ports.sh` to ensure safety
3. Start test server with `./start-test-server.sh`
4. Test your changes
5. Stop with Ctrl+C when done

## Troubleshooting

**Port 40000 already in use:**
- Another test server might be running
- Check with: `lsof -i :40000`
- Kill if needed: `kill $(lsof -t -i :40000)`

**Can't connect:**
- Make sure you're using port 40000
- Check server is running: `./check-ports.sh`
- Check logs: `tail -f test-server.log`

**Build fails:**
- Install dependencies: `sudo apt-get install build-essential cmake libsqlite3-dev`
- Check CMake version (need 3.5+)

## Manual Testing

Connect with Luanti client:
```bash
luanti --address 127.0.0.1 --port 40000
```

Or Minetest:
```bash
minetest --address 127.0.0.1 --port 40000
```

## Never Do This! ❌

- Don't change port from 40000 to 30000
- Don't run on production server
- Don't expose to internet (bind_address = 127.0.0.1)
- Don't use production world path

## Always Do This! ✅

- Run `./check-ports.sh` before starting
- Use port 40000 for testing
- Keep test world separate
- Stop server when done testing