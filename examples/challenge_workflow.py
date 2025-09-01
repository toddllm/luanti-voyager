"""
Complete Challenge System Workflow Example

This example demonstrates the complete workflow of the Luanti Voyager Challenge System,
including creating challenges, making submissions, community interaction, and showcase.
"""
import asyncio
import random
from datetime import datetime, timedelta
from uuid import uuid4

from luanti_voyager.challenge_system import (
    ChallengeSystem, ChallengeType, ChallengeStatus,
    ShowcaseCategory, ScheduleFrequency, ChallengeTemplate, ChallengeScheduler
)
from luanti_voyager.challenge_system.storage import InMemoryStorage

async def main():
    # Initialize the system with in-memory storage
    storage = InMemoryStorage()
    challenge_system = ChallengeSystem(storage)
    
    print("=== Luanti Voyager Challenge System Demo ===\n")
    
    # 1. Create a challenge
    print("1. Creating a new building challenge...")
    challenge = challenge_system.create_challenge(
        name="Epic Castle Build",
        description="Build the most impressive medieval castle",
        challenge_type=ChallengeType.BUILDING,
        rules={
            "allowed_blocks": ["stone", "wood", "glass", "brick"],
            "dimensions": {"max_width": 100, "max_length": 100, "max_height": 50},
            "scoring_criteria": [
                {"name": "size", "weight": 0.3, "max_score": 100},
                {"name": "detail", "weight": 0.4, "max_score": 100},
                {"name": "creativity", "weight": 0.3, "max_score": 100}
            ]
        },
        duration_days=14,
        max_team_size=3,
        tags=["building", "creative", "medieval"]
    )
    
    # Start the challenge
    challenge_system.start_challenge(challenge.id)
    print(f"   Created challenge: {challenge.name} (ID: {challenge.id})\n")
    
    # 2. Simulate participants making submissions
    participants = [
        {"id": "builder1", "name": "Master Builder"},
        {"id": "crafter2", "name": "Creative Crafter"},
        {"id": "designer3", "name": "Design Wizard"}
    ]
    
    print("2. Simulating submissions...")
    submissions = []
    for i, participant in enumerate(participants, 1):
        submission = challenge_system.submit_entry(
            challenge_id=challenge.id,
            participant_ids=[participant["id"]],
            team_id=f"team_{i}",
            content={
                "screenshot_url": f"https://example.com/submissions/{participant['id']}.png",
                "build_data": {"blocks_used": random.randint(500, 2000)}
            },
            metadata={
                "build_time": random.randint(1800, 7200),  # 30m to 2h
                "blocks_used": {"stone": random.randint(200, 800), "wood": random.randint(100, 400)}
            }
        )
        submissions.append((participant, submission))
        print(f"   - {participant['name']} submitted an entry")
    
    # 3. Evaluate submissions
    print("\n3. Evaluating submissions...")
    for participant, submission in submissions:
        # Simulate evaluation with random scores
        evaluation = await challenge_system.evaluate_submission(
            submission_id=submission.id,
            metrics={
                "size": random.randint(70, 100),
                "detail": random.randint(60, 100),
                "creativity": random.randint(50, 100)
            },
            feedback=f"Great work on the {participant['name'].lower()} submission!",
            is_final=True
        )
        print(f"   - Evaluated {participant['name']}'s submission: {evaluation.score:.1f}/100")
    
    # 4. Show leaderboard
    print("\n4. Current Leaderboard:")
    leaderboard = challenge_system.get_leaderboard(challenge.id)
    for i, entry in enumerate(leaderboard.get_ranked_entries(), 1):
        participant = next(p for p, s in submissions if s.id == entry.submission_id)
        print(f"   {i}. {participant['name']}: {entry.score:.1f}")
    
    # 5. Community interaction
    print("\n5. Simulating community interaction...")
    winning_submission = submissions[0][1]  # First submission
    
    # Add comments
    await challenge_system.community.add_comment(
        author_id="spectator1",
        submission_id=winning_submission.id,
        content="Amazing castle! Love the details on the towers."
    )
    
    # Add votes
    for voter in ["user4", "user5", "user6"]:
        await challenge_system.community.add_vote(
            voter_id=voter,
            target_id=winning_submission.id,
            target_type="submission",
            vote_type="like"
        )
    
    print("   - Added comments and votes to the winning submission")
    
    # 6. Add to showcase
    print("\n6. Adding top submission to showcase...")
    showcase_entry = await challenge_system.showcase.add_to_showcase(
        submission_id=winning_submission.id,
        category=ShowcaseCategory.WINNERS,
        title="Best Medieval Castle",
        description="An outstanding example of medieval architecture with incredible attention to detail.",
        featured=True,
        featured_days=30,
        tags=["featured", "medieval", "castle"]
    )
    
    print(f"   - Added to showcase as '{showcase_entry.title}'")
    
    # 7. Set up a scheduled challenge
    print("\n7. Setting up a monthly challenge series...")
    scheduler = ChallengeScheduler(storage)
    
    scheduler.add_template(
        "monthly_building",
        ChallengeTemplate(
            name="Monthly Master Builders",
            description="A new building challenge every month with rotating themes",
            challenge_type=ChallengeType.BUILDING,
            rules={
                "scoring_criteria": [
                    {"name": "creativity", "weight": 0.4},
                    {"name": "technical_skill", "weight": 0.3},
                    {"name": "aesthetics", "weight": 0.3}
                ]
            },
            duration_days=30,
            max_team_size=4,
            frequency=ScheduleFrequency.MONTHLY,
            start_date=datetime.utcnow() + timedelta(days=1)  # Start tomorrow
        )
    )
    
    print("   - Added monthly challenge template")
    print("   - Scheduler will automatically create new challenges each month")
    
    print("\n=== Demo Complete! ===")
    print("\nThe challenge system is now running with:")
    print(f"- 1 active challenge: {challenge.name}")
    print(f"- {len(submissions)} submissions")
    print(f"- 1 showcase entry")
    print(f"- Monthly challenge series configured")

if __name__ == "__main__":
    asyncio.run(main())
