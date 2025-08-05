# Project Structure

This document describes the organization of the Luanti Voyager repository.

## Directory Layout

```
luanti-voyager/
├── config/                 # Configuration files
│   ├── pytest.ini         # Pytest configuration
│   └── terrain-test-server.conf  # Luanti server configuration
│
├── docs/                   # Documentation
│   ├── AI_MAKERSPACE_TECHNICAL_REPORT.md  # AI integration report
│   ├── ai-makerspace-resources/           # AI Makerspace materials
│   │   ├── implementation-guides/         # 10 AI technique guides
│   │   ├── notebooks/                     # Jupyter notebooks
│   │   ├── synthesis/                     # Synthesized documentation
│   │   └── transcripts/                   # YouTube transcriptions
│   ├── images/             # Screenshots and diagrams
│   ├── mindcraft_analysis.md              # Mindcraft framework analysis
│   └── ...                 # Other documentation files
│
├── examples/               # Example code and demos
│   ├── multi_agent_demo.py
│   └── udp_connection_example.py
│
├── logs/                   # Runtime logs
│   └── ollama_traffic/     # Ollama API monitoring logs
│
├── luanti_voyager/         # Main package source code
│   ├── __init__.py
│   ├── agent.py           # Core agent implementation
│   ├── multi_agent.py     # Multi-agent coordination
│   └── ...
│
├── mods/                   # Luanti game mods
│   └── agent_game_mechanics/
│
├── reference/              # External reference materials
│   └── craftium-docs/
│
├── research_reports/       # AI research documentation
│   ├── distributed_skill_learning_research_*.md
│   └── ...
│
├── scripts/                # Utility and automation scripts
│   ├── enhanced_batch_processor.py
│   └── ...                # 40+ scripts for various tasks
│
├── tests/                  # Test files
│   ├── comprehensive_feature_test.py
│   ├── multi_agent_minimal_example.py
│   ├── simple_llm_test.py
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── behaviors/         # Behavior tests
│
├── tools/                  # Development tools
│   ├── quick_start_ollama.sh      # Quick setup script
│   ├── quickstart.sh              # Alternative setup
│   └── create_github_issues.sh    # Issue creation utility
│
├── worlds/                 # Luanti world saves
│
├── LICENSE                 # MIT License
├── README.md              # Main project documentation
├── INSTALL.md             # Installation guide
├── requirements.txt       # Python dependencies
└── setup.py              # Package setup
```

## Key Directories

### `/luanti_voyager`
The main Python package containing all source code for the AI agents, including:
- Agent behaviors and decision-making
- Multi-agent coordination systems
- LLM integrations
- Network protocols

### `/docs`
Comprehensive documentation including:
- Technical reports and analyses
- AI Makerspace integration materials
- Implementation guides for 10 AI techniques
- Research findings and proposals

### `/scripts`
40+ automation scripts for:
- AI Makerspace content processing
- Notebook downloading and analysis
- Synthesis generation
- Monitoring and debugging

### `/tests`
Test suite organized by type:
- Unit tests for individual components
- Integration tests for system interactions
- Behavior tests for agent capabilities
- Example scripts for testing features

### `/config`
Configuration files for:
- Testing framework (pytest)
- Luanti server settings
- Future: Agent configurations

### `/tools`
Developer utilities:
- Quick setup scripts
- GitHub automation
- Development helpers

## Finding Things

- **Want to run the project?** Start with `README.md` and `tools/quick_start_ollama.sh`
- **Looking for AI techniques?** Check `docs/ai-makerspace-resources/implementation-guides/`
- **Need test examples?** Look in `tests/` and `examples/`
- **Want to contribute?** Scripts in `scripts/` show how we process and generate content
- **Debugging?** Check `logs/` for runtime information

## Recent Changes

The repository was reorganized to improve maintainability:
- Configuration files moved to `config/`
- Test files consolidated in `tests/`
- Utility scripts moved to `tools/`
- Documentation organized in `docs/`

This structure follows common Python project conventions while accommodating the unique needs of an AI-powered game agent system.