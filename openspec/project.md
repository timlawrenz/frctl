# Project Context

## Purpose
To create a deterministic, topological architecture for agentic software engineering. The project's goal is to solve the "Context Coherence Crisis" in current AI models and bridge the "Trust Gap" by shifting from probabilistic code generation to a deterministic, spec-driven development model. This ensures AI agents can reliably architect and implement complex systems.

## Tech Stack
- **Core Language**: TypeScript
- **Interface Definition**: TypeSpec (mandated for all component interfaces)
- **Graph Serialization**: DAG-JSON (for deterministic hashing of the architecture graph)
- **Dependency Management**: CycloneDX and Package URL (PURL) for SBOM generation and security compliance.
- **Artifacts**: Markdown (`proposal.md`, `tasks.md`) for human-readable plans.

## Project Conventions

### Code Style
- **Spec-Driven Development (SDD)**: The core methodology. All implementation is derived from a rigorously planned and approved specification.
- **Contract-First**: All component interfaces must be defined in TypeSpec before implementation begins. These contracts are treated as immutable sources of truth for dependent components.
- **Deterministic Naming**: Synthetic models generated in "Loose Mode" use deterministic hashes of their structure for consistent naming.

### Architecture Patterns
- **Recursive Context-Aware Planning (ReCAP)**: A recursive algorithm for decomposing high-level goals into atomic tasks, avoiding context window limitations and ensuring architectural coherence.
- **Federated Graph Architecture**: The system's source of truth is a Directed Acyclic Graph (DAG) representing the software's topology, not the file system.
- **'Tandem' Human-in-the-Loop Protocol**: A strict four-state (INTENT, REVIEW, GATE, EXECUTION) "Plan/Apply" workflow that requires human approval before any code is executed.
- **Topological Drafting ("Wave" Execution)**: Agents execute in waves based on the dependency graph, ensuring that dependencies are implemented before the components that consume them.
- **Transactional File Operations**: A "Staging and Swap" strategy with compensating transactions ensures that file system operations are atomic and recoverable.

### Testing Strategy
- **Design-Time Validation**: The primary focus is on preventing errors before implementation. The "GATE" phase of the Tandem protocol validates the architectural plan against a "Constitution".
- **Pre-Execution Checks**:
    - **Cycle Detection**: Ensures the dependency graph remains acyclic (via DFS traversal).
    - **Breaking Change Analysis**: Uses TypeSpec's AST for semantic diffing to prevent breaking API changes.
    - **Policy Enforcement**: Checks new dependencies against allow/deny lists defined in `openspec/AGENTS.md`.
- **Ghost Compiler**: A compiler runs in memory to validate syntax and types of generated code before it is written to disk.

### Git Workflow
- The development process is centered around the `frctl` CLI and the Tandem Protocol.
- **1. Plan (`frctl plan`)**: An AI Architect generates a proposal (`proposal.md`, `tasks.md`) without writing code.
- **2. Review & Edit**: A human developer reviews the plan, makes corrective edits to the Markdown, and aligns the AI's plan with their intent.
- **3. Approve (`frctl approve`)**: The developer cryptographically signs off on the plan, which is then validated by the Gate engine and locked.
- **4. Apply (`frctl apply`)**: An AI Engineer executes the locked plan, writing code that is correct by construction.

## Domain Context
- **Context Coherence Crisis**: The failure of linear reasoning (Chain of Thought) in LLMs to maintain architectural integrity in large projects due to finite context windows.
- **Trust Gap**: The economic problem where the cost of verifying AI-generated code exceeds the cost of manual implementation.
- **Sibling Blindness**: The inability of agents working on separate, decomposed parts of a system to see each other's interfaces, leading to integration failures.
- **Sad Path Architecture**: A design philosophy that assumes failures (network, file system, etc.) are normal conditions and builds in robust recovery mechanisms like transactional rollbacks and drift resolution.

## Important Constraints
- **AI is a Planner, not an Executor**: The AI's primary role is to generate architectural proposals. It cannot execute code without explicit, cryptographic approval from a human.
- **TypeSpec Mandate**: All component interactions (edges in the graph) *must* be defined with a strict TypeSpec contract.
- **Acyclicity**: The system's dependency graph must always remain a Directed Acyclic Graph (DAG). Circular dependencies are a hard failure state.
- **Immutability**: Once an interface contract is published by a component in an execution "Wave," it is considered immutable for subsequent waves.

## External Dependencies
- **LLMs**: Requires high-intelligence models (e.g., GPT-4o, Claude 3.5 Sonnet) for reasoning and planning.
- **OpenSpec Standard**: Fractal V3 is the reference implementation and generative engine for the OpenSpec standard, populating its file system schema.
- **Developer Ecosystem**: Designed to integrate with existing developer tools (Cursor, GitHub Copilot), CI/CD pipelines, and platform engineering ecosystems (Backstage).
