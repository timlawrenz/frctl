# Plan JSON Schema

Complete reference for the frctl planning data format.

## Overview

Plans are persisted as JSON files in `.frctl/plans/<plan-id>.json`. This format enables:
- **Portability**: Plans can be shared, versioned, and backed up
- **Inspectability**: Human-readable planning state
- **Integration**: Easy parsing by external tools
- **Resume**: Plans can be paused and resumed
- **Versioning**: Track planning progress over time

---

## Schema Version

**Current Version**: 1.0  
**Format**: JSON  
**Encoding**: UTF-8  
**File Location**: `.frctl/plans/<plan-id>.json`

---

## Top-Level Structure

```json
{
    "id": string,
    "root_goal_id": string,
    "goals": object,
    "created_at": string (ISO 8601),
    "updated_at": string (ISO 8601),
    "status": enum,
    "total_tokens": integer,
    "max_depth": integer,
    "description": string (optional)
}
```

### Field Definitions

#### `id` (string, required)
Unique identifier for the plan (8-character hex).

**Example**: `"0398a958"`

**Generation**: Auto-generated using first 8 chars of UUID4.

#### `root_goal_id` (string, required)
Reference to the root goal in the `goals` map.

**Example**: `"0398a958-root"`

**Format**: `<plan-id>-root`

#### `goals` (object, required)
Map of goal IDs to Goal objects (see Goal Schema below).

**Example**:
```json
{
    "0398a958-root": { /* Goal object */ },
    "0398a958-g1": { /* Goal object */ },
    "0398a958-g2": { /* Goal object */ }
}
```

**Structure**: Flat map (not nested). Hierarchy via `parent_id` and `child_ids`.

#### `created_at` (string, required)
Timestamp when plan was created.

**Format**: ISO 8601 with timezone  
**Example**: `"2025-11-30T17:27:47.714794Z"`

#### `updated_at` (string, required)
Timestamp when plan was last modified.

**Format**: ISO 8601 with timezone  
**Example**: `"2025-11-30T12:27:47.714827-05:00"`

**Note**: Updates on any goal status change, decomposition, or completion.

#### `status` (enum, required)
Overall plan status.

**Values**:
- `"in_progress"`: Planning is ongoing
- `"complete"`: All atomic goals identified
- `"paused"`: Planning manually paused
- `"failed"`: Unrecoverable error occurred

**Example**: `"in_progress"`

#### `total_tokens` (integer, required)
Total LLM tokens consumed across all goals.

**Example**: `42538`

**Usage**: Cost tracking and optimization.

#### `max_depth` (integer, required)
Deepest level reached in the planning tree.

**Example**: `3`

**Usage**: Complexity metric and depth limit enforcement.

#### `description` (string, optional)
Human-readable description of the plan.

**Example**: `"Build user authentication system"`

**Default**: Root goal's description if not specified.

---

## Goal Schema

Each goal in the `goals` map has this structure:

```json
{
    "id": string,
    "description": string,
    "status": enum,
    "parent_id": string | null,
    "child_ids": array,
    "depth": integer,
    "created_at": string,
    "updated_at": string,
    "reasoning": string | null,
    "digest": object | null,
    "tokens_used": integer,
    "dependencies": array,
    "graph_node_id": string | null
}
```

### Field Definitions

#### `id` (string, required)
Unique identifier for this goal.

**Format**: `<plan-id>-<suffix>`  
**Example**: `"0398a958-g1"`

**Root**: Uses suffix `-root` (e.g., `"0398a958-root"`)

#### `description` (string, required)
Natural language description of what to accomplish.

**Example**: `"Implement JWT authentication for API endpoints"`

**Guidelines**:
- Specific and actionable
- 1-2 sentences
- Focuses on the "what", not "how"

#### `status` (enum, required)
Current state of the goal.

**Values**:
- `"pending"`: Not yet assessed
- `"decomposing"`: Currently being broken down
- `"atomic"`: Identified as implementable directly
- `"complete"`: Implementation finished
- `"failed"`: Could not be completed

**Transitions**:
```
pending → decomposing → atomic → complete
        ↓
        atomic (if simple enough)
```

#### `parent_id` (string | null, required)
Reference to parent goal, or `null` for root.

**Example**: `"0398a958-root"`

**Root Goal**: Always has `parent_id: null`

#### `child_ids` (array, required)
List of direct child goal IDs.

**Example**: `["0398a958-g1", "0398a958-g2", "0398a958-g3"]`

**Leaf Goals**: Empty array `[]`

**Order**: Implicit execution order (dependencies via sequence).

#### `depth` (integer, required)
Level in the planning tree (0 = root).

**Example**: `2`

**Calculation**: Parent's depth + 1

**Usage**: Depth limit enforcement, visualization.

#### `created_at` (string, required)
Timestamp when goal was created.

**Format**: ISO 8601  
**Example**: `"2025-11-30T17:27:47.714790Z"`

#### `updated_at` (string, required)
Timestamp when goal was last modified.

**Format**: ISO 8601  
**Example**: `"2025-11-30T17:27:47.714791Z"`

#### `reasoning` (string | null, optional)
LLM's explanation for atomicity or decomposition decision.

**Example**: `"This is a focused task that can be implemented in a single component with ~100 lines of code"`

**Null**: When no LLM assessment performed yet.

**Usage**: Debugging, audit trail, understanding LLM decisions.

#### `digest` (object | null, optional)
Compressed summary of completed work (see Digest Schema below).

**Example**:
```json
{
    "summary": "Authentication endpoints implemented with JWT",
    "key_decisions": ["Chose RS256 for better rotation"],
    "artifacts": ["auth/jwt.py", "auth/routes.py"]
}
```

**Null**: For incomplete or atomic goals.

#### `tokens_used` (integer, required)
LLM tokens consumed for this goal (atomicity check + decomposition).

**Example**: `1250`

**Usage**: Cost tracking per goal.

#### `dependencies` (array, required)
List of goal IDs that must complete before this one.

**Example**: `["0398a958-g1", "0398a958-g2"]`

**Empty**: `[]` if no dependencies.

**Note**: Currently populated via dependency inference LLM call.

#### `graph_node_id` (string | null, optional)
Reference to corresponding node in the architectural graph.

**Example**: `"node-123"`

**Null**: If not linked to graph.

**Usage**: Bi-directional linking between planning and architecture.

---

## Digest Schema

Digests compress completed goal information:

```json
{
    "summary": string,
    "key_decisions": array,
    "artifacts": array,
    "compression_ratio": float (optional),
    "fidelity_score": float (optional)
}
```

### Field Definitions

#### `summary` (string, required)
Concise description of what was accomplished (2-3 sentences).

**Example**: `"Authentication system complete with JWT (RS256) and session management. All endpoints implemented and tested."`

**Target**: <100 words, 95%+ information fidelity.

#### `key_decisions` (array, required)
Important architectural or implementation choices.

**Example**:
```json
[
    "Chose RS256 over HS256 for better key rotation support",
    "Implemented sliding session expiration (30 min idle, 24hr max)"
]
```

**Guidelines**: Only significant decisions, not routine choices.

#### `artifacts` (array, required)
Main deliverables (files, components, APIs).

**Example**:
```json
[
    "auth/jwt.py",
    "auth/middleware.py",
    "auth/routes.py"
]
```

**Guidelines**: Key outputs, not every file touched.

#### `compression_ratio` (float, optional)
Ratio of digest size to original content size.

**Example**: `0.18` (digest is 18% of original)

**Usage**: Quality metric for digest algorithm.

#### `fidelity_score` (float, optional)
Estimated information retention (0.0-1.0).

**Example**: `0.97` (97% fidelity)

**Target**: ≥0.95 for production use.

---

## Complete Example

```json
{
    "id": "a1b2c3d4",
    "root_goal_id": "a1b2c3d4-root",
    "description": "Build user authentication system",
    "status": "in_progress",
    "created_at": "2025-11-30T10:00:00Z",
    "updated_at": "2025-11-30T10:15:00Z",
    "total_tokens": 8750,
    "max_depth": 2,
    "goals": {
        "a1b2c3d4-root": {
            "id": "a1b2c3d4-root",
            "description": "Build user authentication system",
            "status": "decomposing",
            "parent_id": null,
            "child_ids": ["a1b2c3d4-g1", "a1b2c3d4-g2", "a1b2c3d4-g3"],
            "depth": 0,
            "created_at": "2025-11-30T10:00:00Z",
            "updated_at": "2025-11-30T10:05:00Z",
            "reasoning": "Complex system requiring multiple components: data model, API, and security",
            "digest": null,
            "tokens_used": 1200,
            "dependencies": [],
            "graph_node_id": "auth-system"
        },
        "a1b2c3d4-g1": {
            "id": "a1b2c3d4-g1",
            "description": "Create user model with password hashing",
            "status": "complete",
            "parent_id": "a1b2c3d4-root",
            "child_ids": [],
            "depth": 1,
            "created_at": "2025-11-30T10:05:00Z",
            "updated_at": "2025-11-30T10:10:00Z",
            "reasoning": "Focused task, single file, standard pattern with bcrypt",
            "digest": {
                "summary": "User model created with bcrypt password hashing and email validation",
                "key_decisions": [
                    "Used bcrypt with cost factor 12 for security/performance balance",
                    "Email field unique and indexed for fast lookup"
                ],
                "artifacts": ["models/user.py", "migrations/001_create_users.sql"],
                "compression_ratio": 0.15,
                "fidelity_score": 0.98
            },
            "tokens_used": 850,
            "dependencies": [],
            "graph_node_id": "user-model"
        },
        "a1b2c3d4-g2": {
            "id": "a1b2c3d4-g2",
            "description": "Implement JWT authentication endpoints",
            "status": "atomic",
            "parent_id": "a1b2c3d4-root",
            "child_ids": [],
            "depth": 1,
            "created_at": "2025-11-30T10:05:00Z",
            "updated_at": "2025-11-30T10:12:00Z",
            "reasoning": "Standard JWT implementation with login/logout endpoints",
            "digest": null,
            "tokens_used": 920,
            "dependencies": ["a1b2c3d4-g1"],
            "graph_node_id": "auth-endpoints"
        },
        "a1b2c3d4-g3": {
            "id": "a1b2c3d4-g3",
            "description": "Add session management middleware",
            "status": "pending",
            "parent_id": "a1b2c3d4-root",
            "child_ids": [],
            "depth": 1,
            "created_at": "2025-11-30T10:05:00Z",
            "updated_at": "2025-11-30T10:05:00Z",
            "reasoning": null,
            "digest": null,
            "tokens_used": 0,
            "dependencies": ["a1b2c3d4-g2"],
            "graph_node_id": null
        }
    }
}
```

---

## Plan Index

The plan index (`.frctl/plans/index.json`) tracks all plans:

```json
{
    "plans": [
        {
            "id": "a1b2c3d4",
            "description": "Build user authentication system",
            "status": "in_progress",
            "created_at": "2025-11-30T10:00:00Z",
            "updated_at": "2025-11-30T10:15:00Z",
            "total_goals": 4,
            "atomic_goals": 2,
            "complete_goals": 1
        }
    ],
    "last_updated": "2025-11-30T10:15:00Z"
}
```

**Usage**: Quick listing without loading full plan files.

---

## Versioning & Migration

### Version 1.0 (Current)

Initial stable schema.

### Future Versions

Schema changes will:
1. Increment version number in plan file
2. Provide migration utilities (`frctl plan migrate`)
3. Support reading older versions
4. Document breaking changes

**Backward Compatibility**: Reader supports older schemas, writer uses latest.

---

## Validation

### JSON Schema

A formal JSON Schema is available at `schemas/plan-v1.schema.json` for validation.

**Usage**:
```bash
# Validate a plan file
jsonschema -i .frctl/plans/a1b2c3d4.json schemas/plan-v1.schema.json
```

### Python Validation

```python
from frctl.planning.persistence import PlanStore

store = PlanStore()
plan = store.load("a1b2c3d4")

# Automatically validates on load
# Raises ValueError if invalid
```

---

## Best Practices

### File Management

✅ **Do**:
- Keep plans under version control
- Back up `.frctl/plans/` directory
- Use plan IDs in commit messages
- Archive completed plans

❌ **Don't**:
- Manually edit plan JSON (use CLI)
- Share plans with absolute paths
- Store sensitive data in descriptions
- Delete plans (archive instead)

### Performance

**Large Plans** (>100 goals):
- Index loads only metadata
- Goals lazy-loaded on demand
- Digests reduce memory usage
- Consider splitting very large plans

**Token Limits**:
- Monitor `total_tokens` field
- Set budget limits in configuration
- Use aggressive digest compression
- Review high-token goals for optimization

---

## Integration Examples

### Reading Plans Programmatically

```python
import json

# Load plan
with open('.frctl/plans/a1b2c3d4.json') as f:
    plan = json.load(f)

# Access goals
root = plan['goals'][plan['root_goal_id']]
print(f"Root goal: {root['description']}")

# Find atomic goals
atomic = [g for g in plan['goals'].values() if g['status'] == 'atomic']
print(f"Atomic goals: {len(atomic)}")

# Calculate progress
total = len(plan['goals'])
complete = len([g for g in plan['goals'].values() if g['status'] == 'complete'])
print(f"Progress: {complete}/{total} ({100*complete/total:.1f}%)")
```

### Exporting to Other Formats

```python
from frctl.planning.persistence import PlanStore

store = PlanStore()
plan = store.load("a1b2c3d4")

# Export to JSON (with custom formatting)
store.export(plan.id, "plan.json")

# Export to Markdown (TODO)
# store.export(plan.id, "plan.md", format="markdown")

# Export to GraphML (TODO)
# store.export(plan.id, "plan.graphml", format="graphml")
```

---

## Troubleshooting

### Issue: Plan won't load

**Check**:
1. Valid JSON syntax
2. Required fields present
3. ID references valid
4. Timestamps in ISO 8601 format

**Fix**:
```bash
# Validate JSON
python3 -m json.tool < .frctl/plans/a1b2c3d4.json

# Load with error details
frctl plan status a1b2c3d4 --debug
```

### Issue: Circular dependencies

**Symptom**: Goals reference each other circularly in `dependencies`.

**Detection**: Automatic during load (raises error).

**Fix**: Remove circular references manually or recreate plan.

### Issue: Orphaned goals

**Symptom**: Goals with `parent_id` not in `goals` map.

**Detection**: Validation catches on load.

**Fix**: Remove orphaned goals or add missing parents.

---

## References

- **Specification**: `openspec/changes/add-recap-engine/specs/`
- **Code**: `frctl/planning/goal.py`, `frctl/planning/persistence.py`
- **Tests**: `tests/planning/test_persistence.py`
- **Examples**: `.frctl/plans/` (after running `frctl plan init`)

---

**Need Help?**

- Run `frctl plan status <plan-id> --verbose` for detailed plan inspection
- Check logs in `.frctl/logs/` for error details
- See troubleshooting guide: `docs/guides/troubleshooting.md`
