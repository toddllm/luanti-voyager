from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Set
from uuid import UUID, uuid4


class ChallengeType(Enum):
    """Types of challenges supported by the system."""
    BUILDING = "building"
    SURVIVAL = "survival"
    INNOVATION = "innovation"
    EDUCATION = "education"
    EXPLORATION = "exploration"


class ChallengeStatus(Enum):
    """Possible statuses for a challenge."""
    DRAFT = "draft"
    ANNOUNCED = "announced"
    ACTIVE = "active"
    JUDGING = "judging"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Challenge:
    """Represents a single challenge in the system."""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    challenge_type: ChallengeType = ChallengeType.BUILDING
    status: ChallengeStatus = ChallengeStatus.DRAFT
    rules: Dict[str, Any] = field(default_factory=dict)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_team_size: int = 1
    tags: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[UUID] = None
    
    def update(self, **kwargs) -> None:
        """Update challenge fields and set updated_at timestamp."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        """Check if the challenge is currently active."""
        now = datetime.utcnow()
        return (
            self.status == ChallengeStatus.ACTIVE
            and self.start_date is not None
            and self.end_date is not None
            and self.start_date <= now <= self.end_date
        )


class ChallengeSystem:
    """Core system for managing challenges and submissions."""
    
    def __init__(self, storage_backend=None):
        self.challenges: Dict[UUID, Challenge] = {}
        self.storage_backend = storage_backend
    
    def create_challenge(
        self,
        name: str,
        description: str,
        challenge_type: ChallengeType,
        rules: Dict[str, Any],
        duration_days: int = 30,
        max_team_size: int = 1,
        tags: Optional[List[str]] = None,
        created_by: Optional[UUID] = None
    ) -> Challenge:
        """Create a new challenge.
        
        Args:
            name: Name of the challenge
            description: Detailed description of the challenge
            challenge_type: Type of challenge
            rules: Dictionary containing challenge-specific rules and scoring criteria
            duration_days: Duration of the challenge in days
            max_team_size: Maximum number of participants per team
            tags: List of tags for categorization
            created_by: UUID of the user creating the challenge
            
        Returns:
            The created Challenge object
        """
        now = datetime.utcnow()
        challenge = Challenge(
            name=name,
            description=description,
            challenge_type=challenge_type,
            rules=rules,
            max_team_size=max_team_size,
            tags=set(tags or []),
            created_by=created_by,
            start_date=now,
            end_date=now + timedelta(days=duration_days),
            status=ChallengeStatus.DRAFT
        )
        
        self.challenges[challenge.id] = challenge
        if self.storage_backend:
            self.storage_backend.save_challenge(challenge)
            
        return challenge
    
    def get_challenge(self, challenge_id: UUID) -> Optional[Challenge]:
        """Retrieve a challenge by ID."""
        if self.storage_backend:
            return self.storage_backend.get_challenge(challenge_id)
        return self.challenges.get(challenge_id)
    
    def update_challenge(self, challenge_id: UUID, **updates) -> Optional[Challenge]:
        """Update an existing challenge."""
        challenge = self.get_challenge(challenge_id)
        if not challenge:
            return None
            
        challenge.update(**updates)
        
        if self.storage_backend:
            self.storage_backend.save_challenge(challenge)
            
        return challenge
    
    def list_challenges(
        self,
        status: Optional[ChallengeStatus] = None,
        challenge_type: Optional[ChallengeType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Challenge]:
        """List challenges with optional filtering."""
        result = []
        
        if self.storage_backend:
            return self.storage_backend.list_challenges(
                status=status,
                challenge_type=challenge_type,
                tags=tags,
                limit=limit,
                offset=offset
            )
        
        for challenge in self.challenges.values():
            if status and challenge.status != status:
                continue
            if challenge_type and challenge.challenge_type != challenge_type:
                continue
            if tags and not any(tag in challenge.tags for tag in tags):
                continue
                
            result.append(challenge)
            
        return result[offset:offset+limit]
    
    def start_challenge(self, challenge_id: UUID) -> bool:
        """Mark a challenge as active."""
        challenge = self.get_challenge(challenge_id)
        if not challenge:
            return False
            
        if challenge.status not in [ChallengeStatus.DRAFT, ChallengeStatus.ANNOUNCED]:
            return False
            
        challenge.status = ChallengeStatus.ACTIVE
        challenge.start_date = datetime.utcnow()
        
        if self.storage_backend:
            self.storage_backend.save_challenge(challenge)
            
        return True
    
    def end_challenge(self, challenge_id: UUID) -> bool:
        """Mark a challenge as completed and move to judging."""
        challenge = self.get_challenge(challenge_id)
        if not challenge or challenge.status != ChallengeStatus.ACTIVE:
            return False
            
        challenge.status = ChallengeStatus.JUDGING
        challenge.end_date = datetime.utcnow()
        
        if self.storage_backend:
            self.storage_backend.save_challenge(challenge)
            
        return True
