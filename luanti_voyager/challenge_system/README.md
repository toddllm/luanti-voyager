# Luanti Voyager Challenge System

A flexible, community-driven challenge system designed for Luanti Voyager, supporting various types of challenges, automated scoring, leaderboards, and community engagement features.

## Features

- 🏆 **Challenge Management**: Create and manage different types of challenges (building, survival, innovation, etc.)
- 🚀 **Automated Evaluation**: Built-in evaluation system with customizable scoring criteria
- 🏅 **Leaderboards**: Track performance across different challenges
- 💬 **Community Features**: Comments, voting, and feedback mechanisms
- 🖼️ **Showcase Gallery**: Highlight top submissions and notable achievements
- 📅 **Scheduled Challenges**: Automate challenge rotation and scheduling
- 📚 **Documentation**: Built-in documentation system for guides and tutorials

## Core Components

### 1. Challenge System
- Create and manage challenges with custom rules and scoring
- Support for different challenge types and themes
- Automated challenge lifecycle management

### 2. Submission & Evaluation
- Submit entries to challenges
- Automated evaluation based on predefined criteria
- Support for manual judging when needed

### 3. Leaderboards
- Real-time ranking of participants
- Multiple scoring metrics and categories
- Historical performance tracking

### 4. Community Features
- Comments and discussions on submissions
- Voting and reactions
- User reputation system

### 5. Showcase Gallery
- Highlight exceptional submissions
- Curated collections and featured challenges
- Search and discovery tools

### 6. Documentation
- Guides and tutorials
- API documentation
- Challenge-specific documentation

## Installation

```bash
pip install -e .
```

## Quick Start

### Creating a Challenge

```python
from luanti_voyager.challenge_system import ChallengeSystem, ChallengeType
from datetime import datetime, timedelta

# Initialize the challenge system with in-memory storage
storage = InMemoryStorage()
challenge_system = ChallengeSystem(storage)

# Create a new challenge
challenge = challenge_system.create_challenge(
    name="Tower Building Challenge",
    description="Build the tallest tower possible with limited resources",
    challenge_type=ChallengeType.BUILDING,
    rules={
        "max_height": 100,  # blocks
        "time_limit": 3600,  # seconds
        "allowed_blocks": ["stone", "wood", "glass"],
        "scoring_criteria": [
            {"name": "height", "weight": 0.7, "max_score": 100},
            {"name": "aesthetics", "weight": 0.3, "max_score": 100}
        ]
    },
    duration_days=7,
    max_team_size=4,
    tags=["building", "creative"]
)

# Start the challenge
challenge_system.start_challenge(challenge.id)
```

### Submitting an Entry

```python
# Submit an entry to the challenge
submission = challenge_system.submit_entry(
    challenge_id=challenge.id,
    participant_ids=["user123", "user456"],
    team_id="team_awesome",
    content={
        "height": 85,
        "aesthetics": 90,
        "screenshot_url": "https://example.com/screenshot.png",
        "build_data": {...}
    },
    metadata={
        "build_time": 3542,  # seconds
        "blocks_used": {"stone": 500, "wood": 200, "glass": 100}
    }
)
```

### Setting Up a Scheduled Challenge

```python
from luanti_voyager.challenge_system import ChallengeScheduler, ScheduleFrequency

scheduler = ChallengeScheduler(storage)

# Add a monthly building challenge template
scheduler.add_template(
    "monthly_building",
    ChallengeTemplate(
        name="Monthly Building Challenge",
        description="A new building challenge every month with different themes",
        challenge_type=ChallengeType.BUILDING,
        rules={
            "scoring_criteria": [
                {"name": "creativity", "weight": 0.4},
                {"name": "execution", "weight": 0.4},
                {"name": "community_impact", "weight": 0.2}
            ]
        },
        duration_days=30,
        max_team_size=4,
        frequency=ScheduleFrequency.MONTHLY,
        start_date=datetime(2023, 1, 1)
    )
)

# Start the scheduler
await scheduler.start()
```

## API Reference

### ChallengeSystem

Core class for managing challenges and submissions.

#### Methods

- `create_challenge()`: Create a new challenge
- `get_challenge()`: Retrieve a challenge by ID
- `list_challenges()`: List challenges with optional filters
- `start_challenge()`: Mark a challenge as active
- `end_challenge()`: Mark a challenge as completed
- `submit_entry()`: Submit an entry to a challenge
- `evaluate_submission()`: Evaluate a submission
- `get_leaderboard()`: Get the leaderboard for a challenge

### CommunityManager

Handles community interactions like comments and voting.

#### Methods

- `add_comment()`: Add a comment to a submission
- `get_comments()`: Get comments for a submission
- `add_vote()`: Vote on a submission
- `get_votes()`: Get votes for a submission

### ShowcaseManager

Manages the showcase gallery of top submissions.

#### Methods

- `add_to_showcase()`: Add a submission to the showcase
- `get_showcase_entries()`: Get showcase entries
- `feature_entry()`: Feature a specific entry

### DocumentationManager

Manages documentation and guides.

#### Methods

- `create_guide()`: Create a new guide
- `get_guide()`: Get a guide by ID
- `list_guides()`: List available guides
- `update_guide()`: Update a guide

## Testing

Run the test suite with:

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

MIT
