# Tasks: Add ReCAP Planning Engine

## 1. Setup & Dependencies

- [x] 1.1 Add litellm >= 1.0 to pyproject.toml dependencies
- [x] 1.2 Add jinja2 >= 3.0 to pyproject.toml dependencies
- [x] 1.3 Create `frctl/planning/` package directory with __init__.py
- [x] 1.4 Create `frctl/context/` package directory with __init__.py
- [x] 1.5 Create `frctl/llm/` package directory with __init__.py
- [x] 1.6 Create `frctl/llm/prompts/` directory for templates

## 2. LLM Provider Abstraction (frctl/llm/)

- [x] 2.1 Implement `LLMProvider` class wrapping LiteLLM
- [x] 2.2 Add configuration for model selection (model name string)
- [x] 2.3 Implement generate() method using litellm.completion()
- [x] 2.4 Implement count_tokens() using litellm.token_counter()
- [x] 2.5 Add provider configuration from environment variables
- [x] 2.6 Configure LiteLLM retry logic (num_retries=3)
- [x] 2.7 Add response parsing and validation
- [x] 2.8 Implement cost tracking with completion_cost()
- [x] 2.9 Add verbose logging for transparency (litellm.set_verbose)
- [x] 2.10 Create success/failure callbacks for observability

## 3. Prompt Engineering (frctl/llm/prompts/)

- [x] 3.1 Create Jinja2 prompt templates directory
- [x] 3.2 Implement atomicity check prompt template
- [x] 3.3 Implement goal decomposition prompt template
- [x] 3.4 Implement dependency inference prompt template
- [x] 3.5 Implement digest generation prompt template
- [x] 3.6 Add system prompts for Fractal V3 context
- [x] 3.7 Create prompt rendering utility
- [x] 3.8 Add few-shot examples for each prompt type
- [x] 3.9 Implement prompt versioning
- [x] 3.10 Add prompt validation and testing

## 4. Goal Data Model (frctl/planning/)

- [x] 4.1 Implement `Goal` class with id, description, status
- [x] 4.2 Add goal status enum: Pending, Decomposing, Atomic, Complete
- [x] 4.3 Implement parent/child relationship tracking
- [x] 4.4 Add goal metadata (depth, tokens, created_at)
- [x] 4.5 Implement `AtomicGoal` subclass for leaf nodes
- [x] 4.6 Implement `CompositeGoal` subclass for branches
- [x] 4.7 Add goal validation logic
- [x] 4.8 Implement goal serialization to/from dict
- [x] 4.9 Add goal dependency tracking
- [x] 4.10 Create goal graph integration (link to FederatedGraph)

## 5. Context Management (frctl/context/)

- [x] 5.1 Implement `ContextTree` class for hierarchical context
- [x] 5.2 Add context node with parent/children pointers
- [x] 5.3 Implement hydration: inject parent context into child
- [x] 5.4 Implement dehydration: compress child results to digest
- [x] 5.5 Add global context registry (project settings, constraints)
- [x] 5.6 Implement token hygiene tracking per context node
- [x] 5.7 Add context window limit enforcement
- [x] 5.8 Create context isolation mechanism
- [x] 5.9 Implement parent intent propagation
- [x] 5.10 Add context serialization for persistence

## 6. Planning Engine (frctl/planning/)

- [x] 6.1 Implement `PlanningEngine` class
- [x] 6.2 Add recursive decomposition algorithm
- [x] 6.3 Implement atomicity detection with LLM
- [x] 6.4 Add goal splitting logic (1 composite -> N children)
- [ ] 6.5 Implement dependency inference between siblings
- [x] 6.6 Add planning state machine (assess -> decompose -> atomic)
- [ ] 6.7 Implement depth-first planning traversal
- [ ] 6.8 Add planning pause/resume capability
- [ ] 6.9 Implement planning rollback (undo decomposition)
- [ ] 6.10 Create planning session management

## 7. Digest Protocol (frctl/planning/)

- [x] 7.1 Implement `Digest` class for compressed summaries
- [x] 7.2 Add digest generation from goal results
- [x] 7.3 Implement LLM-based digest creation
- [x] 7.4 Add digest validation (preserve key information)
- [x] 7.5 Implement digest aggregation (multiple children -> parent)
- [x] 7.6 Add digest metadata (compression ratio, fidelity)
- [x] 7.7 Create digest storage and retrieval
- [x] 7.8 Implement digest versioning
- [x] 7.9 Add digest quality metrics
- [x] 7.10 Create digest archive for completed plans

## 8. Plan Persistence (frctl/planning/)

- [x] 8.1 Implement plan serialization to JSON
- [x] 8.2 Create plan storage in `.frctl/plans/<plan-id>.json`
- [x] 8.3 Add plan metadata (created, updated, status)
- [x] 8.4 Implement plan loading from JSON
- [x] 8.5 Add plan versioning with Git integration
- [x] 8.6 Create plan index for quick lookup
- [x] 8.7 Implement plan archiving
- [x] 8.8 Add plan export to other formats
- [x] 8.9 Create plan backup mechanism
- [x] 8.10 Implement plan deletion with safety checks

## 9. CLI Commands (frctl/__main__.py)

- [x] 9.1 Create `plan` command group using Click
- [x] 9.2 Implement `frctl plan init <goal>` - Start planning session
- [x] 9.3 Implement `frctl plan status [plan-id]` - Show planning tree
- [x] 9.4 Implement `frctl plan continue <plan-id>` - Resume planning
- [x] 9.5 Implement `frctl plan review <node-id>` - Review goal details
- [x] 9.6 Implement `frctl plan export <plan-id>` - Export plan as JSON
- [x] 9.7 Implement `frctl plan visualize <plan-id>` - Generate tree diagram
- [x] 9.8 Implement `frctl plan list` - List all plans
- [x] 9.9 Implement `frctl plan delete <plan-id>` - Delete plan
- [x] 9.10 Add `--provider` flag for LLM selection

## 10. Configuration Management

- [ ] 10.1 Add LLM configuration to `.frctl/config.toml`
- [ ] 10.2 Implement API key management (env vars: OPENAI_API_KEY, etc.)
- [ ] 10.3 Add model selection (llm.model = "gpt-4" or "claude-3-5-sonnet")
- [ ] 10.4 Add provider-specific settings (temperature, max_tokens)
- [ ] 10.5 Add planning preferences (max_depth, auto_decompose)
- [ ] 10.6 Implement fallback chain configuration (primary + backup models)
- [ ] 10.7 Add local model support config (ollama/codellama, etc.)
- [ ] 10.8 Create configuration documentation with provider examples
- [ ] 10.9 Add configuration validation and migration utilities
- [ ] 10.10 Document cost tracking and logging options

## 11. Testing

- [x] 11.1 Write unit tests for Goal class (10 tests)
- [x] 11.2 Write unit tests for ContextTree (18 tests)
- [x] 11.3 Write unit tests for hydration/dehydration
- [ ] 11.4 Write unit tests for digest generation
- [ ] 11.5 Write unit tests for atomicity detection
- [x] 11.6 Write unit tests for planning engine (6 integration tests)
- [x] 11.7 Write integration tests with mock LLM responses
- [ ] 11.8 Write integration tests for CLI commands
- [ ] 11.9 Add mock LiteLLM provider for deterministic testing
- [ ] 11.10 Create end-to-end planning test with multiple providers

## 12. Documentation

- [ ] 12.1 Document ReCAP algorithm in technical guide
- [ ] 12.2 Create planning workflow tutorial
- [ ] 12.3 Document LLM provider configuration (all supported providers)
- [ ] 12.4 Add prompt engineering guide
- [ ] 12.5 Document context management principles
- [ ] 12.6 Create planning examples with different providers
- [ ] 12.7 Add CLI command reference
- [ ] 12.8 Document plan JSON schema
- [ ] 12.9 Create architecture diagrams
- [ ] 12.10 Add troubleshooting guide (including local model setup)

## 13. Validation & Polish

- [ ] 13.1 Run `openspec validate add-recap-engine --strict`
- [ ] 13.2 Fix any validation issues
- [ ] 13.3 Ensure all tests pass
- [ ] 13.4 Run linters on new code
- [ ] 13.5 Verify token counting accuracy across providers
- [ ] 13.6 Test with multiple LLM providers (OpenAI, Anthropic, local)
- [ ] 13.7 Validate planning depth limits
- [ ] 13.8 Test planning with complex goals
- [ ] 13.9 Verify digest quality (95%+ fidelity)
- [ ] 13.10 Performance test: 100-goal plan in <5 min
