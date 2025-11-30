"""Unit tests for FederatedGraph DAG operations."""

import pytest
import json
import tempfile
from pathlib import Path

from frctl.graph import FederatedGraph, Node, NodeType, Edge, EdgeType
from frctl.graph.dag import (
    CycleDetectedError,
    NodeNotFoundError,
    generate_purl
)


class TestGraphBasics:
    """Test basic graph operations."""
    
    def test_create_empty_graph(self):
        """Test creating an empty graph."""
        g = FederatedGraph()
        
        assert g.node_count() == 0
        assert g.edge_count() == 0
        assert g.depth() == 0
    
    def test_add_single_node(self):
        """Test adding a single node."""
        g = FederatedGraph()
        node = Node(
            id="pkg:frctl/test@local",
            type=NodeType.SERVICE,
            name="test"
        )
        g.add_node(node)
        
        assert g.node_count() == 1
        assert g.get_node("pkg:frctl/test@local") == node
    
    def test_reject_duplicate_node(self):
        """Test that duplicate node IDs are rejected."""
        g = FederatedGraph()
        node1 = Node(id="pkg:frctl/test@local", type=NodeType.SERVICE, name="test1")
        node2 = Node(id="pkg:frctl/test@local", type=NodeType.SERVICE, name="test2")
        
        g.add_node(node1)
        with pytest.raises(ValueError, match="already exists"):
            g.add_node(node2)
    
    def test_remove_node(self):
        """Test removing a node."""
        g = FederatedGraph()
        node = Node(id="pkg:frctl/test@local", type=NodeType.SERVICE, name="test")
        g.add_node(node)
        
        g.remove_node("pkg:frctl/test@local")
        
        assert g.node_count() == 0
        assert g.get_node("pkg:frctl/test@local") is None
    
    def test_remove_nonexistent_node(self):
        """Test removing a node that doesn't exist."""
        g = FederatedGraph()
        
        with pytest.raises(NodeNotFoundError):
            g.remove_node("pkg:frctl/nonexistent@local")


class TestGraphEdges:
    """Test graph edge operations."""
    
    def test_add_edge(self):
        """Test adding an edge between nodes."""
        g = FederatedGraph()
        node_a = Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a")
        node_b = Node(id="pkg:frctl/b@local", type=NodeType.SERVICE, name="b")
        g.add_node(node_a)
        g.add_node(node_b)
        
        edge = Edge(
            source="pkg:frctl/a@local",
            target="pkg:frctl/b@local",
            edge_type=EdgeType.DEPENDS_ON
        )
        g.add_edge(edge)
        
        assert g.edge_count() == 1
        retrieved_edge = g.get_edge("pkg:frctl/a@local", "pkg:frctl/b@local")
        assert retrieved_edge == edge
    
    def test_reject_edge_with_missing_source(self):
        """Test that edges with missing source nodes are rejected."""
        g = FederatedGraph()
        node_b = Node(id="pkg:frctl/b@local", type=NodeType.SERVICE, name="b")
        g.add_node(node_b)
        
        edge = Edge(
            source="pkg:frctl/a@local",
            target="pkg:frctl/b@local",
            edge_type=EdgeType.DEPENDS_ON
        )
        
        with pytest.raises(NodeNotFoundError, match="Source node.*not found"):
            g.add_edge(edge)
    
    def test_reject_edge_with_missing_target(self):
        """Test that edges with missing target nodes are rejected."""
        g = FederatedGraph()
        node_a = Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a")
        g.add_node(node_a)
        
        edge = Edge(
            source="pkg:frctl/a@local",
            target="pkg:frctl/b@local",
            edge_type=EdgeType.DEPENDS_ON
        )
        
        with pytest.raises(NodeNotFoundError, match="Target node.*not found"):
            g.add_edge(edge)
    
    def test_remove_edge(self):
        """Test removing an edge."""
        g = FederatedGraph()
        node_a = Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a")
        node_b = Node(id="pkg:frctl/b@local", type=NodeType.SERVICE, name="b")
        edge = Edge(
            source="pkg:frctl/a@local",
            target="pkg:frctl/b@local",
            edge_type=EdgeType.DEPENDS_ON
        )
        
        g.add_node(node_a)
        g.add_node(node_b)
        g.add_edge(edge)
        
        g.remove_edge("pkg:frctl/a@local", "pkg:frctl/b@local")
        
        assert g.edge_count() == 0
    
    def test_remove_node_cascades_edges(self):
        """Test that removing a node also removes connected edges."""
        g = FederatedGraph()
        node_a = Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a")
        node_b = Node(id="pkg:frctl/b@local", type=NodeType.SERVICE, name="b")
        node_c = Node(id="pkg:frctl/c@local", type=NodeType.SERVICE, name="c")
        
        g.add_node(node_a)
        g.add_node(node_b)
        g.add_node(node_c)
        
        # A -> B -> C
        g.add_edge(Edge(source="pkg:frctl/a@local", target="pkg:frctl/b@local", edge_type=EdgeType.DEPENDS_ON))
        g.add_edge(Edge(source="pkg:frctl/b@local", target="pkg:frctl/c@local", edge_type=EdgeType.DEPENDS_ON))
        
        # Remove B - should remove both edges
        g.remove_node("pkg:frctl/b@local")
        
        assert g.node_count() == 2
        assert g.edge_count() == 0


class TestCycleDetection:
    """Test cycle detection in the DAG."""
    
    def test_detect_simple_cycle(self):
        """Test detection of a simple 2-node cycle."""
        g = FederatedGraph()
        node_a = Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a")
        node_b = Node(id="pkg:frctl/b@local", type=NodeType.SERVICE, name="b")
        
        g.add_node(node_a)
        g.add_node(node_b)
        
        # Add A -> B
        g.add_edge(Edge(source="pkg:frctl/a@local", target="pkg:frctl/b@local", edge_type=EdgeType.DEPENDS_ON))
        
        # Try to add B -> A (creates cycle)
        with pytest.raises(CycleDetectedError, match="would create a cycle"):
            g.add_edge(Edge(source="pkg:frctl/b@local", target="pkg:frctl/a@local", edge_type=EdgeType.DEPENDS_ON))
    
    def test_detect_three_node_cycle(self):
        """Test detection of a 3-node cycle."""
        g = FederatedGraph()
        node_a = Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a")
        node_b = Node(id="pkg:frctl/b@local", type=NodeType.SERVICE, name="b")
        node_c = Node(id="pkg:frctl/c@local", type=NodeType.SERVICE, name="c")
        
        g.add_node(node_a)
        g.add_node(node_b)
        g.add_node(node_c)
        
        # A -> B -> C
        g.add_edge(Edge(source="pkg:frctl/a@local", target="pkg:frctl/b@local", edge_type=EdgeType.DEPENDS_ON))
        g.add_edge(Edge(source="pkg:frctl/b@local", target="pkg:frctl/c@local", edge_type=EdgeType.DEPENDS_ON))
        
        # Try to add C -> A (creates cycle)
        with pytest.raises(CycleDetectedError, match="would create a cycle"):
            g.add_edge(Edge(source="pkg:frctl/c@local", target="pkg:frctl/a@local", edge_type=EdgeType.DEPENDS_ON))
    
    def test_allow_diamond_structure(self):
        """Test that diamond structures (non-cycles) are allowed."""
        g = FederatedGraph()
        node_a = Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a")
        node_b = Node(id="pkg:frctl/b@local", type=NodeType.SERVICE, name="b")
        node_c = Node(id="pkg:frctl/c@local", type=NodeType.SERVICE, name="c")
        node_d = Node(id="pkg:frctl/d@local", type=NodeType.SERVICE, name="d")
        
        g.add_node(node_a)
        g.add_node(node_b)
        g.add_node(node_c)
        g.add_node(node_d)
        
        # Diamond: A -> B -> D, A -> C -> D
        g.add_edge(Edge(source="pkg:frctl/a@local", target="pkg:frctl/b@local", edge_type=EdgeType.DEPENDS_ON))
        g.add_edge(Edge(source="pkg:frctl/a@local", target="pkg:frctl/c@local", edge_type=EdgeType.DEPENDS_ON))
        g.add_edge(Edge(source="pkg:frctl/b@local", target="pkg:frctl/d@local", edge_type=EdgeType.DEPENDS_ON))
        g.add_edge(Edge(source="pkg:frctl/c@local", target="pkg:frctl/d@local", edge_type=EdgeType.DEPENDS_ON))
        
        # Should succeed - no cycle
        assert g.edge_count() == 4


class TestTopologicalSort:
    """Test topological sorting."""
    
    def test_topological_sort_linear(self):
        """Test topological sort on a linear graph."""
        g = FederatedGraph()
        node_a = Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a")
        node_b = Node(id="pkg:frctl/b@local", type=NodeType.SERVICE, name="b")
        node_c = Node(id="pkg:frctl/c@local", type=NodeType.SERVICE, name="c")
        
        g.add_node(node_a)
        g.add_node(node_b)
        g.add_node(node_c)
        
        # A -> B -> C
        g.add_edge(Edge(source="pkg:frctl/a@local", target="pkg:frctl/b@local", edge_type=EdgeType.DEPENDS_ON))
        g.add_edge(Edge(source="pkg:frctl/b@local", target="pkg:frctl/c@local", edge_type=EdgeType.DEPENDS_ON))
        
        sorted_nodes = g.topological_sort()
        
        # A should come before B, B before C
        assert sorted_nodes.index("pkg:frctl/a@local") < sorted_nodes.index("pkg:frctl/b@local")
        assert sorted_nodes.index("pkg:frctl/b@local") < sorted_nodes.index("pkg:frctl/c@local")
    
    def test_topological_sort_diamond(self):
        """Test topological sort on a diamond graph."""
        g = FederatedGraph()
        for name in ["a", "b", "c", "d"]:
            g.add_node(Node(id=f"pkg:frctl/{name}@local", type=NodeType.SERVICE, name=name))
        
        # Diamond: A -> B -> D, A -> C -> D
        g.add_edge(Edge(source="pkg:frctl/a@local", target="pkg:frctl/b@local", edge_type=EdgeType.DEPENDS_ON))
        g.add_edge(Edge(source="pkg:frctl/a@local", target="pkg:frctl/c@local", edge_type=EdgeType.DEPENDS_ON))
        g.add_edge(Edge(source="pkg:frctl/b@local", target="pkg:frctl/d@local", edge_type=EdgeType.DEPENDS_ON))
        g.add_edge(Edge(source="pkg:frctl/c@local", target="pkg:frctl/d@local", edge_type=EdgeType.DEPENDS_ON))
        
        sorted_nodes = g.topological_sort()
        
        # A before B and C, B and C before D
        a_idx = sorted_nodes.index("pkg:frctl/a@local")
        b_idx = sorted_nodes.index("pkg:frctl/b@local")
        c_idx = sorted_nodes.index("pkg:frctl/c@local")
        d_idx = sorted_nodes.index("pkg:frctl/d@local")
        
        assert a_idx < b_idx
        assert a_idx < c_idx
        assert b_idx < d_idx
        assert c_idx < d_idx
    
    def test_topological_sort_empty_graph(self):
        """Test topological sort on an empty graph."""
        g = FederatedGraph()
        
        sorted_nodes = g.topological_sort()
        
        assert sorted_nodes == []


class TestGraphTraversal:
    """Test graph traversal operations."""
    
    def test_get_ancestors(self):
        """Test getting ancestor nodes."""
        g = FederatedGraph()
        for name in ["a", "b", "c"]:
            g.add_node(Node(id=f"pkg:frctl/{name}@local", type=NodeType.SERVICE, name=name))
        
        # A -> B -> C
        g.add_edge(Edge(source="pkg:frctl/a@local", target="pkg:frctl/b@local", edge_type=EdgeType.DEPENDS_ON))
        g.add_edge(Edge(source="pkg:frctl/b@local", target="pkg:frctl/c@local", edge_type=EdgeType.DEPENDS_ON))
        
        ancestors = g.get_ancestors("pkg:frctl/c@local")
        
        assert set(ancestors) == {"pkg:frctl/a@local", "pkg:frctl/b@local"}
        # Should be in dependency order: A before B
        assert ancestors.index("pkg:frctl/a@local") < ancestors.index("pkg:frctl/b@local")
    
    def test_get_descendants(self):
        """Test getting descendant nodes."""
        g = FederatedGraph()
        for name in ["a", "b", "c"]:
            g.add_node(Node(id=f"pkg:frctl/{name}@local", type=NodeType.SERVICE, name=name))
        
        # A -> B -> C
        g.add_edge(Edge(source="pkg:frctl/a@local", target="pkg:frctl/b@local", edge_type=EdgeType.DEPENDS_ON))
        g.add_edge(Edge(source="pkg:frctl/b@local", target="pkg:frctl/c@local", edge_type=EdgeType.DEPENDS_ON))
        
        descendants = g.get_descendants("pkg:frctl/a@local")
        
        assert set(descendants) == {"pkg:frctl/b@local", "pkg:frctl/c@local"}
    
    def test_get_ancestors_nonexistent_node(self):
        """Test getting ancestors of a nonexistent node."""
        g = FederatedGraph()
        
        with pytest.raises(NodeNotFoundError):
            g.get_ancestors("pkg:frctl/nonexistent@local")
    
    def test_get_descendants_nonexistent_node(self):
        """Test getting descendants of a nonexistent node."""
        g = FederatedGraph()
        
        with pytest.raises(NodeNotFoundError):
            g.get_descendants("pkg:frctl/nonexistent@local")
    
    def test_extract_subgraph(self):
        """Test extracting a subgraph."""
        g = FederatedGraph()
        for name in ["a", "b", "c", "d"]:
            g.add_node(Node(id=f"pkg:frctl/{name}@local", type=NodeType.SERVICE, name=name))
        
        # A -> B -> C, D disconnected
        g.add_edge(Edge(source="pkg:frctl/a@local", target="pkg:frctl/b@local", edge_type=EdgeType.DEPENDS_ON))
        g.add_edge(Edge(source="pkg:frctl/b@local", target="pkg:frctl/c@local", edge_type=EdgeType.DEPENDS_ON))
        
        # Extract subgraph with B and C
        subgraph = g.extract_subgraph(["pkg:frctl/b@local", "pkg:frctl/c@local"])
        
        assert subgraph.node_count() == 2
        assert subgraph.edge_count() == 1
        assert subgraph.get_node("pkg:frctl/b@local") is not None
        assert subgraph.get_node("pkg:frctl/c@local") is not None
        assert subgraph.get_edge("pkg:frctl/b@local", "pkg:frctl/c@local") is not None
    
    def test_extract_subgraph_nonexistent_node(self):
        """Test extracting subgraph with nonexistent node."""
        g = FederatedGraph()
        
        with pytest.raises(NodeNotFoundError):
            g.extract_subgraph(["pkg:frctl/nonexistent@local"])


class TestGraphValidation:
    """Test graph validation."""
    
    def test_validate_empty_graph(self):
        """Test validating an empty graph."""
        g = FederatedGraph()
        
        errors = g.validate()
        
        assert errors == []
    
    def test_validate_valid_graph(self):
        """Test validating a valid graph."""
        g = FederatedGraph()
        node_a = Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a")
        node_b = Node(id="pkg:frctl/b@local", type=NodeType.SERVICE, name="b")
        
        g.add_node(node_a)
        g.add_node(node_b)
        g.add_edge(Edge(source="pkg:frctl/a@local", target="pkg:frctl/b@local", edge_type=EdgeType.DEPENDS_ON))
        
        errors = g.validate()
        
        assert errors == []


class TestGraphStatistics:
    """Test graph statistics."""
    
    def test_node_count(self):
        """Test counting nodes."""
        g = FederatedGraph()
        
        assert g.node_count() == 0
        
        g.add_node(Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a"))
        assert g.node_count() == 1
        
        g.add_node(Node(id="pkg:frctl/b@local", type=NodeType.SERVICE, name="b"))
        assert g.node_count() == 2
    
    def test_edge_count(self):
        """Test counting edges."""
        g = FederatedGraph()
        node_a = Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a")
        node_b = Node(id="pkg:frctl/b@local", type=NodeType.SERVICE, name="b")
        
        g.add_node(node_a)
        g.add_node(node_b)
        
        assert g.edge_count() == 0
        
        g.add_edge(Edge(source="pkg:frctl/a@local", target="pkg:frctl/b@local", edge_type=EdgeType.DEPENDS_ON))
        assert g.edge_count() == 1
    
    def test_depth_linear_graph(self):
        """Test depth calculation on a linear graph."""
        g = FederatedGraph()
        for name in ["a", "b", "c"]:
            g.add_node(Node(id=f"pkg:frctl/{name}@local", type=NodeType.SERVICE, name=name))
        
        # A -> B -> C (depth 2)
        g.add_edge(Edge(source="pkg:frctl/a@local", target="pkg:frctl/b@local", edge_type=EdgeType.DEPENDS_ON))
        g.add_edge(Edge(source="pkg:frctl/b@local", target="pkg:frctl/c@local", edge_type=EdgeType.DEPENDS_ON))
        
        assert g.depth() == 2
    
    def test_depth_empty_graph(self):
        """Test depth of an empty graph."""
        g = FederatedGraph()
        
        assert g.depth() == 0


class TestPURLGeneration:
    """Test PURL identifier generation."""
    
    def test_generate_simple_purl(self):
        """Test generating a simple PURL."""
        purl = generate_purl("api-gateway")
        
        assert purl == "pkg:frctl/api-gateway@local"
    
    def test_sanitize_spaces(self):
        """Test that spaces are converted to hyphens."""
        purl = generate_purl("my service")
        
        assert purl == "pkg:frctl/my-service@local"
    
    def test_sanitize_underscores(self):
        """Test that underscores are converted to hyphens."""
        purl = generate_purl("my_service")
        
        assert purl == "pkg:frctl/my-service@local"
    
    def test_lowercase_conversion(self):
        """Test that names are converted to lowercase."""
        purl = generate_purl("MyService")
        
        assert purl == "pkg:frctl/myservice@local"
