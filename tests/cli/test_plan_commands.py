"""Tests for CLI planning commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path
import json

from frctl.__main__ import cli
from frctl.planning import Plan, Goal, GoalStatus
from frctl.planning.persistence import PlanStore


@pytest.fixture
def runner():
    """Create Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_frctl_dir(tmp_path):
    """Create temporary .frctl directory."""
    frctl_dir = tmp_path / ".frctl"
    frctl_dir.mkdir()
    (frctl_dir / "plans").mkdir()
    return frctl_dir


@pytest.fixture
def sample_plan(temp_frctl_dir):
    """Create a sample plan for testing."""
    store = PlanStore(base_path=temp_frctl_dir / "plans")
    
    # Create a simple plan
    plan = Plan(id="test-plan", root_goal_id="test-root")
    root = Goal(
        id="test-root",
        description="Test goal",
        status=GoalStatus.COMPLETE,
        depth=0,
    )
    child1 = Goal(
        id="test-child-1",
        description="Child goal 1",
        status=GoalStatus.ATOMIC,
        depth=1,
        parent_id="test-root",
    )
    child2 = Goal(
        id="test-child-2",
        description="Child goal 2",
        status=GoalStatus.ATOMIC,
        depth=1,
        parent_id="test-root",
    )
    
    root.child_ids = ["test-child-1", "test-child-2"]
    
    plan.add_goal(root)
    plan.add_goal(child1)
    plan.add_goal(child2)
    plan.mark_complete()
    
    store.save(plan)
    return plan, store


class TestPlanList:
    """Tests for 'frctl plan list' command."""
    
    def test_list_no_plans(self, runner, tmp_path, monkeypatch):
        """Test listing when no plans exist."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".frctl" / "plans").mkdir(parents=True)
        
        result = runner.invoke(cli, ["plan", "list"])
        assert result.exit_code == 0
        assert "No plans found" in result.output
    
    def test_list_with_plans(self, runner, tmp_path, monkeypatch, sample_plan):
        """Test listing plans."""
        plan, store = sample_plan
        monkeypatch.chdir(tmp_path)
        
        result = runner.invoke(cli, ["plan", "list"])
        assert result.exit_code == 0
        assert "test-plan" in result.output
        assert "Test goal" in result.output


class TestPlanStatus:
    """Tests for 'frctl plan status' command."""
    
    def test_status_with_plan_id(self, runner, tmp_path, monkeypatch, sample_plan):
        """Test viewing plan status."""
        plan, store = sample_plan
        monkeypatch.chdir(tmp_path)
        
        result = runner.invoke(cli, ["plan", "status", "test-plan"])
        assert result.exit_code == 0
        assert "test-plan" in result.output
        assert "Test goal" in result.output
        assert "Statistics" in result.output
        assert "Total goals: 3" in result.output
    
    def test_status_shows_goal_tree(self, runner, tmp_path, monkeypatch, sample_plan):
        """Test that status shows the goal tree."""
        plan, store = sample_plan
        monkeypatch.chdir(tmp_path)
        
        result = runner.invoke(cli, ["plan", "status", "test-plan"])
        assert result.exit_code == 0
        assert "Goal Tree:" in result.output
        assert "test-root" in result.output


class TestPlanReview:
    """Tests for 'frctl plan review' command."""
    
    def test_review_goal(self, runner, tmp_path, monkeypatch, sample_plan):
        """Test reviewing a specific goal."""
        plan, store = sample_plan
        monkeypatch.chdir(tmp_path)
        
        result = runner.invoke(cli, ["plan", "review", "test-root", "--plan-id", "test-plan"])
        assert result.exit_code == 0
        assert "test-root" in result.output
        assert "Test goal" in result.output


class TestPlanExport:
    """Tests for 'frctl plan export' command."""
    
    def test_export_to_stdout(self, runner, tmp_path, monkeypatch, sample_plan):
        """Test exporting plan to stdout."""
        plan, store = sample_plan
        monkeypatch.chdir(tmp_path)
        
        result = runner.invoke(cli, ["plan", "export", "test-plan"])
        assert result.exit_code == 0
        
        # Parse JSON output
        plan_data = json.loads(result.output)
        assert plan_data["id"] == "test-plan"
        assert "test-root" in plan_data["goals"]


class TestPlanVisualize:
    """Tests for 'frctl plan visualize' command."""
    
    def test_visualize_ascii(self, runner, tmp_path, monkeypatch, sample_plan):
        """Test ASCII visualization."""
        plan, store = sample_plan
        monkeypatch.chdir(tmp_path)
        
        result = runner.invoke(cli, ["plan", "visualize", "test-plan", "--format", "ascii"])
        assert result.exit_code == 0
        assert "test-plan" in result.output
        assert "Test goal" in result.output
    
    def test_visualize_mermaid(self, runner, tmp_path, monkeypatch, sample_plan):
        """Test Mermaid visualization."""
        plan, store = sample_plan
        monkeypatch.chdir(tmp_path)
        
        result = runner.invoke(cli, ["plan", "visualize", "test-plan", "--format", "mermaid"])
        assert result.exit_code == 0
        assert "```mermaid" in result.output
        assert "graph TD" in result.output
        assert "test-root" in result.output


class TestPlanDelete:
    """Tests for 'frctl plan delete' command."""
    
    def test_delete_with_force(self, runner, tmp_path, monkeypatch, sample_plan):
        """Test deleting plan with force flag."""
        plan, store = sample_plan
        monkeypatch.chdir(tmp_path)
        
        result = runner.invoke(cli, ["plan", "delete", "test-plan", "--force"])
        assert result.exit_code == 0
        assert "deleted" in result.output
        
        # Verify plan is deleted
        assert not store.exists("test-plan")
