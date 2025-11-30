"""Unit tests for Edge class."""

import pytest
from pydantic import ValidationError

from frctl.graph.edge import Edge, EdgeType


class TestEdgeValidation:
    """Test Edge class validation."""
    
    def test_create_valid_edge(self):
        """Test creating a valid edge."""
        edge = Edge(
            source="pkg:frctl/a@local",
            target="pkg:frctl/b@local",
            edge_type=EdgeType.DEPENDS_ON
        )
        
        assert edge.source == "pkg:frctl/a@local"
        assert edge.target == "pkg:frctl/b@local"
        assert edge.edge_type == EdgeType.DEPENDS_ON
        assert edge.metadata == {}
        assert edge.contract is None
    
    def test_create_edge_with_metadata(self):
        """Test creating an edge with metadata."""
        metadata = {"version": "1.0"}
        edge = Edge(
            source="pkg:frctl/a@local",
            target="pkg:frctl/b@local",
            edge_type=EdgeType.CONSUMES,
            metadata=metadata
        )
        
        assert edge.metadata == metadata
    
    def test_create_edge_with_contract(self):
        """Test creating an edge with a TypeSpec contract."""
        edge = Edge(
            source="pkg:frctl/a@local",
            target="pkg:frctl/b@local",
            edge_type=EdgeType.IMPLEMENTS,
            contract="contracts/api.tsp"
        )
        
        assert edge.contract == "contracts/api.tsp"
    
    def test_reject_empty_source(self):
        """Test that empty source IDs are rejected."""
        with pytest.raises(ValidationError, match="Node ID cannot be empty"):
            Edge(
                source="",
                target="pkg:frctl/b@local",
                edge_type=EdgeType.DEPENDS_ON
            )
    
    def test_reject_empty_target(self):
        """Test that empty target IDs are rejected."""
        with pytest.raises(ValidationError, match="Node ID cannot be empty"):
            Edge(
                source="pkg:frctl/a@local",
                target="",
                edge_type=EdgeType.DEPENDS_ON
            )
    
    def test_strip_whitespace_from_source(self):
        """Test that whitespace is stripped from source."""
        edge = Edge(
            source="  pkg:frctl/a@local  ",
            target="pkg:frctl/b@local",
            edge_type=EdgeType.DEPENDS_ON
        )
        
        assert edge.source == "pkg:frctl/a@local"
    
    def test_strip_whitespace_from_target(self):
        """Test that whitespace is stripped from target."""
        edge = Edge(
            source="pkg:frctl/a@local",
            target="  pkg:frctl/b@local  ",
            edge_type=EdgeType.DEPENDS_ON
        )
        
        assert edge.target == "pkg:frctl/b@local"
    
    def test_empty_contract_becomes_none(self):
        """Test that empty contract strings become None."""
        edge = Edge(
            source="pkg:frctl/a@local",
            target="pkg:frctl/b@local",
            edge_type=EdgeType.DEPENDS_ON,
            contract="   "
        )
        
        assert edge.contract is None


class TestEdgeTypes:
    """Test different edge types."""
    
    @pytest.mark.parametrize("edge_type", [
        EdgeType.DEPENDS_ON,
        EdgeType.CONSUMES,
        EdgeType.OWNS,
        EdgeType.IMPLEMENTS,
    ])
    def test_all_edge_types(self, edge_type):
        """Test creating edges of all types."""
        edge = Edge(
            source="pkg:frctl/a@local",
            target="pkg:frctl/b@local",
            edge_type=edge_type
        )
        
        assert edge.edge_type == edge_type
    
    def test_invalid_edge_type(self):
        """Test that invalid edge types are rejected."""
        with pytest.raises(ValidationError):
            Edge(
                source="pkg:frctl/a@local",
                target="pkg:frctl/b@local",
                edge_type="InvalidType"
            )


class TestEdgeRepresentation:
    """Test Edge string representations."""
    
    def test_str_representation(self):
        """Test __str__ output."""
        edge = Edge(
            source="pkg:frctl/a@local",
            target="pkg:frctl/b@local",
            edge_type=EdgeType.DEPENDS_ON
        )
        
        assert str(edge) == "pkg:frctl/a@local --[DEPENDS_ON]--> pkg:frctl/b@local"
    
    def test_repr_representation(self):
        """Test __repr__ output."""
        edge = Edge(
            source="pkg:frctl/a@local",
            target="pkg:frctl/b@local",
            edge_type=EdgeType.CONSUMES
        )
        
        repr_str = repr(edge)
        assert "Edge(" in repr_str
        assert "source='pkg:frctl/a@local'" in repr_str
        assert "target='pkg:frctl/b@local'" in repr_str
        assert "type=CONSUMES" in repr_str
