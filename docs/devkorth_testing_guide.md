# Devkorth Testing Guide

This guide explains how to test the Devkorth mod using the luanti-voyager testing framework.

## Overview

The Devkorth mod adds an omnipotent entity that manifests when specific shrine conditions are met. This testing suite helps verify the mod is working correctly.

## Test Scripts

### 1. `scripts/launch_devkorth_test_server.sh`
Launches a dedicated test server on port 50000 with Devkorth mod installed.

```bash
cd /home/tdeshane/luanti/luanti-voyager
./scripts/launch_devkorth_test_server.sh
```

### 2. `scripts/manual_devkorth_test.py`
Generates commands for manual testing. Run this and copy/paste commands into the game.

```bash
python3 scripts/manual_devkorth_test.py
```

### 3. `scripts/test_devkorth_shrine.py`
Automated test using voyager bot (requires voyager agent setup).

```bash
python3 scripts/test_devkorth_shrine.py --host localhost --port 50000
```

### 4. `scripts/debug_devkorth.py`
Monitors server logs and checks mod status.

```bash
python3 scripts/debug_devkorth.py /home/tdeshane/luanti/devkorth_test.log
```

## Manual Testing Steps

1. **Start the test server:**
   ```bash
   ./scripts/launch_devkorth_test_server.sh
   ```

2. **Connect with client:**
   ```bash
   minetest --address localhost --port 50000
   ```

3. **Grant privileges:**
   ```
   /grant <your_username> all
   ```

4. **Get building materials:**
   ```
   /giveme default:diamondblock 99
   /giveme default:mese 10
   /giveme default:water_source 10
   /giveme default:coalblock 10
   ```

5. **Build the shrine:**
   - Base: 5x5 diamond blocks at ground level
   - Center: 1 mese block (1 block above center)
   - Pillars: 3-high diamond blocks at each corner

6. **Set conditions:**
   - Place water within 10 blocks
   - Place coal block within 15 blocks  
   - Set night time: `/time 0:00`
   - Ensure open sky above

## Expected Results

When all conditions are met:
- Chat message: "The fabric of reality trembles..."
- Chat message: "DEVKORTH HAS MANIFESTED!"
- Particle effects around shrine
- Devkorth entity appears above shrine

## Debugging

Check the log file for debug messages:
```bash
tail -f /home/tdeshane/luanti/devkorth_test.log | grep -E "\[Devkorth"
```

Common issues:
- **No manifestation:** Check all conditions with debug messages
- **Crash on time crystal:** Fixed in latest version
- **Mod not loading:** Check world.mt has `load_mod_devkorth_mod = true`

## Shrine Coordinates Example

For shrine centered at (10, 10, 10):

**Base (y=10):**
- (8,10,8) to (12,10,12) - all diamond blocks

**Center (y=11):**
- (10,11,10) - mese block

**Pillars (y=11,12,13):**
- (8,11-13,8) - diamond blocks
- (8,11-13,12) - diamond blocks  
- (12,11-13,8) - diamond blocks
- (12,11-13,12) - diamond blocks

**Conditions:**
- Water at (15,10,10)
- Coal at (2,10,10)
- Night time
- Clear sky above

## Integration with Voyager

The test scripts are integrated into the luanti-voyager project:
- Uses voyager connection API for automated testing
- Logs compatible with voyager monitoring
- Can be extended with voyager agent behaviors

## Production vs Test

- **Production:** Port 30000 - DO NOT TEST HERE
- **Test:** Port 50000 - Safe for testing
- **Debug mode:** Enabled on test server only