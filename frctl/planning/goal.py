"""Goal data model for hierarchical planning."""

from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class GoalStatus(str, Enum):
    """Status of a goal in the planning process."""
    
    PENDING = "pending"           # Not yet processed
    DECOMPOSING = "decomposing"   # Currently being broken down
    ATOMIC = "atomic"             # Identified as atomic (ready for implementation)
    COMPLETE = "complete"         # Decomposition complete
    FAILED = "failed"             # Decomposition failed


class Goal(BaseModel):
    """A goal in the planning tree.
    
    Goals form a hierarchical tree structure where composite goals
    are decomposed into child goals until atomic goals are reached.
    """
    
    id: str = Field(..., description="Unique identifier for the goal")
    description: str = Field(..., description="Natural language description of the goal")
    status: GoalStatus = Field(default=GoalStatus.PENDING, description="Current status")
    
    # Hierarchy
    parent_id: Optional[str] = Field(None, description="ID of parent goal")
    child_ids: List[str] = Field(default_factory=list, description="IDs of child goals")
    
    # Metadata
    depth: int = Field(0, description="Depth in the planning tree (0 = root)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Context and results
    reasoning: Optional[str] = Field(None, description="LLM reasoning for decomposition")
    digest: Optional[str] = Field(None, description="Compressed summary of subtree")
    tokens_used: int = Field(0, description="Total tokens used for this goal")
    
    # Dependencies (references to other goals or graph nodes)
    dependencies: List[str] = Field(default_factory=list, description="IDs of goals this depends on")
    graph_node_id: Optional[str] = Field(None, description="Associated node in FederatedGraph")
    
    def is_atomic(self) -> bool:
        """Check if this goal is atomic (no children)."""
        return self.status == GoalStatus.ATOMIC or (
            self.status == GoalStatus.COMPLETE and len(self.child_ids) == 0
        )
    
    def is_composite(self) -> bool:
        """Check if this goal is composite (has children)."""
        return len(self.child_ids) > 0
    
    def mark_atomic(self) -> None:
        """Mark this goal as atomic."""
        self.status = GoalStatus.ATOMIC
        self.updated_at = datetime.utcnow()
    
    def mark_complete(self) -> None:
        """Mark this goal as complete."""
        self.status = GoalStatus.COMPLETE
        self.updated_at = datetime.utcnow()
    
    def add_child(self, child_id: str) -> None:
        """Add a child goal."""
        if child_id not in self.child_ids:
            self.child_ids.append(child_id)
            self.updated_at = datetime.utcnow()
    
    def add_dependency(self, goal_id: str) -> None:
        """Add a dependency on another goal."""
        if goal_id not in self.dependencies:
            self.dependencies.append(goal_id)
            self.updated_at = datetime.utcnow()
    
    def __str__(self) -> str:
        return f"Goal({self.id}, {self.status.value}, depth={self.depth}): {self.description[:50]}"
    
    def __repr__(self) -> str:
        return f"Goal(id='{self.id}', status={self.status.value}, depth={self.depth})"


class Plan(BaseModel):
    """A planning session containing a tree of goals.
    
    Plans represent a complete planning session from a high-level goal
    down to atomic implementation tasks.
    """
    
    id: str = Field(..., description="Unique plan identifier")
    root_goal_id: str = Field(..., description="ID of the root goal")
    goals: Dict[str, Goal] = Field(default_factory=dict, description="All goals indexed by ID")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field("in_progress", description="Plan status: in_progress, complete, failed")
    
    # Statistics
    total_tokens: int = Field(0, description="Total tokens used across all goals")
    max_depth: int = Field(0, description="Maximum depth reached")
    
    def add_goal(self, goal: Goal) -> None:
        """Add a goal to the plan."""
        self.goals[goal.id] = goal
        self.updated_at = datetime.utcnow()
        
        # Update statistics
        if goal.depth > self.max_depth:
            self.max_depth = goal.depth
        self.total_tokens += goal.tokens_used
    
    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Get a goal by ID."""
        return self.goals.get(goal_id)
    
    def get_root_goal(self) -> Optional[Goal]:
        """Get the root goal."""
        return self.goals.get(self.root_goal_id)
    
    def get_children(self, goal_id: str) -> List[Goal]:
        """Get all children of a goal."""
        goal = self.goals.get(goal_id)
        if not goal:
            return []
        return [self.goals[child_id] for child_id in goal.child_ids if child_id in self.goals]
    
    def get_atomic_goals(self) -> List[Goal]:
        """Get all atomic goals in the plan."""
        return [goal for goal in self.goals.values() if goal.is_atomic()]
    
    def get_pending_goals(self) -> List[Goal]:
        """Get all pending goals."""
        return [goal for goal in self.goals.values() if goal.status == GoalStatus.PENDING]
    
    def is_complete(self) -> bool:
        """Check if planning is complete (all goals are atomic or complete)."""
        for goal in self.goals.values():
            if goal.status in [GoalStatus.PENDING, GoalStatus.DECOMPOSING]:
                return False
        return True
    
    def mark_complete(self) -> None:
        """Mark the plan as complete."""
        self.status = "complete"
        self.updated_at = datetime.utcnow()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get plan statistics."""
        atomic_count = len(self.get_atomic_goals())
        total_goals = len(self.goals)
        
        return {
            "total_goals": total_goals,
            "atomic_goals": atomic_count,
            "max_depth": self.max_depth,
            "total_tokens": self.total_tokens,
            "status": self.status,
            "is_complete": self.is_complete(),
        }
