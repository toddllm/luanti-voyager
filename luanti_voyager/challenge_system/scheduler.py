import asyncio
from datetime import datetime, timedelta, timezone
from enum import Enum, auto
from typing import Dict, List, Optional, Callable, Any, Coroutine
from uuid import UUID
import logging

from .challenge import Challenge, ChallengeStatus, ChallengeType
from .storage import StorageBackend

logger = logging.getLogger(__name__)


class ScheduleFrequency(Enum):
    """Frequency at which challenges are scheduled."""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ChallengeTemplate:
    """Template for automatically creating challenges."""
    
    def __init__(
        self,
        name: str,
        description: str,
        challenge_type: ChallengeType,
        rules: Dict[str, Any],
        duration_days: int = 30,
        max_team_size: int = 1,
        tags: Optional[List[str]] = None,
        frequency: ScheduleFrequency = ScheduleFrequency.MONTHLY,
        start_date: Optional[datetime] = None,
        active: bool = True
    ):
        self.name = name
        self.description = description
        self.challenge_type = challenge_type
        self.rules = rules
        self.duration_days = duration_days
        self.max_team_size = max_team_size
        self.tags = tags or []
        self.frequency = frequency
        self.start_date = start_date or datetime.utcnow()
        self.active = active
        self.last_scheduled: Optional[datetime] = None
    
    def should_schedule(self, current_time: datetime) -> bool:
        """Determine if a new challenge should be scheduled based on the template."""
        if not self.active:
            return False
            
        if self.last_scheduled is None:
            return current_time >= self.start_date
            
        time_since_last = current_time - self.last_scheduled
        
        if self.frequency == ScheduleFrequency.DAILY:
            return time_since_last >= timedelta(days=1)
        elif self.frequency == ScheduleFrequency.WEEKLY:
            return time_since_last >= timedelta(weeks=1)
        elif self.frequency == ScheduleFrequency.BIWEEKLY:
            return time_since_last >= timedelta(weeks=2)
        elif self.frequency == ScheduleFrequency.MONTHLY:
            # Approximate month as 30 days
            return time_since_last >= timedelta(days=30)
        elif self.frequency == ScheduleFrequency.QUARTERLY:
            # Approximate quarter as 90 days
            return time_since_last >= timedelta(days=90)
        elif self.frequency == ScheduleFrequency.YEARLY:
            # Approximate year as 365 days
            return time_since_last >= timedelta(days=365)
            
        return False
    
    def next_occurrence(self, current_time: datetime) -> datetime:
        """Calculate the next occurrence of this challenge."""
        if self.last_scheduled is None:
            return self.start_date
            
        if self.frequency == ScheduleFrequency.DAILY:
            return self.last_scheduled + timedelta(days=1)
        elif self.frequency == ScheduleFrequency.WEEKLY:
            return self.last_scheduled + timedelta(weeks=1)
        elif self.frequency == ScheduleFrequency.BIWEEKLY:
            return self.last_scheduled + timedelta(weeks=2)
        elif self.frequency == ScheduleFrequency.MONTHLY:
            # Add approximately one month
            return self.last_scheduled + timedelta(days=30)
        elif self.frequency == ScheduleFrequency.QUARTERLY:
            # Add approximately three months
            return self.last_scheduled + timedelta(days=90)
        elif self.frequency == ScheduleFrequency.YEARLY:
            # Add approximately one year
            return self.last_scheduled + timedelta(days=365)
            
        return current_time + timedelta(days=1)  # Default to tomorrow


class ChallengeScheduler:
    """Manages the scheduling and automation of challenges."""
    
    def __init__(self, storage: StorageBackend):
        self.storage = storage
        self.templates: Dict[str, ChallengeTemplate] = {}
        self.running = False
        self._task: Optional[asyncio.Task] = None
    
    def add_template(self, name: str, template: ChallengeTemplate) -> None:
        """Add a challenge template to the scheduler."""
        self.templates[name] = template
    
    def remove_template(self, name: str) -> bool:
        """Remove a challenge template by name."""
        if name in self.templates:
            del self.templates[name]
            return True
        return False
    
    def get_template(self, name: str) -> Optional[ChallengeTemplate]:
        """Get a challenge template by name."""
        return self.templates.get(name)
    
    async def start(self, check_interval: int = 3600) -> None:
        """Start the scheduler with the specified check interval in seconds."""
        if self.running:
            logger.warning("Scheduler is already running")
            return
            
        self.running = True
        self._task = asyncio.create_task(self._run_scheduler(check_interval))
        logger.info("Challenge scheduler started")
    
    async def stop(self) -> None:
        """Stop the scheduler."""
        if not self.running or not self._task:
            return
            
        self.running = False
        self._task.cancel()
        
        try:
            await self._task
        except asyncio.CancelledError:
            logger.info("Challenge scheduler stopped")
    
    async def _run_scheduler(self, check_interval: int) -> None:
        """Main scheduler loop."""
        while self.running:
            try:
                await self._check_scheduled_challenges()
                await self._schedule_new_challenges()
                await asyncio.sleep(check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait a minute before retrying on error
    
    async def _check_scheduled_challenges(self) -> None:
        """Check for challenges that need to be started or ended."""
        now = datetime.utcnow()
        
        # Get all active or upcoming challenges
        challenges = await self.storage.list_challenges(
            status=ChallengeStatus.ANNOUNCED,
            limit=1000  # Should be reasonable for most cases
        )
        
        for challenge in challenges:
            # Start challenges that are scheduled to begin
            if challenge.start_date and challenge.start_date <= now:
                await self._start_challenge(challenge.id)
            
            # End challenges that are past their end date
            if challenge.end_date and challenge.end_date <= now:
                await self._end_challenge(challenge.id)
    
    async def _schedule_new_challenges(self) -> None:
        """Check templates and schedule new challenges as needed."""
        now = datetime.utcnow()
        
        for template_name, template in self.templates.items():
            if not template.active:
                continue
                
            if template.should_schedule(now):
                try:
                    # Generate a unique name with timestamp
                    timestamp = now.strftime("%Y%m%d-%H%M%S")
                    challenge_name = f"{template.name} - {timestamp}"
                    
                    # Create the challenge
                    challenge = Challenge(
                        name=challenge_name,
                        description=template.description,
                        challenge_type=template.challenge_type,
                        rules=template.rules,
                        max_team_size=template.max_team_size,
                        tags=set(template.tags),
                        status=ChallengeStatus.ANNOUNCED,
                        start_date=now + timedelta(days=1),  # Start tomorrow
                        end_date=now + timedelta(days=1 + template.duration_days)
                    )
                    
                    # Save the challenge
                    await self.storage.save_challenge(challenge)
                    template.last_scheduled = now
                    
                    logger.info(f"Scheduled new challenge: {challenge_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to schedule challenge from template {template_name}: {e}", exc_info=True)
    
    async def _start_challenge(self, challenge_id: UUID) -> bool:
        """Mark a challenge as active."""
        challenge = await self.storage.get_challenge(challenge_id)
        if not challenge or challenge.status != ChallengeStatus.ANNOUNCED:
            return False
            
        challenge.status = ChallengeStatus.ACTIVE
        await self.storage.save_challenge(challenge)
        logger.info(f"Started challenge: {challenge.name} ({challenge.id})")
        return True
    
    async def _end_challenge(self, challenge_id: UUID) -> bool:
        """Mark a challenge as completed and move to judging."""
        challenge = await self.storage.get_challenge(challenge_id)
        if not challenge or challenge.status != ChallengeStatus.ACTIVE:
            return False
            
        challenge.status = ChallengeStatus.JUDGING
        await self.storage.save_challenge(challenge)
        logger.info(f"Ended challenge: {challenge.name} ({challenge.id})")
        return True
    
    async def close(self) -> None:
        """Clean up resources."""
        await self.stop()
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
