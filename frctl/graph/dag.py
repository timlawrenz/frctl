"""Federated Graph implementation using NetworkX."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import networkx as nx
from pydantic import BaseModel, Field

from frctl.graph.node import Node, NodeType
from frctl.graph.edge import Edge, EdgeType


class CycleDetectedError(Exception):
    """Raised when a cycle would be created in the DAG."""
    pass


class NodeNotFoundError(Exception):
    """Raised when a referenced node doesn't exist."""
    pass


class FederatedGraph(BaseModel):
    """A Directed Acyclic Graph representing software architecture.
    
    The Federated Graph is the core data structure in Fractal V3,
    replacing file-centric representations with a topological model
    that enforces strict dependency management.
    """
    
    nodes: Dict[str, Node] = Field(default_factory=dict, description="Nodes indexed by ID")
    edges: List[Edge] = Field(default_factory=list, description="List of edges")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Graph-level metadata")
    
    class Config:
        arbitrary_types_allowed = True
    
    def _get_nx_graph(self) -> nx.DiGraph:
        """Build NetworkX graph from current state."""
        G = nx.DiGraph()
        
        # Add all nodes
        for node_id, node in self.nodes.items():
            G.add_node(node_id, **node.model_dump())
        
        # Add all edges
        for edge in self.edges:
            G.add_edge(edge.source, edge.target, **edge.model_dump())
        
        return G
    
    def add_node(self, node: Node) -> None:
        """Add a node to the graph.
        
        Args:
            node: The node to add
            
        Raises:
            ValueError: If node with same ID already exists
        """
        if node.id in self.nodes:
            raise ValueError(f"Node with ID '{node.id}' already exists")
        
        self.nodes[node.id] = node
    
    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph.
        
        Args:
            edge: The edge to add
            
        Raises:
            NodeNotFoundError: If source or target node doesn't exist
            CycleDetectedError: If adding this edge would create a cycle
        """
        # Validate nodes exist
        if edge.source not in self.nodes:
            raise NodeNotFoundError(f"Source node '{edge.source}' not found")
        if edge.target not in self.nodes:
            raise NodeNotFoundError(f"Target node '{edge.target}' not found")
        
        # Check for cycles
        temp_edges = self.edges + [edge]
        G = nx.DiGraph()
        for e in temp_edges:
            G.add_edge(e.source, e.target)
        
        if not nx.is_directed_acyclic_graph(G):
            raise CycleDetectedError(
                f"Adding edge {edge.source} -> {edge.target} would create a cycle"
            )
        
        self.edges.append(edge)
    
    def remove_node(self, node_id: str) -> None:
        """Remove a node and all connected edges.
        
        Args:
            node_id: ID of the node to remove
            
        Raises:
            NodeNotFoundError: If node doesn't exist
        """
        if node_id not in self.nodes:
            raise NodeNotFoundError(f"Node '{node_id}' not found")
        
        # Remove the node
        del self.nodes[node_id]
        
        # Remove all edges connected to this node
        self.edges = [
            e for e in self.edges
            if e.source != node_id and e.target != node_id
        ]
    
    def remove_edge(self, source: str, target: str) -> None:
        """Remove an edge from the graph.
        
        Args:
            source: Source node ID
            target: Target node ID
        """
        self.edges = [
            e for e in self.edges
            if not (e.source == source and e.target == target)
        ]
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID.
        
        Args:
            node_id: The node ID to retrieve
            
        Returns:
            The node if found, None otherwise
        """
        return self.nodes.get(node_id)
    
    def get_edge(self, source: str, target: str) -> Optional[Edge]:
        """Get an edge by source and target.
        
        Args:
            source: Source node ID
            target: Target node ID
            
        Returns:
            The edge if found, None otherwise
        """
        for edge in self.edges:
            if edge.source == source and edge.target == target:
                return edge
        return None
    
    def topological_sort(self) -> List[str]:
        """Return nodes in topological order.
        
        Returns:
            List of node IDs in dependency order
            
        Raises:
            CycleDetectedError: If graph contains cycles
        """
        G = self._get_nx_graph()
        
        if not nx.is_directed_acyclic_graph(G):
            raise CycleDetectedError("Graph contains cycles")
        
        return list(nx.topological_sort(G))
    
    def get_ancestors(self, node_id: str) -> List[str]:
        """Get all ancestor nodes (transitive dependencies).
        
        Args:
            node_id: The node to find ancestors for
            
        Returns:
            List of ancestor node IDs in dependency order
            
        Raises:
            NodeNotFoundError: If node doesn't exist
        """
        if node_id not in self.nodes:
            raise NodeNotFoundError(f"Node '{node_id}' not found")
        
        G = self._get_nx_graph()
        ancestors = nx.ancestors(G, node_id)
        
        # Return in topological order
        subgraph = G.subgraph(ancestors)
        return list(nx.topological_sort(subgraph))
    
    def get_descendants(self, node_id: str) -> List[str]:
        """Get all descendant nodes (transitive dependents).
        
        Args:
            node_id: The node to find descendants for
            
        Returns:
            List of descendant node IDs
            
        Raises:
            NodeNotFoundError: If node doesn't exist
        """
        if node_id not in self.nodes:
            raise NodeNotFoundError(f"Node '{node_id}' not found")
        
        G = self._get_nx_graph()
        return list(nx.descendants(G, node_id))
    
    def extract_subgraph(self, node_ids: List[str]) -> "FederatedGraph":
        """Extract a subgraph containing only specified nodes.
        
        Args:
            node_ids: List of node IDs to include
            
        Returns:
            New FederatedGraph with only the specified nodes and their edges
            
        Raises:
            NodeNotFoundError: If any node ID doesn't exist
        """
        for node_id in node_ids:
            if node_id not in self.nodes:
                raise NodeNotFoundError(f"Node '{node_id}' not found")
        
        # Create new graph
        subgraph = FederatedGraph()
        
        # Add nodes
        for node_id in node_ids:
            subgraph.nodes[node_id] = self.nodes[node_id].model_copy(deep=True)
        
        # Add edges that connect nodes in the subgraph
        for edge in self.edges:
            if edge.source in node_ids and edge.target in node_ids:
                subgraph.edges.append(edge.model_copy(deep=True))
        
        return subgraph
    
    def validate(self) -> List[str]:
        """Validate graph integrity.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check for cycles
        G = self._get_nx_graph()
        if not nx.is_directed_acyclic_graph(G):
            errors.append("Graph contains cycles")
        
        # Check that all edges reference valid nodes
        for edge in self.edges:
            if edge.source not in self.nodes:
                errors.append(f"Edge references non-existent source node: {edge.source}")
            if edge.target not in self.nodes:
                errors.append(f"Edge references non-existent target node: {edge.target}")
        
        return errors
    
    def node_count(self) -> int:
        """Get the number of nodes in the graph."""
        return len(self.nodes)
    
    def edge_count(self) -> int:
        """Get the number of edges in the graph."""
        return len(self.edges)
    
    def depth(self) -> int:
        """Get the maximum depth of the graph (longest path)."""
        G = self._get_nx_graph()
        if G.number_of_nodes() == 0:
            return 0
        return nx.dag_longest_path_length(G)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary (DAG-JSON format).
        
        Returns:
            Dictionary with deterministically sorted keys
        """
        nodes_dict = {}
        for node_id in sorted(self.nodes.keys()):
            node_data = self.nodes[node_id].model_dump()
            # Convert enum to string
            node_data['type'] = node_data['type']
            nodes_dict[node_id] = node_data
        
        edges_list = []
        for edge in sorted(self.edges, key=lambda e: (e.source, e.target)):
            edge_data = edge.model_dump()
            # Convert enum to string
            edge_data['edge_type'] = edge_data['edge_type']
            edges_list.append(edge_data)
        
        return {
            "metadata": dict(sorted(self.metadata.items())),
            "nodes": nodes_dict,
            "edges": edges_list,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FederatedGraph":
        """Create graph from dictionary.
        
        Args:
            data: Dictionary in DAG-JSON format
            
        Returns:
            New FederatedGraph instance
        """
        graph = cls()
        graph.metadata = data.get("metadata", {})
        
        # Load nodes
        for node_id, node_data in data.get("nodes", {}).items():
            graph.nodes[node_id] = Node(**node_data)
        
        # Load edges
        for edge_data in data.get("edges", []):
            graph.edges.append(Edge(**edge_data))
        
        return graph
    
    def merkle_hash(self) -> str:
        """Generate Merkle hash of graph structure.
        
        Returns:
            SHA-256 hash of the deterministic JSON representation
        """
        json_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def save(self, path: Path) -> None:
        """Save graph to JSON file.
        
        Args:
            path: Path to save the graph
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, sort_keys=True)
    
    @classmethod
    def load(cls, path: Path) -> "FederatedGraph":
        """Load graph from JSON file.
        
        Args:
            path: Path to load the graph from
            
        Returns:
            Loaded FederatedGraph instance
        """
        with open(path, 'r') as f:
            data = json.load(f)
        
        return cls.from_dict(data)


def generate_purl(name: str) -> str:
    """Generate a PURL (Package URL) identifier for a node.
    
    Args:
        name: Node name
        
    Returns:
        PURL in format: pkg:frctl/<name>@local
    """
    # Sanitize name for PURL
    safe_name = name.lower().replace(" ", "-").replace("_", "-")
    return f"pkg:frctl/{safe_name}@local"
