#!/usr/bin/env python3
"""Test ReCAP planning engine directly with Gemini SDK (bypassing LiteLLM)."""

import os
import sys
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from frctl.planning.goal import Goal, GoalStatus, Plan
import google.generativeai as genai

# Load .env
env_file = Path(".env")
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not set in .env file")
    sys.exit(1)

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

print("=" * 70)
print("Testing ReCAP Planning Engine with Gemini (Direct SDK)")
print("=" * 70)

def assess_atomicity(goal: Goal) -> bool:
    """Check if goal is atomic using Gemini."""
    prompt = f"""Is this goal atomic (simple enough to implement directly) or composite (needs to be broken into sub-goals)?

Goal: {goal.description}

Respond with ONLY this JSON structure (no markdown, no explanation):
{{
    "is_atomic": true,
    "reasoning": "explanation here"
}}"""
    
    response = model.generate_content(prompt)
    content = response.text.strip()
    
    # Extract JSON
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_match = re.search(r'(\{.*\})', content, re.DOTALL)
        json_str = json_match.group(1) if json_match else content
    
    # Parse
    parsed = json.loads(json_str)
    is_atomic = parsed.get("is_atomic", False)
    reasoning = parsed.get("reasoning", "No reasoning")
    
    goal.reasoning = reasoning
    
    return is_atomic

def decompose_goal(goal: Goal) -> list:
    """Decompose goal into sub-goals using Gemini."""
    prompt = f"""Break this goal into 2-5 concrete sub-goals.

Goal: {goal.description}

Respond with ONLY this JSON structure (no markdown, no explanation):
{{
    "sub_goals": [
        {{"description": "first sub-goal"}},
        {{"description": "second sub-goal"}}
    ],
    "reasoning": "explanation"
}}"""
    
    response = model.generate_content(prompt)
    content = response.text.strip()
    
    # Extract JSON
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_match = re.search(r'(\{.*\})', content, re.DOTALL)
        json_str = json_match.group(1) if json_match else content
    
    # Parse
    parsed = json.loads(json_str)
    sub_goals_data = parsed.get("sub_goals", [])
    reasoning = parsed.get("reasoning", "No reasoning")
    
    goal.reasoning = reasoning
    
    # Create child goals
    children = []
    for i, sg in enumerate(sub_goals_data[:5]):
        child = Goal(
            id=f"{goal.id}-{i+1}",
            description=sg.get("description", f"Sub-goal {i+1}"),
            parent_id=goal.id,
            depth=goal.depth + 1,
            status=GoalStatus.PENDING
        )
        children.append(child)
        goal.add_child(child.id)
    
    goal.mark_complete()
    return children

def plan_goal(plan: Plan, goal_id: str, max_depth=2):
    """Recursively plan a goal."""
    goal = plan.get_goal(goal_id)
    if not goal or goal.status != GoalStatus.PENDING or goal.depth >= max_depth:
        if goal and goal.depth >= max_depth:
            goal.mark_atomic()
        return
    
    print(f"\n{'  ' * goal.depth}🔍 Checking: {goal.description[:50]}...")
    
    # Check if atomic
    is_atomic = assess_atomicity(goal)
    
    if is_atomic:
        goal.mark_atomic()
        print(f"{'  ' * goal.depth}✓ Atomic!")
    else:
        # Decompose
        print(f"{'  ' * goal.depth}↓ Decomposing...")
        children = decompose_goal(goal)
        
        for child in children:
            plan.add_goal(child)
            print(f"{'  ' * (goal.depth + 1)}- {child.description}")
        
        # Recursively plan children
        for child in children:
            plan_goal(plan, child.id, max_depth)

# Run test
goal_desc = "Create a simple todo list web application"

print(f"\n🎯 Planning Goal:")
print(f"   '{goal_desc}'")
print("\n" + "=" * 70)

plan = Plan(id="test-plan", root_goal_id="root")
root = Goal(id="root", description=goal_desc, depth=0)
plan.add_goal(root)

plan_goal(plan, "root", max_depth=2)

# Show results
print("\n" + "=" * 70)
print("📊 Results")
print("=" * 70)

stats = plan.get_statistics()
print(f"\n✅ Planning Complete!")
print(f"   Total Goals:  {stats['total_goals']}")
print(f"   Atomic Goals: {stats['atomic_goals']}")
print(f"   Max Depth:    {stats['max_depth']}")

atomic_goals = plan.get_atomic_goals()
if atomic_goals:
    print(f"\n📝 Atomic Goals (ready for implementation):")
    for i, g in enumerate(atomic_goals, 1):
        print(f"   {i}. {g.description}")

print("\n" + "=" * 70)
print("✅ Test Successful! Gemini integration works!")
print("=" * 70)
