# Prompt Engineering Guide

This guide explains how frctl uses LLM prompts to power the ReCAP (Recursive Context-Aware Planning) engine, and how you can customize them for your specific needs.

## Overview

Frctl uses **Jinja2 templates** for all LLM prompts, enabling:
- **Consistency**: Same prompt structure across all LLM calls
- **Maintainability**: Easy to update and version prompts
- **Context injection**: Dynamic context from parent goals and global settings
- **Customization**: Override templates for domain-specific planning

## Prompt Architecture

### Template System

All prompts are located in `frctl/llm/prompts/`:

```
frctl/llm/prompts/
├── system_base.j2           # System-level instructions (shared)
├── atomicity_check.j2       # Determine if goal is atomic
├── decompose_goal.j2        # Break goal into sub-goals
├── infer_dependencies.j2    # Find dependencies between goals
└── generate_digest.j2       # Compress completed work
```

### Prompt Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. ATOMICITY CHECK                                      │
│    Input: Goal description + context                    │
│    Output: {is_atomic: bool, reasoning: str}           │
│                                                          │
│    Decision: Is this goal simple enough to implement?   │
└─────────────────────────────────────────────────────────┘
                         │
                         ├─ TRUE → Mark as atomic (ready to implement)
                         │
                         └─ FALSE ↓
┌─────────────────────────────────────────────────────────┐
│ 2. GOAL DECOMPOSITION                                   │
│    Input: Complex goal + context                        │
│    Output: {sub_goals: [Goal], reasoning: str}         │
│                                                          │
│    Action: Break into 2-7 concrete sub-goals           │
└─────────────────────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 3. DEPENDENCY INFERENCE (optional)                      │
│    Input: List of sibling sub-goals                     │
│    Output: {dependencies: [{from: id, to: id}]}        │
│                                                          │
│    Action: Identify execution order dependencies        │
└─────────────────────────────────────────────────────────┘
                         │
                         ↓ (Recursively repeat for each sub-goal)
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 4. DIGEST GENERATION (when sub-tree complete)          │
│    Input: Completed goal + child results               │
│    Output: {summary: str, key_decisions: [str]}        │
│                                                          │
│    Action: Compress information for parent context      │
└─────────────────────────────────────────────────────────┘
```

---

## 1. System Prompt (system_base.j2)

**Purpose**: Establish the LLM's role and constraints for all planning tasks.

**Template**:
```jinja2
You are an AI assistant for Fractal V3, an advanced software planning 
and architecture system.

## Core Principles

1. **Recursive Decomposition**: Break complex goals into simpler sub-goals
2. **Context Awareness**: Each goal operates in isolated context with parent intent
3. **Atomicity Focus**: Identify when goals are simple enough to implement directly
4. **Determinism**: Provide consistent, reproducible reasoning

## Your Role

You help decompose high-level software goals into executable architectural 
plans by:
- Assessing goal complexity and atomicity
- Breaking down composite goals into concrete sub-goals
- Maintaining context coherence across planning depth
- Generating compressed digests of completed work

Always respond with valid JSON structures as specified in each prompt.
```

**Design Decisions**:
- **Fractal V3 context**: Establishes domain knowledge
- **Core principles**: Guides decision-making
- **JSON-only output**: Ensures parseable responses
- **Determinism emphasis**: Reduces variability across runs

**Customization Tips**:
```jinja2
{# Add domain-specific context #}
You specialize in {{ domain }} architecture (e.g., "web applications", "embedded systems")

{# Add organization constraints #}
Follow {{ company_name }} coding standards and best practices

{# Add technology constraints #}
All solutions should use {{ tech_stack }} (e.g., "Python and FastAPI")
```

---

## 2. Atomicity Check (atomicity_check.j2)

**Purpose**: Determine if a goal is simple enough to implement directly.

**Key Criteria**:
1. **Scope**: Single file/component (~50-200 LOC)
2. **Complexity**: Single system/concern
3. **Dependencies**: No blocking prerequisites
4. **Clarity**: Specific enough to implement

**Template Variables**:
```python
{
    "goal_description": str,      # Required: The goal to analyze
    "parent_intent": str | None,  # Optional: Parent goal for context
    "global_context": str | None  # Optional: Project-wide context
}
```

**Response Format**:
```json
{
    "is_atomic": true,
    "reasoning": "Brief explanation (1-2 sentences)"
}
```

**Examples**:

✅ **Atomic Goals**:
```
"Add JWT authentication to /login endpoint"
→ is_atomic: true
→ reasoning: "Single endpoint with standard auth pattern, ~100 LOC"

"Write unit tests for UserService.create_user()"
→ is_atomic: true
→ reasoning: "Focused test coverage for one method, straightforward"

"Fix bug in payment validation regex"
→ is_atomic: true
→ reasoning: "Isolated fix in single function"
```

❌ **Composite Goals**:
```
"Build user authentication system"
→ is_atomic: false
→ reasoning: "Needs registration, login, password reset, session management, etc."

"Implement data export feature"
→ is_atomic: false
→ reasoning: "Requires format selection, data filtering, async processing, download UI"

"Add caching to improve performance"
→ is_atomic: false
→ reasoning: "Needs cache strategy, invalidation, monitoring, integration across layers"
```

**Customization Examples**:

```jinja2
{# Stricter atomicity (smaller tasks) #}
- **Atomic**: Can be implemented in ~25-50 lines of code
- **Atomic**: Takes < 30 minutes to implement

{# Domain-specific criteria #}
- **Atomic**: Single React component with < 3 props
- **Atomic**: Single SQL migration file
- **Atomic**: Single Terraform resource definition

{# Team-specific criteria #}
- **Atomic**: Junior developer can implement with minimal guidance
- **Atomic**: No cross-team dependencies
```

---

## 3. Goal Decomposition (decompose_goal.j2)

**Purpose**: Break complex goals into 2-7 concrete sub-goals.

**Decomposition Patterns**:

### Pattern 1: Architectural Layers
```
"Implement user profile feature"
→ 1. "Create user profile data model with validation"
→ 2. "Implement profile CRUD API endpoints"
→ 3. "Add profile edit UI components"
→ 4. "Implement profile image upload"
```

### Pattern 2: Setup → Core → Polish
```
"Add search functionality"
→ 1. "Set up search index infrastructure"
→ 2. "Implement core search query logic"
→ 3. "Add search result ranking"
→ 4. "Create search UI with autocomplete"
```

### Pattern 3: Read → Write → Validate
```
"Implement data export"
→ 1. "Create export format selection UI"
→ 2. "Implement CSV export generation"
→ 3. "Add data filtering options"
→ 4. "Implement async export processing"
```

**Template Variables**:
```python
{
    "goal_description": str,      # Required: Goal to decompose
    "parent_intent": str | None,  # Optional: Parent context
    "global_context": str | None  # Optional: Project context
}
```

**Response Format**:
```json
{
    "sub_goals": [
        {"description": "First concrete sub-goal"},
        {"description": "Second concrete sub-goal"}
    ],
    "reasoning": "Decomposition strategy (1-2 sentences)"
}
```

**Quality Guidelines**:

✅ **Good Sub-Goals**:
- Specific and actionable
- 2-7 sub-goals (sweet spot: 3-5)
- Each simpler than parent
- Together fully address parent
- Implicit ordering (dependencies through sequence)

❌ **Poor Sub-Goals**:
- Too vague: "Handle edge cases"
- Too many: 15 sub-goals (too granular)
- Overlapping: "Add validation" + "Add input checking"
- Missing pieces: Forgot error handling
- Circular: Goals that depend on each other

**Customization Examples**:

```jinja2
{# Backend-focused decomposition #}
Common patterns:
- **API + Service + Repository**: Separate HTTP, business logic, data access
- **Model + Migration + Seeder**: For database changes

{# Frontend-focused decomposition #}
Common patterns:
- **Component + Hook + Context**: React component patterns
- **View + ViewModel + Model**: MVVM architecture

{# DevOps-focused decomposition #}
Common patterns:
- **Infrastructure + Config + Deploy**: Separate concerns
- **Build + Test + Release**: CI/CD pipeline stages
```

---

## 4. Dependency Inference (infer_dependencies.j2)

**Purpose**: Identify execution order dependencies between sibling goals.

**When Used**: After decomposition, to determine which sub-goals must complete before others.

**Template Variables**:
```python
{
    "goals": List[Dict],          # List of sibling goals with ids and descriptions
    "parent_intent": str | None,  # Parent goal for context
    "global_context": str | None  # Project context
}
```

**Response Format**:
```json
{
    "dependencies": [
        {"from": "goal-1", "to": "goal-2"},  // goal-2 depends on goal-1
        {"from": "goal-1", "to": "goal-3"}
    ],
    "reasoning": "Dependency rationale"
}
```

**Examples**:

```
Goals:
  1. "Create database schema"
  2. "Implement business logic"
  3. "Add API endpoints"
  4. "Write integration tests"

Dependencies:
  1 → 2  (logic needs schema)
  2 → 3  (API needs logic)
  3 → 4  (tests need API)
```

**Customization**: Focus on your domain's dependency patterns (e.g., infrastructure before code, models before controllers).

---

## 5. Digest Generation (generate_digest.j2)

**Purpose**: Compress completed work into concise summaries for parent context.

**Why Important**:
- Prevents token limit issues as planning depth increases
- Provides clean context for sibling goals
- Maintains information fidelity while reducing size

**Template Variables**:
```python
{
    "goal_description": str,      # The completed goal
    "result_summary": str,        # What was accomplished
    "child_digests": List[str],   # Digests from child goals
    "global_context": str | None  # Project context
}
```

**Response Format**:
```json
{
    "summary": "Concise summary of what was accomplished (2-3 sentences)",
    "key_decisions": [
        "Important decision or insight #1",
        "Important decision or insight #2"
    ],
    "artifacts": [
        "Key file or component created"
    ]
}
```

**Example**:

```
Input:
  Goal: "Implement user authentication system"
  Child results: [
    "JWT auth implemented with RS256",
    "Login/logout endpoints created",
    "Session middleware added",
    "Password reset flow complete"
  ]

Digest:
{
    "summary": "Authentication system complete with JWT (RS256) and session management. All endpoints implemented and tested.",
    "key_decisions": [
        "Chose RS256 over HS256 for better key rotation support",
        "Implemented sliding session expiration (30 min idle, 24hr max)"
    ],
    "artifacts": [
        "auth/jwt.py",
        "auth/middleware.py",
        "auth/routes.py"
    ]
}
```

**Compression Targets**:
- **Summary**: 95%+ fidelity with <20% tokens
- **Key decisions**: Only architectural/important choices
- **Artifacts**: Main deliverables, not all files

---

## Best Practices

### 1. Prompt Design

✅ **Do**:
- Be explicit about output format (JSON schema)
- Provide concrete examples
- State constraints clearly (e.g., "2-7 sub-goals")
- Use consistent terminology
- Test prompts with multiple LLMs

❌ **Don't**:
- Ask open-ended questions
- Allow freeform text responses
- Assume domain knowledge
- Mix multiple tasks in one prompt
- Forget error cases

### 2. Context Management

**Hierarchical Context**:
```
Global Context (project-wide)
  ↓
Parent Intent (from parent goal)
  ↓
Local Context (current goal)
```

**Keep Global Context Lean**:
```python
# ✅ Good global context
{
    "project": "E-commerce platform",
    "tech_stack": "Python + FastAPI + PostgreSQL",
    "constraints": ["GDPR compliant", "< 200ms API response"]
}

# ❌ Too verbose global context
{
    "project": "...",
    "entire_codebase": "...",  # Wastes tokens
    "all_requirements": "..."   # Too much
}
```

### 3. Testing Prompts

**Test Matrix**:
```
Goals to test:
├── Very simple (should be atomic)
├── Complex (should decompose)
├── Ambiguous (test error handling)
└── Domain-specific (test accuracy)

LLMs to test:
├── GPT-4 (baseline)
├── Claude 3.5 Sonnet
├── Gemini 1.5 Pro
└── Your primary model
```

### 4. Customization Workflow

1. **Copy template**: `cp atomicity_check.j2 atomicity_check_custom.j2`
2. **Modify**: Add domain-specific criteria
3. **Test**: Run with sample goals
4. **Configure**: Point frctl to custom templates
5. **Version**: Track in git with your project

---

## Advanced Topics

### Custom Template Directory

```python
from frctl.planning.engine import PlanningEngine
from frctl.llm.renderer import PromptRenderer

# Use custom prompt templates
renderer = PromptRenderer(template_dir="/path/to/custom/prompts")
engine = PlanningEngine(prompt_renderer=renderer)
```

### Multi-Language Support

```jinja2
{# Localize prompts #}
{% if language == "es" %}
Eres un arquitecto de software experto...
{% else %}
You are an expert software architect...
{% endif %}
```

### Domain-Specific Prompts

```jinja2
{# Machine learning project #}
Common patterns:
- **Data + Model + Evaluation**: Separate data prep, training, validation
- **Experiment + Baseline + Production**: Dev workflow stages

{# Mobile app development #}
Common patterns:
- **UI + State + Navigation**: Component architecture
- **Feature + Permission + Analytics**: Feature implementation
```

---

## Troubleshooting

### Issue: LLM returns non-JSON

**Solution**: Add format enforcement
```jinja2
Respond with ONLY this JSON structure (no markdown, no code blocks, no explanation):
{"is_atomic": true, "reasoning": "..."}
```

### Issue: Inconsistent decomposition quality

**Solution**: Add more examples and constraints
```jinja2
BAD examples:
- "Handle edge cases" (too vague)
- 15 sub-goals (too granular)

GOOD examples:
- "Validate email format in registration form" (specific)
- 3-5 sub-goals (right granularity)
```

### Issue: Token limits exceeded

**Solution**: Aggressive digest compression
```jinja2
Summary must be < 100 words. Focus only on:
1. What was built
2. Critical decisions
3. Key artifacts
```

---

## Resources

- **Jinja2 Documentation**: https://jinja.palletsprojects.com/
- **LiteLLM Providers**: https://docs.litellm.ai/docs/providers
- **Prompt Engineering Guide**: https://www.promptingguide.ai/
- **Frctl Examples**: `docs/examples/`

---

**Next Steps**:
- Review existing templates in `frctl/llm/prompts/`
- Test with your domain's goals
- Create custom templates if needed
- Share improvements with the community!
