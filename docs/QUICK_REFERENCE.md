# Frctl Quick Reference

## Configuration Commands

### Setup
```bash
# Initialize configuration (project-level)
frctl config init

# Initialize global configuration (user-level)
frctl config init --global

# Overwrite existing config
frctl config init --force
```

### View & Validate
```bash
# Show current configuration
frctl config show

# Show all config sources
frctl config show --all

# Validate configuration
frctl config validate

# Test LLM provider connection
frctl config test

# Test with specific model
frctl config test --model claude-3-5-sonnet-20241022
```

### Environment Variables
```bash
# LLM Settings
export FRCTL_LLM_MODEL=gpt-4
export FRCTL_LLM_TEMPERATURE=0.7
export FRCTL_LLM_MAX_TOKENS=2000

# API Keys
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GEMINI_API_KEY=...

# Planning Settings
export FRCTL_PLANNING_MAX_DEPTH=10
export FRCTL_PLANNING_AUTO_DECOMPOSE=false
```

## Planning Commands

### Start Planning
```bash
# Initialize a new plan
frctl plan init "Build a microservices architecture"

# Continue planning session
frctl plan continue <plan-id>
```

### View Plans
```bash
# List all plans
frctl plan list

# Show plan status
frctl plan status <plan-id>

# Review specific goal
frctl plan review <goal-id>

# Visualize plan tree (ASCII)
frctl plan visualize <plan-id>

# Visualize as Mermaid diagram
frctl plan visualize <plan-id> --format mermaid
```

### Export & Delete
```bash
# Export plan to JSON
frctl plan export <plan-id>
frctl plan export <plan-id> output.json

# Delete plan (with archive)
frctl plan delete <plan-id>

# Delete without archive
frctl plan delete <plan-id> --no-archive

# Force delete (no confirmation)
frctl plan delete <plan-id> --force
```

## Graph Commands

### Initialize
```bash
frctl graph init
```

### Add Nodes
```bash
frctl graph add-node Service api-gateway
frctl graph add-node Library auth-utils
frctl graph add-node Schema user-schema
frctl graph add-node Endpoint /api/users
frctl graph add-node Component cache-layer
```

### Add Edges
```bash
# Dependency
frctl graph add-edge pkg:frctl/api-gateway@local pkg:frctl/auth-utils@local --type DEPENDS_ON

# Consumption
frctl graph add-edge pkg:frctl/service@local pkg:frctl/events@local --type CONSUMES

# Ownership
frctl graph add-edge pkg:frctl/service@local pkg:frctl/endpoint@local --type OWNS

# Implementation
frctl graph add-edge pkg:frctl/service@local pkg:frctl/schema@local --type IMPLEMENTS
```

### View & Validate
```bash
frctl graph show      # Display graph structure
frctl graph stats     # Show statistics
frctl graph validate  # Validate integrity
frctl graph export    # Export to JSON
```

### Remove
```bash
frctl graph remove-node pkg:frctl/node-id@local
frctl graph remove-edge pkg:frctl/source@local pkg:frctl/target@local
```

## Python API

### Create Graph
```python
from frctl.graph import FederatedGraph, Node, NodeType, Edge, EdgeType
from frctl.graph.dag import generate_purl
from pathlib import Path

g = FederatedGraph()
```

### Add Nodes
```python
node = Node(
    id=generate_purl("api-gateway"),
    type=NodeType.SERVICE,
    name="api-gateway",
    metadata={"version": "1.0", "team": "platform"}
)
g.add_node(node)
```

### Add Edges
```python
edge = Edge(
    source=generate_purl("api-gateway"),
    target=generate_purl("auth-utils"),
    edge_type=EdgeType.DEPENDS_ON,
    metadata={"required": True}
)
g.add_edge(edge)
```

### Query Graph
```python
# Get ancestors (dependencies)
ancestors = g.get_ancestors("pkg:frctl/api-gateway@local")

# Get descendants (dependents)
descendants = g.get_descendants("pkg:frctl/auth-utils@local")

# Topological sort (build order)
sorted_nodes = g.topological_sort()

# Extract subgraph
subgraph = g.extract_subgraph(["pkg:frctl/a@local", "pkg:frctl/b@local"])
```

### Persistence
```python
# Save
g.save(Path(".frctl/graph.json"))

# Load
g = FederatedGraph.load(Path(".frctl/graph.json"))

# Get fingerprint
hash = g.merkle_hash()
```

## Node Types

| Type | Purpose | Example |
|------|---------|---------|
| Service | Deployable service/app | `api-gateway`, `payment-service` |
| Library | Shared code library | `auth-utils`, `logging-lib` |
| Schema | Data/API contract | `user-schema`, `order-events` |
| Endpoint | API endpoint | `/api/users`, `UserService.get` |
| Component | Logical component | `cache-layer`, `event-bus` |

## Edge Types

| Type | Meaning | Example |
|------|---------|---------|
| DEPENDS_ON | Runtime dependency | `api-gateway` depends on `auth-utils` |
| CONSUMES | Data/event consumption | `service` consumes `events` |
| OWNS | Ownership/responsibility | `service` owns `endpoint` |
| IMPLEMENTS | Contract implementation | `service` implements `schema` |

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=frctl --cov-report=html

# Run only fast tests
pytest -m "not slow"

# Run specific test file
pytest tests/graph/test_dag.py
```

## Documentation

- [Graph Basics Guide](docs/guides/graph-basics.md)
- [JSON Schema](docs/schemas/graph-json.md)
- [Microservices Example](docs/examples/microservices_example.py)
- [Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)
