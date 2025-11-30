# Tasks: Add ReCAP Planning Engine

## 1. Setup & Dependencies

- [ ] 1.1 Add litellm >= 1.0 to pyproject.toml dependencies
- [ ] 1.2 Add jinja2 >= 3.0 to pyproject.toml dependencies
- [ ] 1.3 Create `frctl/planning/` package directory with __init__.py
- [ ] 1.4 Create `frctl/context/` package directory with __init__.py
- [ ] 1.5 Create `frctl/llm/` package directory with __init__.py
- [ ] 1.6 Create `frctl/llm/prompts/` directory for templates

## 2. LLM Provider Abstraction (frctl/llm/)

- [ ] 2.1 Implement `LLMProvider` class wrapping LiteLLM
- [ ] 2.2 Add configuration for model selection (model name string)
- [ ] 2.3 Implement generate() method using litellm.completion()
- [ ] 2.4 Implement count_tokens() using litellm.token_counter()
- [ ] 2.5 Add provider configuration from environment variables
- [ ] 2.6 Configure LiteLLM retry logic (num_retries=3)
- [ ] 2.7 Add response parsing and validation
- [ ] 2.8 Implement cost tracking with completion_cost()
- [ ] 2.9 Add verbose logging for transparency (litellm.set_verbose)
- [ ] 2.10 Create success/failure callbacks for observability

## 3. Prompt Engineering (frctl/llm/prompts/)

- [ ] 3.1 Create Jinja2 prompt templates directory
- [ ] 3.2 Implement atomicity check prompt template
- [ ] 3.3 Implement goal decomposition prompt template
- [ ] 3.4 Implement dependency inference prompt template
- [ ] 3.5 Implement digest generation prompt template
- [ ] 3.6 Add system prompts for Fractal V3 context
- [ ] 3.7 Create prompt rendering utility
- [ ] 3.8 Add few-shot examples for each prompt type
- [ ] 3.9 Implement prompt versioning
- [ ] 3.10 Add prompt validation and testing

## 4. Goal Data Model (frctl/planning/)

- [ ] 4.1 Implement `Goal` class with id, description, status
- [ ] 4.2 Add goal status enum: Pending, Decomposing, Atomic, Complete
- [ ] 4.3 Implement parent/child relationship tracking
- [ ] 4.4 Add goal metadata (depth, tokens, created_at)
- [ ] 4.5 Implement `AtomicGoal` subclass for leaf nodes
- [ ] 4.6 Implement `CompositeGoal` subclass for branches
- [ ] 4.7 Add goal validation logic
- [ ] 4.8 Implement goal serialization to/from dict
- [ ] 4.9 Add goal dependency tracking
- [ ] 4.10 Create goal graph integration (link to FederatedGraph)

## 5. Context Management (frctl/context/)

- [ ] 5.1 Implement `ContextTree` class for hierarchical context
- [ ] 5.2 Add context node with parent/children pointers
- [ ] 5.3 Implement hydration: inject parent context into child
- [ ] 5.4 Implement dehydration: compress child results to digest
- [ ] 5.5 Add global context registry (project settings, constraints)
- [ ] 5.6 Implement token hygiene tracking per context node
- [ ] 5.7 Add context window limit enforcement
- [ ] 5.8 Create context isolation mechanism
- [ ] 5.9 Implement parent intent propagation
- [ ] 5.10 Add context serialization for persistence

## 6. Planning Engine (frctl/planning/)

- [ ] 6.1 Implement `PlanningEngine` class
- [ ] 6.2 Add recursive decomposition algorithm
- [ ] 6.3 Implement atomicity detection with LLM
- [ ] 6.4 Add goal splitting logic (1 composite -> N children)
- [ ] 6.5 Implement dependency inference between siblings
- [ ] 6.6 Add planning state machine (assess -> decompose -> atomic)
- [ ] 6.7 Implement depth-first planning traversal
- [ ] 6.8 Add planning pause/resume capability
- [ ] 6.9 Implement planning rollback (undo decomposition)
- [ ] 6.10 Create planning session management

## 7. Digest Protocol (frctl/planning/)

- [ ] 7.1 Implement `Digest` class for compressed summaries
- [ ] 7.2 Add digest generation from goal results
- [ ] 7.3 Implement LLM-based digest creation
- [ ] 7.4 Add digest validation (preserve key information)
- [ ] 7.5 Implement digest aggregation (multiple children -> parent)
- [ ] 7.6 Add digest metadata (compression ratio, fidelity)
- [ ] 7.7 Create digest storage and retrieval
- [ ] 7.8 Implement digest versioning
- [ ] 7.9 Add digest quality metrics
- [ ] 7.10 Create digest archive for completed plans

## 8. Plan Persistence (frctl/planning/)

- [ ] 8.1 Implement plan serialization to JSON
- [ ] 8.2 Create plan storage in `.frctl/plans/<plan-id>.json`
- [ ] 8.3 Add plan metadata (created, updated, status)
- [ ] 8.4 Implement plan loading from JSON
- [ ] 8.5 Add plan versioning with Git integration
- [ ] 8.6 Create plan index for quick lookup
- [ ] 8.7 Implement plan archiving
- [ ] 8.8 Add plan export to other formats
- [ ] 8.9 Create plan backup mechanism
- [ ] 8.10 Implement plan deletion with safety checks

## 9. CLI Commands (frctl/__main__.py)

- [ ] 9.1 Create `plan` command group using Click
- [ ] 9.2 Implement `frctl plan init <goal>` - Start planning session
- [ ] 9.3 Implement `frctl plan status [plan-id]` - Show planning tree
- [ ] 9.4 Implement `frctl plan continue <plan-id>` - Resume planning
- [ ] 9.5 Implement `frctl plan review <node-id>` - Review goal details
- [ ] 9.6 Implement `frctl plan export <plan-id>` - Export plan as JSON
- [ ] 9.7 Implement `frctl plan visualize <plan-id>` - Generate tree diagram
- [ ] 9.8 Implement `frctl plan list` - List all plans
- [ ] 9.9 Implement `frctl plan delete <plan-id>` - Delete plan
- [ ] 9.10 Add `--provider` flag for LLM selection

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

- [ ] 11.1 Write unit tests for Goal class
- [ ] 11.2 Write unit tests for ContextTree
- [ ] 11.3 Write unit tests for hydration/dehydration
- [ ] 11.4 Write unit tests for digest generation
- [ ] 11.5 Write unit tests for atomicity detection
- [ ] 11.6 Write unit tests for planning engine
- [ ] 11.7 Write integration tests with mock LLM responses
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
