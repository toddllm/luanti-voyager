from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID, uuid4


class VoteType(Enum):
    """Types of votes that can be cast."""
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"
    LIKE = "like"
    STAR = "star"  # 1-5 star rating
    EMOJI = "emoji"  # Generic emoji reaction


class CommentStatus(Enum):
    """Status of a comment."""
    ACTIVE = "active"
    HIDDEN = "hidden"
    DELETED = "deleted"
    FLAGGED = "flagged"


@dataclass
class Vote:
    """Represents a single vote on a submission or comment."""
    id: UUID = field(default_factory=uuid4)
    voter_id: UUID = field(default_factory=uuid4)
    target_id: UUID = field(default_factory=uuid4)  # Submission or comment ID
    target_type: str = "submission"  # 'submission' or 'comment'
    vote_type: VoteType = VoteType.LIKE
    value: int = 1  # Can be used for star ratings or weighted votes
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Comment:
    """Represents a comment on a submission."""
    id: UUID = field(default_factory=uuid4)
    author_id: UUID = field(default_factory=uuid4)
    submission_id: UUID = field(default_factory=uuid4)
    parent_id: Optional[UUID] = None  # For nested comments
    content: str = ""
    status: CommentStatus = CommentStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_deleted(self) -> bool:
        return self.status == CommentStatus.DELETED
    
    @property
    def is_visible(self) -> bool:
        return self.status in [CommentStatus.ACTIVE, CommentStatus.FLAGGED]


class CommunityManager:
    """Manages community interactions like voting and comments."""
    
    def __init__(self, storage_backend):
        self.storage = storage_backend
        self.vote_weights = {
            VoteType.UPVOTE: 1,
            VoteType.DOWNVOTE: -1,
            VoteType.LIKE: 1,
            VoteType.STAR: 1,  # Actual value stored in vote.value
            VoteType.EMOJI: 0  # Emoji reactions don't affect score
        }
    
    # Voting methods
    async def add_vote(
        self,
        voter_id: UUID,
        target_id: UUID,
        target_type: str = "submission",
        vote_type: VoteType = VoteType.LIKE,
        value: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Vote:
        """Add or update a vote on a submission or comment."""
        # Check if user already voted on this target
        existing_vote = await self.storage.get_vote(voter_id, target_id, target_type)
        
        if existing_vote:
            # Update existing vote
            existing_vote.vote_type = vote_type
            existing_vote.value = value
            existing_vote.updated_at = datetime.utcnow()
            existing_vote.metadata.update(metadata or {})
            await self.storage.save_vote(existing_vote)
            return existing_vote
        else:
            # Create new vote
            vote = Vote(
                voter_id=voter_id,
                target_id=target_id,
                target_type=target_type,
                vote_type=vote_type,
                value=value,
                metadata=metadata or {}
            )
            await self.storage.save_vote(vote)
            return vote
    
    async def remove_vote(self, voter_id: UUID, target_id: UUID) -> bool:
        """Remove a user's vote from a target."""
        return await self.storage.delete_vote(voter_id, target_id)
    
    async def get_vote_score(self, target_id: UUID, target_type: str = "submission") -> int:
        """Calculate the total vote score for a target."""
        votes = await self.storage.get_votes_for_target(target_id, target_type)
        return sum(
            vote.value * self.vote_weights.get(vote.vote_type, 0)
            for vote in votes
        )
    
    # Comment methods
    async def add_comment(
        self,
        author_id: UUID,
        submission_id: UUID,
        content: str,
        parent_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Comment:
        """Add a new comment to a submission."""
        comment = Comment(
            author_id=author_id,
            submission_id=submission_id,
            parent_id=parent_id,
            content=content,
            metadata=metadata or {}
        )
        await self.storage.save_comment(comment)
        return comment
    
    async def get_comment(self, comment_id: UUID) -> Optional[Comment]:
        """Get a comment by ID."""
        return await self.storage.get_comment(comment_id)
    
    async def get_submission_comments(
        self,
        submission_id: UUID,
        include_hidden: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Comment]:
        """Get all comments for a submission."""
        comments = await self.storage.get_comments(
            submission_id=submission_id,
            include_hidden=include_hidden,
            limit=limit,
            offset=offset
        )
        return self._organize_comments(comments)
    
    async def update_comment(
        self,
        comment_id: UUID,
        editor_id: UUID,
        content: Optional[str] = None,
        status: Optional[CommentStatus] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Comment]:
        """Update a comment's content or status."""
        comment = await self.storage.get_comment(comment_id)
        if not comment:
            return None
            
        # Verify editor has permission
        if comment.author_id != editor_id:
            # TODO: Check if editor is admin/moderator
            return None
            
        if content is not None:
            comment.content = content
        if status is not None:
            comment.status = status
        if metadata is not None:
            comment.metadata.update(metadata)
            
        comment.updated_at = datetime.utcnow()
        await self.storage.save_comment(comment)
        return comment
    
    async def delete_comment(self, comment_id: UUID, user_id: UUID) -> bool:
        """Mark a comment as deleted."""
        comment = await self.storage.get_comment(comment_id)
        if not comment:
            return False
            
        # Only author or admin can delete
        if comment.author_id != user_id:
            # TODO: Check if user is admin/moderator
            return False
            
        comment.status = CommentStatus.DELETED
        comment.updated_at = datetime.utcnow()
        await self.storage.save_comment(comment)
        return True
    
    # Helper methods
    def _organize_comments(self, comments: List[Comment]) -> List[Comment]:
        """Organize comments into a threaded structure."""
        comment_map = {comment.id: comment for comment in comments}
        root_comments = []
        
        for comment in comments:
            if comment.parent_id is None or comment.parent_id not in comment_map:
                root_comments.append(comment)
            else:
                parent = comment_map[comment.parent_id]
                if not hasattr(parent, 'replies'):
                    parent.replies = []
                parent.replies.append(comment)
        
        return root_comments
