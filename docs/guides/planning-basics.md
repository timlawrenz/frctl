# Planning Basics Guide

This guide covers the ReCAP (Recursive Context-Aware Planning) engine in Frctl.

## Overview

The ReCAP planning engine decomposes high-level goals into atomic, executable tasks using hierarchical decomposition with LLM reasoning. Plans automatically persist to `.frctl/plans/` for resumable workflows.

## Key Concepts

### Goals

Goals represent nodes in the planning tree. Each goal has:
- **Description**: Natural language description of what to accomplish
- **Status**: `pending`, `decomposing`, `atomic`, `complete`, or `failed`
- **Depth**: Position in the planning tree (0 = root)
- **Parent/Children**: Hierarchical relationships
- **Dependencies**: References to other goals

### Plans

Plans contain the complete goal tree and metadata:
- **Goals**: Dictionary of all goals indexed by ID
- **Root Goal**: Top-level goal that started the planning
- **Statistics**: Token usage, max depth, goal counts
- **Status**: `in_progress`, `complete`, or `failed`

### Atomicity

The engine uses LLM reasoning to determine if a goal is **atomic** (can't be meaningfully decomposed further) or **composite** (should be broken down into sub-goals).

## Basic Usage

### Starting a Planning Session

```python
from frctl.planning import PlanningEngine

# Create engine (auto-save enabled by default)
engine = PlanningEngine()

# Start planning
plan = engine.run("Build a REST API for user management")

print(f"Plan ID: {plan.id}")
print(f"Total goals: {len(plan.goals)}")
print(f"Atomic goals: {len(plan.get_atomic_goals())}")
```

The plan is automatically saved to `.frctl/plans/<plan-id>.json`.

### Loading Existing Plans

```python
# Load by ID
plan = engine.load_plan("abc123")

if plan:
    print(f"Loaded: {plan.get_root_goal().description}")
    print(f"Status: {plan.status}")
```

### Listing Plans

```python
# List all plans
all_plans = engine.list_plans()

for p in all_plans:
    print(f"{p['id']}: {p['description']}")
    print(f"  Status: {p['status']}")
    print(f"  Goals: {p['goal_count']} (Atomic: {p['atomic_count']})")
    print(f"  Updated: {p['updated_at']}")

# Filter by status
active = engine.list_plans(status="in_progress")
complete = engine.list_plans(status="complete")
```

## Plan Persistence

### Storage Structure

Plans are stored in `.frctl/plans/`:

```
.frctl/plans/
├── index.json                    # Fast lookup index
├── <plan-id>.json                # Plan data
├── .<plan-id>.backup_*.json      # Automatic backups
└── archive/
    └── <plan-id>_*.json          # Archived plans
```

### Auto-Save Behavior

By default, plans automatically save at these points:
1. When created (`create_plan()`)
2. After each goal decomposition
3. On planning completion

Disable auto-save if needed:

```python
engine = PlanningEngine(auto_save=False)
plan = engine.create_plan("My goal")
# ... manual work ...
engine.save_plan(plan)  # Save when ready
```

### Manual Save/Load

```python
from frctl.planning import PlanStore

store = PlanStore()

# Save
store.save(plan)

# Load
plan = store.load("plan-id")

# Check if exists
if store.exists("plan-id"):
    print("Plan exists")

# Export
from pathlib import Path
store.export("plan-id", Path("output/plan.json"))
```

## Working with Goals

### Accessing Goals

```python
# Get root goal
root = plan.get_root_goal()
print(root.description)

# Get specific goal
goal = plan.get_goal("goal-123")

# Get children
children = plan.get_children("goal-123")
for child in children:
    print(f"  - {child.description}")

# Get all atomic goals
atomic_goals = plan.get_atomic_goals()
```

### Goal Properties

```python
goal = plan.get_goal("goal-123")

print(f"ID: {goal.id}")
print(f"Description: {goal.description}")
print(f"Status: {goal.status}")
print(f"Depth: {goal.depth}")
print(f"Is atomic: {goal.is_atomic()}")
print(f"Is composite: {goal.is_composite()}")
print(f"Children: {goal.child_ids}")
print(f"Dependencies: {goal.dependencies}")
print(f"Tokens used: {goal.tokens_used}")
```

## LLM Configuration

### Using Different Providers

The planning engine supports 100+ LLM providers via LiteLLM:

```python
from frctl.llm import LLMProvider
from frctl.planning import PlanningEngine

# OpenAI (default)
provider = LLMProvider(model="gpt-4")

# Anthropic Claude
provider = LLMProvider(model="claude-3-5-sonnet-20241022")

# Local model (Ollama)
provider = LLMProvider(model="ollama/codellama")

# Create engine with custom provider
engine = PlanningEngine(llm_provider=provider)
```

### API Keys

Set your API key as an environment variable:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# For local models (Ollama), no key needed
```

Or use a `.env` file:

```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## Advanced Features

### Custom Storage Location

```python
from pathlib import Path
from frctl.planning import PlanStore, PlanningEngine

# Custom storage path
store = PlanStore(base_path=Path("/custom/path/plans"))
engine = PlanningEngine(plan_store=store)
```

### Plan Management

```python
# Archive a plan (moves to archive/)
engine.plan_store.archive("plan-id")

# Delete a plan (archives by default)
engine.delete_plan("plan-id", archive=True)

# Delete without archiving
engine.delete_plan("plan-id", archive=False)

# Export to file
engine.plan_store.export("plan-id", Path("export/plan.json"))
```

### Context Tree Integration

Plans use a Context Tree for hierarchical context management. See [Context Tree Guide](./context-tree.md) for details.

## Example: Complete Workflow

```python
from frctl.planning import PlanningEngine

# 1. Create engine
engine = PlanningEngine()

# 2. Start planning
print("Starting planning...")
plan = engine.run("Build a microservices authentication system")

# 3. Inspect results
print(f"\nPlan complete!")
print(f"ID: {plan.id}")
print(f"Total goals: {len(plan.goals)}")
print(f"Atomic goals: {len(plan.get_atomic_goals())}")
print(f"Max depth: {plan.max_depth}")
print(f"Total tokens: {plan.total_tokens}")

# 4. Show goal tree
def print_tree(plan, goal_id, indent=0):
    goal = plan.get_goal(goal_id)
    prefix = "  " * indent
    status_icon = "✓" if goal.is_atomic() else "↓"
    print(f"{prefix}{status_icon} {goal.description}")
    
    for child_id in goal.child_ids:
        print_tree(plan, child_id, indent + 1)

print("\nGoal Tree:")
print_tree(plan, plan.root_goal_id)

# 5. Plan is auto-saved at .frctl/plans/<plan-id>.json

# 6. Later: Load and continue
loaded = engine.load_plan(plan.id)
print(f"\nLoaded plan: {loaded.get_root_goal().description}")
```

## CLI Usage

```bash
# Start planning (auto-saves)
frctl plan init "Build a REST API for user management"

# Coming soon:
# frctl plan list              # List all plans
# frctl plan status [plan-id]  # Show tree
# frctl plan continue <plan-id> # Resume planning
# frctl plan export <plan-id>  # Export to file
# frctl plan delete <plan-id>  # Delete plan
```

## Troubleshooting

### Plans not saving

Check that `.frctl/plans/` directory is writable:

```python
from pathlib import Path
plans_dir = Path.cwd() / ".frctl" / "plans"
print(f"Plans directory: {plans_dir}")
print(f"Exists: {plans_dir.exists()}")
```

### LLM API errors

Ensure your API key is set:

```bash
echo $OPENAI_API_KEY  # Should show your key
```

For local models, ensure Ollama is running:

```bash
ollama serve
ollama pull codellama
```

### Large plan files

Plans are stored as JSON. Large plans (100+ goals) may be several MB. Consider:
- Archiving completed plans
- Using the Digest Protocol (coming soon) for context compression

## Next Steps

- See [Context Tree Guide](./context-tree.md) for hierarchical context management
- See [Roadmap](../roadmap.md) for upcoming features
- See [PERSISTENCE_COMPLETE.md](../../PERSISTENCE_COMPLETE.md) for implementation details

## Related

- [Context Tree](./context-tree.md) - Hierarchical context management
- [Graph Basics](./graph-basics.md) - Graph architecture
- [Fractal V3 Architecture](../fractal-v3-architecture.md) - Complete specification
