"""Unit tests for graph serialization."""

import pytest
import json
import tempfile
from pathlib import Path

from frctl.graph import FederatedGraph, Node, NodeType, Edge, EdgeType


class TestSerialization:
    """Test graph serialization and deserialization."""
    
    def test_to_dict_empty_graph(self):
        """Test serializing an empty graph to dict."""
        g = FederatedGraph()
        
        data = g.to_dict()
        
        assert data == {
            "metadata": {},
            "nodes": {},
            "edges": []
        }
    
    def test_to_dict_with_nodes(self):
        """Test serializing a graph with nodes."""
        g = FederatedGraph()
        g.add_node(Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a"))
        g.add_node(Node(id="pkg:frctl/b@local", type=NodeType.LIBRARY, name="b"))
        
        data = g.to_dict()
        
        assert "pkg:frctl/a@local" in data["nodes"]
        assert "pkg:frctl/b@local" in data["nodes"]
        assert data["nodes"]["pkg:frctl/a@local"]["type"] == "Service"
        assert data["nodes"]["pkg:frctl/b@local"]["type"] == "Library"
    
    def test_to_dict_with_edges(self):
        """Test serializing a graph with edges."""
        g = FederatedGraph()
        node_a = Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a")
        node_b = Node(id="pkg:frctl/b@local", type=NodeType.SERVICE, name="b")
        g.add_node(node_a)
        g.add_node(node_b)
        g.add_edge(Edge(
            source="pkg:frctl/a@local",
            target="pkg:frctl/b@local",
            edge_type=EdgeType.DEPENDS_ON
        ))
        
        data = g.to_dict()
        
        assert len(data["edges"]) == 1
        assert data["edges"][0]["source"] == "pkg:frctl/a@local"
        assert data["edges"][0]["target"] == "pkg:frctl/b@local"
        assert data["edges"][0]["edge_type"] == "DEPENDS_ON"
    
    def test_from_dict_empty_graph(self):
        """Test deserializing an empty graph."""
        data = {
            "metadata": {},
            "nodes": {},
            "edges": []
        }
        
        g = FederatedGraph.from_dict(data)
        
        assert g.node_count() == 0
        assert g.edge_count() == 0
    
    def test_from_dict_with_nodes(self):
        """Test deserializing a graph with nodes."""
        data = {
            "metadata": {},
            "nodes": {
                "pkg:frctl/a@local": {
                    "id": "pkg:frctl/a@local",
                    "type": "Service",
                    "name": "a",
                    "metadata": {}
                }
            },
            "edges": []
        }
        
        g = FederatedGraph.from_dict(data)
        
        assert g.node_count() == 1
        node = g.get_node("pkg:frctl/a@local")
        assert node is not None
        assert node.type == NodeType.SERVICE
        assert node.name == "a"
    
    def test_from_dict_with_edges(self):
        """Test deserializing a graph with edges."""
        data = {
            "metadata": {},
            "nodes": {
                "pkg:frctl/a@local": {
                    "id": "pkg:frctl/a@local",
                    "type": "Service",
                    "name": "a",
                    "metadata": {}
                },
                "pkg:frctl/b@local": {
                    "id": "pkg:frctl/b@local",
                    "type": "Service",
                    "name": "b",
                    "metadata": {}
                }
            },
            "edges": [
                {
                    "source": "pkg:frctl/a@local",
                    "target": "pkg:frctl/b@local",
                    "edge_type": "DEPENDS_ON",
                    "metadata": {},
                    "contract": None
                }
            ]
        }
        
        g = FederatedGraph.from_dict(data)
        
        assert g.edge_count() == 1
        edge = g.get_edge("pkg:frctl/a@local", "pkg:frctl/b@local")
        assert edge is not None
        assert edge.edge_type == EdgeType.DEPENDS_ON
    
    def test_roundtrip_serialization(self):
        """Test that to_dict/from_dict is lossless."""
        g1 = FederatedGraph()
        g1.metadata["version"] = "1.0"
        
        # Add nodes
        for name in ["a", "b", "c"]:
            g1.add_node(Node(
                id=f"pkg:frctl/{name}@local",
                type=NodeType.SERVICE,
                name=name,
                metadata={"version": "1.0"}
            ))
        
        # Add edges
        g1.add_edge(Edge(
            source="pkg:frctl/a@local",
            target="pkg:frctl/b@local",
            edge_type=EdgeType.DEPENDS_ON,
            metadata={"weight": 1}
        ))
        
        # Serialize and deserialize
        data = g1.to_dict()
        g2 = FederatedGraph.from_dict(data)
        
        assert g2.node_count() == g1.node_count()
        assert g2.edge_count() == g1.edge_count()
        assert g2.metadata == g1.metadata
        
        # Check nodes are identical
        for node_id in g1.nodes.keys():
            assert g2.get_node(node_id) == g1.get_node(node_id)


class TestMerkleHash:
    """Test Merkle hash generation."""
    
    def test_merkle_hash_deterministic(self):
        """Test that Merkle hash is deterministic."""
        g = FederatedGraph()
        g.add_node(Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a"))
        
        hash1 = g.merkle_hash()
        hash2 = g.merkle_hash()
        
        assert hash1 == hash2
    
    def test_merkle_hash_different_for_changes(self):
        """Test that Merkle hash changes when graph changes."""
        g = FederatedGraph()
        g.add_node(Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a"))
        
        hash1 = g.merkle_hash()
        
        g.add_node(Node(id="pkg:frctl/b@local", type=NodeType.SERVICE, name="b"))
        
        hash2 = g.merkle_hash()
        
        assert hash1 != hash2
    
    def test_merkle_hash_same_structure_same_hash(self):
        """Test that identical graphs produce the same hash."""
        g1 = FederatedGraph()
        g1.add_node(Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a"))
        g1.add_node(Node(id="pkg:frctl/b@local", type=NodeType.SERVICE, name="b"))
        
        g2 = FederatedGraph()
        g2.add_node(Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a"))
        g2.add_node(Node(id="pkg:frctl/b@local", type=NodeType.SERVICE, name="b"))
        
        assert g1.merkle_hash() == g2.merkle_hash()
    
    def test_merkle_hash_format(self):
        """Test that Merkle hash is a valid SHA-256 hex string."""
        g = FederatedGraph()
        
        hash_str = g.merkle_hash()
        
        assert len(hash_str) == 64  # SHA-256 produces 64 hex characters
        assert all(c in "0123456789abcdef" for c in hash_str)


class TestFilePersistence:
    """Test saving and loading graphs from files."""
    
    def test_save_empty_graph(self):
        """Test saving an empty graph to file."""
        g = FederatedGraph()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            g.save(path)
            
            assert path.exists()
            
            # Verify JSON structure
            with open(path) as f:
                data = json.load(f)
            
            assert "nodes" in data
            assert "edges" in data
            assert "metadata" in data
    
    def test_save_creates_parent_dirs(self):
        """Test that save creates parent directories."""
        g = FederatedGraph()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "path" / "graph.json"
            g.save(path)
            
            assert path.exists()
    
    def test_load_graph(self):
        """Test loading a graph from file."""
        g1 = FederatedGraph()
        g1.add_node(Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a"))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            g1.save(path)
            
            g2 = FederatedGraph.load(path)
            
            assert g2.node_count() == 1
            assert g2.get_node("pkg:frctl/a@local") is not None
    
    def test_roundtrip_file_persistence(self):
        """Test that save/load is lossless."""
        g1 = FederatedGraph()
        g1.metadata["version"] = "1.0"
        
        # Create a complex graph
        for name in ["a", "b", "c"]:
            g1.add_node(Node(
                id=f"pkg:frctl/{name}@local",
                type=NodeType.SERVICE,
                name=name,
                metadata={"env": "prod"}
            ))
        
        g1.add_edge(Edge(
            source="pkg:frctl/a@local",
            target="pkg:frctl/b@local",
            edge_type=EdgeType.DEPENDS_ON,
            contract="contracts/api.tsp"
        ))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            
            # Save and load
            g1.save(path)
            g2 = FederatedGraph.load(path)
            
            # Verify they're identical
            assert g2.to_dict() == g1.to_dict()
            assert g2.merkle_hash() == g1.merkle_hash()
    
    def test_json_keys_sorted(self):
        """Test that saved JSON has alphabetically sorted keys."""
        g = FederatedGraph()
        g.add_node(Node(id="pkg:frctl/z@local", type=NodeType.SERVICE, name="z"))
        g.add_node(Node(id="pkg:frctl/a@local", type=NodeType.SERVICE, name="a"))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            g.save(path)
            
            with open(path) as f:
                content = f.read()
            
            # Verify JSON is valid and keys are sorted
            data = json.loads(content)
            
            # Node keys should be alphabetically sorted
            node_keys = list(data["nodes"].keys())
            assert node_keys == sorted(node_keys)
