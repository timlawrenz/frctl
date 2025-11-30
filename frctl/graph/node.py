"""Node class for graph representation."""

from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, field_validator


class NodeType(str, Enum):
    """Types of nodes in the architectural graph."""
    
    SERVICE = "Service"
    LIBRARY = "Library"
    SCHEMA = "Schema"
    ENDPOINT = "Endpoint"
    COMPONENT = "Component"


class Node(BaseModel):
    """A node in the architectural graph.
    
    Represents a semantic component in the software architecture.
    Each node has a unique identifier, type, name, and optional metadata.
    """
    
    id: str = Field(..., description="Unique identifier (PURL format)")
    type: NodeType = Field(..., description="Type of the node")
    name: str = Field(..., description="Human-readable name")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that name is not empty."""
        if not v or not v.strip():
            raise ValueError("Node name cannot be empty")
        return v.strip()
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate that id is not empty."""
        if not v or not v.strip():
            raise ValueError("Node id cannot be empty")
        return v.strip()
    
    def __str__(self) -> str:
        return f"{self.type.value}:{self.name}"
    
    def __repr__(self) -> str:
        return f"Node(id='{self.id}', type={self.type.value}, name='{self.name}')"
