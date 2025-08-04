# Working Alternatives for Devkorth Testing

Since the network connection is not functional, here are working alternatives:

## 1. Manual Testing with Generated Commands

Use the command generation scripts:

```bash
# Generate commands for manual testing
python3 scripts/test_shrine_commands.py --username ToddLLM

# Or use the simple demo
python3 examples/devkorth_shrine_demo_simple.py
```

Copy and paste the generated commands into your Minetest client.

## 2. File-Based VoyagerAgent

The main `VoyagerAgent` class uses file-based communication:

```python
from luanti_voyager import VoyagerAgent

agent = VoyagerAgent(
    name="TestBot",
    world_path="/home/tdeshane/luanti/devkorth_test_world"
)
```

This requires the voyager_bot mod to be installed in the world.

## 3. Mock Testing

Use mock connections for development:

```bash
# Test with mock connection
python3 scripts/voyager_shrine_builder.py --mock
```

## 4. Direct Server Interaction

For testing Devkorth:

1. **Start test server**: 
   ```bash
   ./scripts/launch_devkorth_test_server.sh
   ```

2. **Monitor activity**:
   ```bash
   ./scripts/monitor_shrine_activity.sh
   ```

3. **Check status**:
   ```bash
   ./scripts/check_devkorth_status.sh
   ```

## 5. Debug Scripts

Use the debug scripts to verify mod functionality:

```bash
# Monitor Devkorth debug messages
python3 scripts/debug_devkorth.py /home/tdeshane/luanti/devkorth_test.log

# Watch for shrine activity
./scripts/monitor_devkorth_live.sh
```

## Summary

While the network connection doesn't work due to protocol mismatch (TCP vs UDP), the testing framework provides:

✅ Command generation for manual testing
✅ Server management scripts  
✅ Log monitoring and debugging tools
✅ Mock testing capabilities
✅ File-based agent communication (with mod)

These tools are sufficient for testing the Devkorth mod functionality.