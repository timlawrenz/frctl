# frctl Project Documentation

This directory contains documentation for the **frctl** (Fractal) project - a deterministic topological architecture for agentic software engineering.

## Documents

- **[fractal-v3-architecture.md](./fractal-v3-architecture.md)** - Complete technical specification for Fractal V3, including the theoretical foundations, architectural design, and implementation details
- **[roadmap.md](./roadmap.md)** - Implementation roadmap with phased development plan from core data structures through execution layer

## Overview

Fractal V3 is a deterministic architecture for AI-driven software engineering that solves the "Context Coherence Crisis" through:

### Core Innovations

1. **Federated Graph Architecture** - Topological DAG-based representation replacing file-centric models
2. **Tandem Protocol** - Human-in-the-loop system where agents propose architectural plans rather than execute autonomously
3. **Recursive Context-Aware Planning (ReCAP)** - Hierarchical planning that maintains architectural integrity

### Key Components

- **Planning Layer** - Decomposes high-level goals into executable tasks
- **State Management** - Graph-based system state with strict dependency tracking  
- **Execution Layer** - Transactional code generation with rollback capabilities
- **Drift Resolution** - Automatic detection and reconciliation of implementation vs. plan divergence

### Technologies & Concepts

- **DAG (Directed Acyclic Graph)** - Core data structure for dependency management
- **Topological Sorting** - Ensures valid execution order
- **Transactional Rollback** - Safe failure recovery
- **Context-Coupling Orthogonality** - Managing vertical hierarchy and horizontal dependencies

---

*For complete details, see the [Fractal V3 Architecture document](./fractal-v3-architecture.md).*
