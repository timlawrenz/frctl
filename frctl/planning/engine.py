"""Recursive Context-Aware Planning (ReCAP) engine."""

import uuid
from typing import Dict, List, Optional, Any
from pathlib import Path

from frctl.planning.goal import Goal, GoalStatus, Plan
from frctl.llm.provider import LLMProvider
from frctl.context import ContextTree
from frctl.planning.persistence import PlanStore


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
        token_limit: int = 8192,
        global_context: Optional[Dict[str, Any]] = None,
        plan_store: Optional[PlanStore] = None,
        auto_save: bool = True,
    ):
        """Initialize planning engine.
        
        Args:
            llm_provider: LLM provider for reasoning (defaults to gpt-4)
            max_depth: Maximum planning depth before forcing atomic
            max_children: Maximum children per decomposition
            token_limit: Token limit per context node
            global_context: Global project context
            plan_store: Plan store for persistence (defaults to .frctl/plans)
            auto_save: Whether to automatically save plans after changes
        """
        self.llm = llm_provider or LLMProvider(model="gpt-4")
        self.max_depth = max_depth
        self.max_children = max_children
        self.context_tree = ContextTree(
            default_token_limit=token_limit,
            global_context=global_context or {},
        )
        self.plan_store = plan_store or PlanStore()
        self.auto_save = auto_save
    
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
        
        # Create root context
        self.context_tree.create_root_context(root_goal_id)
        
        # Auto-save if enabled
        if self.auto_save:
            self.plan_store.save(plan)
        
        return plan
    
    def assess_atomicity(self, goal: Goal) -> bool:
        """Assess if a goal is atomic using LLM with context.
        
        Args:
            goal: Goal to assess
            
        Returns:
            True if atomic, False if composite
        """
        # Force atomic at max depth
        if goal.depth >= self.max_depth:
            return True
        
        # Get hydrated context for this goal
        context = self.context_tree.hydrate_context(goal.id)
        
        # Build context-aware prompt
        context_info = ""
        if context.get("parent_intent"):
            context_info += f"\nParent Goal: {context['parent_intent']}"
        if context.get("global"):
            context_info += f"\nProject Context: {context['global']}"
        
        # Simple prompt for atomicity check
        messages = [
            {
                "role": "system",
                "content": "You are an expert software architect. Determine if a goal is atomic (can be implemented in a single file/component) or composite (needs to be broken down). Always respond with valid JSON."
            },
            {
                "role": "user",
                "content": f"""Goal: {goal.description}{context_info}

Is this goal atomic (simple enough to implement directly) or composite (needs to be broken into sub-goals)?

Respond with ONLY this JSON structure (no markdown, no explanation):
{{
    "is_atomic": true,
    "reasoning": "explanation here"
}}"""
            }
        ]
        
        try:
            response = self.llm.generate(messages, temperature=0.3)
            content = response["content"].strip()
            
            # Extract JSON from response (handle markdown code blocks)
            import json
            import re
            
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r'(\{.*\})', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
            
            # Parse JSON
            try:
                parsed = json.loads(json_str)
                is_atomic = parsed.get("is_atomic", False)
                reasoning = parsed.get("reasoning", "No reasoning provided")
            except json.JSONDecodeError as je:
                print(f"JSON parsing failed: {je}")
                print(f"Content: {content}")
                # Fallback to keyword detection
                is_atomic = "true" in content.lower() and "is_atomic" in content.lower()
                reasoning = content
            
            # Store reasoning and update token usage
            goal.reasoning = reasoning
            tokens = response["usage"]["total_tokens"]
            goal.tokens_used += tokens
            self.context_tree.update_token_usage(goal.id, tokens)
            
            return is_atomic
            
        except Exception as e:
            print(f"Atomicity check failed: {e}")
            # Default to atomic on failure
            return True
    
    def decompose_goal(self, goal: Goal) -> List[Goal]:
        """Decompose a composite goal into children with isolated contexts.
        
        Args:
            goal: Goal to decompose
            
        Returns:
            List of child goals
        """
        goal.status = GoalStatus.DECOMPOSING
        
        # Get hydrated context for this goal
        context = self.context_tree.hydrate_context(goal.id)
        
        # Build context-aware prompt
        context_info = ""
        if context.get("parent_intent"):
            context_info += f"\nParent Goal: {context['parent_intent']}"
        if context.get("global"):
            context_info += f"\nProject Context: {context['global']}"
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert software architect. Break down complex goals into 2-7 concrete sub-goals. Always respond with valid JSON."
            },
            {
                "role": "user",
                "content": f"""Goal: {goal.description}{context_info}

Break this down into concrete sub-goals. Each sub-goal should be clear and specific.

Respond with ONLY this JSON structure (no markdown, no explanation):
{{
    "sub_goals": [
        {{"description": "first sub-goal"}},
        {{"description": "second sub-goal"}},
        ...
    ],
    "reasoning": "explanation of decomposition strategy"
}}"""
            }
        ]
        
        try:
            response = self.llm.generate(messages, temperature=0.5)
            content = response["content"].strip()
            
            # Extract JSON from response (handle markdown code blocks)
            import json
            import re
            
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r'(\{.*\})', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
            
            # Parse JSON
            try:
                parsed = json.loads(json_str)
                sub_goals_data = parsed.get("sub_goals", [])
                reasoning = parsed.get("reasoning", "No reasoning provided")
            except json.JSONDecodeError as je:
                print(f"JSON parsing failed: {je}")
                print(f"Content: {content}")
                # Fallback to simple parsing
                sub_goals_data = []
                reasoning = content
            
            # Create child goals from parsed data with isolated contexts
            children = []
            for i, sub_goal_data in enumerate(sub_goals_data[:self.max_children]):
                child_id = f"{goal.id}-{i+1}"
                child_desc = sub_goal_data.get("description", f"Sub-goal {i+1}")
                
                child = Goal(
                    id=child_id,
                    description=child_desc,
                    parent_id=goal.id,
                    depth=goal.depth + 1,
                    status=GoalStatus.PENDING,
                )
                children.append(child)
                goal.add_child(child_id)
                
                # Create isolated context for child with parent intent
                self.context_tree.create_child_context(
                    goal_id=child_id,
                    parent_goal_id=goal.id,
                    parent_intent=child_desc,
                )
            
            # If parsing failed or no sub-goals, create default fallback
            if not children:
                print(f"Warning: No sub-goals parsed, creating fallback decomposition")
                for i in range(min(3, self.max_children)):
                    child_id = f"{goal.id}-{i+1}"
                    child_desc = f"Sub-task {i+1}: {goal.description[:40]}..."
                    
                    child = Goal(
                        id=child_id,
                        description=child_desc,
                        parent_id=goal.id,
                        depth=goal.depth + 1,
                        status=GoalStatus.PENDING,
                    )
                    children.append(child)
                    goal.add_child(child_id)
                    
                    # Create context for fallback child
                    self.context_tree.create_child_context(
                        goal_id=child_id,
                        parent_goal_id=goal.id,
                        parent_intent=child_desc,
                    )
            
            # Update parent goal with reasoning and token usage
            goal.reasoning = reasoning
            tokens = response["usage"]["total_tokens"]
            goal.tokens_used += tokens
            self.context_tree.update_token_usage(goal.id, tokens)
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
            
            # Auto-save progress after each decomposition
            if self.auto_save:
                self.plan_store.save(plan)
    
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
        
        # Get context tree statistics
        stats = self.context_tree.get_tree_stats()
        
        print(f"\n✅ Planning complete!")
        print(f"   Total goals: {len(plan.goals)}")
        print(f"   Atomic goals: {len(plan.get_atomic_goals())}")
        print(f"   Max depth: {plan.max_depth}")
        print(f"   Total tokens: {plan.total_tokens}")
        print(f"   Context nodes: {stats['total_nodes']}")
        print(f"   Avg tokens/context: {stats['avg_tokens_per_node']:.0f}")
        
        # Auto-save if enabled
        if self.auto_save:
            self.plan_store.save(plan)
        
        return plan
    
    def load_plan(self, plan_id: str) -> Optional[Plan]:
        """Load a plan from storage.
        
        Args:
            plan_id: ID of plan to load
            
        Returns:
            Loaded plan or None if not found
        """
        return self.plan_store.load(plan_id)
    
    def save_plan(self, plan: Plan) -> Path:
        """Save a plan to storage.
        
        Args:
            plan: Plan to save
            
        Returns:
            Path to saved plan file
        """
        return self.plan_store.save(plan)
    
    def list_plans(self, status: Optional[str] = None) -> List[Dict]:
        """List all plans.
        
        Args:
            status: Filter by status (in_progress, complete, failed)
            
        Returns:
            List of plan metadata
        """
        return self.plan_store.list_plans(status=status)
    
    def delete_plan(self, plan_id: str, archive: bool = True) -> bool:
        """Delete a plan.
        
        Args:
            plan_id: Plan ID to delete
            archive: Whether to archive before deleting
            
        Returns:
            True if deleted successfully
        """
        return self.plan_store.delete(plan_id, archive=archive)
