"""Unit tests for Node class."""

import pytest
from pydantic import ValidationError

from frctl.graph.node import Node, NodeType


class TestNodeValidation:
    """Test Node class validation."""
    
    def test_create_valid_node(self):
        """Test creating a valid node."""
        node = Node(
            id="pkg:frctl/test@local",
            type=NodeType.SERVICE,
            name="test-service"
        )
        
        assert node.id == "pkg:frctl/test@local"
        assert node.type == NodeType.SERVICE
        assert node.name == "test-service"
        assert node.metadata == {}
    
    def test_create_node_with_metadata(self):
        """Test creating a node with metadata."""
        metadata = {"version": "1.0", "owner": "team-a"}
        node = Node(
            id="pkg:frctl/api@local",
            type=NodeType.SERVICE,
            name="api",
            metadata=metadata
        )
        
        assert node.metadata == metadata
    
    def test_reject_empty_name(self):
        """Test that empty names are rejected."""
        with pytest.raises(ValidationError, match="Node name cannot be empty"):
            Node(
                id="pkg:frctl/test@local",
                type=NodeType.SERVICE,
                name=""
            )
    
    def test_reject_whitespace_name(self):
        """Test that whitespace-only names are rejected."""
        with pytest.raises(ValidationError, match="Node name cannot be empty"):
            Node(
                id="pkg:frctl/test@local",
                type=NodeType.SERVICE,
                name="   "
            )
    
    def test_reject_empty_id(self):
        """Test that empty IDs are rejected."""
        with pytest.raises(ValidationError, match="Node id cannot be empty"):
            Node(
                id="",
                type=NodeType.SERVICE,
                name="test"
            )
    
    def test_strip_whitespace_from_name(self):
        """Test that whitespace is stripped from names."""
        node = Node(
            id="pkg:frctl/test@local",
            type=NodeType.SERVICE,
            name="  test  "
        )
        
        assert node.name == "test"
    
    def test_strip_whitespace_from_id(self):
        """Test that whitespace is stripped from IDs."""
        node = Node(
            id="  pkg:frctl/test@local  ",
            type=NodeType.SERVICE,
            name="test"
        )
        
        assert node.id == "pkg:frctl/test@local"


class TestNodeTypes:
    """Test different node types."""
    
    @pytest.mark.parametrize("node_type", [
        NodeType.SERVICE,
        NodeType.LIBRARY,
        NodeType.SCHEMA,
        NodeType.ENDPOINT,
        NodeType.COMPONENT,
    ])
    def test_all_node_types(self, node_type):
        """Test creating nodes of all types."""
        node = Node(
            id=f"pkg:frctl/{node_type.value}@local",
            type=node_type,
            name=f"test-{node_type.value}"
        )
        
        assert node.type == node_type
    
    def test_invalid_node_type(self):
        """Test that invalid node types are rejected."""
        with pytest.raises(ValidationError):
            Node(
                id="pkg:frctl/test@local",
                type="InvalidType",
                name="test"
            )


class TestNodeRepresentation:
    """Test Node string representations."""
    
    def test_str_representation(self):
        """Test __str__ output."""
        node = Node(
            id="pkg:frctl/api@local",
            type=NodeType.SERVICE,
            name="api-gateway"
        )
        
        assert str(node) == "Service:api-gateway"
    
    def test_repr_representation(self):
        """Test __repr__ output."""
        node = Node(
            id="pkg:frctl/api@local",
            type=NodeType.SERVICE,
            name="api-gateway"
        )
        
        repr_str = repr(node)
        assert "Node(" in repr_str
        assert "id='pkg:frctl/api@local'" in repr_str
        assert "type=Service" in repr_str
        assert "name='api-gateway'" in repr_str
