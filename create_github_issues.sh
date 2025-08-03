#!/bin/bash
# Script to create GitHub issues for Luanti Voyager project

echo "Creating GitHub issues for good first contributions..."

# Issue 1: Mock World System
gh issue create \
  --title "Create MockWorld class for isolated agent testing" \
  --body "## Description
Currently tests depend on running a full Luanti server. Create a \`MockWorld\` class that simulates world state for unit testing agent behaviors without server dependencies.

## Requirements
- Implement \`MockWorld\` in \`luanti_voyager/test_utils.py\`
- Support basic operations: place/remove blocks, agent position, inventory
- Add fixtures to \`tests/conftest.py\`
- Write example test using MockWorld
- Update existing tests to use MockWorld where appropriate

## Value
Enables fast, reliable testing and easier development workflow

## Skills Needed
- Python testing patterns
- Basic understanding of agent architecture
- Fixture design

## Getting Started
1. Look at current test structure in \`tests/\`
2. Study how agent interacts with world in \`agent.py\`
3. Create minimal mock implementation
4. Add example usage" \
  --label "good first issue" \
  --label "testing" \
  --label "infrastructure"

# Issue 2: Skill Code Validator
gh issue create \
  --title "Create secure skill execution sandbox for LLM-generated code" \
  --body "## Description
Agents need to execute LLM-generated Python code safely. Create a skill validator that checks for dangerous operations and sandboxes execution.

## Requirements
- Create \`SkillValidator\` class in \`luanti_voyager/skills/validator.py\`
- Block dangerous imports (\`os\`, \`subprocess\`, \`eval\`, etc.)
- Restrict function calls to approved agent actions
- Add execution timeout limits
- Include comprehensive test suite for malicious code attempts
- Document security model

## Value
Critical for safe LLM skill execution

## Skills Needed
- Python security best practices
- AST parsing
- Sandboxing techniques

## Getting Started
1. Research Python AST module for code analysis
2. Look at existing skill structure in codebase
3. Start with basic import blocking
4. Expand to full sandboxing" \
  --label "good first issue" \
  --label "security" \
  --label "llm" \
  --label "core-feature"

# Issue 3: Visual Skill Debugger
gh issue create \
  --title "Add real-time skill visualization to web interface" \
  --body "## Description
Add a debugging panel to the web interface showing current agent thoughts, skill execution steps, and decision reasoning in real-time.

## Requirements
- Add \`/debug\` endpoint to \`web_server.py\`
- Create HTML/CSS/JS debugging interface
- Show current skill being executed
- Display LLM reasoning/prompts (when available)
- Add skill execution timeline
- Make it responsive and visually appealing

## Value
Improves developer experience and makes agent behavior transparent

## Skills Needed
- Web development (HTML/CSS/JavaScript)
- WebSocket communication
- UI/UX design

## Getting Started
1. Check existing web UI in \`web_ui/\`
2. Study WebSocket implementation in \`web_server.py\`
3. Create basic debug panel layout
4. Add real-time updates" \
  --label "good first issue" \
  --label "ui" \
  --label "developer-experience"

# Issue 4: Curriculum Learning Framework
gh issue create \
  --title "Implement structured skill progression system" \
  --body "## Description
Build a curriculum system that guides agents through structured learning paths from basic to advanced skills.

## Requirements
- Design YAML curriculum format
- Create \`CurriculumManager\` class
- Implement skill dependency tracking
- Add progression assessment methods
- Include 3-level example curriculum (beginner/intermediate/advanced)
- Create curriculum visualization tool

## Example Curriculum Structure:
\`\`\`yaml
beginner:
  - name: \"Basic Movement\"
    skills: [move_forward, turn]
    success_criteria: \"Move 100 blocks total\"
  - name: \"Resource Gathering\"
    skills: [find_wood, mine_block]
    prerequisites: [\"Basic Movement\"]
\`\`\`

## Value
Enables systematic skill development and progress tracking

## Skills Needed
- Educational design thinking
- Dependency management
- YAML/configuration handling

## Getting Started
1. Review STRATEGIC_ROADMAP.md for curriculum ideas
2. Design simple YAML format
3. Implement basic loader
4. Add progression tracking" \
  --label "good first issue" \
  --label "learning" \
  --label "curriculum" \
  --label "core-feature"

# Issue 5: Performance Profiling
gh issue create \
  --title "Create agent performance measurement suite" \
  --body "## Description
Add profiling tools and benchmark tasks to measure agent performance and track improvements over time.

## Requirements
- Create \`luanti_voyager/profiling.py\` with timing decorators
- Design 5 benchmark tasks:
  - Exploration (blocks discovered per minute)
  - Resource gathering (items collected)
  - Building (blocks placed correctly)
  - Survival (time without dying)
  - Goal completion (tasks achieved)
- Implement performance metrics collection
- Add benchmark running script with reporting
- Create simple progress visualization
- Integration with pytest for automated benchmarking

## Value
Enables performance optimization and regression detection

## Skills Needed
- Python profiling tools
- Metrics design
- Data visualization
- Pytest integration

## Getting Started
1. Review Python's cProfile and time modules
2. Create simple timing decorator
3. Design first benchmark task
4. Add reporting functionality" \
  --label "good first issue" \
  --label "performance" \
  --label "benchmarking"

# Issue 6: Skill Marketplace
gh issue create \
  --title "Create skill sharing and discovery system" \
  --body "## Description
Build a web interface for agents to share learned skills with the community and discover skills created by others.

## Requirements
- Add skill export/import functionality to \`SkillMemory\`
- Create \`/marketplace\` web interface
- Support skill rating and comments
- Add skill search and filtering
- Include usage examples and success rates
- Make skills downloadable as JSON

## Mock UI Elements:
- Skill cards with name, description, author
- Success rate statistics
- Download count
- User ratings
- Code preview

## Value
Enables community skill sharing and accelerates learning

## Skills Needed
- Full-stack web development
- API design
- Database basics (for ratings/comments)
- UI/UX design

## Getting Started
1. Study current SkillMemory implementation
2. Design skill export format
3. Create basic marketplace UI
4. Add community features" \
  --label "good first issue" \
  --label "community" \
  --label "skills" \
  --label "ui"

# Issue 7: Agent Health Dashboard
gh issue create \
  --title "Add comprehensive agent monitoring and health metrics" \
  --body "## Description
Create a monitoring dashboard showing agent health, performance metrics, error rates, and system status.

## Requirements
- Add health check methods to \`VoyagerAgent\`
- Track metrics:
  - Uptime and stability
  - Actions per minute
  - Error rates and types
  - Memory usage
  - LLM API usage/costs
- Create \`/health\` dashboard page
- Add alerting for stuck agents or errors
- Include historical trend charts
- Export metrics in JSON format

## Dashboard Components:
- Real-time status indicators
- Performance graphs
- Error log viewer
- Resource usage meters
- Alert configuration

## Value
Improves agent reliability and debugging capabilities

## Skills Needed
- Monitoring and observability patterns
- Chart/graph libraries (Chart.js, D3.js)
- Dashboard design
- Metrics collection

## Getting Started
1. Add basic health check to agent
2. Collect simple metrics
3. Create dashboard layout
4. Add real-time updates" \
  --label "good first issue" \
  --label "monitoring" \
  --label "ui" \
  --label "reliability"

# Issue 8: Interactive Command Interface
gh issue create \
  --title "Build chat-style interface for real-time agent interaction" \
  --body "## Description
Add a chat interface allowing users to give commands to agents in natural language and see responses in real-time.

## Requirements
- Add \`/chat\` interface to web UI
- Implement command parsing for agent actions
- Support both text and voice input (optional)
- Show agent responses with reasoning
- Add command history and templates
- Make it work with all LLM providers

## Example Commands:
- \"Go find some wood\"
- \"Build a simple shelter\"
- \"What do you see around you?\"
- \"Show me your inventory\"
- \"Explain your current goal\"

## Value
Enables direct human-agent interaction and testing

## Skills Needed
- Conversational UI design
- Natural language processing basics
- WebSocket for real-time communication
- Frontend development

## Getting Started
1. Create basic chat UI layout
2. Connect to existing WebSocket
3. Parse simple commands
4. Add LLM integration for natural language" \
  --label "good first issue" \
  --label "ui" \
  --label "interaction" \
  --label "llm"

echo "✅ All issues created successfully!"
echo "View them at: https://github.com/toddllm/luanti-voyager/issues"