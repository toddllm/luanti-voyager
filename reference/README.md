# Reference Directory

This directory contains external projects that serve as references and inspiration for Luanti Voyager development.

## Contents

### mindcraft-ai-agent/
**Source**: https://github.com/kolbytn/mindcraft  
**Purpose**: Reference implementation for AI agents in Minecraft  
**License**: MIT License (see mindcraft-ai-agent/LICENSE)

Mindcraft is the pioneering work that inspired many concepts in Luanti Voyager:
- Multi-agent coordination in voxel worlds
- LLM-driven gameplay mechanics  
- Agent memory and learning systems
- Task planning and execution frameworks

**Key Differences:**
- **Mindcraft**: Minecraft + Mineflayer (JavaScript/Node.js)
- **Luanti Voyager**: Luanti/Minetest + Python UDP protocol

## Usage

These are reference-only copies for study and analysis. They are **not** part of the Luanti Voyager codebase.

### Initializing Submodules

When cloning this repository:
```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/toddllm/luanti-voyager.git

# Or if already cloned, initialize submodules
git submodule update --init --recursive
```

### Updating References

To update to latest versions:
```bash
git submodule update --remote reference/mindcraft-ai-agent
```

## Related Documentation

See our analysis documents:
- `../docs/mindcraft_analysis.md` 
- `../docs/mindcraft_integration_proposal.md`
- `../research_reports/mindcraft_integration_research_2025-08-03.md`

## License Notes

Each reference project maintains its own license. Please respect the original authors' licensing terms when studying or adapting concepts.