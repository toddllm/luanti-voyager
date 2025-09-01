from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from .submission import EvaluationResult, Submission


@dataclass
class LeaderboardEntry:
    """Represents an entry on a challenge leaderboard."""
    rank: int = 0
    submission_id: UUID = field(default_factory=uuid4)
    challenge_id: UUID = field(default_factory=uuid4)
    team_name: str = ""
    team_id: Optional[UUID] = None
    participant_ids: List[UUID] = field(default_factory=list)
    score: float = 0.0
    metrics: Dict[str, float] = field(default_factory=dict)
    submitted_at: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def from_submission(
        cls, 
        submission: Submission, 
        evaluation: Optional[EvaluationResult] = None
    ) -> 'LeaderboardEntry':
        """Create a leaderboard entry from a submission and its evaluation."""
        if evaluation is None and submission.final_evaluation:
            evaluation = submission.final_evaluation
        
        return cls(
            submission_id=submission.id,
            challenge_id=submission.challenge_id,
            team_id=submission.team_id,
            participant_ids=submission.participant_ids,
            score=evaluation.score if evaluation else 0.0,
            metrics=evaluation.metrics if evaluation else {},
            submitted_at=submission.submitted_at,
            last_updated=datetime.utcnow()
        )


class Leaderboard:
    """Manages the leaderboard for a challenge."""
    
    def __init__(self, challenge_id: UUID):
        self.challenge_id = challenge_id
        self.entries: Dict[UUID, LeaderboardEntry] = {}
        self.last_updated = datetime.utcnow()
    
    def add_or_update_entry(
        self, 
        submission: Submission, 
        evaluation: Optional[EvaluationResult] = None
    ) -> LeaderboardEntry:
        """Add or update a leaderboard entry for a submission."""
        entry = LeaderboardEntry.from_submission(submission, evaluation)
        self.entries[entry.submission_id] = entry
        self.last_updated = datetime.utcnow()
        return entry
    
    def remove_entry(self, submission_id: UUID) -> bool:
        """Remove an entry from the leaderboard."""
        if submission_id in self.entries:
            del self.entries[submission_id]
            self.last_updated = datetime.utcnow()
            return True
        return False
    
    def get_ranked_entries(self, limit: int = 100, offset: int = 0) -> List[LeaderboardEntry]:
        """Get ranked entries, sorted by score (descending)."""
        sorted_entries = sorted(
            self.entries.values(),
            key=lambda x: (x.score, x.submitted_at),
            reverse=True
        )
        
        # Update ranks
        for i, entry in enumerate(sorted_entries, 1):
            entry.rank = i
        
        return sorted_entries[offset:offset + limit]
    
    def get_rank(self, submission_id: UUID) -> Optional[int]:
        """Get the current rank of a submission."""
        entries = self.get_ranked_entries()
        for i, entry in enumerate(entries, 1):
            if entry.submission_id == submission_id:
                return i
        return None
    
    def get_top_teams(self, limit: int = 10) -> List[Tuple[Optional[UUID], float]]:
        """Get the top teams by their highest scoring submission."""
        team_scores: Dict[Optional[UUID], float] = {}
        
        for entry in self.entries.values():
            current_score = team_scores.get(entry.team_id, 0.0)
            if entry.score > current_score:
                team_scores[entry.team_id] = entry.score
        
        # Sort by score descending
        return sorted(
            team_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
    
    def get_team_entries(self, team_id: UUID) -> List[LeaderboardEntry]:
        """Get all entries for a specific team."""
        return [
            entry for entry in self.entries.values()
            if entry.team_id == team_id
        ]
    
    def get_participant_entries(self, participant_id: UUID) -> List[LeaderboardEntry]:
        """Get all entries for a specific participant."""
        return [
            entry for entry in self.entries.values()
            if participant_id in entry.participant_ids
        ]
    
    def clear(self) -> None:
        """Clear all entries from the leaderboard."""
        self.entries.clear()
        self.last_updated = datetime.utcnow()
