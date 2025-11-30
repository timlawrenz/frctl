#!/usr/bin/env python3
"""Test script to validate ReCAP engine with Gemini API.

This script tests the planning engine with a simple goal using Gemini.
It demonstrates:
1. LLM provider initialization
2. Goal decomposition with JSON parsing
3. Recursive planning

Usage:
    export GEMINI_API_KEY=your_key
    python test_gemini_planning.py
"""

import os
import sys
from pathlib import Path

# Add frctl to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from frctl.planning.engine import PlanningEngine
from frctl.llm.provider import LLMProvider


def test_simple_planning():
    """Test planning with a simple goal."""
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export GEMINI_API_KEY=your_key_here")
        sys.exit(1)
    
    print("=" * 70)
    print("Testing ReCAP Planning Engine with Gemini")
    print("=" * 70)
    
    # Initialize LLM provider with Gemini
    print("\n📡 Initializing Gemini LLM provider...")
    print(f"   Model: gemini-2.5-flash")
    
    llm = LLMProvider(
        model="gemini-2.5-flash",  # Gemini 2.5 Flash (latest available)
        temperature=0.7,
        max_tokens=1000,
        verbose=False,
    )
    
    # Create planning engine
    print("🧠 Creating planning engine...")
    engine = PlanningEngine(
        llm_provider=llm,
        max_depth=3,  # Limit depth for testing
        max_children=5,
    )
    
    # Test goal
    goal = "Create a simple todo list web application"
    
    print(f"\n🎯 Planning Goal:")
    print(f"   '{goal}'")
    print(f"\n{'=' * 70}")
    
    try:
        # Run planning
        print("\n🚀 Starting recursive planning...\n")
        plan = engine.run(goal)
        
        # Show results
        print(f"\n{'=' * 70}")
        print("📊 Planning Results")
        print("=" * 70)
        
        stats = plan.get_statistics()
        print(f"\n✅ Planning Complete!")
        print(f"   Total Goals:   {stats['total_goals']}")
        print(f"   Atomic Goals:  {stats['atomic_goals']}")
        print(f"   Max Depth:     {stats['max_depth']}")
        print(f"   Total Tokens:  {stats['total_tokens']}")
        print(f"   Status:        {stats['status']}")
        
        # Show atomic goals (ready for implementation)
        atomic_goals = plan.get_atomic_goals()
        if atomic_goals:
            print(f"\n📝 Atomic Goals (ready for implementation):")
            for i, goal in enumerate(atomic_goals, 1):
                print(f"   {i}. {goal.description}")
        
        # Show LLM statistics
        llm_stats = llm.get_statistics()
        print(f"\n💰 Gemini Usage:")
        print(f"   API Calls:     {llm_stats['call_count']}")
        print(f"   Total Tokens:  {llm_stats['total_tokens']}")
        print(f"   Avg Tokens:    {llm_stats['avg_tokens']}")
        print(f"   Total Cost:    ${llm_stats['total_cost']}")
        
        # Show goal tree
        print(f"\n🌳 Goal Tree:")
        print_goal_tree(plan, plan.root_goal_id, indent=0)
        
        print(f"\n{'=' * 70}")
        print("✅ Test Successful! JSON parsing is working correctly.")
        print("=" * 70)
        
        return plan
        
    except Exception as e:
        print(f"\n❌ Error during planning: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def print_goal_tree(plan, goal_id, indent=0):
    """Print goal tree recursively."""
    goal = plan.get_goal(goal_id)
    if not goal:
        return
    
    prefix = "  " * indent
    status_emoji = {
        "pending": "⏳",
        "decomposing": "🔄",
        "atomic": "✓",
        "complete": "✅",
        "failed": "❌",
    }.get(goal.status.value, "?")
    
    # Truncate long descriptions
    desc = goal.description if len(goal.description) <= 60 else goal.description[:57] + "..."
    
    print(f"{prefix}{status_emoji} [{goal.status.value:12}] {desc}")
    
    # Show reasoning if available (first line only)
    if goal.reasoning and indent < 2:  # Only show for top levels
        reasoning_lines = goal.reasoning.split('\n')
        first_line = reasoning_lines[0][:70] if reasoning_lines else ""
        if first_line:
            print(f"{prefix}   💭 {first_line}...")
    
    # Recursively print children
    for child_id in goal.child_ids:
        print_goal_tree(plan, child_id, indent + 1)


if __name__ == "__main__":
    test_simple_planning()
