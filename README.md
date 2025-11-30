# frctl - Fractal V3

> A Deterministic Topological Architecture for Agentic Software Engineering

[![Tests](https://img.shields.io/badge/tests-230%20passing-brightgreen)](./tests)
[![Phase 2](https://img.shields.io/badge/phase%202-83%25%20complete-blue)](./dev-docs/SESSION_BRIEF.md)
[![Documentation](https://img.shields.io/badge/docs-complete-green)](./docs)

Frctl implements the **Fractal V3 architecture** - a system that transforms AI agents from erratic code generators into disciplined architectural planners by solving the "Context Coherence Crisis" through deterministic, graph-based planning.

## What is Frctl?

Frctl is a planning and architecture management tool designed for AI-assisted software development. It provides:

- 🏗️ **Federated Graph Architecture** - DAG-based dependency management for components
- 🤖 **ReCAP Planning Engine** - Recursive Context-Aware Planning with LLM integration
- 🔄 **100+ LLM Provider Support** - OpenAI, Anthropic, Google, Cohere, local models (Ollama)
- 📊 **Hierarchical Task Decomposition** - Break complex goals into atomic, executable tasks
- 💾 **Plan Persistence** - Save, load, and version architectural plans
- 🔒 **Secure Configuration** - API key management via environment variables

## Why Frctl?

Traditional AI coding agents suffer from the **Context Coherence Crisis** - as reasoning chains grow, architectural decisions become disjointed and contradictory. Frctl solves this by:

1. **Recursive Decomposition** - Breaking complex goals into manageable subtasks
2. **Context Isolation** - Each subtask gets a fresh context window
3. **Digest Protocol** - Compressing results while preserving architectural intent
4. **Graph Validation** - Ensuring consistency across the entire system

## Quick Start

### Installation

\`\`\`bash
# Clone the repository
git clone https://github.com/timlawrenz/frctl.git
cd frctl

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install frctl
pip install -e .
\`\`\`

### Configuration

\`\`\`bash
# Initialize configuration
frctl config init

# Set your LLM API key (choose one)
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GEMINI_API_KEY=...

# Or use local models (no API key needed!)
export FRCTL_LLM_MODEL=ollama/codellama

# Test your setup
frctl config test
\`\`\`

### Your First Plan

\`\`\`bash
# Start planning
frctl plan init "Build a REST API with authentication"

# The planning engine will:
# 1. Recursively decompose your goal
# 2. Identify dependencies
# 3. Generate atomic tasks

# View the plan
frctl plan status <plan-id>

# Visualize as a tree
frctl plan visualize <plan-id>
\`\`\`

### Working with Graphs

\`\`\`bash
# Initialize architectural graph
frctl graph init

# Add components
frctl graph add-node Service api-gateway
frctl graph add-node Library auth-utils
frctl graph add-node Schema user-schema

# Define relationships
frctl graph add-edge \\
  pkg:frctl/api-gateway@local \\
  pkg:frctl/auth-utils@local \\
  --type DEPENDS_ON

# View your architecture
frctl graph show
\`\`\`

## Core Features

### 🤖 Multi-Provider LLM Support

Frctl supports 100+ LLM providers via LiteLLM:

- **OpenAI** - GPT-4, GPT-4 Turbo, GPT-3.5
- **Anthropic** - Claude 3.5 Sonnet, Claude 3 Opus
- **Google** - Gemini 1.5 Pro/Flash
- **Cohere** - Command R+
- **Local Models** - Ollama (CodeLlama, Mistral, etc.)
- **And 95+ more** - Azure, AWS Bedrock, Together, etc.

### 📊 Recursive Planning (ReCAP)

The ReCAP algorithm decomposes goals hierarchically:

\`\`\`
Goal: Build REST API
├── Design API Schema
│   ├── Define User Model
│   ├── Define Authentication Endpoints
│   └── Define Resource Endpoints
├── Implement Authentication
│   ├── Setup JWT Library
│   ├── Implement Login
│   └── Implement Token Validation
└── Implement Endpoints
    ├── User CRUD Operations
    └── Error Handling
\`\`\`

Each level maintains context coherence while isolating complexity.

### 🏗️ Graph Architecture

Manage component dependencies with a directed acyclic graph:

\`\`\`python
from frctl.graph import FederatedGraph, Node, NodeType

graph = FederatedGraph()
graph.add_node(Node(
    id="pkg:frctl/api@local",
    type=NodeType.SERVICE,
    name="api-gateway"
))
\`\`\`

### 💾 Plan Persistence

Save and version your architectural plans:

\`\`\`bash
# Plans auto-save to .frctl/plans/
frctl plan list
frctl plan export <plan-id> output.json
\`\`\`

### 🔒 Secure Configuration

Never commit API keys - use environment variables:

\`\`\`toml
# .frctl/config.toml
[llm]
model = "gpt-4"
temperature = 0.7
max_tokens = 2000

[planning]
max_depth = 10
context_window_size = 128000
\`\`\`

## Documentation

### User Guides

- [Configuration Guide](./docs/guides/configuration.md) - Complete LLM setup guide
- [Planning Basics](./docs/guides/planning-basics.md) - Using the ReCAP engine
- [Graph Basics](./docs/guides/graph-basics.md) - Working with architectural graphs
- [Quick Reference](./docs/QUICK_REFERENCE.md) - CLI command cheat sheet

### Technical Documentation

- [Fractal V3 Architecture](./docs/fractal-v3-architecture.md) - Complete technical specification
- [Implementation Roadmap](./docs/roadmap.md) - Development phases
- [Graph JSON Schema](./docs/schemas/graph-json.md) - Graph serialization format

### Development

- [Development Docs](./dev-docs/) - Development process documentation
- [Session Brief](./dev-docs/SESSION_BRIEF.md) - Current development status

## CLI Commands

\`\`\`bash
# Configuration
frctl config init              # Initialize config
frctl config show              # Display current config
frctl config test              # Test LLM connection

# Planning
frctl plan init "goal"         # Start new plan
frctl plan status <id>         # View plan status
frctl plan visualize <id>      # Visualize plan tree
frctl plan export <id>         # Export to JSON

# Graph
frctl graph init               # Initialize graph
frctl graph add-node TYPE NAME # Add component
frctl graph add-edge A B       # Add dependency
frctl graph show               # Display graph
frctl graph validate           # Validate integrity
\`\`\`

See [Quick Reference](./docs/QUICK_REFERENCE.md) for complete command list.

## Project Status

**Phase 1: Federated Graph** ✅ Complete (100%)
- Full DAG implementation
- 85 tests passing
- Complete documentation

**Phase 2: ReCAP Planning Engine** ⚠️ In Progress (83%)
- ✅ LLM provider integration (100+ providers)
- ✅ Goal decomposition engine
- ✅ Context tree with hydration/dehydration
- ✅ Digest protocol for context compression
- ✅ Plan persistence with versioning
- ✅ Complete CLI
- ✅ Configuration system
- ⚠️ Documentation in progress
- ⚠️ Final validation pending

**Total**: 230 tests passing | 83% complete

See [Session Brief](./dev-docs/SESSION_BRIEF.md) for detailed progress.

## Architecture

Frctl implements three core subsystems:

1. **Federated Graph** - Manages component dependencies as a DAG
2. **ReCAP Planning** - Recursively decomposes goals with LLM assistance
3. **Context Tree** - Maintains hierarchical context for coherent planning

The system ensures that architectural decisions remain consistent even as complexity grows, solving the Context Coherence Crisis that plagues traditional AI coding agents.

## Contributing

This project is under active development. See [development docs](./dev-docs/) for current status and implementation notes.

## License

[License information to be added]

## Links

- **Repository**: https://github.com/timlawrenz/frctl
- **Documentation**: [./docs](./docs)
- **Issues**: [GitHub Issues](https://github.com/timlawrenz/frctl/issues)

---

**Built with** ❤️ **using Fractal V3 architecture principles**
