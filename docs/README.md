# frctl Project Documentation

This directory contains documentation for the **frctl** (Fractal) project - a deterministic topological architecture for agentic software engineering.

## Documents

### Architecture & Planning
- **[fractal-v3-architecture.md](./fractal-v3-architecture.md)** - Complete technical specification for Fractal V3, including theoretical foundations and design
- **[roadmap.md](./roadmap.md)** - Implementation roadmap with phased development plan

### User Guides
- **[guides/graph-basics.md](./guides/graph-basics.md)** - Getting started with Federated Graph
- **[guides/context-tree.md](./guides/context-tree.md)** - Understanding hierarchical context management ✨ *NEW*

### Reference
- **[schemas/graph-json.md](./schemas/graph-json.md)** - Graph JSON schema documentation

## Overview

Fractal V3 is a deterministic architecture for AI-driven software engineering that solves the "Context Coherence Crisis" through:

### Core Innovations

1. **Federated Graph Architecture** - Topological DAG-based representation replacing file-centric models ✅ *Implemented*
2. **Recursive Context-Aware Planning (ReCAP)** - Hierarchical planning that maintains architectural integrity 🚧 *In Progress*
3. **Tandem Protocol** - Human-in-the-loop system where agents propose architectural plans rather than execute autonomously 📋 *Planned*

### Implementation Status

#### ✅ Phase 1 Complete: Federated Graph
- Full DAG implementation with cycle detection
- 10 CLI commands for graph management
- Serialization with Merkle hashing
- 85 comprehensive tests
- See: `guides/graph-basics.md`

#### 🚧 Phase 2 In Progress: ReCAP Planning (29% complete)
- ✅ Goal and Plan data models
- ✅ LLM provider abstraction (LiteLLM)
- ✅ Basic planning engine with atomicity detection
- ✅ **Context Tree for hierarchical context management** ✨ *NEW*
- 🔄 Digest protocol for context compression
- 🔄 Prompt templates (Jinja2)
- 🔄 Plan persistence

**New This Week:**
- **Context Tree** - Full implementation of hydration/dehydration protocol
- 18 comprehensive context tests
- 6 integration tests for engine-context interaction
- See: `guides/context-tree.md`

#### 📋 Phase 3 Planned: Tandem Protocol
- Interactive review interface
- Approval workflow
- Policy gates
- Version control integration

### Key Components

- **Planning Layer** - Decomposes high-level goals into executable tasks
- **Context Tree** - Manages context isolation and token hygiene ✨ *NEW*
- **State Management** - Graph-based system state with strict dependency tracking  
- **Execution Layer** - Transactional code generation with rollback capabilities
- **Drift Resolution** - Automatic detection and reconciliation of implementation vs. plan divergence

### Technologies & Concepts

- **DAG (Directed Acyclic Graph)** - Core data structure for dependency management
- **ReCAP (Recursive Context-Aware Planning)** - Hierarchical goal decomposition
- **Context Tree** - Hierarchical context with O(N·D) complexity vs O(N²) for linear chains ✨ *NEW*
- **Hydration/Dehydration** - Token-efficient context propagation ✨ *NEW*
- **Topological Sorting** - Ensures valid execution order
- **Transactional Rollback** - Safe failure recovery
- **Context-Coupling Orthogonality** - Managing vertical hierarchy and horizontal dependencies

---

*For complete details, see the [Fractal V3 Architecture document](./fractal-v3-architecture.md).*
