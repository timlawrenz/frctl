"""Unit tests for atomicity detection."""

import pytest
from frctl.planning.goal import Goal, Plan
from frctl.planning.engine import PlanningEngine
from tests.llm.test_mock_provider import MockLLMProvider


class TestAtomicityDetection:
    """Tests for LLM-based atomicity detection."""
    
    def test_detect_atomic_goal(self):
        """Test detecting an atomic goal."""
        # Mock LLM says it's atomic
        provider = MockLLMProvider(responses=[
            '{"is_atomic": true, "reasoning": "This is a simple, single-step task"}'
        ])
        
        engine = PlanningEngine(llm_provider=provider)
        plan = engine.create_plan("Write a unit test")
        goal = plan.get_goal(plan.root_goal_id)
        
        # Assess atomicity
        is_atomic = engine.assess_atomicity(goal)
        
        assert is_atomic is True
        assert provider.call_count == 1
        # Check that goal description is in one of the messages
        messages_text = str(provider.last_messages)
        assert "Write a unit test" in messages_text
    
    def test_detect_composite_goal(self):
        """Test detecting a composite goal that needs decomposition."""
        # Mock LLM says it's not atomic
        provider = MockLLMProvider(responses=[
            '{"is_atomic": false, "reasoning": "This requires multiple steps: design, implement, test"}'
        ])
        
        engine = PlanningEngine(llm_provider=provider)
        plan = engine.create_plan("Build a web application")
        goal = plan.get_goal(plan.root_goal_id)
        
        # Assess atomicity
        is_atomic = engine.assess_atomicity(goal)
        
        assert is_atomic is False
        assert provider.call_count == 1
        messages_text = str(provider.last_messages)
        assert "Build a web application" in messages_text
    
    def test_atomicity_updates_goal_status(self):
        """Test that atomicity detection returns correct result."""
        # Atomic goal
        provider = MockLLMProvider(responses=[
            '{"is_atomic": true, "reasoning": "Simple task"}'
        ])
        
        engine = PlanningEngine(llm_provider=provider)
        plan = engine.create_plan("Run tests")
        goal = plan.get_goal(plan.root_goal_id)
        
        # Assess atomicity
        is_atomic = engine.assess_atomicity(goal)
        
        # Should return True
        assert is_atomic is True
        # Reasoning should be stored
        assert hasattr(goal, 'reasoning')
        assert "Simple task" in goal.reasoning
    
    def test_atomicity_tracks_tokens(self):
        """Test that atomicity detection tracks token usage."""
        provider = MockLLMProvider(responses=[
            '{"is_atomic": true, "reasoning": "Simple task"}'
        ])
        
        engine = PlanningEngine(llm_provider=provider)
        plan = engine.create_plan("Write documentation")
        goal = plan.get_goal(plan.root_goal_id)
        
        # Initially no tokens used
        assert goal.tokens_used == 0
        
        # Assess atomicity
        engine.assess_atomicity(goal)
        
        # Should have tracked tokens
        assert goal.tokens_used > 0
    
class TestAtomicityEdgeCases:
    """Edge case tests for atomicity detection."""
    
    def test_very_long_goal_description(self):
        """Test atomicity with very long description."""
        long_description = "Do something " * 1000
        
        provider = MockLLMProvider(responses=[
            '{"is_atomic": false, "reasoning": "Complex task"}'
        ])
        
        engine = PlanningEngine(llm_provider=provider)
        plan = engine.create_plan(long_description)
        goal = plan.get_goal(plan.root_goal_id)
        
        # Should handle long descriptions
        is_atomic = engine.assess_atomicity(goal)
        assert isinstance(is_atomic, bool)
        
        # Prompt should include description (truncated if needed)
        assert provider.call_count == 1
    
    def test_atomicity_unicode_description(self):
        """Test atomicity with unicode characters."""
        provider = MockLLMProvider(responses=[
            '{"is_atomic": true, "reasoning": "Simple task"}'
        ])
        
        engine = PlanningEngine(llm_provider=provider)
        plan = engine.create_plan("创建测试 🎯")
        goal = plan.get_goal(plan.root_goal_id)
        
        # Should handle unicode
        is_atomic = engine.assess_atomicity(goal)
        assert isinstance(is_atomic, bool)
        messages_text = str(provider.last_messages)
        assert "创建测试" in messages_text or "🎯" in messages_text
