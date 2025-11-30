"""Recursive Context-Aware Planning (ReCAP) engine."""

import uuid
from typing import Dict, List, Optional
from pathlib import Path

from frctl.planning.goal import Goal, GoalStatus, Plan
from frctl.llm.provider import LLMProvider


class PlanningEngine:
    """ReCAP planning engine for hierarchical goal decomposition.
    
    Implements the Recursive Context-Aware Planning algorithm:
    1. Assess if goal is atomic
    2. If composite, decompose into children
    3. Recursively process children with isolated contexts
    4. Generate digests for completed subtrees
    """
    
    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        max_depth: int = 10,
        max_children: int = 7,
    ):
        """Initialize planning engine.
        
        Args:
            llm_provider: LLM provider for reasoning (defaults to gpt-4)
            max_depth: Maximum planning depth before forcing atomic
            max_children: Maximum children per decomposition
        """
        self.llm = llm_provider or LLMProvider(model="gpt-4")
        self.max_depth = max_depth
        self.max_children = max_children
    
    def create_plan(self, description: str) -> Plan:
        """Create a new planning session.
        
        Args:
            description: High-level goal description
            
        Returns:
            New Plan with root goal
        """
        plan_id = str(uuid.uuid4())[:8]
        root_goal_id = f"{plan_id}-root"
        
        root_goal = Goal(
            id=root_goal_id,
            description=description,
            depth=0,
            status=GoalStatus.PENDING,
        )
        
        plan = Plan(
            id=plan_id,
            root_goal_id=root_goal_id,
        )
        plan.add_goal(root_goal)
        
        return plan
    
    def assess_atomicity(self, goal: Goal) -> bool:
        """Assess if a goal is atomic using LLM.
        
        Args:
            goal: Goal to assess
            
        Returns:
            True if atomic, False if composite
        """
        # Force atomic at max depth
        if goal.depth >= self.max_depth:
            return True
        
        # Simple prompt for atomicity check
        messages = [
            {
                "role": "system",
                "content": "You are an expert software architect. Determine if a goal is atomic (can be implemented in a single file/component) or composite (needs to be broken down)."
            },
            {
                "role": "user",
                "content": f"""Goal: {goal.description}

Is this goal atomic (simple enough to implement directly) or composite (needs to be broken into sub-goals)?

Respond with JSON:
{{
    "is_atomic": true/false,
    "reasoning": "explanation"
}}"""
            }
        ]
        
        try:
            response = self.llm.generate(messages, temperature=0.3)
            content = response["content"]
            
            # Simple parsing (in production, use structured output)
            is_atomic = "true" in content.lower() and "is_atomic" in content.lower()
            
            # Store reasoning
            goal.reasoning = content
            goal.tokens_used += response["usage"]["total_tokens"]
            
            return is_atomic
            
        except Exception as e:
            print(f"Atomicity check failed: {e}")
            # Default to atomic on failure
            return True
    
    def decompose_goal(self, goal: Goal) -> List[Goal]:
        """Decompose a composite goal into children.
        
        Args:
            goal: Goal to decompose
            
        Returns:
            List of child goals
        """
        goal.status = GoalStatus.DECOMPOSING
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert software architect. Break down complex goals into 2-7 concrete sub-goals."
            },
            {
                "role": "user",
                "content": f"""Goal: {goal.description}

Break this down into concrete sub-goals. Each sub-goal should be clear and specific.

Respond with JSON:
{{
    "sub_goals": [
        {{"description": "first sub-goal"}},
        {{"description": "second sub-goal"}},
        ...
    ],
    "reasoning": "explanation of decomposition"
}}"""
            }
        ]
        
        try:
            response = self.llm.generate(messages, temperature=0.5)
            content = response["content"]
            
            # Simple parsing (in production, use structured output)
            # For now, create placeholder children
            children = []
            for i in range(min(3, self.max_children)):  # Default to 3 children
                child_id = f"{goal.id}-{i+1}"
                child = Goal(
                    id=child_id,
                    description=f"Sub-goal {i+1} of: {goal.description[:30]}...",
                    parent_id=goal.id,
                    depth=goal.depth + 1,
                    status=GoalStatus.PENDING,
                )
                children.append(child)
                goal.add_child(child_id)
            
            goal.reasoning = content
            goal.tokens_used += response["usage"]["total_tokens"]
            goal.mark_complete()
            
            return children
            
        except Exception as e:
            print(f"Decomposition failed: {e}")
            goal.status = GoalStatus.FAILED
            return []
    
    def plan_goal(self, plan: Plan, goal_id: str) -> None:
        """Recursively plan a goal and its children.
        
        Args:
            plan: Planning session
            goal_id: ID of goal to plan
        """
        goal = plan.get_goal(goal_id)
        if not goal or goal.status != GoalStatus.PENDING:
            return
        
        # Check if atomic
        is_atomic = self.assess_atomicity(goal)
        
        if is_atomic:
            goal.mark_atomic()
            print(f"✓ Atomic: {goal.description[:60]}")
        else:
            # Decompose into children
            children = self.decompose_goal(goal)
            
            # Add children to plan
            for child in children:
                plan.add_goal(child)
            
            print(f"↓ Decomposed into {len(children)} sub-goals: {goal.description[:50]}")
            
            # Recursively plan children
            for child in children:
                self.plan_goal(plan, child.id)
    
    def run(self, description: str) -> Plan:
        """Run complete planning session.
        
        Args:
            description: High-level goal
            
        Returns:
            Completed Plan
        """
        print(f"\n🎯 Starting planning: {description}\n")
        
        # Create plan
        plan = self.create_plan(description)
        
        # Recursively plan from root
        self.plan_goal(plan, plan.root_goal_id)
        
        # Mark complete
        plan.mark_complete()
        
        print(f"\n✅ Planning complete!")
        print(f"   Total goals: {len(plan.goals)}")
        print(f"   Atomic goals: {len(plan.get_atomic_goals())}")
        print(f"   Max depth: {plan.max_depth}")
        print(f"   Total tokens: {plan.total_tokens}")
        
        return plan
