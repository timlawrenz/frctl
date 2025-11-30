# Change: Add ReCAP Planning Engine

## Why

Phase 1 established the Federated Graph for managing horizontal coupling (component dependencies). Phase 2 addresses the vertical dimension: hierarchical goal decomposition through Recursive Context-Aware Planning (ReCAP).

The Context Coherence Crisis occurs when linear reasoning chains exceed the LLM's context window, causing architectural decisions to become disjointed. ReCAP solves this by:
1. **Recursive decomposition** - Breaking complex goals into atomic tasks
2. **Context isolation** - Each subtask gets a fresh context window
3. **Hydration/Dehydration** - Minimizing token usage while preserving intent
4. **Digest protocol** - Compressing results for parent contexts

This change implements the planning engine that transforms high-level goals into executable architectural plans, maintaining coherence across arbitrarily deep planning trees.

## What Changes

**Completed:**
- ✅ Implement Context Tree for hierarchical context management
- ✅ Add hydration/dehydration protocol for token hygiene
- ✅ Create LLM provider abstraction layer
- ✅ Implement atomicity detection using LLM reasoning
- ✅ Implement parent-child context propagation
- ✅ Add recursive planning engine with goal decomposition algorithm (basic version)

**In Progress:**
- 🔄 Add planning state persistence to `.frctl/plans/`
- 🔄 Create CLI commands for planning workflows
- 🔄 Add digest generation for context compression
- 🔄 Prompt templates with Jinja2

## Impact

### Affected specs
- **NEW**: `planning-core` - ReCAP planning engine and context management

### Affected code
- New package: `frctl/planning/` - Planning engine and goal management
- New package: `frctl/context/` - Context tree and hydration logic
- New package: `frctl/llm/` - LLM provider abstraction
- Updated: `frctl/__main__.py` - Add plan command group
- Updated: `pyproject.toml` - Add LLM SDK dependencies

### Breaking Changes
None - this is a new capability building on Phase 1's graph foundation.

## Dependencies

- litellm >= 1.0 (Unified LLM interface for 100+ providers, includes token counting)
- jinja2 >= 3.0 (Prompt templating)

## Technical Notes

This proposal follows Phase 2 of the implementation roadmap (see `docs/roadmap.md`). The planning engine uses the Federated Graph from Phase 1 as its state store - plans decompose into goals that reference graph nodes, ensuring consistency between planning and architecture.

**LLM Provider Strategy**: We use LiteLLM as a unified interface to support maximum openness and flexibility:
- Supports 100+ providers (OpenAI, Anthropic, Cohere, Together, Azure, etc.)
- Supports local models (Ollama, vLLM, OpenLLM)
- Built-in retry logic, fallback chains, and rate limiting
- Automatic token counting across all providers
- Cost tracking and observability
- No vendor lock-in - users choose their preferred provider

This aligns with Fractal V3's philosophy of transparency and determinism while giving users complete control over their LLM provider choice.

ReCAP implements the theoretical foundation described in the Fractal V3 architecture document:
- Recursive decomposition with atomicity detection
- Context Tree with O(N·D) complexity vs O(N²) for linear CoT
- Hydration/Dehydration for token hygiene
- Digest protocol for information preservation

The design intentionally defers execution (Phase 4) - this phase focuses purely on planning and architectural specification, maintaining the separation between "what to build" and "how to build it."

Future phases will add:
- Tandem Protocol for human approval (Phase 3)
- Execution engine with transactional safety (Phase 4)
- Drift detection and reconciliation (Phase 4)
