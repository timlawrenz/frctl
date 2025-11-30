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

### 🔨 ReCAP Planning Engine (Phase 2 - In Progress)

**Status**: 47% complete (59/126 tasks)

Hierarchical goal decomposition with:
- ✅ **Context Tree** - Hierarchical context management with token hygiene
- ✅ **Plan Persistence** - Automatic save/load to `.frctl/plans/`
- ✅ **LLM Integration** - Support for 100+ providers via LiteLLM
- ✅ **Atomicity Detection** - LLM-based assessment of task decomposability
- 🚧 **Digest Protocol** - Context compression (coming soon)
- 🚧 **Prompt Templates** - Jinja2 templating (coming soon)

**Usage**:
```python
from frctl.planning import PlanningEngine

# Create planning engine with auto-save
engine = PlanningEngine()

# Run recursive planning
plan = engine.run("Build a microservices authentication system")

# Plans auto-save to .frctl/plans/
# Load existing plan
loaded = engine.load_plan(plan.id)

# List all plans
plans = engine.list_plans()
```

See [Context Tree Guide](./docs/guides/context-tree.md) for details on hierarchical context management.

### 🚧 Coming Soon

- **Tandem Protocol** - Human-in-the-loop workflow (Phase 3)
- **Policy Gates** - Validation rules and constraints (Phase 3)
- **Drift Detection** - Architecture reconciliation (Phase 4)

## Documentation

- **Guides**
  - [Graph Basics](./docs/guides/graph-basics.md) - Introduction and tutorial
  - [Context Tree](./docs/guides/context-tree.md) - Hierarchical context management
- **Schemas**
  - [Graph JSON Format](./docs/schemas/graph-json.md) - Serialization format
- **Examples**
  - [Microservices Architecture](./docs/examples/microservices_example.py) - Complete example
- **Architecture**
  - [Fractal V3 Specification](./docs/fractal-v3-architecture.md) - Complete technical specification
  - [Implementation Roadmap](./docs/roadmap.md) - Development plan
- **Implementation Notes**
  - [Plan Persistence](./PERSISTENCE_COMPLETE.md) - Plan storage implementation details

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=frctl --cov-report=html

# Run only fast tests (skip performance tests)
pytest -m "not slow"
```

**Test Coverage**: 141 tests covering:
- **Graph** (85 tests): Node validation, edge validation, DAG operations, cycle detection, serialization, performance
- **Planning** (38 tests): Goal models, context tree, plan persistence, engine integration
- **Context** (18 tests): Hierarchical context, token tracking, hydration/dehydration

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

# Planning commands (Phase 2 - In Progress)
frctl plan init <description>  # Start planning session (saves to .frctl/plans/)
# Coming soon:
# frctl plan list              # List all plans
# frctl plan status [plan-id]  # Show planning tree
# frctl plan continue <plan-id> # Resume planning
# frctl plan export <plan-id>  # Export plan
# frctl plan delete <plan-id>  # Delete plan
```

## Project Status

**Phase 1 Complete** ✅ - Federated Graph implementation (v0.1.0)
- Full DAG-based dependency management
- 85 tests, 100% pass rate
- Complete CLI and documentation

**Phase 2 In Progress** 🔨 - ReCAP Planning Engine (47% complete)
- ✅ Context Tree with hierarchical context management
- ✅ Plan Persistence with automatic save/load
- ✅ LLM integration supporting 100+ providers
- ✅ 56 tests for planning and context
- 🚧 Digest Protocol, Prompt Templates, expanded CLI coming soon

**Overall Progress**: ~55% complete

## License

TBD
