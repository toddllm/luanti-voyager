from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4


class SubmissionStatus(Enum):
    """Possible statuses for a submission."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    EVALUATED = "evaluated"
    DISQUALIFIED = "disqualified"
    WITHDRAWN = "withdrawn"


@dataclass
class EvaluationResult:
    """Results of evaluating a submission."""
    score: float = 0.0
    metrics: Dict[str, float] = field(default_factory=dict)
    feedback: str = ""
    evaluated_at: datetime = field(default_factory=datetime.utcnow)
    evaluated_by: Optional[UUID] = None  # System or user who performed evaluation
    is_final: bool = False
    notes: str = ""


@dataclass
class Submission:
    """Represents a submission to a challenge."""
    id: UUID = field(default_factory=uuid4)
    challenge_id: UUID = field(default_factory=uuid4)
    team_id: Optional[UUID] = None
    participant_ids: List[UUID] = field(default_factory=list)
    status: SubmissionStatus = SubmissionStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    title: str = ""
    description: str = ""
    content: Dict[str, Any] = field(default_factory=dict)  # Submission data (code, files, etc.)
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata
    evaluation_results: List[EvaluationResult] = field(default_factory=list)
    
    @property
    def latest_evaluation(self) -> Optional[EvaluationResult]:
        """Get the most recent evaluation result, if any."""
        if not self.evaluation_results:
            return None
        return sorted(self.evaluation_results, key=lambda x: x.evaluated_at, reverse=True)[0]
    
    @property
    def final_evaluation(self) -> Optional[EvaluationResult]:
        """Get the final evaluation result, if any."""
        for result in reversed(self.evaluation_results):
            if result.is_final:
                return result
        return None
    
    def add_evaluation(self, result: EvaluationResult) -> None:
        """Add a new evaluation result."""
        self.evaluation_results.append(result)
        self.updated_at = datetime.utcnow()
    
    def submit(self) -> bool:
        """Mark the submission as submitted."""
        if self.status != SubmissionStatus.DRAFT:
            return False
            
        self.status = SubmissionStatus.SUBMITTED
        self.submitted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return True
    
    def update_status(self, new_status: SubmissionStatus) -> bool:
        """Update the submission status with validation."""
        valid_transitions = {
            SubmissionStatus.DRAFT: [SubmissionStatus.SUBMITTED, SubmissionStatus.WITHDRAWN],
            SubmissionStatus.SUBMITTED: [
                SubmissionStatus.UNDER_REVIEW, 
                SubmissionStatus.WITHDRAWN,
                SubmissionStatus.DISQUALIFIED
            ],
            SubmissionStatus.UNDER_REVIEW: [
                SubmissionStatus.EVALUATED, 
                SubmissionStatus.DISQUALIFIED
            ],
            SubmissionStatus.EVALUATED: [SubmissionStatus.UNDER_REVIEW, SubmissionStatus.DISQUALIFIED],
            SubmissionStatus.DISQUALIFIED: [SubmissionStatus.UNDER_REVIEW],
            SubmissionStatus.WITHDRAWN: []
        }
        
        if new_status not in valid_transitions.get(self.status, []):
            return False
            
        self.status = new_status
        self.updated_at = datetime.utcnow()
        return True
