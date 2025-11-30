"""Tests for plan persistence."""

import json
import pytest
from pathlib import Path
from datetime import datetime, timezone

from frctl.planning.goal import Goal, GoalStatus, Plan
from frctl.planning.persistence import PlanStore


@pytest.fixture
def temp_store(tmp_path):
    """Create a temporary plan store."""
    return PlanStore(base_path=tmp_path / ".frctl" / "plans")


@pytest.fixture
def sample_plan():
    """Create a sample plan for testing."""
    plan = Plan(
        id="test-plan-123",
        root_goal_id="goal-1",
    )
    
    # Add root goal
    root_goal = Goal(
        id="goal-1",
        description="Build a web application",
        status=GoalStatus.DECOMPOSING,
        depth=0,
    )
    plan.add_goal(root_goal)
    
    # Add child goals
    child1 = Goal(
        id="goal-2",
        description="Design database schema",
        status=GoalStatus.ATOMIC,
        parent_id="goal-1",
        depth=1,
    )
    child2 = Goal(
        id="goal-3",
        description="Create API endpoints",
        status=GoalStatus.PENDING,
        parent_id="goal-1",
        depth=1,
    )
    
    root_goal.add_child("goal-2")
    root_goal.add_child("goal-3")
    
    plan.add_goal(child1)
    plan.add_goal(child2)
    
    return plan


class TestPlanStore:
    """Test PlanStore basic functionality."""
    
    def test_create_store_creates_directories(self, temp_store):
        """Test that creating a store creates necessary directories."""
        assert temp_store.plans_dir.exists()
        assert temp_store.archive_dir.exists()
        assert temp_store.index_file.exists()
    
    def test_save_plan(self, temp_store, sample_plan):
        """Test saving a plan."""
        plan_path = temp_store.save(sample_plan)
        
        assert plan_path.exists()
        assert plan_path.name == "test-plan-123.json"
        
        # Verify JSON content
        with open(plan_path) as f:
            data = json.load(f)
        
        assert data['id'] == "test-plan-123"
        assert data['root_goal_id'] == "goal-1"
        assert len(data['goals']) == 3
    
    def test_load_plan(self, temp_store, sample_plan):
        """Test loading a plan."""
        temp_store.save(sample_plan)
        
        loaded_plan = temp_store.load("test-plan-123")
        
        assert loaded_plan is not None
        assert loaded_plan.id == sample_plan.id
        assert loaded_plan.root_goal_id == sample_plan.root_goal_id
        assert len(loaded_plan.goals) == 3
        
        # Verify goals are loaded correctly
        root_goal = loaded_plan.get_root_goal()
        assert root_goal is not None
        assert root_goal.description == "Build a web application"
        assert len(root_goal.child_ids) == 2
    
    def test_load_nonexistent_plan(self, temp_store):
        """Test loading a plan that doesn't exist."""
        result = temp_store.load("nonexistent-plan")
        assert result is None
    
    def test_save_updates_timestamp(self, temp_store, sample_plan):
        """Test that saving updates the plan's updated_at timestamp."""
        original_time = sample_plan.updated_at
        
        # Small delay to ensure timestamp changes
        import time
        time.sleep(0.01)
        
        temp_store.save(sample_plan)
        
        # Load and check timestamp changed
        loaded = temp_store.load(sample_plan.id)
        assert loaded.updated_at >= original_time


class TestPlanIndex:
    """Test plan indexing functionality."""
    
    def test_index_created_on_save(self, temp_store, sample_plan):
        """Test that saving a plan updates the index."""
        temp_store.save(sample_plan)
        
        index = temp_store._load_index()
        assert "test-plan-123" in index
        
        plan_meta = index["test-plan-123"]
        assert plan_meta['id'] == "test-plan-123"
        assert plan_meta['description'] == "Build a web application"
        assert plan_meta['status'] == "in_progress"
        assert plan_meta['goal_count'] == 3
        assert plan_meta['atomic_count'] == 1
    
    def test_list_plans(self, temp_store, sample_plan):
        """Test listing all plans."""
        temp_store.save(sample_plan)
        
        # Create another plan
        plan2 = Plan(id="test-plan-456", root_goal_id="goal-x")
        plan2.add_goal(Goal(id="goal-x", description="Another goal", depth=0))
        temp_store.save(plan2)
        
        plans = temp_store.list_plans()
        
        assert len(plans) == 2
        plan_ids = [p['id'] for p in plans]
        assert "test-plan-123" in plan_ids
        assert "test-plan-456" in plan_ids
    
    def test_list_plans_by_status(self, temp_store):
        """Test filtering plans by status."""
        # Create plans with different statuses
        plan1 = Plan(id="plan-1", root_goal_id="g1", status="in_progress")
        plan1.add_goal(Goal(id="g1", description="Goal 1", depth=0))
        
        plan2 = Plan(id="plan-2", root_goal_id="g2", status="complete")
        plan2.add_goal(Goal(id="g2", description="Goal 2", depth=0))
        
        plan3 = Plan(id="plan-3", root_goal_id="g3", status="in_progress")
        plan3.add_goal(Goal(id="g3", description="Goal 3", depth=0))
        
        temp_store.save(plan1)
        temp_store.save(plan2)
        temp_store.save(plan3)
        
        # Filter by in_progress
        in_progress = temp_store.list_plans(status="in_progress")
        assert len(in_progress) == 2
        
        # Filter by complete
        complete = temp_store.list_plans(status="complete")
        assert len(complete) == 1
        assert complete[0]['id'] == "plan-2"
    
    def test_plans_sorted_by_updated_at(self, temp_store):
        """Test that plans are sorted by updated_at descending."""
        import time
        
        plan1 = Plan(id="old-plan", root_goal_id="g1")
        plan1.add_goal(Goal(id="g1", description="Old", depth=0))
        temp_store.save(plan1)
        
        time.sleep(0.01)
        
        plan2 = Plan(id="new-plan", root_goal_id="g2")
        plan2.add_goal(Goal(id="g2", description="New", depth=0))
        temp_store.save(plan2)
        
        plans = temp_store.list_plans()
        assert plans[0]['id'] == "new-plan"  # Most recent first
        assert plans[1]['id'] == "old-plan"


class TestPlanExists:
    """Test plan existence checking."""
    
    def test_exists_returns_true_for_existing_plan(self, temp_store, sample_plan):
        """Test exists() returns True for saved plan."""
        temp_store.save(sample_plan)
        assert temp_store.exists("test-plan-123") is True
    
    def test_exists_returns_false_for_missing_plan(self, temp_store):
        """Test exists() returns False for missing plan."""
        assert temp_store.exists("nonexistent") is False


class TestPlanDeletion:
    """Test plan deletion and archiving."""
    
    def test_delete_plan_with_archive(self, temp_store, sample_plan):
        """Test deleting a plan (with archiving)."""
        temp_store.save(sample_plan)
        
        result = temp_store.delete("test-plan-123", archive=True)
        
        assert result is True
        assert not temp_store.exists("test-plan-123")
        
        # Check plan was archived
        archive_files = list(temp_store.archive_dir.glob("test-plan-123_*.json"))
        assert len(archive_files) == 1
        
        # Check removed from index
        index = temp_store._load_index()
        assert "test-plan-123" not in index
    
    def test_delete_plan_without_archive(self, temp_store, sample_plan):
        """Test deleting a plan without archiving."""
        temp_store.save(sample_plan)
        
        result = temp_store.delete("test-plan-123", archive=False)
        
        assert result is True
        assert not temp_store.exists("test-plan-123")
        
        # Check plan was NOT archived
        archive_files = list(temp_store.archive_dir.glob("test-plan-123_*.json"))
        assert len(archive_files) == 0
    
    def test_delete_nonexistent_plan(self, temp_store):
        """Test deleting a plan that doesn't exist."""
        result = temp_store.delete("nonexistent")
        assert result is False


class TestPlanArchiving:
    """Test plan archiving."""
    
    def test_archive_plan(self, temp_store, sample_plan):
        """Test archiving a plan."""
        temp_store.save(sample_plan)
        
        archive_path = temp_store.archive("test-plan-123")
        
        assert archive_path is not None
        assert archive_path.exists()
        assert archive_path.parent == temp_store.archive_dir
        assert "test-plan-123_" in archive_path.name
        
        # Original should be moved
        assert not temp_store.exists("test-plan-123")
    
    def test_archive_nonexistent_plan(self, temp_store):
        """Test archiving a plan that doesn't exist."""
        result = temp_store.archive("nonexistent")
        assert result is None


class TestPlanExport:
    """Test plan export functionality."""
    
    def test_export_to_json(self, temp_store, sample_plan, tmp_path):
        """Test exporting a plan to JSON."""
        temp_store.save(sample_plan)
        
        output_path = tmp_path / "export" / "plan.json"
        result = temp_store.export("test-plan-123", output_path, format="json")
        
        assert result is True
        assert output_path.exists()
        
        # Verify exported content
        with open(output_path) as f:
            data = json.load(f)
        
        assert data['id'] == "test-plan-123"
        assert len(data['goals']) == 3
    
    def test_export_creates_parent_dirs(self, temp_store, sample_plan, tmp_path):
        """Test that export creates parent directories."""
        temp_store.save(sample_plan)
        
        output_path = tmp_path / "deep" / "nested" / "path" / "plan.json"
        result = temp_store.export("test-plan-123", output_path)
        
        assert result is True
        assert output_path.exists()
    
    def test_export_nonexistent_plan(self, temp_store, tmp_path):
        """Test exporting a plan that doesn't exist."""
        output_path = tmp_path / "plan.json"
        result = temp_store.export("nonexistent", output_path)
        assert result is False


class TestPlanBackup:
    """Test plan backup functionality."""
    
    def test_save_creates_backup_of_existing_plan(self, temp_store, sample_plan):
        """Test that saving an existing plan creates a backup."""
        # Save initial version
        temp_store.save(sample_plan, create_backup=False)
        
        # Modify and save again
        sample_plan.status = "complete"
        temp_store.save(sample_plan, create_backup=True)
        
        # Check backup was created
        backup_files = list(temp_store.plans_dir.glob(".test-plan-123.backup_*.json"))
        assert len(backup_files) == 1
        
        # Verify backup content
        with open(backup_files[0]) as f:
            backup_data = json.load(f)
        
        # Backup should have original status
        assert backup_data['status'] == "in_progress"
    
    def test_save_without_backup(self, temp_store, sample_plan):
        """Test saving without creating backup."""
        temp_store.save(sample_plan, create_backup=False)
        
        sample_plan.status = "complete"
        temp_store.save(sample_plan, create_backup=False)
        
        # Check no backup was created
        backup_files = list(temp_store.plans_dir.glob(".test-plan-123.backup_*.json"))
        assert len(backup_files) == 0


class TestRoundtripSerialization:
    """Test that plans survive save/load cycles."""
    
    def test_complex_plan_roundtrip(self, temp_store):
        """Test saving and loading a complex plan."""
        # Create a complex plan
        plan = Plan(id="complex-plan", root_goal_id="root")
        
        # Root goal
        root = Goal(
            id="root",
            description="Complex project",
            status=GoalStatus.COMPLETE,
            depth=0,
            reasoning="This is a complex reasoning",
            tokens_used=1234,
        )
        
        # Add children with dependencies
        child1 = Goal(
            id="child1",
            description="Step 1",
            status=GoalStatus.ATOMIC,
            parent_id="root",
            depth=1,
            graph_node_id="node-123",
        )
        
        child2 = Goal(
            id="child2",
            description="Step 2",
            status=GoalStatus.PENDING,
            parent_id="root",
            depth=1,
        )
        child2.add_dependency("child1")
        
        root.add_child("child1")
        root.add_child("child2")
        
        plan.add_goal(root)
        plan.add_goal(child1)
        plan.add_goal(child2)
        
        # Save and load
        temp_store.save(plan)
        loaded = temp_store.load("complex-plan")
        
        # Verify all fields preserved
        assert loaded.id == plan.id
        assert loaded.root_goal_id == plan.root_goal_id
        assert len(loaded.goals) == 3
        
        loaded_root = loaded.get_goal("root")
        assert loaded_root.reasoning == "This is a complex reasoning"
        assert loaded_root.tokens_used == 1234
        assert len(loaded_root.child_ids) == 2
        
        loaded_child1 = loaded.get_goal("child1")
        assert loaded_child1.graph_node_id == "node-123"
        assert loaded_child1.status == GoalStatus.ATOMIC
        
        loaded_child2 = loaded.get_goal("child2")
        assert "child1" in loaded_child2.dependencies
