# Installation Guide

This guide provides step-by-step instructions for setting up Luanti Voyager on your system.

## Supported Platforms

- ✅ **macOS** - Fully tested and supported
- 🔄 **Linux (Ubuntu)** - Expected to work ([contribute instructions](https://github.com/toddllm/luanti-voyager/issues))
- 🔄 **Windows (WSL)** - Expected to work via WSL ([contribute instructions](https://github.com/toddllm/luanti-voyager/issues))
- ❌ **Windows (Native)** - Not supported, please use WSL

## Quick Start

For the fastest setup experience:

```bash
# Clone the repository
git clone --recursive https://github.com/toddllm/luanti-voyager.git
cd luanti-voyager

# Run the automated setup (includes Ollama)
./tools/quick_start_ollama.sh
```

This will handle everything automatically and start your first agent!

## macOS Installation

### Prerequisites

1. **Homebrew** - Package manager for macOS
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Python 3.8+** - Usually pre-installed on macOS
   ```bash
   python3 --version
   ```

### Step 1: Install Luanti

```bash
brew install --cask luanti
```

### Step 2: Clone the Repository

```bash
git clone --recursive https://github.com/toddllm/luanti-voyager.git
cd luanti-voyager
```

### Step 3: Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Install Game Files

Luanti requires a game to run. Install the standard Minetest Game:

```bash
# Create games directory
mkdir -p ~/Library/Application\ Support/minetest/games

# Clone Minetest Game
cd ~/Library/Application\ Support/minetest/games
git clone https://github.com/minetest/minetest_game.git
cd -
```

### Step 5: Install Craftium Mod

The Craftium mod enables AI agents to interact with the game:

```bash
# Install globally for all worlds
mkdir -p ~/Library/Application\ Support/minetest/mods
cd ~/Library/Application\ Support/minetest/mods
git clone https://github.com/mikelma/craftium.git
cd -
```

### Step 6: Start Luanti Server

```bash
# Create a world directory
mkdir -p ~/Library/Application\ Support/minetest/worlds/voyager_world

# Start the server (development port 40000)
/Applications/Luanti.app/Contents/MacOS/luanti --server \
  --world ~/Library/Application\ Support/minetest/worlds/voyager_world \
  --gameid minetest_game \
  --port 40000
```

You should see:
```
 _                   _   _ 
| |_   _  __ _ _ __ | |_(_)
| | | | |/ _` | '_ \| __| |
| | |_| | (_| | | | | |_| |
|_|\__,_|\__,_|_| |_|\__|_|
ACTION[Main]: Server for gameid="minetest_game" listening on [::]:40000.
```

### Step 7: Run Your First Agent

In a new terminal:

```bash
# Navigate to project directory
cd luanti-voyager

# Activate Python environment
source venv/bin/activate

# Run basic agent (no LLM)
python -m luanti_voyager.main \
  --name MyFirstBot \
  --port 40000 \
  --world-path ~/Library/Application\ Support/minetest/worlds/voyager_world \
  --llm none
```

### Step 8: View Your Agent

Open http://localhost:8090/viewer in your browser to see your agent explore!

## Linux (Ubuntu) Installation

*Instructions coming soon! We expect the setup to be similar to macOS.*

**Want to help?** Please test on Ubuntu and [contribute instructions](https://github.com/toddllm/luanti-voyager/issues).

Expected steps:
1. Install Luanti/Minetest via package manager
2. Clone repository and set up Python environment
3. Install game files and Craftium mod
4. Run server and agent

## Windows (WSL) Installation

*Instructions coming soon! Windows users should use WSL (Windows Subsystem for Linux).*

**Want to help?** Please test on WSL and [contribute instructions](https://github.com/toddllm/luanti-voyager/issues).

Expected steps:
1. Install WSL2 with Ubuntu
2. Follow Linux installation steps within WSL
3. Access web interface from Windows browser

## LLM Integration Options

### Local LLM with Ollama (Recommended)

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama and pull a model
ollama serve
ollama pull llama3.1

# Run agent with local LLM
python -m luanti_voyager.main --name LocalBot --port 40000 --llm ollama
```

### OpenAI GPT

```bash
export OPENAI_API_KEY=your_key_here
python -m luanti_voyager.main --name GPTBot --port 40000 --llm openai
```

### Anthropic Claude

```bash
export ANTHROPIC_API_KEY=your_key_here
python -m luanti_voyager.main --name ClaudeBot --port 40000 --llm anthropic
```

## Port Configuration

- **Production**: Port 30000 (default Minetest port)
- **Development**: Port 40000 (recommended for local development)
- **Testing**: Port 40001+

Using different ports allows you to run multiple environments simultaneously.

## Troubleshooting

### Common Issues

#### "Command timeout" errors
- Ensure Craftium mod is installed correctly
- Verify the server is running on the correct port
- Check that the world path matches

#### "Port already in use"
```bash
# macOS/Linux
lsof -i :40000
pkill -f luanti

# WSL
netstat -ano | findstr :40000
```

#### "Game not found"
- Verify minetest_game is cloned in the correct directory
- Check the game ID matches exactly

### Getting Help

1. Check the [README](README.md) for more information
2. Search [existing issues](https://github.com/toddllm/luanti-voyager/issues)
3. Join the discussion on Matrix: `#luanti-voyager:matrix.org`
4. Create a new issue with your specific problem

## Contributing

We welcome contributions! Areas where help is needed:

1. **Linux (Ubuntu) installation instructions**
2. **WSL installation instructions**
3. **Package manager integrations** (apt, dnf, etc.)
4. **Docker setup** for consistent environments
5. **Automated installation scripts** for different platforms

Please test the installation process on your platform and submit a PR with instructions!

## Next Steps

Once you have Luanti Voyager running:

1. Try different LLM providers
2. Experiment with multi-agent systems
3. Create custom agent behaviors
4. Share your discoveries with the community!

Happy exploring! 🎮🤖🚀