# Spec: Planning Core

This specification defines the Recursive Context-Aware Planning (ReCAP) engine for hierarchical goal decomposition.

## ADDED Requirements

### Requirement: Goal Decomposition

The system SHALL recursively decompose high-level goals into atomic tasks.

#### Scenario: Assess goal atomicity

- **WHEN** a planning engine receives a goal "Implement OAuth 2.0"
- **THEN** the system queries the LLM to assess if the goal is atomic
- **AND** the LLM responds with a determination (atomic or composite)
- **AND** the response includes reasoning for the decision

#### Scenario: Decompose composite goal

- **WHEN** a goal is determined to be composite
- **THEN** the system generates 2-7 child goals that fully cover the parent
- **AND** each child goal has a clear description
- **AND** the child goals are ordered by dependency
- **AND** the decomposition is saved to the planning tree

#### Scenario: Identify atomic goal

- **WHEN** a goal is determined to be atomic
- **THEN** the system marks it as a leaf node
- **AND** no further decomposition occurs
- **AND** the goal is ready for implementation (in Phase 4)

### Requirement: Context Management

The system SHALL maintain hierarchical context using hydration and dehydration.

#### Scenario: Hydrate child context

- **WHEN** decomposing a goal into children
- **THEN** each child receives global context (project settings)
- **AND** each child receives parent intent (goal description)
- **AND** each child receives relevant constraints
- **AND** each child does NOT receive sibling details (isolation)

#### Scenario: Dehydrate child results

- **WHEN** a child goal completes decomposition
- **THEN** the system generates a digest of the results
- **AND** the digest is compressed to <20% of original tokens
- **AND** the digest preserves key architectural decisions
- **AND** the digest is passed to the parent context

#### Scenario: Enforce token limits

- **WHEN** building context for an LLM call
- **THEN** the system counts tokens using tiktoken
- **AND** the system ensures total tokens < model limit
- **AND** if limit is exceeded, older context is dehydrated further
- **AND** essential constraints are always preserved

### Requirement: LLM Provider Abstraction

The system SHALL support multiple LLM providers through LiteLLM unified interface.

#### Scenario: Use any supported provider

- **WHEN** a user configures a model (e.g., "gpt-4", "claude-3-5-sonnet", "ollama/codellama")
- **THEN** the system initializes LiteLLM with that model
- **AND** API calls work transparently regardless of provider
- **AND** responses are parsed correctly
- **AND** token usage is tracked accurately

#### Scenario: Switch providers via configuration

- **WHEN** a user updates `.frctl/config.toml` with a different model
- **THEN** the system uses the new provider for subsequent calls
- **AND** no code changes are required
- **AND** the system logs provider being used for transparency

#### Scenario: Use local models

- **WHEN** configured to use a local model (e.g., "ollama/codellama")
- **THEN** the system connects to the local model server
- **AND** no data is sent to external APIs
- **AND** planning works identically to cloud providers
- **AND** the user has complete privacy

#### Scenario: Automatic retry on failure

- **WHEN** an LLM API call fails with a transient error
- **THEN** the system retries up to 3 times with exponential backoff
- **AND** the system logs each retry attempt
- **AND** if all retries fail, the error is reported to the user
- **AND** planning state is saved for later resumption

#### Scenario: Fallback to secondary provider

- **WHEN** configured with a fallback chain (e.g., gpt-4 → claude-3-5-sonnet)
- **THEN** the system tries the primary model first
- **AND** if primary fails, automatically tries fallback
- **AND** the fallback is logged for transparency
- **AND** planning continues without user intervention

#### Scenario: Track costs across providers

- **WHEN** using a cloud provider with metered pricing
- **THEN** the system tracks token usage and estimated cost
- **AND** cost is displayed in planning statistics
- **AND** users can set spending alerts/limits
- **AND** cost breakdown is available per planning session

### Requirement: Planning State Persistence

The system SHALL save and restore planning state.

#### Scenario: Save planning session

- **WHEN** planning is interrupted or paused
- **THEN** the system saves the planning tree to `.frctl/plans/<id>.json`
- **AND** the file includes all goals and their status
- **AND** the file includes context digests
- **AND** the file includes metadata (created, updated, depth)

#### Scenario: Resume planning session

- **WHEN** a user runs `frctl plan continue <plan-id>`
- **THEN** the system loads the planning tree from JSON
- **AND** the system resumes from the last incomplete goal
- **AND** the system restores parent context via hydration
- **AND** planning continues seamlessly

#### Scenario: List planning sessions

- **WHEN** a user runs `frctl plan list`
- **THEN** the system displays all plans in `.frctl/plans/`
- **AND** each plan shows: ID, goal, status, depth, created date
- **AND** plans are sorted by recency

### Requirement: Dependency Inference

The system SHALL infer dependencies between sibling goals.

#### Scenario: Detect sequential dependencies

- **WHEN** decomposing a goal into children
- **THEN** the system asks the LLM to identify dependencies
- **AND** the LLM returns pairs of (source, target) dependencies
- **AND** dependencies are validated against the graph
- **AND** circular dependencies are detected and rejected

#### Scenario: Create edges in graph

- **WHEN** dependencies are identified between child goals
- **THEN** the system creates corresponding nodes in the FederatedGraph
- **AND** the system creates DEPENDS_ON edges between nodes
- **AND** the graph maintains DAG properties
- **AND** planning can reference the graph for ordering

### Requirement: Digest Protocol

The system SHALL generate compressed summaries of planning results.

#### Scenario: Generate digest for completed subtree

- **WHEN** all children of a composite goal are complete
- **THEN** the system collects child digests
- **AND** the system asks the LLM to create a parent digest
- **AND** the digest is <20% of combined child content
- **AND** the digest includes key decisions, interfaces, constraints

#### Scenario: Validate digest fidelity

- **WHEN** a digest is generated
- **THEN** the system estimates information preservation
- **AND** the system warns if fidelity < 90%
- **AND** the system includes digest metadata (compression ratio)
- **AND** original content is archived for reference

### Requirement: CLI Planning Interface

The system SHALL provide command-line interface for planning workflows.

#### Scenario: Initialize planning session

- **WHEN** a user runs `frctl plan init "Build user authentication"`
- **THEN** the system creates a new planning session
- **AND** the system assigns a unique plan ID
- **AND** the system creates the root goal
- **AND** planning begins automatically or waits for continue

#### Scenario: Display planning tree

- **WHEN** a user runs `frctl plan status <plan-id>`
- **THEN** the system displays the goal hierarchy as a tree
- **AND** each goal shows: status, depth, description
- **AND** atomic goals are marked differently than composite
- **AND** the current focus is highlighted

#### Scenario: Review goal details

- **WHEN** a user runs `frctl plan review <goal-id>`
- **THEN** the system displays full goal information
- **AND** the display includes parent goal
- **AND** the display includes child goals (if any)
- **AND** the display includes digest content
- **AND** the display includes dependencies

### Requirement: Recursive Depth Management

The system SHALL limit and track planning depth.

#### Scenario: Enforce maximum depth

- **WHEN** planning reaches depth 10 (configurable)
- **THEN** the system treats goals at depth 10 as atomic
- **AND** the system warns about depth limit reached
- **AND** the system suggests breaking into multiple plans

#### Scenario: Track depth statistics

- **WHEN** a user views plan statistics
- **THEN** the system reports: total depth, average depth, deepest path
- **AND** the system identifies bottleneck goals (high depth)
- **AND** the system suggests optimization opportunities

### Requirement: Error Handling and Recovery

The system SHALL handle LLM failures gracefully.

#### Scenario: Handle API timeout

- **WHEN** an LLM API call times out
- **THEN** the system retries up to 3 times with exponential backoff
- **AND** if all retries fail, the system saves state
- **AND** the system reports the error to the user
- **AND** planning can be resumed later

#### Scenario: Handle invalid LLM response

- **WHEN** the LLM returns unparseable or invalid output
- **THEN** the system logs the raw response
- **AND** the system retries with a clarifying prompt
- **AND** if retry fails, the system marks the goal for manual review
- **AND** planning continues with other goals

#### Scenario: Handle rate limiting

- **WHEN** the LLM provider returns a rate limit error
- **THEN** the system waits for the specified retry-after duration
- **AND** the system saves current state
- **AND** the system resumes automatically when ready
- **AND** the user is notified of the delay

### Requirement: Performance and Scalability

The system SHALL handle large planning trees efficiently.

#### Scenario: Plan with 100+ goals

- **WHEN** a planning tree contains 100+ goals
- **THEN** planning completes in under 10 minutes
- **AND** memory usage remains under 1GB
- **AND** the JSON file size is manageable (<10MB)
- **AND** tree visualization remains readable

#### Scenario: Parallel goal decomposition

- **WHEN** multiple sibling goals can be decomposed independently
- **THEN** the system may decompose them in parallel
- **AND** each decomposition uses isolated context
- **AND** results are merged correctly into the planning tree
- **AND** race conditions are prevented
