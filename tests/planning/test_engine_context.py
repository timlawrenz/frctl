"""Integration tests for Planning Engine with Context Tree."""

import pytest
from unittest.mock import Mock, MagicMock
from frctl.planning.engine import PlanningEngine
from frctl.planning.goal import GoalStatus
from frctl.llm.provider import LLMProvider


class TestPlanningEngineContextIntegration:
    """Test that Planning Engine properly integrates with Context Tree."""
    
    def test_create_plan_creates_root_context(self):
        """Test that creating a plan also creates root context."""
        engine = PlanningEngine()
        
        plan = engine.create_plan("Build a feature")
        
        # Verify context was created
        root_context = engine.context_tree.get_context(plan.root_goal_id)
        assert root_context is not None
        assert root_context.goal_id == plan.root_goal_id
        assert root_context.parent_goal_id is None
    
    def test_decompose_creates_child_contexts(self):
        """Test that decomposing creates isolated child contexts."""
        # Mock LLM to return deterministic decomposition
        mock_llm = Mock(spec=LLMProvider)
        mock_llm.generate.return_value = {
            "content": '{"sub_goals": [{"description": "Task A"}, {"description": "Task B"}], "reasoning": "Split into A and B"}',
            "usage": {"total_tokens": 100}
        }
        
        engine = PlanningEngine(llm_provider=mock_llm)
        plan = engine.create_plan("Parent goal")
        root_goal = plan.get_goal(plan.root_goal_id)
        
        # Decompose
        children = engine.decompose_goal(root_goal)
        
        # Verify child contexts were created
        assert len(children) == 2
        
        for child in children:
            child_context = engine.context_tree.get_context(child.id)
            assert child_context is not None
            assert child_context.parent_goal_id == root_goal.id
            assert child_context.parent_intent in ["Task A", "Task B"]
    
    def test_token_tracking_across_contexts(self):
        """Test that token usage is tracked in context tree."""
        # Mock LLM
        mock_llm = Mock(spec=LLMProvider)
        mock_llm.generate.return_value = {
            "content": '{"is_atomic": true, "reasoning": "Simple task"}',
            "usage": {"total_tokens": 50}
        }
        
        engine = PlanningEngine(llm_provider=mock_llm)
        plan = engine.create_plan("Test goal")
        root_goal = plan.get_goal(plan.root_goal_id)
        
        # Assess atomicity (uses tokens)
        engine.assess_atomicity(root_goal)
        
        # Verify tokens tracked in both goal and context
        assert root_goal.tokens_used == 50
        
        root_context = engine.context_tree.get_context(root_goal.id)
        assert root_context.tokens_used == 50
        
        # Total should match
        assert engine.context_tree.get_total_tokens() == 50
    
    def test_context_isolation_between_siblings(self):
        """Test that sibling contexts are isolated."""
        # Mock LLM to return decomposition
        mock_llm = Mock(spec=LLMProvider)
        mock_llm.generate.return_value = {
            "content": '{"sub_goals": [{"description": "Feature A"}, {"description": "Feature B"}], "reasoning": "Split"}',
            "usage": {"total_tokens": 100}
        }
        
        engine = PlanningEngine(llm_provider=mock_llm)
        plan = engine.create_plan("Parent")
        root_goal = plan.get_goal(plan.root_goal_id)
        
        # Decompose
        children = engine.decompose_goal(root_goal)
        
        # Set local context for each child
        engine.context_tree.set_local_context(children[0].id, "approach", "method1")
        engine.context_tree.set_local_context(children[1].id, "approach", "method2")
        
        # Hydrate contexts
        ctx1 = engine.context_tree.hydrate_context(children[0].id)
        ctx2 = engine.context_tree.hydrate_context(children[1].id)
        
        # Siblings should not see each other's local context
        assert ctx1["local"]["approach"] == "method1"
        assert ctx2["local"]["approach"] == "method2"
        
        # But both should have different parent intents
        assert ctx1["parent_intent"] == "Feature A"
        assert ctx2["parent_intent"] == "Feature B"
    
    def test_global_context_propagates(self):
        """Test that global context propagates to all nodes."""
        mock_llm = Mock(spec=LLMProvider)
        mock_llm.generate.return_value = {
            "content": '{"sub_goals": [{"description": "Child"}], "reasoning": "Split"}',
            "usage": {"total_tokens": 50}
        }
        
        engine = PlanningEngine(
            llm_provider=mock_llm,
            global_context={"project": "frctl", "version": "0.1"}
        )
        
        plan = engine.create_plan("Root")
        root_goal = plan.get_goal(plan.root_goal_id)
        
        # Decompose to create child
        children = engine.decompose_goal(root_goal)
        
        # Set additional global context
        engine.context_tree.set_global_context("constraint", "Python 3.11+")
        
        # Both root and child should see global context
        root_ctx = engine.context_tree.get_context(plan.root_goal_id)
        child_ctx = engine.context_tree.get_context(children[0].id)
        
        assert root_ctx.global_context["project"] == "frctl"
        assert root_ctx.global_context["constraint"] == "Python 3.11+"
        assert child_ctx.global_context["project"] == "frctl"
        assert child_ctx.global_context["constraint"] == "Python 3.11+"
    
    def test_context_tree_stats_in_plan_summary(self):
        """Test that context tree stats are included in plan summary."""
        mock_llm = Mock(spec=LLMProvider)
        
        # First call: is_atomic = false (decompose)
        # Second call: decomposition
        # Third/Fourth calls: is_atomic = true for children
        mock_llm.generate.side_effect = [
            {"content": '{"is_atomic": false, "reasoning": "Needs breakdown"}', "usage": {"total_tokens": 50}},
            {"content": '{"sub_goals": [{"description": "A"}, {"description": "B"}], "reasoning": "Split"}', "usage": {"total_tokens": 100}},
            {"content": '{"is_atomic": true, "reasoning": "Simple"}', "usage": {"total_tokens": 30}},
            {"content": '{"is_atomic": true, "reasoning": "Simple"}', "usage": {"total_tokens": 30}},
        ]
        
        engine = PlanningEngine(llm_provider=mock_llm)
        plan = engine.run("Build feature")
        
        # Verify context tree stats
        stats = engine.context_tree.get_tree_stats()
        
        assert stats["total_nodes"] == 3  # root + 2 children
        assert stats["total_tokens"] == 210  # 50 + 100 + 30 + 30
        assert stats["avg_tokens_per_node"] == pytest.approx(70, rel=0.1)
