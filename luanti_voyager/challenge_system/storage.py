from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from .challenge import Challenge, ChallengeStatus, ChallengeType
from .submission import Submission, SubmissionStatus
from .leaderboard import Leaderboard, LeaderboardEntry
from .community import Vote, Comment, CommentStatus, VoteType
from .showcase import ShowcaseEntry, ShowcaseCategory


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    # Challenge methods
    @abstractmethod
    async def save_challenge(self, challenge: Challenge) -> bool:
        """Save a challenge to storage."""
        pass
    
    @abstractmethod
    async def get_challenge(self, challenge_id: UUID) -> Optional[Challenge]:
        """Retrieve a challenge by ID."""
        pass
    
    @abstractmethod
    async def list_challenges(
        self,
        status: Optional[ChallengeStatus] = None,
        challenge_type: Optional[ChallengeType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Challenge]:
        """List challenges with optional filtering."""
        pass
    
    # Submission methods
    @abstractmethod
    async def save_submission(self, submission: Submission) -> bool:
        """Save a submission to storage."""
        pass
    
    @abstractmethod
    async def get_submission(self, submission_id: UUID) -> Optional[Submission]:
        """Retrieve a submission by ID."""
        pass
    
    @abstractmethod
    async def list_submissions(
        self,
        challenge_id: Optional[UUID] = None,
        team_id: Optional[UUID] = None,
        participant_id: Optional[UUID] = None,
        status: Optional[SubmissionStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Submission]:
        """List submissions with optional filtering."""
        pass
    
    # Leaderboard methods
    @abstractmethod
    async def get_leaderboard(self, challenge_id: UUID) -> Optional[Leaderboard]:
        """Get the leaderboard for a challenge."""
        pass
    
    @abstractmethod
    async def update_leaderboard(
        self, 
        challenge_id: UUID, 
        submission_id: UUID, 
        evaluation: 'EvaluationResult'
    ) -> bool:
        """Update the leaderboard with new submission results."""
        pass
    
    @abstractmethod
    async def get_leaderboard_entry(
        self, 
        challenge_id: UUID, 
        submission_id: UUID
    ) -> Optional[LeaderboardEntry]:
        """Get a specific leaderboard entry."""
        pass
    
    # Community methods
    @abstractmethod
    async def save_vote(self, vote: 'Vote') -> bool:
        """Save a vote to storage."""
        pass
    
    @abstractmethod
    async def get_vote(self, voter_id: UUID, target_id: UUID, target_type: str) -> Optional['Vote']:
        """Get a specific vote by voter and target."""
        pass
    
    @abstractmethod
    async def delete_vote(self, voter_id: UUID, target_id: UUID) -> bool:
        """Delete a vote."""
        pass
    
    @abstractmethod
    async def get_votes_for_target(
        self, 
        target_id: UUID, 
        target_type: str,
        vote_type: Optional[VoteType] = None
    ) -> List['Vote']:
        """Get all votes for a specific target."""
        pass
    
    @abstractmethod
    async def save_comment(self, comment: 'Comment') -> bool:
        """Save a comment to storage."""
        pass
    
    @abstractmethod
    async def get_comment(self, comment_id: UUID) -> Optional['Comment']:
        """Get a comment by ID."""
        pass
    
    @abstractmethod
    async def get_comments(
        self,
        submission_id: UUID,
        parent_id: Optional[UUID] = None,
        include_hidden: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List['Comment']:
        """Get comments for a submission, optionally filtered by parent comment."""
        pass
    
    @abstractmethod
    async def get_comment_count(
        self,
        submission_id: UUID,
        include_hidden: bool = False
    ) -> int:
        """Get the count of comments for a submission."""
        pass
    
    # Showcase methods
    @abstractmethod
    async def save_showcase_entry(self, entry: ShowcaseEntry) -> bool:
        """Save a showcase entry to storage."""
        pass
    
    @abstractmethod
    async def get_showcase_entry(self, entry_id: UUID) -> Optional[ShowcaseEntry]:
        """Get a showcase entry by ID."""
        pass
    
    @abstractmethod
    async def list_showcase_entries(
        self,
        challenge_id: Optional[UUID] = None,
        category: Optional[ShowcaseCategory] = None,
        featured_only: bool = False,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ShowcaseEntry]:
        """List showcase entries with optional filtering."""
        pass
    
    @abstractmethod
    async def delete_showcase_entry(self, entry_id: UUID) -> bool:
        """Delete a showcase entry."""
        pass
    
    # Documentation methods
    @abstractmethod
    async def save_document(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        """Save a document to storage."""
        pass
    
    @abstractmethod
    async def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        pass
    
    @abstractmethod
    async def query_documents(
        self,
        collection: str,
        challenge_id: Optional[str] = None,
        author_id: Optional[str] = None,
        tag: Optional[str] = None,
        published_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Query documents with optional filtering."""
        pass
    
    @abstractmethod
    async def increment_document_counter(
        self, 
        collection: str, 
        doc_id: str, 
        field: str, 
        amount: int = 1
    ) -> bool:
        """Atomically increment a counter field in a document."""
        pass


class InMemoryStorage(StorageBackend):
    """Simple in-memory storage for testing and development."""
    
    def __init__(self):
        self.challenges: Dict[UUID, Challenge] = {}
        self.submissions: Dict[UUID, Submission] = {}
        self.leaderboards: Dict[UUID, Leaderboard] = {}
        self.votes: Dict[Tuple[UUID, UUID], Vote] = {}  # (voter_id, target_id) -> Vote
        self.comments: Dict[UUID, Comment] = {}  # comment_id -> Comment
        self.showcase_entries: Dict[UUID, ShowcaseEntry] = {}  # entry_id -> ShowcaseEntry
        self.documents: Dict[str, Dict[str, Any]] = {}  # collection -> {doc_id -> doc}
    
    # Challenge methods
    async def save_challenge(self, challenge: Challenge) -> bool:
        self.challenges[challenge.id] = challenge
        return True
    
    async def get_challenge(self, challenge_id: UUID) -> Optional[Challenge]:
        return self.challenges.get(challenge_id)
    
    async def list_challenges(
        self,
        status: Optional[ChallengeStatus] = None,
        challenge_type: Optional[ChallengeType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Challenge]:
        result = []
        
        for challenge in self.challenges.values():
            if status and challenge.status != status:
                continue
            if challenge_type and challenge.challenge_type != challenge_type:
                continue
            if tags and not any(tag in challenge.tags for tag in tags):
                continue
                
            result.append(challenge)
            
        return result[offset:offset+limit]
    
    # Submission methods
    async def save_submission(self, submission: Submission) -> bool:
        self.submissions[submission.id] = submission
        return True
    
    async def get_submission(self, submission_id: UUID) -> Optional[Submission]:
        return self.submissions.get(submission_id)
    
    async def list_submissions(
        self,
        challenge_id: Optional[UUID] = None,
        team_id: Optional[UUID] = None,
        participant_id: Optional[UUID] = None,
        status: Optional[SubmissionStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Submission]:
        result = []
        
        for submission in self.submissions.values():
            if challenge_id and submission.challenge_id != challenge_id:
                continue
            if team_id and submission.team_id != team_id:
                continue
            if participant_id and participant_id not in submission.participant_ids:
                continue
            if status and submission.status != status:
                continue
                
            result.append(submission)
            
        return result[offset:offset+limit]
    
    # Leaderboard methods
    async def get_leaderboard(self, challenge_id: UUID) -> Optional[Leaderboard]:
        return self.leaderboards.get(challenge_id)
    
    async def update_leaderboard(
        self, 
        challenge_id: UUID, 
        submission_id: UUID, 
        evaluation: 'EvaluationResult'
    ) -> bool:
        if challenge_id not in self.leaderboards:
            self.leaderboards[challenge_id] = Leaderboard(challenge_id)
            
        submission = await self.get_submission(submission_id)
        if not submission:
            return False
            
        leaderboard = self.leaderboards[challenge_id]
        leaderboard.add_or_update_entry(submission, evaluation)
        return True
    
    async def get_leaderboard_entry(
        self, 
        challenge_id: UUID, 
        submission_id: UUID
    ) -> Optional[LeaderboardEntry]:
        leaderboard = await self.get_leaderboard(challenge_id)
        if not leaderboard:
            return None
            
        for entry in leaderboard.entries.values():
            if entry.submission_id == submission_id:
                return entry
                
        return None
    
    # Community methods
    async def save_vote(self, vote: Vote) -> bool:
        self.votes[(vote.voter_id, vote.target_id)] = vote
        return True
    
    async def get_vote(self, voter_id: UUID, target_id: UUID, target_type: str) -> Optional[Vote]:
        return self.votes.get((voter_id, target_id))
    
    async def delete_vote(self, voter_id: UUID, target_id: UUID) -> bool:
        key = (voter_id, target_id)
        if key in self.votes:
            del self.votes[key]
            return True
        return False
    
    async def get_votes_for_target(
        self, 
        target_id: UUID, 
        target_type: str,
        vote_type: Optional[VoteType] = None
    ) -> List[Vote]:
        return [
            vote for vote in self.votes.values()
            if vote.target_id == target_id 
            and vote.target_type == target_type
            and (vote_type is None or vote.vote_type == vote_type)
        ]
    
    async def save_comment(self, comment: Comment) -> bool:
        self.comments[comment.id] = comment
        return True
    
    async def get_comment(self, comment_id: UUID) -> Optional[Comment]:
        return self.comments.get(comment_id)
    
    async def get_comments(
        self,
        submission_id: UUID,
        parent_id: Optional[UUID] = None,
        include_hidden: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Comment]:
        result = []
        
        for comment in self.comments.values():
            if comment.submission_id != submission_id:
                continue
                
            if parent_id is not None and comment.parent_id != parent_id:
                continue
                
            if not include_hidden and comment.status != CommentStatus.ACTIVE:
                continue
                
            result.append(comment)
        
        # Sort by creation date, oldest first
        result.sort(key=lambda x: x.created_at)
        return result[offset:offset+limit]
    
    async def get_comment_count(
        self,
        submission_id: UUID,
        include_hidden: bool = False
    ) -> int:
        count = 0
        for comment in self.comments.values():
            if comment.submission_id != submission_id:
                continue
                
            if not include_hidden and comment.status != CommentStatus.ACTIVE:
                continue
                
            count += 1
            
        return count
    
    # Showcase methods
    async def save_showcase_entry(self, entry: ShowcaseEntry) -> bool:
        self.showcase_entries[entry.id] = entry
        return True
    
    async def get_showcase_entry(self, entry_id: UUID) -> Optional[ShowcaseEntry]:
        return self.showcase_entries.get(entry_id)
    
    async def list_showcase_entries(
        self,
        challenge_id: Optional[UUID] = None,
        category: Optional[ShowcaseCategory] = None,
        featured_only: bool = False,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ShowcaseEntry]:
        result = []
        now = datetime.utcnow()
        
        for entry in self.showcase_entries.values():
            if challenge_id and entry.challenge_id != challenge_id:
                continue
                
            if category and entry.category != category:
                continue
                
            if featured_only and (
                not entry.featured or 
                (entry.featured_until and entry.featured_until < now)
            ):
                continue
                
            if tags and not any(tag in entry.tags for tag in tags):
                continue
                
            result.append(entry)
        
        # Sort by featured status and creation date
        result.sort(
            key=lambda x: (
                not x.featured or (x.featured_until and x.featured_until < now),
                -x.created_at.timestamp()
            )
        )
        
        return result[offset:offset + limit]
    
    async def delete_showcase_entry(self, entry_id: UUID) -> bool:
        if entry_id in self.showcase_entries:
            del self.showcase_entries[entry_id]
            return True
        return False
    
    # Documentation methods
    async def save_document(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        if collection not in self.documents:
            self.documents[collection] = {}
        self.documents[collection][doc_id] = data
        return True
    
    async def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        return self.documents.get(collection, {}).get(doc_id)
    
    async def query_documents(
        self,
        collection: str,
        challenge_id: Optional[str] = None,
        author_id: Optional[str] = None,
        tag: Optional[str] = None,
        published_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        if collection not in self.documents:
            return []
            
        result = []
        
        for doc in self.documents[collection].values():
            if published_only and not doc.get("is_published", False):
                continue
                
            if challenge_id and doc.get("challenge_id") != challenge_id:
                continue
                
            if author_id and doc.get("author_id") != author_id:
                continue
                
            if tag and tag not in doc.get("tags", []):
                continue
                
            result.append(doc)
        
        # Sort by update time, newest first
        result.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        return result[offset:offset + limit]
    
    async def increment_document_counter(
        self, 
        collection: str, 
        doc_id: str, 
        field: str, 
        amount: int = 1
    ) -> bool:
        if collection not in self.documents or doc_id not in self.documents[collection]:
            return False
            
        doc = self.documents[collection][doc_id]
        doc[field] = doc.get(field, 0) + amount
        return True
