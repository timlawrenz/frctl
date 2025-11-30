"""Performance tests for large graphs."""

import pytest
import time

from frctl.graph import FederatedGraph, Node, NodeType, Edge, EdgeType


@pytest.mark.slow
class TestPerformance:
    """Test performance with large graphs."""
    
    def test_1000_node_graph_creation(self):
        """Test creating a graph with 1000 nodes."""
        g = FederatedGraph()
        
        start = time.time()
        
        # Add 1000 nodes
        for i in range(1000):
            g.add_node(Node(
                id=f"pkg:frctl/node-{i}@local",
                type=NodeType.SERVICE,
                name=f"node-{i}"
            ))
        
        elapsed = time.time() - start
        
        assert g.node_count() == 1000
        assert elapsed < 1.0, f"Creating 1000 nodes took {elapsed:.2f}s (should be < 1s)"
    
    def test_1000_node_linear_graph_operations(self):
        """Test operations on a 1000-node linear graph."""
        g = FederatedGraph()
        
        # Create linear graph: 0 -> 1 -> 2 -> ... -> 999
        for i in range(1000):
            g.add_node(Node(
                id=f"pkg:frctl/node-{i}@local",
                type=NodeType.SERVICE,
                name=f"node-{i}"
            ))
        
        for i in range(999):
            g.add_edge(Edge(
                source=f"pkg:frctl/node-{i}@local",
                target=f"pkg:frctl/node-{i+1}@local",
                edge_type=EdgeType.DEPENDS_ON
            ))
        
        # Test topological sort performance
        start = time.time()
        sorted_nodes = g.topological_sort()
        topo_time = time.time() - start
        
        assert len(sorted_nodes) == 1000
        assert topo_time < 1.0, f"Topological sort took {topo_time:.2f}s (should be < 1s)"
        
        # Test cycle detection performance (should be fast since graph is valid)
        start = time.time()
        errors = g.validate()
        validate_time = time.time() - start
        
        assert errors == []
        assert validate_time < 1.0, f"Validation took {validate_time:.2f}s (should be < 1s)"
    
    def test_serialization_performance(self):
        """Test serialization performance on a large graph."""
        g = FederatedGraph()
        
        # Create a graph with 1000 nodes and ~2000 edges (2 per node on average)
        for i in range(1000):
            g.add_node(Node(
                id=f"pkg:frctl/node-{i}@local",
                type=NodeType.SERVICE,
                name=f"node-{i}"
            ))
        
        # Create edges in a tree-like structure
        for i in range(1, 1000):
            parent = (i - 1) // 2
            g.add_edge(Edge(
                source=f"pkg:frctl/node-{parent}@local",
                target=f"pkg:frctl/node-{i}@local",
                edge_type=EdgeType.DEPENDS_ON
            ))
        
        # Test serialization
        start = time.time()
        data = g.to_dict()
        serialize_time = time.time() - start
        
        assert serialize_time < 2.0, f"Serialization took {serialize_time:.2f}s (should be < 2s)"
        
        # Test deserialization
        start = time.time()
        g2 = FederatedGraph.from_dict(data)
        deserialize_time = time.time() - start
        
        assert deserialize_time < 2.0, f"Deserialization took {deserialize_time:.2f}s (should be < 2s)"
        assert g2.node_count() == 1000
    
    def test_merkle_hash_performance(self):
        """Test Merkle hash performance on a large graph."""
        g = FederatedGraph()
        
        for i in range(1000):
            g.add_node(Node(
                id=f"pkg:frctl/node-{i}@local",
                type=NodeType.SERVICE,
                name=f"node-{i}"
            ))
        
        start = time.time()
        hash1 = g.merkle_hash()
        hash_time = time.time() - start
        
        assert len(hash1) == 64
        assert hash_time < 2.0, f"Merkle hash took {hash_time:.2f}s (should be < 2s)"
    
    def test_ancestor_query_performance(self):
        """Test ancestor query performance on a deep graph."""
        g = FederatedGraph()
        
        # Create a linear graph of depth 100
        for i in range(100):
            g.add_node(Node(
                id=f"pkg:frctl/node-{i}@local",
                type=NodeType.SERVICE,
                name=f"node-{i}"
            ))
        
        for i in range(99):
            g.add_edge(Edge(
                source=f"pkg:frctl/node-{i}@local",
                target=f"pkg:frctl/node-{i+1}@local",
                edge_type=EdgeType.DEPENDS_ON
            ))
        
        # Query ancestors of the last node
        start = time.time()
        ancestors = g.get_ancestors("pkg:frctl/node-99@local")
        query_time = time.time() - start
        
        assert len(ancestors) == 99
        assert query_time < 0.5, f"Ancestor query took {query_time:.2f}s (should be < 0.5s)"
    
    def test_subgraph_extraction_performance(self):
        """Test subgraph extraction performance."""
        g = FederatedGraph()
        
        # Create a graph with 1000 nodes
        for i in range(1000):
            g.add_node(Node(
                id=f"pkg:frctl/node-{i}@local",
                type=NodeType.SERVICE,
                name=f"node-{i}"
            ))
        
        # Add some edges
        for i in range(100):
            g.add_edge(Edge(
                source=f"pkg:frctl/node-{i}@local",
                target=f"pkg:frctl/node-{i+1}@local",
                edge_type=EdgeType.DEPENDS_ON
            ))
        
        # Extract subgraph with 100 nodes
        node_ids = [f"pkg:frctl/node-{i}@local" for i in range(100)]
        
        start = time.time()
        subgraph = g.extract_subgraph(node_ids)
        extract_time = time.time() - start
        
        assert subgraph.node_count() == 100
        assert extract_time < 0.5, f"Subgraph extraction took {extract_time:.2f}s (should be < 0.5s)"


@pytest.mark.slow
class TestMemoryEfficiency:
    """Test memory usage with large graphs."""
    
    def test_memory_usage_1000_nodes(self):
        """Test that a 1000-node graph uses reasonable memory."""
        import sys
        
        g = FederatedGraph()
        
        # Add 1000 nodes
        for i in range(1000):
            g.add_node(Node(
                id=f"pkg:frctl/node-{i}@local",
                type=NodeType.SERVICE,
                name=f"node-{i}",
                metadata={"index": i, "description": f"Node {i}"}
            ))
        
        # Rough memory estimate (very approximate)
        size = sys.getsizeof(g.model_dump())
        
        # Should be much less than 500MB (spec requirement)
        assert size < 500 * 1024 * 1024, f"Graph size {size} bytes exceeds 500MB limit"
