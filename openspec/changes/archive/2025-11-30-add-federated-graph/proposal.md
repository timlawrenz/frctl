# Change: Add Federated Graph Architecture

## Why

The current CLI structure lacks a fundamental data model for representing software architecture. According to the Fractal V3 architecture, we need to replace file-centric representations with a topological Directed Acyclic Graph (DAG) that enforces strict dependency management and enables deterministic reasoning about system architecture.

This change implements the foundational **Federated Graph** - the core data structure that solves the Context-Coupling Orthogonality problem by managing both vertical hierarchy (goals decomposition) and horizontal coupling (component dependencies) in a unified, machine-verifiable representation.

## What Changes

- Add complete graph data model with Node and Edge abstractions
- Implement DAG validation (cycle detection, topological sorting)
- Add DAG-JSON serialization with deterministic hashing
- Implement PURL (Package URL) identifiers for nodes
- Add graph persistence to `.frctl/graph.json`
- Create CLI commands for graph manipulation and visualization
- Add NetworkX as core graph operations library
- Implement graph traversal and subgraph extraction
- Add basic TypeSpec contract support for edges

## Impact

### Affected specs
- **NEW**: `graph-core` - Core graph data structures and operations

### Affected code
- New package: `frctl/graph/` - Graph data model
- New package: `frctl/serialization/` - DAG-JSON persistence
- New package: `frctl/types/` - TypeSpec integration (basic)
- Updated: `frctl/__main__.py` - Add graph command group
- Updated: `pyproject.toml` - Add NetworkX dependency

### Breaking Changes
None - this is a new capability with no existing functionality to break.

## Dependencies

- NetworkX >= 3.0 (graph algorithms and DAG operations)
- pydantic >= 2.0 (data validation for nodes/edges)

## Technical Notes

This proposal follows Phase 1 of the implementation roadmap (see `docs/roadmap.md`). The graph implementation uses NetworkX as the underlying DAG engine for proven reliability in cycle detection and topological sorting. DAG-JSON serialization ensures deterministic hashing for architecture fingerprinting, which will be critical for drift detection in later phases.

The design intentionally starts simple (nodes, edges, basic operations) and will be extended in future proposals to support:
- Full TypeSpec contract validation (Phase 2)
- Policy gates and validation rules (Phase 3)
- Drift detection and reconciliation (Phase 4)
