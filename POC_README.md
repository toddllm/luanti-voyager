# Luanti Voyager POC - Getting Started

This is the first proof of concept for Luanti Voyager! 🚀

## What's Working

- ✅ Basic bot that can spawn in the world
- ✅ Simple movement and exploration
- ✅ Block detection and digging
- ✅ Inventory tracking
- ✅ Communication between Python and Luanti via mod

## Quick Start

1. **Install dependencies:**
   ```bash
   ./quickstart.sh
   ```

2. **Start Luanti server:**
   - Launch Luanti
   - Create a new world (or use existing)
   - Enable the `voyager_bot` mod in the world settings
   - Start the game

3. **Run the agent:**
   ```bash
   python -m luanti_voyager.main --name Explorer
   ```

## How It Works

The POC uses a simple file-based communication system:

1. **Luanti Mod** (`mods/voyager_bot/`): Provides bot control API
2. **Python Agent** (`luanti_voyager/`): Sends commands and makes decisions
3. **Communication**: Via text files in the world directory

### Available Commands

The bot currently supports:
- `spawn <name> <x> <y> <z>` - Create a bot
- `move <name> <direction> <distance>` - Move the bot
- `turn <name> <angle>` - Rotate the bot
- `dig <name> <x> <y> <z>` - Dig a block
- `place <name> <x> <y> <z> <item>` - Place a block
- `state <name>` - Get bot state

## Next Steps

1. **Add LLM Integration**: Connect OpenAI/Anthropic for intelligent behavior
2. **Skill System**: Save and reuse learned behaviors
3. **Better Perception**: More detailed world understanding
4. **Craftium Integration**: For faster, more robust communication
5. **Multi-Agent**: Support multiple agents working together

## Experimenting

Try modifying:
- `agent.py`: Change the `_decide_action()` method for different behaviors
- `init.lua`: Add new bot capabilities
- Create your own examples in `examples/`

## Known Limitations

- Simple file-based communication (will be replaced)
- No persistence between sessions yet
- Basic pathfinding only
- Limited error handling

But hey, it's a start! 🎉

## Contributing

This is super early - everything can change! Feel free to:
- Try wild experiments
- Break things
- Suggest better approaches
- Add whatever seems fun

The goal is to learn what works before building the "proper" version.