"""Tests for digest protocol."""

import pytest
from datetime import datetime, timezone

from frctl.planning.digest import (
    Digest,
    DigestMetadata,
    DigestStore,
)


class TestDigestMetadata:
    """Tests for DigestMetadata."""
    
    def test_create_metadata(self):
        """Test creating digest metadata."""
        metadata = DigestMetadata(
            original_tokens=1000,
            digest_tokens=150,
            compression_ratio=0.15,
            fidelity_estimate=0.95,
        )
        
        assert metadata.original_tokens == 1000
        assert metadata.digest_tokens == 150
        assert metadata.compression_ratio == 0.15
        assert metadata.fidelity_estimate == 0.95
        assert metadata.version == 1
        assert isinstance(metadata.created_at, datetime)
    
    def test_compression_percentage(self):
        """Test compression percentage calculation."""
        metadata = DigestMetadata(
            original_tokens=1000,
            digest_tokens=150,
            compression_ratio=0.15,
            fidelity_estimate=0.95,
        )
        
        assert metadata.compression_percentage == 15.0


class TestDigest:
    """Tests for Digest class."""
    
    def test_create_digest(self):
        """Test creating a basic digest."""
        metadata = DigestMetadata(
            original_tokens=500,
            digest_tokens=100,
            compression_ratio=0.2,
            fidelity_estimate=0.95,
        )
        
        digest = Digest(
            goal_id="test-goal-1",
            summary="Implemented authentication with JWT tokens.",
            key_artifacts=["frctl/auth/jwt.py", "tests/auth/test_jwt.py"],
            decisions=["Used PyJWT library", "7-day token expiry"],
            metadata=metadata,
        )
        
        assert digest.goal_id == "test-goal-1"
        assert "authentication" in digest.summary
        assert len(digest.key_artifacts) == 2
        assert len(digest.decisions) == 2
        assert digest.metadata.compression_ratio == 0.2
    
    def test_digest_with_children(self):
        """Test digest with child digest references."""
        metadata = DigestMetadata(
            original_tokens=1000,
            digest_tokens=150,
            compression_ratio=0.15,
            fidelity_estimate=0.93,
        )
        
        digest = Digest(
            goal_id="parent-goal",
            summary="Completed user management system.",
            child_digest_ids=["child-1", "child-2", "child-3"],
            metadata=metadata,
        )
        
        assert len(digest.child_digest_ids) == 3
        assert "child-1" in digest.child_digest_ids
    
    def test_to_context_string(self):
        """Test converting digest to context string."""
        metadata = DigestMetadata(
            original_tokens=500,
            digest_tokens=100,
            compression_ratio=0.2,
            fidelity_estimate=0.95,
        )
        
        digest = Digest(
            goal_id="test-goal",
            summary="Implemented user authentication.",
            key_artifacts=["auth.py"],
            decisions=["JWT tokens"],
            constraints=["Must use HTTPS"],
            metadata=metadata,
        )
        
        context_str = digest.to_context_string()
        
        assert "Implemented user authentication" in context_str
        assert "auth.py" in context_str
        assert "JWT tokens" in context_str
        assert "Must use HTTPS" in context_str
    
    def test_to_context_string_minimal(self):
        """Test context string with minimal digest."""
        metadata = DigestMetadata(
            original_tokens=100,
            digest_tokens=50,
            compression_ratio=0.5,
            fidelity_estimate=0.85,
        )
        
        digest = Digest(
            goal_id="minimal-goal",
            summary="Simple task completed.",
            metadata=metadata,
        )
        
        context_str = digest.to_context_string()
        assert context_str == "Summary: Simple task completed."
    
    def test_validate_fidelity_pass(self):
        """Test fidelity validation passing."""
        metadata = DigestMetadata(
            original_tokens=500,
            digest_tokens=100,
            compression_ratio=0.2,
            fidelity_estimate=0.95,
        )
        
        digest = Digest(
            goal_id="test-goal",
            summary="High fidelity digest.",
            metadata=metadata,
        )
        
        assert digest.validate_fidelity(threshold=0.90)
    
    def test_validate_fidelity_fail(self):
        """Test fidelity validation failing."""
        metadata = DigestMetadata(
            original_tokens=500,
            digest_tokens=100,
            compression_ratio=0.2,
            fidelity_estimate=0.85,
        )
        
        digest = Digest(
            goal_id="test-goal",
            summary="Lower fidelity digest.",
            metadata=metadata,
        )
        
        assert not digest.validate_fidelity(threshold=0.90)
        assert digest.validate_fidelity(threshold=0.80)


class TestDigestStore:
    """Tests for DigestStore."""
    
    def test_create_empty_store(self):
        """Test creating empty digest store."""
        store = DigestStore()
        
        assert len(store.digests) == 0
        assert len(store.archive) == 0
    
    def test_add_digest(self):
        """Test adding digest to store."""
        store = DigestStore()
        
        metadata = DigestMetadata(
            original_tokens=500,
            digest_tokens=100,
            compression_ratio=0.2,
            fidelity_estimate=0.95,
        )
        
        digest = Digest(
            goal_id="goal-1",
            summary="First digest.",
            metadata=metadata,
        )
        
        store.add(digest)
        
        assert len(store.digests) == 1
        assert "goal-1" in store.digests
        assert store.digests["goal-1"].summary == "First digest."
    
    def test_add_digest_with_archival(self):
        """Test that adding digest archives previous version."""
        store = DigestStore()
        
        # Add first version
        metadata1 = DigestMetadata(
            original_tokens=500,
            digest_tokens=100,
            compression_ratio=0.2,
            fidelity_estimate=0.90,
        )
        digest1 = Digest(
            goal_id="goal-1",
            summary="First version.",
            metadata=metadata1,
        )
        store.add(digest1)
        
        # Add second version (should archive first)
        metadata2 = DigestMetadata(
            original_tokens=600,
            digest_tokens=120,
            compression_ratio=0.2,
            fidelity_estimate=0.92,
        )
        digest2 = Digest(
            goal_id="goal-1",
            summary="Second version.",
            metadata=metadata2,
        )
        store.add(digest2)
        
        # Check current version
        assert store.digests["goal-1"].summary == "Second version."
        
        # Check archived version
        assert len(store.archive["goal-1"]) == 1
        assert store.archive["goal-1"][0].summary == "First version."
    
    def test_get_digest(self):
        """Test retrieving digest from store."""
        store = DigestStore()
        
        metadata = DigestMetadata(
            original_tokens=500,
            digest_tokens=100,
            compression_ratio=0.2,
            fidelity_estimate=0.95,
        )
        digest = Digest(goal_id="goal-1", summary="Test.", metadata=metadata)
        store.add(digest)
        
        retrieved = store.get("goal-1")
        assert retrieved is not None
        assert retrieved.summary == "Test."
    
    def test_get_missing_digest(self):
        """Test retrieving non-existent digest."""
        store = DigestStore()
        
        retrieved = store.get("missing")
        assert retrieved is None
    
    def test_get_history(self):
        """Test retrieving digest history."""
        store = DigestStore()
        
        # Add multiple versions
        for i in range(3):
            metadata = DigestMetadata(
                original_tokens=500 + i * 100,
                digest_tokens=100 + i * 10,
                compression_ratio=0.2,
                fidelity_estimate=0.90 + i * 0.01,
            )
            digest = Digest(
                goal_id="goal-1",
                summary=f"Version {i+1}.",
                metadata=metadata,
            )
            store.add(digest)
        
        history = store.get_history("goal-1")
        assert len(history) == 3
        assert history[0].summary == "Version 1."
        assert history[1].summary == "Version 2."
        assert history[2].summary == "Version 3."
    
    def test_get_history_empty(self):
        """Test history for goal without digests."""
        store = DigestStore()
        
        history = store.get_history("missing")
        assert len(history) == 0
    
    def test_get_multiple(self):
        """Test retrieving multiple digests."""
        store = DigestStore()
        
        for i in range(5):
            metadata = DigestMetadata(
                original_tokens=500,
                digest_tokens=100,
                compression_ratio=0.2,
                fidelity_estimate=0.95,
            )
            digest = Digest(
                goal_id=f"goal-{i}",
                summary=f"Digest {i}.",
                metadata=metadata,
            )
            store.add(digest)
        
        # Get subset
        retrieved = store.get_multiple(["goal-1", "goal-3", "goal-5", "missing"])
        
        assert len(retrieved) == 2  # goal-1 and goal-3 (goal-5 and missing don't exist)
        assert any(d.goal_id == "goal-1" for d in retrieved)
        assert any(d.goal_id == "goal-3" for d in retrieved)
    
    def test_aggregate_tokens(self):
        """Test aggregating token counts."""
        store = DigestStore()
        
        # Add digests with different token counts
        for i, tokens in enumerate([100, 150, 200]):
            metadata = DigestMetadata(
                original_tokens=500,
                digest_tokens=tokens,
                compression_ratio=0.2,
                fidelity_estimate=0.95,
            )
            digest = Digest(
                goal_id=f"goal-{i}",
                summary=f"Digest {i}.",
                metadata=metadata,
            )
            store.add(digest)
        
        total = store.aggregate_tokens(["goal-0", "goal-1", "goal-2"])
        assert total == 450  # 100 + 150 + 200
        
        partial = store.aggregate_tokens(["goal-0", "goal-2"])
        assert partial == 300  # 100 + 200
    
    def test_get_quality_stats_empty(self):
        """Test quality stats for empty store."""
        store = DigestStore()
        
        stats = store.get_quality_stats()
        assert stats["avg_compression"] == 0.0
        assert stats["avg_fidelity"] == 0.0
        assert stats["total_digests"] == 0
    
    def test_get_quality_stats(self):
        """Test quality statistics calculation."""
        store = DigestStore()
        
        # Add digests with varying quality
        compressions = [0.1, 0.2, 0.3]
        fidelities = [0.95, 0.90, 0.85]
        
        for i, (comp, fid) in enumerate(zip(compressions, fidelities)):
            metadata = DigestMetadata(
                original_tokens=1000,
                digest_tokens=int(1000 * comp),
                compression_ratio=comp,
                fidelity_estimate=fid,
            )
            digest = Digest(
                goal_id=f"goal-{i}",
                summary=f"Digest {i}.",
                metadata=metadata,
            )
            store.add(digest)
        
        stats = store.get_quality_stats()
        
        assert stats["total_digests"] == 3
        assert abs(stats["avg_compression"] - 0.2) < 0.01  # (0.1 + 0.2 + 0.3) / 3
        assert abs(stats["avg_fidelity"] - 0.90) < 0.01    # (0.95 + 0.90 + 0.85) / 3
    
    def test_quality_stats_with_archive(self):
        """Test quality stats include archive count."""
        store = DigestStore()
        
        # Add and update same goal multiple times
        for i in range(3):
            metadata = DigestMetadata(
                original_tokens=500,
                digest_tokens=100,
                compression_ratio=0.2,
                fidelity_estimate=0.90,
            )
            digest = Digest(
                goal_id="goal-1",
                summary=f"Version {i+1}.",
                metadata=metadata,
            )
            store.add(digest)
        
        stats = store.get_quality_stats()
        
        assert stats["total_digests"] == 1
        assert stats["total_archived"] == 2  # First two versions archived
