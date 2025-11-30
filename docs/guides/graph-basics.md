# Graph Basics Guide

This guide introduces the Federated Graph - the core data structure in Fractal V3.

## Overview

The Federated Graph represents your software architecture as a Directed Acyclic Graph (DAG) where:

- **Nodes** represent architectural components (services, libraries, schemas, etc.)
- **Edges** represent relationships between components (dependencies, consumption, ownership, etc.)
- **DAG properties** ensure no circular dependencies

## Quick Start

### Initialize a Graph

```bash
# Create a new graph
frctl graph init

# This creates .frctl/graph.json
```

### Add Nodes

Nodes represent architectural components. Each node has:
- **ID**: A unique PURL identifier (automatically generated)
- **Type**: One of Service, Library, Schema, Endpoint, Component
- **Name**: Human-readable name
- **Metadata**: Optional key-value pairs

```bash
# Add a service node
frctl graph add-node Service api-gateway

# Add a library node
frctl graph add-node Library auth-utils

# Add a schema node
frctl graph add-node Schema user-schema
```

### Add Edges

Edges represent relationships between nodes. Each edge has:
- **Source**: The node that depends on or owns the target
- **Target**: The node being depended on or owned
- **Type**: DEPENDS_ON, CONSUMES, OWNS, or IMPLEMENTS
- **Contract** (optional): Path to a TypeSpec contract file

```bash
# Create a dependency relationship
frctl graph add-edge pkg:frctl/api-gateway@local pkg:frctl/auth-utils@local --type DEPENDS_ON

# Create a consumption relationship
frctl graph add-edge pkg:frctl/api-gateway@local pkg:frctl/user-schema@local --type CONSUMES
```

### View the Graph

```bash
# Show graph structure
frctl graph show

# Example output:
# Graph Statistics:
#   Nodes: 3
#   Edges: 2
#   Depth: 1
#   Hash:  a3f5e2c1d4b6...
#
# Nodes:
#   - Service    api-gateway         (pkg:frctl/api-gateway@local)
#   - Library    auth-utils          (pkg:frctl/auth-utils@local)
#   - Schema     user-schema         (pkg:frctl/user-schema@local)
#
# Edges:
#   - pkg:frctl/api-gateway@local --[DEPENDS_ON]--> pkg:frctl/auth-utils@local
#   - pkg:frctl/api-gateway@local --[CONSUMES]--> pkg:frctl/user-schema@local
```

### Validate the Graph

The graph automatically prevents cycles, but you can manually validate:

```bash
frctl graph validate

# Output: ✓ Graph is valid
```

### Export the Graph

```bash
# Export to a specific file
frctl graph export output.json

# Or print to stdout
frctl graph export
```

## Node Types

### Service
A deployable service or application.

**Example**: `api-gateway`, `payment-processor`, `notification-service`

### Library
A shared code library or package.

**Example**: `auth-utils`, `logging-lib`, `http-client`

### Schema
A data schema or contract definition.

**Example**: `user-schema`, `order-schema`, `event-definitions`

### Endpoint
An API endpoint or interface.

**Example**: `/api/users`, `/api/orders`, `UserService.getUser`

### Component
A logical architectural component.

**Example**: `authentication-module`, `payment-gateway`, `cache-layer`

## Edge Types

### DEPENDS_ON
Source depends on target for functionality.

```
api-gateway --[DEPENDS_ON]--> auth-utils
```

**Meaning**: `api-gateway` requires `auth-utils` to function.

### CONSUMES
Source consumes data or events from target.

```
payment-service --[CONSUMES]--> order-events
```

**Meaning**: `payment-service` reads events from `order-events`.

### OWNS
Source owns or is responsible for target.

```
api-gateway --[OWNS]--> /api/users
```

**Meaning**: `api-gateway` is responsible for the `/api/users` endpoint.

### IMPLEMENTS
Source implements an interface or contract defined by target.

```
user-service --[IMPLEMENTS]--> user-schema
```

**Meaning**: `user-service` implements the contract in `user-schema`.

## DAG Properties

The graph enforces **Directed Acyclic Graph** properties:

### ✅ Allowed: Linear Dependencies

```
A --[DEPENDS_ON]--> B --[DEPENDS_ON]--> C
```

This is valid - A depends on B, which depends on C.

### ✅ Allowed: Diamond Structure

```
    A
   / \
  B   C
   \ /
    D
```

This is valid - multiple paths to the same node are allowed.

### ❌ Forbidden: Cycles

```
A --[DEPENDS_ON]--> B --[DEPENDS_ON]--> A
```

This is **invalid** - creates a circular dependency. The system will reject this edge.

## Advanced Operations

### Topological Sort

Get nodes in dependency order:

```python
from frctl.graph import FederatedGraph
from pathlib import Path

g = FederatedGraph.load(Path(".frctl/graph.json"))
sorted_nodes = g.topological_sort()

# Nodes are returned in build order
# (dependencies before dependents)
```

### Query Ancestors

Find all transitive dependencies:

```python
ancestors = g.get_ancestors("pkg:frctl/api-gateway@local")
# Returns all nodes that api-gateway depends on
```

### Query Descendants

Find all dependents:

```python
descendants = g.get_descendants("pkg:frctl/auth-utils@local")
# Returns all nodes that depend on auth-utils
```

### Extract Subgraph

Extract a subset of the graph:

```python
subgraph = g.extract_subgraph([
    "pkg:frctl/api-gateway@local",
    "pkg:frctl/auth-utils@local"
])
# Returns a new graph with only these nodes
```

## Programmatic Usage

### Creating a Graph

```python
from frctl.graph import FederatedGraph, Node, NodeType, Edge, EdgeType
from frctl.graph.dag import generate_purl
from pathlib import Path

# Create a new graph
g = FederatedGraph()

# Add nodes
api_gateway = Node(
    id=generate_purl("api-gateway"),
    type=NodeType.SERVICE,
    name="api-gateway",
    metadata={"version": "1.0", "team": "platform"}
)
g.add_node(api_gateway)

auth_utils = Node(
    id=generate_purl("auth-utils"),
    type=NodeType.LIBRARY,
    name="auth-utils"
)
g.add_node(auth_utils)

# Add edge
edge = Edge(
    source=api_gateway.id,
    target=auth_utils.id,
    edge_type=EdgeType.DEPENDS_ON,
    metadata={"version_constraint": "^1.0"}
)
g.add_edge(edge)

# Save to file
g.save(Path(".frctl/graph.json"))
```

### Loading and Querying

```python
from frctl.graph import FederatedGraph
from pathlib import Path

# Load existing graph
g = FederatedGraph.load(Path(".frctl/graph.json"))

# Get node
node = g.get_node("pkg:frctl/api-gateway@local")
print(f"Node: {node.name} ({node.type})")

# Get edge
edge = g.get_edge(
    "pkg:frctl/api-gateway@local",
    "pkg:frctl/auth-utils@local"
)
print(f"Edge: {edge.edge_type}")

# Statistics
print(f"Nodes: {g.node_count()}")
print(f"Edges: {g.edge_count()}")
print(f"Depth: {g.depth()}")
print(f"Hash: {g.merkle_hash()}")
```

### Error Handling

```python
from frctl.graph.dag import CycleDetectedError, NodeNotFoundError

try:
    # This will raise CycleDetectedError
    g.add_edge(Edge(
        source="pkg:frctl/a@local",
        target="pkg:frctl/b@local",
        edge_type=EdgeType.DEPENDS_ON
    ))
except CycleDetectedError as e:
    print(f"Cycle detected: {e}")
except NodeNotFoundError as e:
    print(f"Node not found: {e}")
```

## Best Practices

### 1. Use Meaningful Names

✅ **Good**: `authentication-service`, `user-api`, `payment-gateway`

❌ **Bad**: `service-1`, `app`, `thing`

### 2. Choose Appropriate Node Types

Match the type to the architectural role:
- Services that run → `Service`
- Shared code → `Library`
- Data contracts → `Schema`
- API endpoints → `Endpoint`
- Logical groupings → `Component`

### 3. Use Edge Types Correctly

- **DEPENDS_ON**: Technical runtime dependency
- **CONSUMES**: Data or event consumption
- **OWNS**: Ownership or responsibility
- **IMPLEMENTS**: Contract implementation

### 4. Keep Metadata Lightweight

Use metadata for:
- Version constraints
- Team ownership
- Deployment configuration
- Links to external resources

Avoid storing large data structures in metadata.

### 5. Regular Validation

Run `frctl graph validate` regularly to ensure graph integrity.

### 6. Track Architecture Changes

The graph's Merkle hash changes when the architecture changes. Use it to detect drift:

```python
# Save current hash
initial_hash = g.merkle_hash()

# ... make changes ...

# Detect changes
if g.merkle_hash() != initial_hash:
    print("Architecture has changed!")
```

## Next Steps

- **TypeSpec Contracts**: Learn about edge contracts in [TypeSpec Guide](typespec-contracts.md)
- **Architecture Visualization**: See [Visualization Guide](visualization.md)
- **Migration Patterns**: See [Migration Guide](migration.md)
- **API Reference**: See [API Documentation](../api/graph.md)
