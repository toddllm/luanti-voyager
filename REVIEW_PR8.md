@cp90-pixel Thanks for the PR! Initial review:
- `luanti_voyager/challenge_system/leaderboard.py` references `uuid4` but only imports `UUID`, causing a `NameError`. Please add `uuid4` to the imports and rerun `pytest tests/test_challenge_system.py`.
- The PR introduces roughly 2.4k lines across many new modules. Consider splitting into smaller pieces or adding more documentation to ease review and maintenance.

To work with related PRs, merge this one first (after fixes) before addressing PR #9, which builds on it.
