"""Tests for advanced planning engine features."""

import pytest
from unittest.mock import Mock

from frctl.planning import PlanningEngine, Goal, GoalStatus, Plan
from frctl.llm.provider import LLMProvider


@pytest.fixture
def mock_llm():
    """Create a mock LLM provider."""
    llm = Mock(spec=LLMProvider)
    llm.count_tokens = Mock(side_effect=lambda text: len(text.split()) * 1.3)
    return llm


@pytest.fixture
def engine(mock_llm):
    """Create planning engine with mock LLM."""
    return PlanningEngine(llm_provider=mock_llm, auto_save=False)


class TestDependencyInference:
    """Tests for dependency inference between sibling goals."""
    
    def test_infer_dependencies(self, engine, mock_llm):
        """Test inferring dependencies between children."""
        mock_llm.generate.return_value = {
            "content": '''```json
{
    "dependencies": [
        {
            "goal_id": "parent-2",
            "depends_on": ["parent-1"],
            "reasoning": "Second depends on first"
        }
    ]
}
```''',
            "usage": {"total_tokens": 100},
        }
        
        plan = Plan(id="test", root_goal_id="parent")
        parent = Goal(id="parent", description="Parent", depth=0)
        plan.add_goal(parent)
        
        # Create children
        children = [
            Goal(id="parent-1", description="First task", parent_id="parent", depth=1),
            Goal(id="parent-2", description="Second task", parent_id="parent", depth=1),
        ]
        
        # Infer dependencies
        engine._infer_dependencies(children, parent, plan)
        
        # Check dependencies were set
        assert children[1].dependencies == ["parent-1"]
    
    def test_no_dependencies_single_child(self, engine):
        """Test no dependency inference for single child."""
        plan = Plan(id="test", root_goal_id="parent")
        parent = Goal(id="parent", description="Parent", depth=0)
        
        children = [
            Goal(id="parent-1", description="Only child", parent_id="parent", depth=1)
        ]
        
        # Should not make LLM call
        engine._infer_dependencies(children, parent, plan)
        # No assertion needed - just verify it doesn't crash


class TestDepthFirstTraversal:
    """Tests for depth-first planning traversal."""
    
    def test_depth_first_planning(self, engine, mock_llm):
        """Test depth-first traversal of planning tree."""
        # Setup mock responses
        mock_llm.generate.side_effect = [
            # First: not atomic, decompose
            {
                "content": '''{"is_atomic": false, "reasoning": "Can decompose"}''',
                "usage": {"total_tokens": 50},
            },
            # Second: decomposition
            {
                "content": '''{"sub_goals": [
                    {"description": "Subtask 1"},
                    {"description": "Subtask 2"}
                ], "reasoning": "Split into 2"}''',
                "usage": {"total_tokens": 100},
            },
            # Third: dependency inference (empty)
            {
                "content": '''{"dependencies": []}''',
                "usage": {"total_tokens": 30},
            },
            # Fourth: subtask 1 is atomic
            {
                "content": '''{"is_atomic": true, "reasoning": "Leaf"}''',
                "usage": {"total_tokens": 40},
            },
            # Fifth: subtask 2 is atomic
            {
                "content": '''{"is_atomic": true, "reasoning": "Leaf"}''',
                "usage": {"total_tokens": 40},
            },
        ]
        
        plan = engine.create_plan("Test goal")
        engine.plan_depth_first(plan)
        
        # Should have created root + 2 children
        assert len(plan.goals) == 3
        
        # Root should be complete (decomposed)
        root = plan.get_goal(plan.root_goal_id)
        assert root.status == GoalStatus.COMPLETE
        assert len(root.child_ids) == 2
        
        # Children should be atomic
        for child_id in root.child_ids:
            child = plan.get_goal(child_id)
            assert child.status == GoalStatus.ATOMIC


class TestPauseResume:
    """Tests for pause/resume functionality."""
    
    def test_pause_planning(self, engine):
        """Test pausing a planning session."""
        plan = engine.create_plan("Test")
        
        path = engine.pause_planning(plan)
        
        assert plan.status == "paused"
        assert path.exists()
    
    def test_resume_planning(self, engine, mock_llm):
        """Test resuming a paused session."""
        # Create and pause a plan
        plan = engine.create_plan("Test")
        plan.status = "paused"
        engine.plan_store.save(plan)
        
        # Mock LLM for resume
        mock_llm.generate.return_value = {
            "content": '''{"is_atomic": true, "reasoning": "Atomic"}''',
            "usage": {"total_tokens": 50},
        }
        
        # Resume
        resumed = engine.resume_planning(plan.id)
        
        assert resumed is not None
        assert resumed.status == "complete"  # Should complete the single goal


class TestRollback:
    """Tests for goal rollback functionality."""
    
    def test_rollback_goal_decomposition(self, engine):
        """Test rolling back a goal's decomposition."""
        plan = engine.create_plan("Test")
        root = plan.get_goal(plan.root_goal_id)
        
        # Add children
        child1 = Goal(id="child-1", description="C1", parent_id=root.id, depth=1)
        child2 = Goal(id="child-2", description="C2", parent_id=root.id, depth=1)
        
        plan.add_goal(child1)
        plan.add_goal(child2)
        root.child_ids = ["child-1", "child-2"]
        root.status = GoalStatus.COMPLETE
        
        # Rollback
        success = engine.rollback_goal(plan, root.id)
        
        assert success
        assert len(root.child_ids) == 0
        assert root.status == GoalStatus.PENDING
        assert "child-1" not in plan.goals
        assert "child-2" not in plan.goals
    
    def test_rollback_no_children(self, engine):
        """Test rollback on goal without children."""
        plan = engine.create_plan("Test")
        root = plan.get_goal(plan.root_goal_id)
        
        success = engine.rollback_goal(plan, root.id)
        
        assert not success  # Can't rollback without children


class TestPlanningStatus:
    """Tests for planning status reporting."""
    
    def test_get_planning_status(self, engine):
        """Test getting detailed planning status."""
        plan = engine.create_plan("Test")
        root = plan.get_goal(plan.root_goal_id)
        
        # Add some goals
        pending = Goal(id="pending", description="P", status=GoalStatus.PENDING, depth=1)
        atomic = Goal(id="atomic", description="A", status=GoalStatus.ATOMIC, depth=1)
        
        plan.add_goal(pending)
        plan.add_goal(atomic)
        
        status = engine.get_planning_status(plan)
        
        assert status["total_goals"] == 3
        assert status["pending_count"] >= 1
        assert "next_goal" in status
        assert "can_continue" in status
    
    def test_planning_status_complete(self, engine):
        """Test status when planning is complete."""
        plan = engine.create_plan("Test")
        root = plan.get_goal(plan.root_goal_id)
        root.status = GoalStatus.ATOMIC
        plan.mark_complete()
        
        status = engine.get_planning_status(plan)
        
        assert status["is_complete"]
        assert not status["can_continue"]
        assert status["next_goal"] is None
