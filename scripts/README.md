# Luanti Voyager Scripts

This directory contains utility scripts for the luanti-voyager project.

## Devkorth Testing Scripts

Scripts for testing the Devkorth mod:

### Server Management
- `launch_devkorth_test_server.sh` - Launch test server on port 50000
- `check_devkorth_status.sh` - Check status of servers and mod

### Testing Tools
- `manual_devkorth_test.py` - Generate commands for manual testing
- `test_devkorth_shrine.py` - Automated shrine building and testing
- `debug_devkorth.py` - Monitor logs and debug issues

## Usage

1. **Start test server:**
   ```bash
   ./launch_devkorth_test_server.sh
   ```

2. **Check everything is working:**
   ```bash
   ./check_devkorth_status.sh
   ```

3. **Get testing commands:**
   ```bash
   python3 manual_devkorth_test.py
   ```

4. **Monitor for issues:**
   ```bash
   python3 debug_devkorth.py /home/tdeshane/luanti/devkorth_test.log
   ```

## Important Notes

- **NEVER** test on production server (port 30000)
- Always use test server on port 50000
- Check `docs/devkorth_testing_guide.md` for full instructions

## Requirements

- Python 3.6+
- Minetest/Luanti server
- lsof (for port checking)
- Basic shell utilities

## Troubleshooting

If scripts fail to run:
1. Check execute permissions: `chmod +x *.sh`
2. Check Python path: `which python3`
3. Check server binary: `which minetest`
4. See logs: `/home/tdeshane/luanti/devkorth_test.log`