"""Digest Protocol for context compression in planning."""

from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class DigestMetadata(BaseModel):
    """Metadata about digest quality and compression."""
    
    original_tokens: int = Field(..., description="Token count before compression")
    digest_tokens: int = Field(..., description="Token count after compression")
    compression_ratio: float = Field(..., description="Compression ratio (0-1)")
    fidelity_estimate: float = Field(..., description="Estimated information preservation (0-1)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = Field(1, description="Digest protocol version")
    
    @property
    def compression_percentage(self) -> float:
        """Return compression as percentage."""
        return self.compression_ratio * 100


class Digest(BaseModel):
    """Compressed summary of planning results.
    
    Digests preserve essential information from completed subtrees
    while minimizing token usage for parent contexts.
    """
    
    goal_id: str = Field(..., description="ID of the goal this digest summarizes")
    summary: str = Field(..., description="Concise summary of completed work")
    key_artifacts: List[str] = Field(
        default_factory=list,
        description="Important artifacts created (files, modules, etc.)"
    )
    decisions: List[str] = Field(
        default_factory=list,
        description="Key architectural or technical decisions made"
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="Important constraints or assumptions"
    )
    
    # Child digests for hierarchical aggregation
    child_digest_ids: List[str] = Field(
        default_factory=list,
        description="IDs of child goal digests aggregated here"
    )
    
    # Metadata
    metadata: DigestMetadata = Field(..., description="Quality and compression metrics")
    
    def to_context_string(self) -> str:
        """Convert digest to string for context injection.
        
        Returns:
            Formatted string suitable for LLM context
        """
        parts = [f"Summary: {self.summary}"]
        
        if self.key_artifacts:
            parts.append(f"Artifacts: {', '.join(self.key_artifacts)}")
        
        if self.decisions:
            parts.append(f"Decisions: {', '.join(self.decisions)}")
        
        if self.constraints:
            parts.append(f"Constraints: {', '.join(self.constraints)}")
        
        return " | ".join(parts)
    
    def validate_fidelity(self, threshold: float = 0.90) -> bool:
        """Check if digest meets fidelity threshold.
        
        Args:
            threshold: Minimum acceptable fidelity (0-1)
            
        Returns:
            True if fidelity >= threshold
        """
        return self.metadata.fidelity_estimate >= threshold


class DigestStore(BaseModel):
    """Storage for digests with versioning and archival."""
    
    digests: Dict[str, Digest] = Field(
        default_factory=dict,
        description="Mapping of goal_id -> Digest"
    )
    archive: Dict[str, List[Digest]] = Field(
        default_factory=dict,
        description="Archived digests by goal_id (versioned)"
    )
    
    def add(self, digest: Digest) -> None:
        """Add or update a digest.
        
        Archives previous version if one exists.
        
        Args:
            digest: Digest to store
        """
        goal_id = digest.goal_id
        
        # Archive existing digest if present
        if goal_id in self.digests:
            if goal_id not in self.archive:
                self.archive[goal_id] = []
            self.archive[goal_id].append(self.digests[goal_id])
        
        # Store new digest
        self.digests[goal_id] = digest
    
    def get(self, goal_id: str) -> Optional[Digest]:
        """Retrieve current digest for a goal.
        
        Args:
            goal_id: Goal identifier
            
        Returns:
            Current digest or None if not found
        """
        return self.digests.get(goal_id)
    
    def get_history(self, goal_id: str) -> List[Digest]:
        """Get all versions of a goal's digest.
        
        Args:
            goal_id: Goal identifier
            
        Returns:
            List of digests ordered from oldest to newest
        """
        history = self.archive.get(goal_id, []).copy()
        current = self.digests.get(goal_id)
        if current:
            history.append(current)
        return history
    
    def get_multiple(self, goal_ids: List[str]) -> List[Digest]:
        """Retrieve digests for multiple goals.
        
        Args:
            goal_ids: List of goal identifiers
            
        Returns:
            List of digests (skips missing ones)
        """
        return [
            self.digests[gid]
            for gid in goal_ids
            if gid in self.digests
        ]
    
    def aggregate_tokens(self, goal_ids: List[str]) -> int:
        """Calculate total tokens for multiple digests.
        
        Args:
            goal_ids: List of goal identifiers
            
        Returns:
            Sum of digest tokens
        """
        return sum(
            self.digests[gid].metadata.digest_tokens
            for gid in goal_ids
            if gid in self.digests
        )
    
    def get_quality_stats(self) -> Dict[str, float]:
        """Calculate quality statistics across all digests.
        
        Returns:
            Dictionary with avg compression, avg fidelity, etc.
        """
        if not self.digests:
            return {
                "avg_compression": 0.0,
                "avg_fidelity": 0.0,
                "total_digests": 0,
            }
        
        compressions = [d.metadata.compression_ratio for d in self.digests.values()]
        fidelities = [d.metadata.fidelity_estimate for d in self.digests.values()]
        
        return {
            "avg_compression": sum(compressions) / len(compressions),
            "avg_fidelity": sum(fidelities) / len(fidelities),
            "total_digests": len(self.digests),
            "total_archived": sum(len(v) for v in self.archive.values()),
        }
