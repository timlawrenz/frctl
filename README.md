# frctl (Fractal V3)

**A Deterministic Topological Architecture for Agentic Software Engineering**

Fractal V3 solves the "Context Coherence Crisis" in AI-driven software development by replacing linear reasoning chains with a graph-based, deterministic architecture.

## Overview

Frctl implements the Fractal V3 architecture - a system that transforms AI agents from erratic code generators into disciplined architectural planners through:

- **Federated Graph Architecture** - DAG-based dependency management
- **Tandem Protocol** - Human-in-the-loop planning workflow
- **Recursive Context-Aware Planning (ReCAP)** - Hierarchical task decomposition
- **Transactional Execution** - Safe rollback and drift resolution

## Documentation

See the [docs/](./docs/) directory for complete technical specifications:

- [Fractal V3 Architecture](./docs/fractal-v3-architecture.md) - Complete technical specification

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/frctl.git
cd frctl

# Install with dev dependencies
pip install -e ".[dev]"
```

### Initialize a Graph

```bash
# Create a new architectural graph
frctl graph init

# Add some nodes
frctl graph add-node Service api-gateway
frctl graph add-node Library auth-utils
frctl graph add-node Schema user-schema

# Add relationships
frctl graph add-edge pkg:frctl/api-gateway@local pkg:frctl/auth-utils@local --type DEPENDS_ON
frctl graph add-edge pkg:frctl/api-gateway@local pkg:frctl/user-schema@local --type CONSUMES

# View the graph
frctl graph show

# Validate integrity
frctl graph validate
```

### Programmatic Usage

```python
from frctl.graph import FederatedGraph, Node, NodeType, Edge, EdgeType
from frctl.graph.dag import generate_purl
from pathlib import Path

# Create a graph
g = FederatedGraph()

# Add nodes
api = Node(
    id=generate_purl("api-gateway"),
    type=NodeType.SERVICE,
    name="api-gateway"
)
g.add_node(api)

# Add dependencies
auth = Node(
    id=generate_purl("auth-lib"),
    type=NodeType.LIBRARY,
    name="auth-lib"
)
g.add_node(auth)

g.add_edge(Edge(
    source=api.id,
    target=auth.id,
    edge_type=EdgeType.DEPENDS_ON
))

# Save to file
g.save(Path(".frctl/graph.json"))

# Query the graph
ancestors = g.get_ancestors(api.id)
sorted_nodes = g.topological_sort()
```

## Features

### ✅ Federated Graph (v0.1.0)

Complete graph data model with:
- **Node Types**: Service, Library, Schema, Endpoint, Component
- **Edge Types**: DEPENDS_ON, CONSUMES, OWNS, IMPLEMENTS
- **DAG Validation**: Automatic cycle detection and prevention
- **Deterministic Serialization**: Merkle hashing for architecture drift detection
- **Graph Operations**: Topological sort, ancestor/descendant queries, subgraph extraction
- **CLI Commands**: Full command-line interface for graph manipulation
- **TypeSpec Support**: Basic edge contract support (full validation in Phase 2)

See [Graph Basics Guide](./docs/guides/graph-basics.md) for detailed usage.

### 🚧 Coming Soon

- **ReCAP Engine** - Recursive context-aware planning (Phase 2)
- **Tandem Protocol** - Human-in-the-loop workflow (Phase 3)
- **Policy Gates** - Validation rules and constraints (Phase 3)
- **Drift Detection** - Architecture reconciliation (Phase 4)

## Documentation

- **Guides**
  - [Graph Basics](./docs/guides/graph-basics.md) - Introduction and tutorial
- **Schemas**
  - [Graph JSON Format](./docs/schemas/graph-json.md) - Serialization format
- **Examples**
  - [Microservices Architecture](./docs/examples/microservices_example.py) - Complete example
- **Architecture**
  - [Fractal V3 Specification](./docs/fractal-v3-architecture.md) - Complete technical specification
  - [Implementation Roadmap](./docs/roadmap.md) - Development plan

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=frctl --cov-report=html

# Run only fast tests (skip performance tests)
pytest -m "not slow"
```

**Test Coverage**: 85 tests covering node validation, edge validation, DAG operations, cycle detection, serialization, and performance.

## CLI Reference

```bash
# Graph commands
frctl graph init              # Initialize empty graph
frctl graph show              # Display graph structure
frctl graph add-node <type> <name>  # Add a node
frctl graph add-edge <from> <to> [--type TYPE]  # Add an edge
frctl graph remove-node <id>  # Remove a node
frctl graph remove-edge <from> <to>  # Remove an edge
frctl graph validate          # Validate DAG integrity
frctl graph export [path]     # Export as JSON
frctl graph stats             # Show statistics

# Planning commands (experimental)
frctl plan init <description> # Start planning session
```

## Project Status

**v0.1.0** - Federated Graph implementation complete with comprehensive tests and documentation.

## License

TBD
