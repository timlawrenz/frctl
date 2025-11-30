# Tasks: Add Federated Graph Architecture

## 1. Setup & Dependencies

- [x] 1.1 Add NetworkX >= 3.0 to pyproject.toml dependencies
- [x] 1.2 Add pydantic >= 2.0 to pyproject.toml dependencies
- [x] 1.3 Create `frctl/graph/` package directory with __init__.py
- [x] 1.4 Create `frctl/serialization/` package directory with __init__.py
- [x] 1.5 Create `frctl/types/` package directory with __init__.py

## 2. Graph Data Model (frctl/graph/)

- [x] 2.1 Implement `Node` class with id, type, metadata, and validation
- [x] 2.2 Implement node types enum: Service, Library, Schema, Endpoint, Component
- [x] 2.3 Implement `Edge` class with source, target, edge_type, and metadata
- [x] 2.4 Implement edge types enum: DEPENDS_ON, CONSUMES, OWNS, IMPLEMENTS
- [x] 2.5 Implement `FederatedGraph` class wrapping NetworkX DiGraph
- [x] 2.6 Add graph.add_node() method with validation
- [x] 2.7 Add graph.add_edge() method with validation
- [x] 2.8 Add graph.remove_node() method with cascade delete
- [x] 2.9 Add graph.remove_edge() method
- [x] 2.10 Add graph.get_node() and graph.get_edge() accessors

## 3. DAG Validation & Operations (frctl/graph/)

- [x] 3.1 Implement cycle detection using NetworkX algorithms
- [x] 3.2 Add validation that raises error on cycle creation
- [x] 3.3 Implement topological_sort() returning ordered node list
- [x] 3.4 Implement get_ancestors(node_id) for dependency chain
- [x] 3.5 Implement get_descendants(node_id) for dependents
- [x] 3.6 Implement extract_subgraph(node_ids) for isolation
- [x] 3.7 Add graph.validate() method checking DAG integrity
- [x] 3.8 Add graph statistics methods (node_count, edge_count, depth)

## 4. Serialization (frctl/serialization/)

- [x] 4.1 Implement DAG-JSON encoder for deterministic serialization
- [x] 4.2 Ensure alphabetically sorted keys in JSON output
- [x] 4.3 Implement Merkle hash generation for graph fingerprint
- [x] 4.4 Implement graph.save(path) method writing to .frctl/graph.json
- [x] 4.5 Implement graph.load(path) class method reading from JSON
- [x] 4.6 Add PURL (Package URL) generation for node identifiers
- [x] 4.7 Implement to_dict() and from_dict() for graph serialization
- [x] 4.8 Add versioning metadata to serialized format

## 5. CLI Commands (frctl/__main__.py)

- [x] 5.1 Create `graph` command group using Click
- [x] 5.2 Implement `frctl graph init` - Initialize empty graph in .frctl/
- [x] 5.3 Implement `frctl graph show` - Display graph structure (tree view)
- [x] 5.4 Implement `frctl graph add-node <type> <name>` - Add node interactively
- [x] 5.5 Implement `frctl graph add-edge <from> <to> [type]` - Add edge
- [x] 5.6 Implement `frctl graph remove-node <id>` - Remove node
- [x] 5.7 Implement `frctl graph remove-edge <from> <to>` - Remove edge
- [x] 5.8 Implement `frctl graph validate` - Check DAG integrity
- [x] 5.9 Implement `frctl graph export [path]` - Export as JSON
- [x] 5.10 Implement `frctl graph stats` - Show graph statistics

## 6. TypeSpec Integration (frctl/types/)

- [x] 6.1 Create TypeSpecContract class (stub for now)
- [x] 6.2 Add contract field to Edge class (optional)
- [x] 6.3 Implement basic contract validation (file exists check)
- [x] 6.4 Add example .tsp file in docs/examples/
- [x] 6.5 Document TypeSpec usage in README

## 7. Testing

- [x] 7.1 Write unit tests for Node class validation
- [x] 7.2 Write unit tests for Edge class validation
- [x] 7.3 Write unit tests for cycle detection
- [x] 7.4 Write unit tests for topological sorting
- [x] 7.5 Write unit tests for graph traversal methods
- [x] 7.6 Write unit tests for serialization (deterministic output)
- [x] 7.7 Write unit tests for Merkle hash stability
- [x] 7.8 Write integration tests for CLI commands
- [x] 7.9 Test graph with 1000+ nodes for performance
- [x] 7.10 Add pytest configuration if not exists

## 8. Documentation

- [x] 8.1 Add docstrings to all public classes and methods
- [x] 8.2 Create docs/guides/graph-basics.md tutorial
- [x] 8.3 Document graph JSON schema in docs/schemas/
- [x] 8.4 Add CLI command examples to main README
- [x] 8.5 Document node and edge type semantics
- [x] 8.6 Create architecture diagram showing graph structure

## 9. Validation & Polish

- [x] 9.1 Run `openspec validate add-federated-graph --strict`
- [x] 9.2 Fix any validation issues
- [x] 9.3 Ensure all tests pass
- [x] 9.4 Run linters (ruff, mypy) on new code
- [x] 9.5 Review code for consistency with Fractal V3 principles
- [x] 9.6 Test edge cases (empty graph, single node, disconnected components)
- [x] 9.7 Verify deterministic serialization with repeated save/load
- [x] 9.8 Performance test: 1000-node graph operations < 1 second

## Implementation Notes

**Status**: ✅ **COMPLETE**

All implementation, testing, and documentation tasks have been completed:

- **Core Functionality**: Fully operational graph implementation with all required features
- **Testing**: 85 comprehensive tests covering all requirements with 100% pass rate
- **Documentation**: Complete guide, schema documentation, and working examples
- **Performance**: All operations on 1000-node graphs complete in < 1 second
- **Validation**: Graph integrity validation with cycle detection working correctly
- **CLI**: All commands functional and tested

The add-federated-graph proposal is ready for archival.
