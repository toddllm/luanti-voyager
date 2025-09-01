import asyncio
import pytest
from uuid import uuid4, UUID
from datetime import datetime, timedelta

from luanti_voyager.challenge_system import (
    ChallengeSystem, Challenge, ChallengeType, ChallengeStatus,
    Submission, SubmissionStatus, Leaderboard, LeaderboardEntry,
    Vote, Comment, ShowcaseEntry, ShowcaseCategory,
    CommunityManager, ShowcaseManager, DocumentationManager,
    ChallengeScheduler, ScheduleFrequency, ChallengeTemplate
)
from luanti_voyager.challenge_system.storage import InMemoryStorage

@pytest.fixture
def storage():
    return InMemoryStorage()

@pytest.fixture
def challenge_system(storage):
    return ChallengeSystem(storage)

@pytest.fixture
def sample_challenge(challenge_system):
    return challenge_system.create_challenge(
        name="Test Challenge",
        description="A test challenge",
        challenge_type=ChallengeType.BUILDING,
        rules={
            "max_score": 100,
            "criteria": ["completeness", "creativity"]
        },
        duration_days=7,
        max_team_size=4
    )

@pytest.mark.asyncio
async def test_create_and_get_challenge(challenge_system):
    # Test creating and retrieving a challenge
    challenge = challenge_system.create_challenge(
        name="Test Challenge",
        description="A test challenge",
        challenge_type=ChallengeType.BUILDING,
        rules={"max_score": 100},
        duration_days=7
    )
    
    retrieved = challenge_system.get_challenge(challenge.id)
    assert retrieved is not None
    assert retrieved.name == "Test Challenge"
    assert retrieved.status == ChallengeStatus.DRAFT

@pytest.mark.asyncio
async def test_submit_and_evaluate(challenge_system, sample_challenge):
    # Test submitting and evaluating an entry
    submission = challenge_system.submit_entry(
        challenge_id=sample_challenge.id,
        participant_ids=["user1"],
        content={"score": 85}
    )
    
    assert submission is not None
    assert submission.status == SubmissionStatus.SUBMITTED
    
    # Evaluate the submission
    evaluation = await challenge_system.evaluate_submission(
        submission_id=submission.id,
        metrics={"completeness": 90, "creativity": 80},
        is_final=True
    )
    
    assert evaluation.score > 0
    
    # Check leaderboard
    leaderboard = challenge_system.get_leaderboard(sample_challenge.id)
    assert leaderboard is not None
    assert len(leaderboard.entries) > 0

@pytest.mark.asyncio
async def test_community_features(challenge_system, sample_challenge):
    # Test community features (comments and voting)
    submission = challenge_system.submit_entry(
        challenge_id=sample_challenge.id,
        participant_ids=["user1"],
        content={"score": 75}
    )
    
    # Add a comment
    comment = await challenge_system.community.add_comment(
        author_id="user2",
        submission_id=submission.id,
        content="Great work!"
    )
    
    assert comment is not None
    
    # Add a vote
    vote = await challenge_system.community.add_vote(
        voter_id="user3",
        target_id=submission.id,
        target_type="submission",
        vote_type="like"
    )
    
    assert vote is not None
    
    # Get comments
    comments = await challenge_system.community.get_submission_comments(submission.id)
    assert len(comments) == 1
    assert comments[0].content == "Great work!"

@pytest.mark.asyncio
async def test_showcase(challenge_system, sample_challenge):
    # Test showcase functionality
    submission = challenge_system.submit_entry(
        challenge_id=sample_challenge.id,
        participant_ids=["user1"],
        content={"score": 95}
    )
    
    # Add to showcase
    entry = await challenge_system.showcase.add_to_showcase(
        submission_id=submission.id,
        category=ShowcaseCategory.WINNERS,
        title="Top Performer",
        description="Exceptional work!"
    )
    
    assert entry is not None
    
    # Get showcase entries
    entries = await challenge_system.showcase.get_showcase_entries()
    assert len(entries) == 1
    assert entries[0].title == "Top Performer"

@pytest.mark.asyncio
async def test_scheduler(storage):
    # Test challenge scheduler
    scheduler = ChallengeScheduler(storage)
    
    # Add a weekly challenge template
    scheduler.add_template(
        "weekly_test",
        ChallengeTemplate(
            name="Weekly Test Challenge",
            description="A weekly test challenge",
            challenge_type=ChallengeType.INNOVATION,
            rules={"max_score": 100},
            duration_days=7,
            frequency=ScheduleFrequency.WEEKLY,
            start_date=datetime.utcnow() - timedelta(days=1)  # Started yesterday
        )
    )
    
    # Run the scheduler
    await scheduler._schedule_new_challenges()
    
    # Check if a challenge was created
    challenges = await storage.list_challenges()
    assert len(challenges) > 0
    assert "Weekly Test Challenge" in [c.name for c in challenges]
