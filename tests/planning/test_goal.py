"""Unit tests for Goal and Plan classes."""

import pytest
from datetime import datetime

from frctl.planning.goal import Goal, GoalStatus, Plan


class TestGoal:
    """Test Goal class."""
    
    def test_create_goal(self):
        """Test creating a goal."""
        goal = Goal(
            id="test-1",
            description="Build a feature",
            depth=0
        )
        
        assert goal.id == "test-1"
        assert goal.description == "Build a feature"
        assert goal.status == GoalStatus.PENDING
        assert goal.depth == 0
        assert goal.parent_id is None
        assert goal.child_ids == []
    
    def test_is_atomic(self):
        """Test atomic goal detection."""
        goal = Goal(id="test-1", description="Test", depth=0)
        
        # Pending with no children - not atomic
        assert not goal.is_atomic()
        
        # Mark as atomic
        goal.mark_atomic()
        assert goal.is_atomic()
        assert goal.status == GoalStatus.ATOMIC
    
    def test_is_composite(self):
        """Test composite goal detection."""
        goal = Goal(id="test-1", description="Test", depth=0)
        
        # No children - not composite
        assert not goal.is_composite()
        
        # Add children
        goal.add_child("test-1-1")
        goal.add_child("test-1-2")
        assert goal.is_composite()
        assert len(goal.child_ids) == 2
    
    def test_add_dependency(self):
        """Test adding dependencies."""
        goal = Goal(id="test-1", description="Test", depth=0)
        
        goal.add_dependency("dep-1")
        goal.add_dependency("dep-2")
        
        assert goal.dependencies == ["dep-1", "dep-2"]
        
        # Don't add duplicates
        goal.add_dependency("dep-1")
        assert goal.dependencies == ["dep-1", "dep-2"]


class TestPlan:
    """Test Plan class."""
    
    def test_create_plan(self):
        """Test creating a plan."""
        root = Goal(id="root", description="Root goal", depth=0)
        plan = Plan(id="plan-1", root_goal_id="root")
        plan.add_goal(root)
        
        assert plan.id == "plan-1"
        assert plan.root_goal_id == "root"
        assert plan.get_root_goal() == root
        assert plan.status == "in_progress"
    
    def test_add_goals(self):
        """Test adding goals to plan."""
        plan = Plan(id="plan-1", root_goal_id="root")
        
        root = Goal(id="root", description="Root", depth=0)
        child1 = Goal(id="child-1", description="Child 1", depth=1, parent_id="root")
        child2 = Goal(id="child-2", description="Child 2", depth=1, parent_id="root")
        
        plan.add_goal(root)
        plan.add_goal(child1)
        plan.add_goal(child2)
        
        assert len(plan.goals) == 3
        assert plan.max_depth == 1
    
    def test_get_children(self):
        """Test getting children of a goal."""
        plan = Plan(id="plan-1", root_goal_id="root")
        
        root = Goal(id="root", description="Root", depth=0)
        child1 = Goal(id="child-1", description="Child 1", depth=1, parent_id="root")
        child2 = Goal(id="child-2", description="Child 2", depth=1, parent_id="root")
        
        root.add_child("child-1")
        root.add_child("child-2")
        
        plan.add_goal(root)
        plan.add_goal(child1)
        plan.add_goal(child2)
        
        children = plan.get_children("root")
        assert len(children) == 2
        assert child1 in children
        assert child2 in children
    
    def test_get_atomic_goals(self):
        """Test getting atomic goals."""
        plan = Plan(id="plan-1", root_goal_id="root")
        
        root = Goal(id="root", description="Root", depth=0)
        atomic1 = Goal(id="atomic-1", description="Atomic 1", depth=1, status=GoalStatus.ATOMIC)
        atomic2 = Goal(id="atomic-2", description="Atomic 2", depth=1, status=GoalStatus.ATOMIC)
        pending = Goal(id="pending", description="Pending", depth=1)
        
        plan.add_goal(root)
        plan.add_goal(atomic1)
        plan.add_goal(atomic2)
        plan.add_goal(pending)
        
        atomic_goals = plan.get_atomic_goals()
        assert len(atomic_goals) == 2
        assert atomic1 in atomic_goals
        assert atomic2 in atomic_goals
    
    def test_is_complete(self):
        """Test plan completion detection."""
        plan = Plan(id="plan-1", root_goal_id="root")
        
        root = Goal(id="root", description="Root", depth=0, status=GoalStatus.COMPLETE)
        atomic1 = Goal(id="atomic-1", description="Atomic 1", depth=1, status=GoalStatus.ATOMIC)
        
        plan.add_goal(root)
        plan.add_goal(atomic1)
        
        # All goals are atomic or complete
        assert plan.is_complete()
        
        # Add pending goal
        pending = Goal(id="pending", description="Pending", depth=1)
        plan.add_goal(pending)
        
        # No longer complete
        assert not plan.is_complete()
    
    def test_statistics(self):
        """Test plan statistics."""
        plan = Plan(id="plan-1", root_goal_id="root")
        
        root = Goal(id="root", description="Root", depth=0, status=GoalStatus.COMPLETE, tokens_used=100)
        root.add_child("atomic-1")
        root.add_child("atomic-2")
        
        atomic1 = Goal(id="atomic-1", description="Atomic 1", depth=1, status=GoalStatus.ATOMIC, tokens_used=50)
        atomic2 = Goal(id="atomic-2", description="Atomic 2", depth=2, status=GoalStatus.ATOMIC, tokens_used=75)
        
        plan.add_goal(root)
        plan.add_goal(atomic1)
        plan.add_goal(atomic2)
        
        stats = plan.get_statistics()
        
        assert stats["total_goals"] == 3
        assert stats["atomic_goals"] == 2
        assert stats["max_depth"] == 2
        assert stats["total_tokens"] == 225
        assert stats["is_complete"] == True
