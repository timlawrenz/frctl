# Frctl Documentation

Complete documentation for the Fractal V3 architecture and frctl tool.

## User Guides

Start here if you're new to frctl:

- **[Quick Reference](./QUICK_REFERENCE.md)** - CLI command cheat sheet
- **[Configuration Guide](./guides/configuration.md)** - Complete LLM provider setup
- **[Planning Basics](./guides/planning-basics.md)** - Using the ReCAP planning engine
- **[Graph Basics](./guides/graph-basics.md)** - Working with architectural graphs
- **[Context Tree Guide](./guides/context-tree.md)** - Understanding hierarchical context

## Technical Documentation

Deep dives into the architecture:

- **[Fractal V3 Architecture](./fractal-v3-architecture.md)** - Complete technical specification
- **[Implementation Roadmap](./roadmap.md)** - Development phases and progress
- **[Implementation Summary](./IMPLEMENTATION_SUMMARY.md)** - What's been built so far

## Reference

- **[Graph JSON Schema](./schemas/graph-json.md)** - Graph serialization format
- **[Examples](./examples/)** - Code examples and tutorials

## Getting Started

### 1. Installation

\`\`\`bash
git clone https://github.com/timlawrenz/frctl.git
cd frctl
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
\`\`\`

### 2. Configuration

\`\`\`bash
frctl config init
export OPENAI_API_KEY=sk-...  # Or ANTHROPIC_API_KEY, GEMINI_API_KEY, etc.
frctl config test
\`\`\`

See the [Configuration Guide](./guides/configuration.md) for all options.

### 3. Start Planning

\`\`\`bash
frctl plan init "Your goal here"
frctl plan status <plan-id>
frctl plan visualize <plan-id>
\`\`\`

See [Planning Basics](./guides/planning-basics.md) for details.

## Documentation Structure

\`\`\`
docs/
├── README.md                          # This file
├── QUICK_REFERENCE.md                 # CLI cheat sheet
├── fractal-v3-architecture.md         # Core architecture spec
├── roadmap.md                         # Implementation plan
├── IMPLEMENTATION_SUMMARY.md          # Current progress
├── guides/                            # User guides
│   ├── configuration.md               # LLM setup
│   ├── planning-basics.md             # Planning guide
│   ├── graph-basics.md                # Graph guide
│   └── context-tree.md                # Context management
├── schemas/                           # Data formats
│   └── graph-json.md                  # Graph JSON spec
└── examples/                          # Code examples
    └── (examples here)
\`\`\`

## Development Documentation

Development process documentation is in [\`/dev-docs\`](../dev-docs/):

- **[Session Brief](../dev-docs/SESSION_BRIEF.md)** - Current development status
- **[Development Docs](../dev-docs/)** - All development notes

## Support

- **Issues**: [GitHub Issues](https://github.com/timlawrenz/frctl/issues)
- **Repository**: https://github.com/timlawrenz/frctl

## Contributing

See [development docs](../dev-docs/) for contribution guidelines and current status.
