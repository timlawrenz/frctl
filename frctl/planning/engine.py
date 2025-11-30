"""Recursive Context-Aware Planning (ReCAP) engine."""

import uuid
from typing import Dict, List, Optional, Any
from pathlib import Path

from frctl.planning.goal import Goal, GoalStatus, Plan
from frctl.llm.provider import LLMProvider
from frctl.llm.renderer import PromptRenderer
from frctl.context import ContextTree
from frctl.planning.persistence import PlanStore
from frctl.planning.digest import Digest, DigestMetadata, DigestStore


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
        prompt_renderer: Optional[PromptRenderer] = None,
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
            prompt_renderer: Prompt template renderer (defaults to default renderer)
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
        self.renderer = prompt_renderer or PromptRenderer()
        self.digest_store = DigestStore()
    
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
        
        # Extract context components
        parent_intent = context.get("parent_intent")
        global_ctx = context.get("global")
        global_context_str = None
        if global_ctx:
            # Convert dict to readable string
            global_context_str = "\n".join(f"{k}: {v}" for k, v in global_ctx.items())
        
        # Render prompt using template
        system_prompt = self.renderer.render_system_prompt()
        user_prompt = self.renderer.render_atomicity_check(
            goal_description=goal.description,
            parent_intent=parent_intent,
            global_context=global_context_str,
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
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
    
    def decompose_goal(self, goal: Goal, plan: Optional[Plan] = None) -> List[Goal]:
        """Decompose a composite goal into children with isolated contexts.
        
        Args:
            goal: Goal to decompose
            plan: Optional plan for dependency inference
            
        Returns:
            List of child goals
        """
        goal.status = GoalStatus.DECOMPOSING
        
        # Get hydrated context for this goal
        context = self.context_tree.hydrate_context(goal.id)
        
        # Extract context components
        parent_intent = context.get("parent_intent")
        global_ctx = context.get("global")
        global_context_str = None
        if global_ctx:
            # Convert dict to readable string
            global_context_str = "\n".join(f"{k}: {v}" for k, v in global_ctx.items())
        
        # Render prompt using template
        system_prompt = self.renderer.render_system_prompt()
        user_prompt = self.renderer.render_decompose_goal(
            goal_description=goal.description,
            parent_intent=parent_intent,
            global_context=global_context_str,
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
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
            
            # Infer dependencies between children (task 6.5)
            if plan and len(children) > 1:
                self._infer_dependencies(children, goal, plan)
            
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
            children = self.decompose_goal(goal, plan)
            
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
    
    def _infer_dependencies(
        self,
        children: List[Goal],
        parent: Goal,
        plan: Plan
    ) -> None:
        """Infer dependencies between sibling goals using LLM.
        
        Args:
            children: List of sibling goals
            parent: Parent goal
            plan: Plan containing the goals
        """
        if len(children) < 2:
            return  # No dependencies needed for single child
        
        # Prepare sibling goal data
        sibling_goals = [
            {"id": child.id, "description": child.description}
            for child in children
        ]
        
        # Get context
        parent_intent = parent.description if parent else None
        global_ctx = self.context_tree.global_context
        global_context_str = None
        if global_ctx:
            global_context_str = "\n".join(f"{k}: {v}" for k, v in global_ctx.items())
        
        # Render prompt
        system_prompt = self.renderer.render_system_prompt()
        user_prompt = self.renderer.render_infer_dependencies(
            sibling_goals=sibling_goals,
            parent_intent=parent_intent,
            global_context=global_context_str,
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.llm.generate(messages, temperature=0.3)
            content = response["content"].strip()
            
            # Extract JSON
            import json
            import re
            
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r'(\{.*\})', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
            
            # Parse dependencies
            try:
                parsed = json.loads(json_str)
                dependencies = parsed.get("dependencies", [])
                
                # Apply dependencies to goals
                for dep in dependencies:
                    goal_id = dep.get("goal_id")
                    depends_on = dep.get("depends_on", [])
                    
                    # Find goal and update
                    for child in children:
                        if child.id == goal_id:
                            child.dependencies = depends_on
                            break
                
            except json.JSONDecodeError:
                print(f"Dependency inference failed: could not parse JSON")
        
        except Exception as e:
            print(f"Dependency inference failed: {e}")
            # Continue without dependencies
    
    def plan_depth_first(
        self,
        plan: Plan,
        goal_id: Optional[str] = None,
        max_iterations: int = 100
    ) -> None:
        """Plan goals using depth-first traversal.
        
        Args:
            plan: Plan to work on
            goal_id: Starting goal ID (defaults to root)
            max_iterations: Maximum iterations to prevent infinite loops
        """
        if goal_id is None:
            goal_id = plan.root_goal_id
        
        iterations = 0
        stack = [goal_id]
        visited = set()
        
        while stack and iterations < max_iterations:
            iterations += 1
            current_id = stack.pop()
            
            if current_id in visited:
                continue
            visited.add(current_id)
            
            goal = plan.get_goal(current_id)
            if not goal:
                continue
            
            # Process goal based on status
            if goal.status == GoalStatus.PENDING:
                # Assess atomicity
                is_atomic = self.assess_atomicity(goal)
                
                if is_atomic:
                    goal.status = GoalStatus.ATOMIC
                else:
                    # Decompose and add children to stack (depth-first)
                    children = self.decompose_goal(goal, plan)
                    for child in children:
                        plan.add_goal(child)
                        stack.append(child.id)  # Add to stack for DFS
                
                # Auto-save after each goal
                if self.auto_save:
                    self.plan_store.save(plan)
            
            elif goal.status == GoalStatus.DECOMPOSING:
                # Already being processed, skip
                continue
        
        if iterations >= max_iterations:
            print(f"Warning: Max iterations ({max_iterations}) reached")
    
    def pause_planning(self, plan: Plan) -> Path:
        """Pause planning and save current state.
        
        Args:
            plan: Plan to pause
            
        Returns:
            Path to saved plan
        """
        plan.status = "paused"
        return self.plan_store.save(plan)
    
    def resume_planning(
        self,
        plan_id: str,
        strategy: str = "depth_first"
    ) -> Optional[Plan]:
        """Resume a paused planning session.
        
        Args:
            plan_id: ID of plan to resume
            strategy: Planning strategy ("depth_first" or "breadth_first")
            
        Returns:
            Resumed plan or None if not found
        """
        plan = self.plan_store.load(plan_id)
        if not plan:
            return None
        
        plan.status = "in_progress"
        
        # Continue planning based on strategy
        if strategy == "depth_first":
            self.plan_depth_first(plan)
        else:
            # Default to existing plan_goal for each pending
            pending = plan.get_pending_goals()
            for goal in pending:
                self.plan_goal(plan, goal.id)
        
        # Mark complete if all goals are done
        if plan.is_complete():
            plan.mark_complete()
        
        if self.auto_save:
            self.plan_store.save(plan)
        
        return plan
    
    def rollback_goal(self, plan: Plan, goal_id: str) -> bool:
        """Rollback a goal decomposition (undo children).
        
        Args:
            plan: Plan containing the goal
            goal_id: ID of goal to rollback
            
        Returns:
            True if rollback successful
        """
        goal = plan.get_goal(goal_id)
        if not goal or not goal.child_ids:
            return False
        
        # Remove children from plan
        for child_id in goal.child_ids:
            if child_id in plan.goals:
                del plan.goals[child_id]
            
            # Remove from context tree
            if child_id in self.context_tree._nodes:
                del self.context_tree._nodes[child_id]
        
        # Reset goal
        goal.child_ids = []
        goal.status = GoalStatus.PENDING
        goal.reasoning = None
        
        # Save if auto-save enabled
        if self.auto_save:
            self.plan_store.save(plan)
        
        return True
    
    def get_planning_status(self, plan: Plan) -> Dict[str, Any]:
        """Get detailed planning status.
        
        Args:
            plan: Plan to analyze
            
        Returns:
            Dictionary with status information
        """
        stats = plan.get_statistics()
        pending = plan.get_pending_goals()
        atomic = plan.get_atomic_goals()
        
        return {
            **stats,
            "pending_count": len(pending),
            "pending_goals": [g.id for g in pending],
            "next_goal": pending[0].id if pending else None,
            "is_paused": plan.status == "paused",
            "can_continue": len(pending) > 0,
        }
    
    def generate_digest(
        self,
        goal: Goal,
        plan: Plan,
        child_digests: Optional[List[Digest]] = None
    ) -> Digest:
        """Generate a compressed digest for a completed goal.
        
        Uses LLM to create a concise summary that preserves essential
        information while minimizing token usage.
        
        Args:
            goal: Completed goal to summarize
            plan: Plan containing the goal
            child_digests: Digests from child goals (if composite)
            
        Returns:
            Generated digest
        """
        # Get parent context if available
        parent_intent = None
        if goal.parent_id:
            parent_goal = plan.get_goal(goal.parent_id)
            if parent_goal:
                parent_intent = parent_goal.description
        
        # Format child digests for prompt
        child_digest_texts = []
        if child_digests:
            child_digest_texts = [d.to_context_string() for d in child_digests]
        
        # Prepare goal results (reasoning + status)
        goal_results = f"Status: {goal.status.value}"
        if goal.reasoning:
            goal_results += f"\nReasoning: {goal.reasoning}"
        
        # Render digest generation prompt
        system_prompt = self.renderer.render_system_prompt()
        user_prompt = self.renderer.render_generate_digest(
            goal_description=goal.description,
            goal_status=goal.status.value,
            goal_results=goal_results,
            child_digests=child_digest_texts if child_digest_texts else None,
            parent_intent=parent_intent,
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Count original tokens (goal + children)
        original_tokens = goal.tokens_used
        if child_digests:
            original_tokens += sum(d.metadata.original_tokens for d in child_digests)
        
        try:
            response = self.llm.generate(messages, temperature=0.3)
            content = response["content"].strip()
            
            # Extract JSON from response
            import json
            import re
            
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r'(\{.*\})', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
            
            # Parse digest data
            try:
                parsed = json.loads(json_str)
                summary = parsed.get("digest", goal.description)
                key_artifacts = parsed.get("key_artifacts", [])
                decisions = parsed.get("decisions", [])
                token_estimate = parsed.get("token_estimate", len(summary.split()) * 1.3)
            except json.JSONDecodeError:
                # Fallback to simple summary
                summary = goal.description[:150]
                key_artifacts = []
                decisions = []
                token_estimate = len(summary.split()) * 1.3
            
            # Count actual digest tokens using LLM provider
            digest_tokens = int(self.llm.count_tokens(summary))
            
            # Calculate compression metrics
            compression_ratio = digest_tokens / original_tokens if original_tokens > 0 else 0.0
            
            # Estimate fidelity (heuristic: longer summary = higher fidelity)
            # Target is <20% compression, so if we're close, fidelity is high
            if compression_ratio <= 0.2:
                fidelity = 0.95  # Excellent compression
            elif compression_ratio <= 0.3:
                fidelity = 0.90  # Good compression
            else:
                fidelity = max(0.85, 1.0 - compression_ratio)
            
            # Create digest metadata
            metadata = DigestMetadata(
                original_tokens=original_tokens,
                digest_tokens=digest_tokens,
                compression_ratio=compression_ratio,
                fidelity_estimate=fidelity,
            )
            
            # Create digest
            digest = Digest(
                goal_id=goal.id,
                summary=summary,
                key_artifacts=key_artifacts,
                decisions=decisions,
                child_digest_ids=[d.goal_id for d in (child_digests or [])],
                metadata=metadata,
            )
            
            # Store in digest store
            self.digest_store.add(digest)
            
            # Update goal with digest reference
            goal.digest = summary
            
            # Warn if fidelity is low
            if not digest.validate_fidelity(threshold=0.90):
                print(f"Warning: Low fidelity digest for goal {goal.id}: {fidelity:.1%}")
                print(f"  Compression: {compression_ratio:.1%} ({original_tokens} → {digest_tokens} tokens)")
            
            return digest
            
        except Exception as e:
            print(f"Digest generation failed: {e}")
            # Return minimal fallback digest
            return Digest(
                goal_id=goal.id,
                summary=goal.description[:100],
                metadata=DigestMetadata(
                    original_tokens=original_tokens,
                    digest_tokens=int(len(goal.description.split()) * 1.3),
                    compression_ratio=0.5,
                    fidelity_estimate=0.7,
                ),
            )
    
    def aggregate_digests(self, goal_ids: List[str]) -> Optional[str]:
        """Aggregate multiple child digests into a summary.
        
        Args:
            goal_ids: List of child goal IDs
            
        Returns:
            Aggregated summary text or None if no digests found
        """
        digests = self.digest_store.get_multiple(goal_ids)
        if not digests:
            return None
        
        # Combine summaries
        parts = [f"- {d.summary}" for d in digests]
        return "\n".join(parts)
    
    def get_digest(self, goal_id: str) -> Optional[Digest]:
        """Retrieve digest for a goal.
        
        Args:
            goal_id: Goal identifier
            
        Returns:
            Digest or None if not found
        """
        return self.digest_store.get(goal_id)
    
    def get_digest_stats(self) -> Dict[str, float]:
        """Get quality statistics for all digests.
        
        Returns:
            Dictionary with compression and fidelity metrics
        """
        return self.digest_store.get_quality_stats()
