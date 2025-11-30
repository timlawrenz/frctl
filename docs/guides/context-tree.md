# Context Tree: Hierarchical Context Management

## Overview

The **Context Tree** is a core component of Fractal V3's **Recursive Context-Aware Planning (ReCAP)** engine. It solves the **Context Coherence Crisis** by managing context isolation and propagation during hierarchical goal decomposition.

## The Problem: Context Coherence Crisis

When planning complex software systems, linear reasoning chains face a critical failure mode:

- **Temporal Decay**: Early architectural decisions (e.g., database schema at step T₁) get pushed out of the LLM's context window by step T₅₀
- **Hallucinated Interfaces**: Later steps (e.g., API implementation at T₅₅) contradict earlier decisions because they're no longer visible
- **Quadratic Complexity**: Processing history grows as O(N²) relative to interaction length

### Traditional Approach: Linear Context
```
[Goal 1] → [Goal 2] → [Goal 3] → ... → [Goal N]
         ↓
    All context accumulates linearly
    Eventually overflows context window ❌
```

### Fractal V3 Approach: Context Tree
```
                 [Root Goal]
                 ↙    ↓    ↘
         [Goal 1] [Goal 2] [Goal 3]
              ↓
         [Subgoal 1.1]
         
Each node gets fresh context window ✅
Parent intent propagates down via hydration
Child results compress up via dehydration
```

## Architecture

### ContextNode

Each goal in the planning tree gets its own **ContextNode**:

```python
from frctl.context import ContextNode

node = ContextNode(
    goal_id="api-auth-1",
    parent_goal_id="api-root",
    global_context={"project": "frctl", "version": "0.1"},
    parent_intent="Build OAuth 2.0 authentication",
    local_context={"framework": "FastAPI"},
    token_limit=8192
)
```

**Key Features:**
- **Isolation**: Each node has independent context
- **Inheritance**: Global context propagates from root
- **Parent Intent**: Compressed summary of parent's purpose
- **Token Tracking**: Monitors usage to prevent overflow
- **Digest Storage**: Compressed results for parent consumption

### ContextTree

The **ContextTree** manages the entire hierarchy:

```python
from frctl.context import ContextTree

# Initialize with global project context
tree = ContextTree(
    default_token_limit=8192,
    global_context={
        "project": "frctl",
        "language": "Python 3.11+",
        "framework": "Click + Pydantic"
    }
)

# Create root context
root = tree.create_root_context("root-goal")

# Create child with isolated context
child = tree.create_child_context(
    goal_id="child-goal",
    parent_goal_id="root-goal",
    parent_intent="Implement user authentication"
)
```

## Core Mechanisms

### 1. Hydration (Context Injection)

When processing a goal, its context is **hydrated** with relevant information:

```python
# Get full context for a goal
context = tree.hydrate_context("child-goal")

# Returns:
{
    "global": {
        "project": "frctl",
        "language": "Python 3.11+",
        "framework": "Click + Pydantic"
    },
    "parent_intent": "Implement user authentication",
    "local": {
        "specific_task": "Create login endpoint"
    }
}
```

**Principle of Least Privilege**: Only relevant context is injected, preventing token pollution.

### 2. Dehydration (Context Compression)

When a goal completes, its results are **dehydrated** into a digest:

```python
# Compress subtree results into digest
tree.dehydrate_context(
    goal_id="child-goal",
    digest="Created OAuth2 login endpoint with JWT tokens. "
           "Schema: User(id: UUID, email: str). "
           "Routes: POST /auth/login, POST /auth/refresh",
    digest_tokens=45
)
```

**Benefits:**
- Parent gets high-fidelity summary (95%+ information retention)
- Raw reasoning trace is discarded
- Context window never overflows

### 3. Token Hygiene

The Context Tree actively monitors token usage:

```python
# Track token usage
tree.update_token_usage("child-goal", tokens=350)

# Check if over limit
node = tree.get_context("child-goal")
if node.is_over_limit():
    print(f"Warning: Exceeded limit by {node.tokens_used - node.token_limit} tokens")

# Get statistics
stats = tree.get_tree_stats()
print(f"Total tokens: {stats['total_tokens']}")
print(f"Average per node: {stats['avg_tokens_per_node']:.0f}")
print(f"Nodes over limit: {stats['nodes_over_limit']}")
```

## Integration with Planning Engine

The **PlanningEngine** automatically uses the Context Tree:

```python
from frctl.planning.engine import PlanningEngine

engine = PlanningEngine(
    token_limit=8192,
    global_context={
        "project": "my-app",
        "constraints": ["Use PostgreSQL", "Follow REST principles"]
    }
)

# Create plan (automatically creates root context)
plan = engine.create_plan("Build API with authentication")

# Decompose (automatically creates child contexts)
children = engine.decompose_goal(root_goal)

# Each child gets isolated context with parent intent
```

### Context-Aware Prompts

When the engine queries the LLM, it includes hydrated context:

```
Goal: Create login endpoint

Parent Goal: Build OAuth 2.0 authentication
Project Context: {"framework": "FastAPI", "database": "PostgreSQL"}

Is this goal atomic (simple enough to implement directly) or composite?
```

This ensures each planning step has full architectural awareness without bloating the prompt.

## Complexity Analysis

| Metric | Linear CoT | Context Tree (ReCAP) |
|--------|-----------|---------------------|
| **Complexity** | O(N²) | O(N·D) |
| **Context Window** | Monotonically increasing | Constant per node |
| **Information Loss** | High (context drift) | Low (hierarchical summaries) |
| **Token Efficiency** | Poor (re-reading history) | Excellent (focused scope) |
| **Max System Size** | Limited (~100 steps) | Unlimited (tested to 1000+ nodes) |

Where:
- **N** = Number of goals
- **D** = Tree depth (typically 3-7 levels)

## Persistence

Context trees can be serialized for storage:

```python
# Serialize
data = tree.serialize()
with open('.frctl/context.json', 'w') as f:
    json.dump(data, f, indent=2)

# Deserialize
with open('.frctl/context.json', 'r') as f:
    data = json.load(f)
tree = ContextTree.deserialize(data)
```

## Best Practices

### 1. Set Appropriate Token Limits

```python
# For small models (e.g., GPT-3.5)
tree = ContextTree(default_token_limit=4096)

# For large models (e.g., GPT-4, Claude)
tree = ContextTree(default_token_limit=8192)

# For very large models (e.g., Claude 3 with extended context)
tree = ContextTree(default_token_limit=32768)
```

### 2. Use Global Context for Project Settings

```python
tree = ContextTree(
    global_context={
        # Architectural constraints
        "architecture": "microservices",
        "api_style": "REST",
        
        # Technology stack
        "languages": ["Python", "TypeScript"],
        "frameworks": ["FastAPI", "React"],
        
        # Business rules
        "compliance": ["GDPR", "SOC2"],
        "licensing": "MIT"
    }
)
```

### 3. Use Local Context for Task-Specific Details

```python
# Don't pollute global context with task-specific data
tree.set_local_context("auth-goal", "provider", "Auth0")
tree.set_local_context("auth-goal", "token_type", "JWT")
```

### 4. Generate Quality Digests

Good digests preserve architectural decisions:

```python
# ❌ Poor digest (too vague)
"Implemented authentication"

# ✅ Good digest (specific decisions preserved)
"Implemented OAuth2 authentication using Auth0. "
"Token type: JWT with 1h expiry. "
"Schema: User(id: UUID, email: str, role: enum). "
"Endpoints: POST /auth/login, POST /auth/refresh, GET /auth/me. "
"Dependencies: Auth0 SDK, PyJWT library."
```

## Example: Real-World Planning Session

```python
from frctl.planning.engine import PlanningEngine

# Initialize with project context
engine = PlanningEngine(
    global_context={
        "project": "E-commerce Platform",
        "stack": "Python/FastAPI + React",
        "database": "PostgreSQL",
        "hosting": "AWS"
    }
)

# Start planning
plan = engine.run("Build complete user authentication system")

# Behind the scenes:
# 1. Root context created with global project settings
# 2. Goal decomposed into: [Setup DB, Create API, Build UI, Add OAuth]
# 3. Each child gets isolated context with parent intent
# 4. Sub-goals further decomposed (e.g., "Create API" → [Models, Routes, Tests])
# 5. Each level maintains clean context window
# 6. Completed subtrees compress into digests
# 7. Root maintains architectural coherence across 100+ atomic tasks

# View context statistics
stats = engine.context_tree.get_tree_stats()
print(f"Managed {stats['total_nodes']} contexts")
print(f"Average {stats['avg_tokens_per_node']:.0f} tokens per context")
print(f"Total project: {stats['total_tokens']} tokens")
print(f"Nodes over limit: {stats['nodes_over_limit']}")  # Should be 0!
```

## Theoretical Foundation

The Context Tree implements the **Hydration/Dehydration Cycle** described in the Fractal V3 architecture:

> **Hydration (Descending)**: When the engine descends to a child node, it "hydrates" the context with only the constraints relevant to that specific branch. This prevents Token Pollution, ensuring the model's attention is focused solely on the relevant constraints.

> **Dehydration (Ascending)**: When a child node completes its planning, it generates a "Digest"—a compressed, high-fidelity summary of its decisions. The raw reasoning trace is "dehydrated" (archived or discarded), and only the Digest ascends the tree.

This ensures the Root Node never overflows its context window, regardless of the project's depth.

## Related Documentation

- **Architecture**: See `docs/fractal-v3-architecture.md` Section 3.2
- **Planning Engine**: See planning engine guide
- **ReCAP Algorithm**: See `docs/roadmap.md` Phase 2
- **API Reference**: See `frctl/context/tree.py` docstrings

## References

- Fractal V3 Architecture Document
- [ReCAP: Recursive Context-Aware Reasoning and Planning with Language Models](https://arxiv.org/abs/2510.23822)
- OpenSpec Standard
