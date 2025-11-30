"""Edge class for graph relationships."""

from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, field_validator


class EdgeType(str, Enum):
    """Types of relationships between nodes."""
    
    DEPENDS_ON = "DEPENDS_ON"
    CONSUMES = "CONSUMES"
    OWNS = "OWNS"
    IMPLEMENTS = "IMPLEMENTS"


class Edge(BaseModel):
    """An edge representing a relationship between nodes.
    
    Edges are directed and typed, representing semantic relationships
    like dependencies, ownership, or interface implementation.
    """
    
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    edge_type: EdgeType = Field(..., description="Type of relationship")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    contract: Optional[str] = Field(None, description="Path to TypeSpec contract file")
    
    @field_validator('source', 'target')
    @classmethod
    def validate_node_ids(cls, v: str) -> str:
        """Validate that node IDs are not empty."""
        if not v or not v.strip():
            raise ValueError("Node ID cannot be empty")
        return v.strip()
    
    @field_validator('contract')
    @classmethod
    def validate_contract(cls, v: Optional[str]) -> Optional[str]:
        """Validate contract path if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v
    
    def __str__(self) -> str:
        return f"{self.source} --[{self.edge_type.value}]--> {self.target}"
    
    def __repr__(self) -> str:
        return f"Edge(source='{self.source}', target='{self.target}', type={self.edge_type.value})"
