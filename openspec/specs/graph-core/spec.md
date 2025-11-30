# graph-core Specification

## Purpose
TBD - created by archiving change add-federated-graph. Update Purpose after archive.
## Requirements
### Requirement: Graph Data Model

The system SHALL provide a graph-based representation of software architecture using nodes and edges.

#### Scenario: Create node with valid type

- **WHEN** a user creates a node with type "Service" and name "api-gateway"
- **THEN** the node is added to the graph with a unique identifier
- **AND** the node has the specified type and name
- **AND** the node can be retrieved by its identifier

#### Scenario: Create edge between nodes

- **WHEN** a user creates an edge from node A to node B with type "DEPENDS_ON"
- **THEN** the edge is added to the graph
- **AND** the edge type is stored correctly
- **AND** node A is recorded as depending on node B

#### Scenario: Reject invalid node type

- **WHEN** a user attempts to create a node with an invalid type
- **THEN** the system raises a validation error
- **AND** the node is not added to the graph

### Requirement: DAG Validation

The system SHALL enforce Directed Acyclic Graph (DAG) properties and prevent cycles.

#### Scenario: Detect cycle on edge creation

- **WHEN** adding an edge would create a cycle (A→B→C→A)
- **THEN** the system raises a cycle detection error
- **AND** the edge is not added to the graph
- **AND** the graph remains in a valid state

#### Scenario: Topological sort of valid DAG

- **WHEN** the user requests a topological sort of the graph
- **THEN** the system returns nodes in dependency order
- **AND** for any edge A→B, A appears before B in the result
- **AND** the sort is deterministic for the same graph structure

#### Scenario: Validate graph integrity

- **WHEN** the user runs graph validation
- **THEN** the system checks for cycles
- **AND** the system verifies all edges reference valid nodes
- **AND** the system reports any integrity violations

### Requirement: Graph Traversal

The system SHALL provide methods to traverse and query the graph structure.

#### Scenario: Get all ancestors of a node

- **WHEN** a user queries ancestors of node C (where A→B→C)
- **THEN** the system returns [A, B] in dependency order
- **AND** the result includes all transitive dependencies

#### Scenario: Get all descendants of a node

- **WHEN** a user queries descendants of node A (where A→B→C)
- **THEN** the system returns [B, C]
- **AND** the result includes all transitive dependents

#### Scenario: Extract subgraph for nodes

- **WHEN** a user extracts a subgraph for nodes [B, C]
- **THEN** the system returns a new graph containing only B, C, and edges between them
- **AND** the subgraph maintains DAG properties
- **AND** the original graph is unchanged

### Requirement: Deterministic Serialization

The system SHALL serialize graphs to DAG-JSON format with deterministic output.

#### Scenario: Save graph to file

- **WHEN** a user saves the graph to .frctl/graph.json
- **THEN** the file contains valid DAG-JSON
- **AND** the JSON keys are alphabetically sorted
- **AND** all nodes and edges are preserved

#### Scenario: Load graph from file

- **WHEN** a user loads a graph from .frctl/graph.json
- **THEN** the graph is reconstructed with identical structure
- **AND** all node and edge metadata is preserved
- **AND** the graph passes validation

#### Scenario: Generate stable Merkle hash

- **WHEN** the same graph is serialized multiple times
- **THEN** the Merkle hash is identical each time
- **AND** any change to the graph produces a different hash
- **AND** the hash can be used to detect architecture drift

### Requirement: Node Identification

The system SHALL assign unique identifiers to nodes using PURL format.

#### Scenario: Generate PURL identifier

- **WHEN** a node is created for a service named "auth-service"
- **THEN** the system generates a PURL like "pkg:frctl/auth-service@local"
- **AND** the PURL is unique within the graph
- **AND** the PURL is stable across save/load cycles

#### Scenario: Lookup node by PURL

- **WHEN** a user queries a node by its PURL
- **THEN** the system returns the correct node
- **AND** the node metadata is accessible

### Requirement: CLI Graph Operations

The system SHALL provide command-line interface for graph manipulation.

#### Scenario: Initialize new graph

- **WHEN** the user runs `frctl graph init`
- **THEN** a new empty graph is created
- **AND** the .frctl directory is created if it doesn't exist
- **AND** an empty graph.json file is created

#### Scenario: Display graph structure

- **WHEN** the user runs `frctl graph show`
- **THEN** the system displays nodes and edges in a readable format
- **AND** the output shows node types and names
- **AND** the output shows dependency relationships

#### Scenario: Add node via CLI

- **WHEN** the user runs `frctl graph add-node Service api-gateway`
- **THEN** a Service node named "api-gateway" is added
- **AND** the graph is saved to .frctl/graph.json
- **AND** a success message is displayed

#### Scenario: Validate graph via CLI

- **WHEN** the user runs `frctl graph validate`
- **THEN** the system checks DAG integrity
- **AND** the system reports "Valid" or lists violations
- **AND** the exit code is 0 for valid, non-zero for invalid

### Requirement: Performance

The system SHALL handle large graphs efficiently.

#### Scenario: Handle 1000-node graph

- **WHEN** the graph contains 1000+ nodes
- **THEN** topological sort completes in under 1 second
- **AND** cycle detection completes in under 1 second
- **AND** serialization completes in under 2 seconds
- **AND** memory usage remains reasonable (<500MB for graph data)

### Requirement: TypeSpec Edge Contracts

The system SHALL support optional TypeSpec contracts for edges.

#### Scenario: Attach TypeSpec contract to edge

- **WHEN** a user creates an edge with a TypeSpec contract file path
- **THEN** the contract path is stored in edge metadata
- **AND** the system validates the contract file exists
- **AND** the contract can be retrieved later

#### Scenario: Edge without contract

- **WHEN** a user creates an edge without specifying a contract
- **THEN** the edge is created successfully
- **AND** the contract field is null
- **AND** the edge functions normally

**Note**: Full TypeSpec AST parsing and validation will be added in Phase 2 (ReCAP Engine).

