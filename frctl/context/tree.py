"""Context Tree for hierarchical context management in ReCAP.

The Context Tree manages context isolation and propagation during planning:
- Each goal gets its own context node
- Parent context is hydrated (injected) into child contexts
- Child results are dehydrated (compressed) into digests
- Token usage is tracked per context to avoid hitting limits
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ContextNode(BaseModel):
    """A node in the context tree.
    
    Each context node represents the context for a specific goal in the planning tree.
    Contexts are isolated from siblings but inherit from parents through hydration.
    """
    
    goal_id: str = Field(..., description="ID of the goal this context belongs to")
    parent_goal_id: Optional[str] = Field(None, description="ID of parent goal")
    
    # Context content
    global_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Global project context (settings, constraints)"
    )
    parent_intent: Optional[str] = Field(
        None,
        description="Propagated intent from parent goal"
    )
    local_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Local context specific to this goal"
    )
    
    # Token tracking
    tokens_used: int = Field(0, description="Tokens consumed in this context")
    token_limit: int = Field(8192, description="Maximum tokens allowed")
    
    # Results and compression
    digest: Optional[str] = Field(
        None,
        description="Compressed summary of this subtree's results"
    )
    digest_tokens: int = Field(0, description="Tokens in the digest")
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def is_over_limit(self) -> bool:
        """Check if token usage exceeds limit."""
        return self.tokens_used > self.token_limit
    
    def remaining_tokens(self) -> int:
        """Calculate remaining token budget."""
        return max(0, self.token_limit - self.tokens_used)
    
    def add_tokens(self, count: int) -> None:
        """Track additional token usage."""
        self.tokens_used += count


class ContextTree:
    """Hierarchical context management for planning trees.
    
    The Context Tree implements:
    - Context isolation: Each goal gets a fresh context window
    - Hydration: Parent context is injected into child contexts
    - Dehydration: Child results are compressed into digests
    - Token hygiene: Tracks and enforces token limits per context
    
    This prevents the Context Coherence Crisis by ensuring each planning
    step operates within a clean context window while preserving parent intent.
    """
    
    def __init__(
        self,
        default_token_limit: int = 8192,
        global_context: Optional[Dict[str, Any]] = None,
    ):
        """Initialize context tree.
        
        Args:
            default_token_limit: Default token limit per context node
            global_context: Global project context shared across all nodes
        """
        self.default_token_limit = default_token_limit
        self.global_context = global_context or {}
        self._nodes: Dict[str, ContextNode] = {}
    
    def create_root_context(self, goal_id: str) -> ContextNode:
        """Create root context for the planning tree.
        
        Args:
            goal_id: ID of the root goal
            
        Returns:
            Root context node
        """
        node = ContextNode(
            goal_id=goal_id,
            parent_goal_id=None,
            global_context=self.global_context.copy(),
            token_limit=self.default_token_limit,
        )
        self._nodes[goal_id] = node
        return node
    
    def create_child_context(
        self,
        goal_id: str,
        parent_goal_id: str,
        parent_intent: Optional[str] = None,
    ) -> ContextNode:
        """Create child context with hydrated parent context.
        
        Args:
            goal_id: ID of the child goal
            parent_goal_id: ID of the parent goal
            parent_intent: Intent propagated from parent
            
        Returns:
            Child context node with hydrated parent context
        """
        # Get parent context
        if parent_goal_id not in self._nodes:
            raise ValueError(f"Parent context not found: {parent_goal_id}")
        
        parent_node = self._nodes[parent_goal_id]
        
        # Create child with hydrated context
        node = ContextNode(
            goal_id=goal_id,
            parent_goal_id=parent_goal_id,
            global_context=parent_node.global_context.copy(),
            parent_intent=parent_intent,
            token_limit=self.default_token_limit,
        )
        
        self._nodes[goal_id] = node
        return node
    
    def hydrate_context(self, goal_id: str) -> Dict[str, Any]:
        """Hydrate context for a goal (inject parent context).
        
        This creates the full context that will be passed to the LLM
        for processing this goal. It includes:
        - Global project context
        - Parent intent (compressed)
        - Local context for this goal
        
        Args:
            goal_id: ID of the goal to hydrate context for
            
        Returns:
            Hydrated context ready for LLM consumption
        """
        if goal_id not in self._nodes:
            raise ValueError(f"Context not found: {goal_id}")
        
        node = self._nodes[goal_id]
        
        # Build hydrated context
        hydrated = {
            "global": node.global_context,
            "local": node.local_context,
        }
        
        # Include parent intent if available
        if node.parent_intent:
            hydrated["parent_intent"] = node.parent_intent
        
        return hydrated
    
    def dehydrate_context(
        self,
        goal_id: str,
        digest: str,
        digest_tokens: int,
    ) -> None:
        """Dehydrate context by compressing results into a digest.
        
        After a goal subtree is complete, its full results are compressed
        into a digest. This preserves the key information while drastically
        reducing token count for parent contexts.
        
        Args:
            goal_id: ID of the goal to dehydrate
            digest: Compressed summary of subtree results
            digest_tokens: Token count of the digest
        """
        if goal_id not in self._nodes:
            raise ValueError(f"Context not found: {goal_id}")
        
        node = self._nodes[goal_id]
        node.digest = digest
        node.digest_tokens = digest_tokens
    
    def get_context(self, goal_id: str) -> Optional[ContextNode]:
        """Get context node for a goal.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            Context node or None if not found
        """
        return self._nodes.get(goal_id)
    
    def update_token_usage(self, goal_id: str, tokens: int) -> None:
        """Update token usage for a context.
        
        Args:
            goal_id: ID of the goal
            tokens: Number of tokens to add
        """
        if goal_id not in self._nodes:
            raise ValueError(f"Context not found: {goal_id}")
        
        self._nodes[goal_id].add_tokens(tokens)
    
    def set_global_context(self, key: str, value: Any) -> None:
        """Set a global context value (propagates to all nodes).
        
        Args:
            key: Context key
            value: Context value
        """
        self.global_context[key] = value
        
        # Update all existing nodes
        for node in self._nodes.values():
            node.global_context[key] = value
    
    def set_local_context(self, goal_id: str, key: str, value: Any) -> None:
        """Set a local context value for a specific goal.
        
        Args:
            goal_id: ID of the goal
            key: Context key
            value: Context value
        """
        if goal_id not in self._nodes:
            raise ValueError(f"Context not found: {goal_id}")
        
        self._nodes[goal_id].local_context[key] = value
    
    def get_total_tokens(self) -> int:
        """Get total tokens used across all contexts.
        
        Returns:
            Total token count
        """
        return sum(node.tokens_used for node in self._nodes.values())
    
    def get_tree_stats(self) -> Dict[str, Any]:
        """Get statistics about the context tree.
        
        Returns:
            Dict with stats (total nodes, total tokens, avg tokens, etc.)
        """
        if not self._nodes:
            return {
                "total_nodes": 0,
                "total_tokens": 0,
                "avg_tokens_per_node": 0,
                "max_tokens": 0,
                "nodes_over_limit": 0,
            }
        
        tokens = [node.tokens_used for node in self._nodes.values()]
        over_limit = sum(1 for node in self._nodes.values() if node.is_over_limit())
        
        return {
            "total_nodes": len(self._nodes),
            "total_tokens": sum(tokens),
            "avg_tokens_per_node": sum(tokens) / len(tokens),
            "max_tokens": max(tokens),
            "nodes_over_limit": over_limit,
        }
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize context tree to dict for persistence.
        
        Returns:
            Serialized context tree
        """
        return {
            "default_token_limit": self.default_token_limit,
            "global_context": self.global_context,
            "nodes": {
                goal_id: node.model_dump()
                for goal_id, node in self._nodes.items()
            },
        }
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "ContextTree":
        """Deserialize context tree from dict.
        
        Args:
            data: Serialized context tree
            
        Returns:
            Reconstructed ContextTree instance
        """
        tree = cls(
            default_token_limit=data["default_token_limit"],
            global_context=data["global_context"],
        )
        
        # Reconstruct nodes
        for goal_id, node_data in data["nodes"].items():
            tree._nodes[goal_id] = ContextNode(**node_data)
        
        return tree
