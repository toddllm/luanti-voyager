# Build Documentation - Luanti Voyager

## ✅ Build Status

**CONFIRMED WORKING**: Vanilla Luanti fork builds and runs successfully!

- **Source**: `/luanti-source-voyager-fork/` (commit 39417cf7a)
- **Binary**: `/luanti-source-voyager-fork/bin/luanti`
- **Version**: Luanti 5.14.0-dev-39417cf7a
- **Test Server**: Running on port 40000 ✓

## 📋 Build Requirements

The following packages are required to build Luanti from source:

### Essential Build Tools
```bash
sudo apt-get install build-essential cmake git
```

### Required Libraries
```bash
sudo apt-get install \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    libcurl4-gnutls-dev \
    libzstd-dev \
    libsqlite3-dev \
    libsdl2-dev \
    libgl1-mesa-dev \
    zlib1g-dev
```

### Optional (but recommended)
```bash
sudo apt-get install \
    libogg-dev \
    libvorbis-dev \
    libopenal-dev \
    libgmp-dev \
    libjsoncpp-dev
```

## 🔨 Build Process

1. **Quick Build** (minimal dependencies):
   ```bash
   ./test-server/build-vanilla.sh
   ```

2. **Manual Build**:
   ```bash
   cd luanti-source-voyager-fork
   mkdir -p build && cd build
   cmake .. -DCMAKE_BUILD_TYPE=Release -DRUN_IN_PLACE=TRUE
   make -j$(nproc)
   ```

3. **Build Time**: ~2-5 minutes on modern hardware

## 🧪 Testing

1. **Start Test Server** (port 40000):
   ```bash
   ./test-server/start-test-server.sh
   ```

2. **Check Server Status**:
   ```bash
   ./test-server/check-ports.sh
   ```

3. **Stop Server**:
   ```bash
   ./test-server/stop-test-server.sh
   ```

## 📁 File Locations

- **Source Code**: `luanti-source-voyager-fork/`
- **Built Binary**: `luanti-source-voyager-fork/bin/luanti`
- **Test Server Config**: `test-server/luanti-test.conf`
- **Test World**: `test-server/test_world/`
- **Server Logs**: `test-server/test-server.log`

## 🎮 Current Configuration

- **Game**: devtest (included with Luanti)
- **Port**: 40000 (production uses 30000)
- **Bind**: 127.0.0.1 (localhost only)
- **Mods**: voyager_bot (our custom bot API)

## 📝 Notes

- The build uses bundled Lua (not LuaJIT) for maximum compatibility
- Sound is disabled in test build for faster compilation
- Server runs with `RUN_IN_PLACE=1` (no installation needed)
- Mod security is currently disabled for development (re-enable for production!)

## 🚀 Next Steps

Now that we have a working vanilla build:
1. Test the voyager_bot mod functionality
2. Add Voyager-specific modifications to the engine
3. Integrate with Craftium for better performance
4. Document any engine changes needed

## ⚠️ Important

This is a TEST setup on port 40000. The production server (if any) runs on port 30000 and should NOT be modified!