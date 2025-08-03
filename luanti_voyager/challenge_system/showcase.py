from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Any
from uuid import UUID, uuid4

from .challenge import Challenge
from .submission import Submission
from .leaderboard import LeaderboardEntry


class ShowcaseCategory(Enum):
    """Categories for showcasing submissions."""
    WINNERS = "winners"
    COMMUNITY_CHOICE = "community_choice"
    MOST_INNOVATIVE = "most_innovative"
    BEST_DESIGN = "best_design"
    BEST_PERFORMANCE = "best_performance"
    HIDDEN_GEM = "hidden_gem"
    STAFF_PICK = "staff_pick"


@dataclass
class ShowcaseEntry:
    """An entry in the showcase gallery."""
    id: UUID = field(default_factory=uuid4)
    submission_id: UUID = field(default_factory=uuid4)
    challenge_id: UUID = field(default_factory=uuid4)
    category: ShowcaseCategory = ShowcaseCategory.STAFF_PICK
    title: str = ""
    description: str = ""
    featured: bool = False
    featured_until: Optional[datetime] = None
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[UUID] = None


class ShowcaseManager:
    """Manages the showcase gallery for featured submissions."""
    
    def __init__(self, storage_backend):
        self.storage = storage_backend
    
    async def add_to_showcase(
        self,
        submission_id: UUID,
        category: ShowcaseCategory,
        title: str,
        description: str = "",
        featured: bool = False,
        featured_days: int = 7,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[UUID] = None
    ) -> ShowcaseEntry:
        """Add a submission to the showcase gallery."""
        # Get submission to verify it exists
        submission = await self.storage.get_submission(submission_id)
        if not submission:
            raise ValueError(f"Submission {submission_id} not found")
        
        # Create showcase entry
        entry = ShowcaseEntry(
            submission_id=submission_id,
            challenge_id=submission.challenge_id,
            category=category,
            title=title,
            description=description,
            featured=featured,
            featured_until=(
                datetime.utcnow() + timedelta(days=featured_days)
                if featured else None
            ),
            tags=set(tags or []),
            metadata=metadata or {},
            created_by=created_by
        )
        
        await self.storage.save_showcase_entry(entry)
        return entry
    
    async def get_showcase_entry(self, entry_id: UUID) -> Optional[ShowcaseEntry]:
        """Get a showcase entry by ID."""
        return await self.storage.get_showcase_entry(entry_id)
    
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
        return await self.storage.list_showcase_entries(
            challenge_id=challenge_id,
            category=category,
            featured_only=featured_only,
            tags=tags,
            limit=limit,
            offset=offset
        )
    
    async def update_showcase_entry(
        self,
        entry_id: UUID,
        **updates
    ) -> Optional[ShowcaseEntry]:
        """Update a showcase entry."""
        entry = await self.storage.get_showcase_entry(entry_id)
        if not entry:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        
        entry.updated_at = datetime.utcnow()
        await self.storage.save_showcase_entry(entry)
        return entry
    
    async def remove_from_showcase(self, entry_id: UUID) -> bool:
        """Remove an entry from the showcase."""
        return await self.storage.delete_showcase_entry(entry_id)
    
    async def get_featured_entries(
        self,
        limit: int = 10,
        include_expired: bool = False
    ) -> List[ShowcaseEntry]:
        """Get currently featured showcase entries."""
        now = datetime.utcnow()
        entries = await self.storage.list_showcase_entries(
            featured_only=True,
            limit=limit
        )
        
        if include_expired:
            return entries
        
        # Filter out expired featured entries
        return [
            entry for entry in entries
            if entry.featured_until is None or entry.featured_until > now
        ]


class DocumentationManager:
    """Manages documentation for the challenge system."""
    
    def __init__(self, storage_backend):
        self.storage = storage_backend
    
    async def create_guide(
        self,
        title: str,
        content: str,
        author_id: UUID,
        challenge_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        related_submissions: Optional[List[UUID]] = None,
        is_published: bool = False
    ) -> Dict[str, Any]:
        """Create a new documentation guide."""
        guide = {
            "id": str(uuid4()),
            "title": title,
            "content": content,
            "author_id": str(author_id),
            "challenge_id": str(challenge_id) if challenge_id else None,
            "tags": tags or [],
            "related_submissions": [str(sid) for sid in (related_submissions or [])],
            "is_published": is_published,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "views": 0,
            "upvotes": 0,
            "downvotes": 0
        }
        
        await self.storage.save_document("guides", guide["id"], guide)
        return guide
    
    async def get_guide(self, guide_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a guide by ID."""
        return await self.storage.get_document("guides", str(guide_id))
    
    async def update_guide(
        self,
        guide_id: UUID,
        updater_id: UUID,
        **updates
    ) -> Optional[Dict[str, Any]]:
        """Update a guide."""
        guide = await self.get_guide(guide_id)
        if not guide:
            return None
        
        # Only allow certain fields to be updated
        allowed_updates = {
            "title", "content", "tags", "related_submissions", 
            "is_published", "updated_at"
        }
        
        for key, value in updates.items():
            if key in allowed_updates:
                guide[key] = value
        
        guide["updated_at"] = datetime.utcnow().isoformat()
        
        # Track who made the last update
        if "editors" not in guide:
            guide["editors"] = []
        
        if str(updater_id) not in guide["editors"]:
            guide["editors"].append(str(updater_id))
        
        await self.storage.save_document("guides", str(guide_id), guide)
        return guide
    
    async def list_guides(
        self,
        challenge_id: Optional[UUID] = None,
        author_id: Optional[UUID] = None,
        tag: Optional[str] = None,
        published_only: bool = True,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List guides with optional filtering."""
        return await self.storage.query_documents(
            "guides",
            challenge_id=str(challenge_id) if challenge_id else None,
            author_id=str(author_id) if author_id else None,
            tag=tag,
            published_only=published_only,
            limit=limit,
            offset=offset
        )
    
    async def record_guide_view(self, guide_id: UUID) -> None:
        """Increment the view count for a guide."""
        await self.storage.increment_document_counter("guides", str(guide_id), "views")
    
    async def vote_on_guide(
        self, 
        guide_id: UUID, 
        voter_id: UUID, 
        is_upvote: bool
    ) -> Optional[Dict[str, Any]]:
        """Vote on a guide."""
        guide = await self.get_guide(guide_id)
        if not guide:
            return None
        
        # Check if user already voted
        vote_key = f"user_votes.{voter_id}"
        current_vote = guide.get("user_votes", {}).get(str(voter_id))
        
        if current_vote == is_upvote:
            # User is undoing their vote
            guide["upvotes" if is_upvote else "downvotes"] -= 1
            guide["user_votes"][str(voter_id)] = None
        else:
            # Handle vote change
            if current_vote is not None:
                # User is changing their vote
                guide["downvotes" if is_upvote else "upvotes"] -= 1
            
            # Add new vote
            guide["upvotes" if is_upvote else "downvotes"] += 1
            if "user_votes" not in guide:
                guide["user_votes"] = {}
            guide["user_votes"][str(voter_id)] = is_upvote
        
        await self.storage.save_document("guides", str(guide_id), guide)
        return {
            "upvotes": guide.get("upvotes", 0),
            "downvotes": guide.get("downvotes", 0),
            "user_vote": guide.get("user_votes", {}).get(str(voter_id))
        }
