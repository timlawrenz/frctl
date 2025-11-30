# Fractal V3 Implementation Roadmap

This roadmap outlines the implementation strategy for **frctl**, following the architectural principles defined in the [Fractal V3 Architecture](./fractal-v3-architecture.md).

## Overview

The implementation follows a bottom-up approach, building foundational data structures first, then layering the planning engine, human-in-the-loop protocols, and finally the execution layer. Each phase uses OpenSpec for rigorous specification before implementation.

---

## Phase 1: Core Data Structures (Weeks 1-2)

### Goal
Build the **Federated Graph** foundation - the topological DAG that replaces file-centric representations.

### OpenSpec Proposal
Create `add-federated-graph` proposal covering:

#### Components to Build

1. **Graph Data Model** (`frctl/graph/`)
   - `Node` class - Represents semantic components (Services, Libraries, Schemas, Endpoints)
   - `Edge` class - Represents typed relationships (dependsOn, consumes, owns)
   - `FederatedGraph` class - The DAG container with validation logic
   - Node types: `Service`, `Library`, `Schema`, `Endpoint`, `Component`
   - Edge types: `DEPENDS_ON`, `CONSUMES`, `OWNS`, `IMPLEMENTS`

2. **Graph Operations**
   - Add/remove nodes and edges
   - Topological sort algorithm (dependency resolution)
   - Cycle detection (ensure DAG property)
   - Graph traversal (ancestors, descendants)
   - Subgraph extraction (isolate components)

3. **Serialization** (`frctl/serialization/`)
   - DAG-JSON format implementation (deterministic encoding)
   - Merkle hashing for architecture fingerprints
   - PURL (Package URL) identifiers for nodes
   - CycloneDX SBOM generation support
   - Save/load graph state to `.frctl/graph.json`

4. **TypeSpec Integration** (`frctl/types/`)
   - TypeSpec schema validation setup
   - Interface contract definitions
   - AST parsing for edge validation
   - Schema evolution tracking

### CLI Commands

```bash
frctl graph init                    # Initialize empty graph
frctl graph show                    # Display graph structure
frctl graph add-node <type> <name>  # Add a node
frctl graph add-edge <from> <to>    # Add dependency edge
frctl graph validate                # Check DAG integrity
frctl graph export                  # Export as CycloneDX SBOM
```

### Acceptance Criteria

- [ ] Graph can represent 1000+ nodes without performance degradation
- [ ] Cycle detection prevents invalid DAG states
- [ ] Deterministic serialization produces identical hashes for identical graphs
- [ ] Topological sort correctly orders dependencies
- [ ] TypeSpec contracts can be attached to edges

### Key Files

- `frctl/graph/node.py`
- `frctl/graph/edge.py`
- `frctl/graph/dag.py`
- `frctl/graph/topological.py`
- `frctl/serialization/dag_json.py`
- `frctl/types/typespec.py`

---

## Phase 2: ReCAP Planning Engine (Weeks 3-4)

### Goal
Implement **Recursive Context-Aware Planning (ReCAP)** - the hierarchical decomposition algorithm that solves the Context Coherence Crisis.

### OpenSpec Proposal
Create `add-recap-engine` proposal covering:

#### Components to Build

1. **Planning Engine** (`frctl/planning/`)
   - `PlanningEngine` class - Orchestrates recursive decomposition
   - `Goal` class - Represents a planning node (composite or atomic)
   - `ContextTree` class - Hierarchical context management
   - Atomicity detection algorithm
   - Dependency inference between sibling goals

2. **Context Management** (`frctl/context/`)
   - Hydration logic - Inject parent constraints into child context
   - Dehydration logic - Compress child results into digests
   - Token hygiene tracking (context window monitoring)
   - Global context registry (project settings, constraints)
   - Parent intent propagation

3. **LLM Integration** (`frctl/llm/`)
   - Abstract LLM provider interface
   - OpenAI/Anthropic adapters
   - Prompt templates for decomposition
   - Atomicity check prompts
   - Dependency extraction prompts
   - Response parsing and validation

4. **Plan Persistence** (`frctl/planning/storage.py`)
   - Save planning trees to `.frctl/plans/<plan-id>.json`
   - Plan versioning
   - Plan status tracking (in-progress, completed, approved)
   - Digest archive storage

### CLI Commands

```bash
frctl plan init <goal>              # Start recursive planning session
frctl plan status [plan-id]         # Show planning tree structure
frctl plan review <node-id>         # Review specific node details
frctl plan continue <plan-id>       # Resume paused planning
frctl plan export <plan-id>         # Export plan as JSON
frctl plan visualize <plan-id>      # Generate tree visualization
```

### Acceptance Criteria

- [ ] Planning can decompose goals 5+ levels deep
- [ ] Context window never exceeds model limits (via dehydration)
- [ ] Atomic goals are correctly identified
- [ ] Sibling dependencies are inferred accurately
- [ ] Planning state can be saved and resumed
- [ ] Digests preserve 95%+ of architectural intent

### Key Files

- `frctl/planning/engine.py`
- `frctl/planning/goal.py`
- `frctl/planning/context_tree.py`
- `frctl/context/hydration.py`
- `frctl/llm/provider.py`
- `frctl/llm/prompts/decompose.py`

---

## Phase 3: Tandem Protocol (Weeks 5-6)

### Goal
Implement the **Tandem Human-in-the-Loop Protocol** - transforming agents from executors to proposers.

### OpenSpec Proposal
Create `add-tandem-protocol` proposal covering:

#### Components to Build

1. **Proposal System** (`frctl/tandem/`)
   - `Proposal` class - Represents a proposed architectural change
   - `ProposalReview` class - Review state and feedback
   - Approval workflow state machine
   - Rejection with feedback mechanism
   - Conditional approval (approve with modifications)

2. **Interactive Review Interface** (`frctl/ui/`)
   - Rich CLI interface using `rich` library
   - Syntax-highlighted plan display
   - Interactive tree navigation
   - Diff view (proposed vs. current state)
   - Inline commenting system
   - Approval confirmation dialogs

3. **Version Control Integration** (`frctl/vcs/`)
   - Git integration for plan versioning
   - Commit plans as `.frctl/plans/` files
   - Branch-based plan isolation
   - Merge conflict detection for overlapping plans
   - Plan rollback via git revert

4. **Policy Gates** (`frctl/policy/`)
   - Configurable validation rules
   - Dependency license checking
   - Security policy enforcement
   - Naming convention validation
   - Architectural pattern compliance

### CLI Commands

```bash
frctl review                        # Enter interactive review mode
frctl review list                   # List pending proposals
frctl review show <proposal-id>     # Display proposal details
frctl approve <proposal-id>         # Approve a proposal
frctl reject <proposal-id> -m "msg" # Reject with feedback
frctl modify <proposal-id>          # Request modifications
frctl policy check <proposal-id>    # Run policy validation
```

### Acceptance Criteria

- [ ] Interactive review interface is intuitive and responsive
- [ ] Proposals can be approved/rejected with feedback
- [ ] Policy gates prevent invalid architectures from being approved
- [ ] Review history is preserved and auditable
- [ ] Multiple reviewers can collaborate on proposals
- [ ] Rejected proposals can be revised and resubmitted

### Key Files

- `frctl/tandem/proposal.py`
- `frctl/tandem/review.py`
- `frctl/ui/review_interface.py`
- `frctl/policy/validator.py`
- `frctl/vcs/git_integration.py`

---

## Phase 4: Execution Layer (Weeks 7-8)

### Goal
Implement **Safe Code Generation with Transactional Execution** and drift detection.

### OpenSpec Proposal
Create `add-execution-engine` proposal covering:

#### Components to Build

1. **Execution Engine** (`frctl/execution/`)
   - `ExecutionEngine` class - Orchestrates code generation
   - `Transaction` class - Atomic filesystem operations
   - `Executor` class - Generates code from approved plans
   - File operation journaling
   - Rollback mechanism

2. **Code Generation** (`frctl/codegen/`)
   - Template-based code generation
   - LLM-based code generation (with schema enforcement)
   - Type-safe code generation from TypeSpec
   - Test generation
   - Documentation generation

3. **Drift Detection** (`frctl/drift/`)
   - `DriftDetector` class - Compares plan vs. reality
   - File hash tracking
   - Dependency drift detection
   - Schema drift detection
   - Auto-reconciliation strategies

4. **Transaction Management** (`frctl/execution/transaction.py`)
   - Write-ahead log (WAL) for filesystem operations
   - Commit/rollback semantics
   - Conflict detection
   - Partial rollback (undo specific files)
   - Transaction history and replay

### CLI Commands

```bash
frctl execute <proposal-id>         # Execute approved proposal
frctl execute status                # Show execution progress
frctl rollback <transaction-id>     # Rollback transaction
frctl rollback list                 # List rollback points
frctl drift check                   # Detect plan vs. reality drift
frctl drift resolve <drift-id>      # Auto-resolve drift
frctl drift report                  # Generate drift report
frctl transaction log               # View transaction history
```

### Acceptance Criteria

- [ ] Execution can be rolled back without data loss
- [ ] Drift is detected with 100% accuracy
- [ ] Failed executions don't leave partial changes
- [ ] Code generation respects TypeSpec contracts
- [ ] Execution can be paused and resumed
- [ ] Transaction log is complete and auditable

### Key Files

- `frctl/execution/engine.py`
- `frctl/execution/transaction.py`
- `frctl/codegen/generator.py`
- `frctl/drift/detector.py`
- `frctl/drift/reconciler.py`

---

## Phase 5: Integration & Polish (Weeks 9-10)

### Goal
Integrate all components and add production-ready features.

### Components to Build

1. **End-to-End Workflow**
   - Integrated CLI experience
   - Progress tracking across phases
   - Error recovery and retry logic
   - Comprehensive logging

2. **Configuration Management** (`frctl/config/`)
   - Project configuration files (`.frctl/config.toml`)
   - LLM provider settings
   - Policy rule definitions
   - Template customization

3. **Documentation & Examples**
   - User guide
   - API reference
   - Example projects
   - Tutorial walkthrough

4. **Testing & Quality**
   - Unit tests for all components
   - Integration tests for workflows
   - Performance benchmarks
   - Security audit

### CLI Commands

```bash
frctl init                          # Initialize new frctl project
frctl config set <key> <value>      # Configure project settings
frctl workflow run <goal>           # Run full workflow (plan → review → execute)
frctl status                        # Project health dashboard
frctl clean                         # Clean temporary artifacts
```

### Acceptance Criteria

- [ ] Complete workflow from goal to execution works end-to-end
- [ ] All components have 80%+ test coverage
- [ ] Documentation is comprehensive and accurate
- [ ] Performance meets benchmarks (1000-node graphs in <1s)
- [ ] Security policies prevent common vulnerabilities

---

## Future Enhancements (Post-MVP)

### Advanced Features

1. **Multi-Agent Collaboration**
   - Multiple agents working on different subgraphs
   - Agent specialization (backend, frontend, DevOps)
   - Collaborative planning sessions

2. **Learning & Optimization**
   - Plan quality scoring
   - Preference learning (DPO-style)
   - Automatic prompt optimization
   - Architecture pattern library

3. **Platform Integration**
   - GitHub Actions integration
   - CI/CD pipeline generation
   - Cloud deployment automation
   - Monitoring & observability setup

4. **Advanced Drift Handling**
   - Predictive drift detection
   - Automatic plan updates
   - Conflict resolution strategies
   - Manual override tracking

---

## Implementation Strategy

### Development Principles

1. **OpenSpec First** - Every feature starts with a rigorous specification
2. **Test-Driven** - Write tests before implementation
3. **Incremental** - Each phase builds on proven foundations
4. **Deterministic** - Favor predictable behavior over clever heuristics
5. **Human-Centric** - Always keep humans in control

### Technology Stack

- **Language**: Python 3.8+
- **CLI Framework**: Click
- **Graph Library**: NetworkX (for DAG operations)
- **Serialization**: DAG-JSON (IPFS standard)
- **LLM Integration**: OpenAI SDK, Anthropic SDK
- **UI**: Rich (terminal UI), Textual (future TUI)
- **Testing**: pytest
- **Linting**: ruff, mypy

### Success Metrics

- **Trust Gap**: Verification cost < 10% of generation value
- **Context Efficiency**: <50% token usage vs. linear CoT
- **Drift Rate**: <5% divergence between plan and reality
- **User Satisfaction**: 90%+ approval rate on generated plans
- **Performance**: Handle 1000-node architectures in <10 minutes

---

## Getting Started

To begin implementation:

```bash
# 1. Create Phase 1 proposal
openspec proposal create add-federated-graph

# 2. Review and refine the specification
openspec show add-federated-graph

# 3. Implement according to spec
# (Follow tasks.md in the proposal)

# 4. Validate and archive
openspec validate add-federated-graph --strict
openspec archive add-federated-graph
```

---

## Questions & Decisions

### Open Questions

1. **LLM Provider Strategy**: Support multiple providers or focus on one?
2. **Storage Format**: SQLite vs. JSON files for graph persistence?
3. **UI Framework**: CLI-only or add web interface?
4. **Deployment**: Local-only or support remote/cloud execution?

### Key Decisions Needed

- [ ] Choose primary LLM provider (OpenAI vs. Anthropic vs. both)
- [ ] Define TypeSpec schema evolution policy
- [ ] Determine policy gate extensibility model
- [ ] Select graph visualization library
- [ ] Choose transaction log storage mechanism

---

*Last Updated: 2025-11-30*
