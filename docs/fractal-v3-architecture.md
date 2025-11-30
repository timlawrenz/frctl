# **Fractal V3: A Deterministic Topological Architecture for Agentic Software Engineering**

## **1\. Executive Summary: The Deterministic Imperative in Agentic Systems**

The discipline of automated software engineering is currently navigating a precarious inflection point. We are witnessing a transition from the era of "Copilots"—stochastic, generative assistants that suggest code fragments—to the era of "Agents"—autonomous entities tasked with architecting and implementing entire systems. However, this transition has been stalled by a fundamental architectural mismatch. Early iterations of agentic frameworks, which we retrospectively classify as Generation 1 and 2, operated on the premise that Large Language Models (LLMs) could serve as autonomous generative engines. These systems leveraged probabilistic token prediction to synthesize code based on natural language prompts. While effective for isolated functions or boilerplate generation, this approach inevitably encounters a critical failure mode when applied to complex, distributed architectures: the **"Context Coherence Crisis"**.  
As the scope of a software system expands, the ability of linear reasoning chains—the dominant cognitive architecture of current LLMs—to maintain architectural integrity degrades non-linearly. The finite context window acts as a cognitive event horizon; beyond this limit, architectural decisions become disjointed, leading to "hallucinated" interfaces, circular dependencies, and code that is syntactically correct but systemically invalid. The industry has hit a "Trust Gap," where the cost of verifying an agent's output exceeds the cost of manual implementation, rendering the agent economically unviable for high-stakes engineering.  
**Fractal Version 3 (V3)** represents a comprehensive strategic response to these failures. It is not merely an iterative improvement but a fundamental re-architecture of the agentic software development lifecycle. The triggers for this research process were the empirical failures of linear "Chain of Thought" (CoT) reasoning to manage cross-cutting system dependencies—a phenomenon we define as the **Context-Coupling Orthogonality** problem.  
The goal of Fractal V3 is to bridge the Trust Gap by shifting the paradigm from probabilistic generation to **Deterministic Architecture**. The strategy employed to achieve this is the decoupling of "Planning" from "State" through two core innovations:

1. **The Federated Graph:** Abandoning file-centric representations in favor of a topological Directed Acyclic Graph (DAG) that enforces strict dependency management.  
2. **The 'Tandem' Human-in-the-Loop Protocol:** Inverting the control loop so that agents act as "Proposers" of rigorous architectural plans rather than autonomous executors of code.

This report provides an exhaustive technical analysis of the Fractal V3 architecture. It dissects the theoretical crisis of linear reasoning, details the operational mechanics of the **Recursive Context-Aware Planning (ReCAP)** methodology, and examines the "Sad Path" reliability engineering—including Transactional Rollback and Drift Resolution—that underpins the system. By synthesizing these elements, Fractal V3 transforms the AI agent from an erratic "Junior Coder" into a disciplined "Staff Architect," capable of operating within strict, machine-verifiable boundaries.

## **2\. The Theoretical Crisis: Triggers and Strategic Drivers**

To understand the architectural decisions inherent in Fractal V3, one must first rigorously analyze the specific technical failures that triggered its development. The shift to V3 was driven by the realization that the prevailing "Chat-driven" and "File-centric" models of interaction were theoretically incapable of scaling to enterprise complexity.

### **2.1 The Context Coherence Crisis**

The primary trigger for the Fractal research initiative was the **Context Coherence Crisis**. Contemporary LLM architectures, based on the Transformer model, rely on a finite context window to maintain state. In the standard "Generation 1" workflow, an agent employs a linear interaction model—often referred to as "Chain of Thought" (CoT) or "Reason \+ Act" (ReAct). The agent appends its history, observations, and reasoning to a monotonically growing context buffer.  
However, as a software system grows, the architectural context required to make valid decisions exceeds this "cognitive horizon." Empirical observation of V1 systems revealed a phenomenon of **Context Drift**:

* **Temporal Decay:** An agent defines a database schema in step T\_1. By step T\_{50}, the specific constraints of that schema (e.g., "User IDs must be UUIDs") have been pushed out of the effective attention window.  
* **Hallucinated Interfaces:** Consequently, when the agent implements the API endpoints at T\_{55}, it "hallucinates" a function signature that contradicts the schema defined at T\_1.

This is not a failure of the model's intelligence; it is a failure of the data structure. Linear buffers are inefficient mechanisms for storing hierarchical system state. Furthermore, the computational cost of this linear reasoning scales quadratically (O(N^2)) relative to the interaction length, as the model must re-process the entire history for every new token generated. This economic inefficiency renders linear agentic workflows unviable for long-horizon architectural tasks.

### **2.2 The Context-Coupling Orthogonality Problem**

While expanding context windows (e.g., to 1 million tokens) is a commonly proposed solution, Fractal's research indicates that the problem is structural, not just distinct. This is formalized as the **Context-Coupling Orthogonality** problem.  
Software architecture possesses a dual, contradictory nature:

1. **Hierarchical Requirements (Vertical Context):** High-level goals ("Build an E-commerce platform") decompose into sub-goals ("Build User Auth," "Build Inventory"), forming a tree structure. Constraints and intent flow vertically down this tree.  
2. **Relational Implementation (Horizontal Coupling):** The implementation of these goals requires components to interact laterally. The "User Auth" service must interact with the "Database," and the "Inventory" service must interact with the "Payment Gateway." These interactions form a graph structure.

**The Failure of Pure Tree Decomposition:** Standard recursive planning methods excel at managing Vertical Context (breaking down the goal) but fail to manage Horizontal Coupling. When a problem is decomposed into isolated sub-problems to fit within context windows, the agents working on these sub-problems suffer from **Sibling Blindness**.

| Aspect | Vertical Context (Tree) | Horizontal Coupling (Graph) |
| :---- | :---- | :---- |
| **Nature** | Hierarchical intent and constraints. | Relational dependencies and contracts. |
| **Data Flow** | Top-down (Goals) / Bottom-up (Summaries). | Lateral (APIs, Schemas, Shared Types). |
| **Agent Failure** | **Context Drift:** Losing high-level purpose. | **Sibling Blindness:** Component A cannot see Component B's interface. |
| **Fractal Solution** | **ReCAP:** Recursive decomposition. | **Federated Registry:** Shared interface definitions. |

This orthogonality—where the method of managing context (Recursion) is orthogonal to the nature of the system (Coupling)—was the specific theoretical trigger that necessitated the move to a Federated Graph architecture in V3.

### **2.3 The Trust Gap and The Economic Trigger**

The culmination of these technical failures is the **Trust Gap**. This is an economic barrier. In software engineering, the value of an automated tool is defined by the equation:  
In V1 and V2 systems, the stochastic nature of LLMs meant that the Cost\_{Verification} was extremely high. If an AI generates 1,000 lines of code, but the human reviewer must inspect every line for subtle logical bugs, security vulnerabilities, or hallucinated dependencies, the efficiency gain is nullified. Often, Cost\_{Verification} \> Cost\_{Manual}, resulting in negative value.  
**Goal of V3:** To reduce Cost\_{Verification} to near zero. **Strategy:** Move failure detection from **Runtime** to **Design Time**. By enforcing a rigorous specification phase where the architecture is validated *before* implementation, Fractal V3 constrains the search space for the AI, ensuring that the generated code is correct by construction rather than by chance.

## **3\. Architectural Foundation: Recursive Context-Aware Planning (ReCAP)**

The core intellectual property driving Fractal V3 is **Recursive Context-Aware Planning (ReCAP)**. This methodology fundamentally alters the relationship between the AI model and the software task, moving away from "streaming consciousness" to "structured reasoning".

### **3.1 Recursive Decomposition Algorithms**

ReCAP models the problem of software specification not as a sequence of steps, but as a recursive decomposition of goals. The process begins with a single high-level node—the **User Query**—and recursively breaks it down until the sub-nodes are **"atomic"**. An atomic goal is defined as a unit of work sufficiently simple to be implemented by a standard coding agent in a single file or a small set of related files without ambiguity.  
The decomposition algorithm proceeds as follows:

1. **State A: Assessment:** The Recursion Engine accepts a Goal string (e.g., "Implement OAuth 2.0") and queries the Reasoning Model (typically a high-intelligence model like GPT-4o or Claude 3.5 Sonnet): "Is this goal atomic?"  
2. **State B: Branching:**  
   * **Composite Nodes:** If the goal is complex, it is broken into child nodes (e.g., "Setup Identity Provider," "Create Callback Route," "Handle Token Storage"). Crucially, the engine asks the model to identify *dependencies* between these children, forming a local Directed Acyclic Graph (DAG).  
   * **Atomic Nodes (Leafs):** If the goal is atomic, the engine generates specific implementation steps (e.g., "Create file src/auth/login.ts with explicit types").  
3. **State C: Context Isolation:** Each child node is processed in a **fresh context window**. This is the mechanism that solves Context Drift. The child node inherits the Global Context (Project Settings) and the Parent's Intent, but it is explicitly shielded from the noisy reasoning history of its siblings.

### **3.2 The Context Tree and Token Hygiene**

To support this recursion, Fractal utilizes a specialized data structure called the **Context Tree**. Unlike vector databases used in Retrieval-Augmented Generation (RAG), which rely on fuzzy semantic similarity, the Context Tree relies on precise structural hierarchy.  
A critical mechanism within this tree is the **Hydration/Dehydration Cycle**, which manages "Token Hygiene" :

* **Hydration (Descending \- The Principle of Least Privilege):** When the engine descends to a child node, it "hydrates" the context with *only* the constraints relevant to that specific branch.  
  * *Example:* A node working on the "Database Layer" receives schema definitions and migration rules from openspec/project.md. It is deliberately shielded from "Frontend CSS" details or "Routing Logic." This prevents **Token Pollution**, ensuring the model's attention is focused solely on the relevant constraints.  
* **Dehydration (Ascending \- The Digest Protocol):** When a child node completes its planning, it does *not* pass its full conversation history back to the parent. Instead, it generates a **"Digest"**—a compressed, high-fidelity summary of its decisions (e.g., "Created User Schema with fields X, Y, Z"). The raw reasoning trace is "dehydrated" (archived or discarded), and only the Digest ascends the tree. This ensures the Root Node never overflows its context window, regardless of the project's depth.

### **3.3 Complexity and Scalability Analysis**

The shift to ReCAP fundamentally alters the computational complexity of specification generation. We can compare the token economics of Linear CoT versus Fractal ReCAP:

| Metric | Linear Chain-of-Thought (CoT) | Fractal ReCAP |
| :---- | :---- | :---- |
| **Complexity** | O(N^2) (Quadratic) | O(N \\cdot D) (Linear relative to depth) |
| **Context Window** | Monotonically increasing. Eventually overflows. | Constant active size (Reset at each node). |
| **Information Retention** | Decays over time (Context Drift). | High fidelity (Hierarchical Summarization). |
| **Cost Efficiency** | Low (Re-reading history costs tokens). | High (Processing only relevant scope). |
| **Suitability** | Short scripts, simple refactors. | Enterprise systems, greenfield architecture. |

By sacrificing "Time" (sequential or parallel API calls) for "Memory" (context window space), ReCAP enables the generation of specifications for massive architectures that would be impossible to process in a single pass.

## **4\. The Federated Graph Architecture**

While ReCAP handles the vertical decomposition of intent, the **Federated Graph** architecture handles the horizontal coupling of components, solving the "Sibling Blindness" problem that plagued V1/V2 systems.

### **4.1 Shift from Filesystem to Topology**

In traditional development environments and previous Fractal versions, the "source of truth" was the filesystem—a hierarchical but semantically flat collection of directories. This structure obscures architectural intent; a file in src/utils might be a core dependency for the entire system, or a helper for one module. An AI agent cannot infer this strictly from file placement.  
Fractal V3 abandons the filesystem as the primary architectural model in favor of a **Topological Graph** maintained in memory as a **Directed Acyclic Graph (DAG)**.

* **Nodes:** Represent semantic components (Services, Libraries, Database Schemas, API Endpoints).  
* **Edges:** Represent typed, semantic relationships (dependsOn, consumes, owns).

This abstraction allows for **Topological Drafting**. When an agent proposes a change, it is not simply writing a new file; it is proposing a mutation to the graph structure (e.g., "Inject a Redis Cache Node between the API Node and the Database Node"). This enables high-level validation: the system can mathematically detect circular dependencies or architectural boundary violations *before* any file I/O occurs.

### **4.2 Data Serialization: DAG-JSON and CycloneDX**

To persist this topological graph, Fractal V3 adopts a hybrid serialization strategy that prioritizes deterministic hashing and industry interoperability.

1. **DAG-JSON:** The core graph is serialized using **DAG-JSON** (from the IPFS ecosystem).  
   * *Why?* Standard JSON is unordered. DAG-JSON mandates sorted keys and deterministic encoding. This allows the system to generate a stable cryptographic fingerprint (Merkle Hash) of the architecture state. If a single edge changes, the root hash changes, signaling a mutation that requires validation.  
2. **CycloneDX & PURL:** To integrate with the broader supply chain security ecosystem, every node is identified by a **Package URL (PURL)** (e.g., pkg:fractal/payment-service@local), compliant with the **CycloneDX** standard.  
   * *Strategic Value:* This natively supports Software Bill of Materials (SBOM) generation. It allows the "Policy Gate" (discussed in Section 6\) to check new dependencies against corporate allow/deny lists (e.g., "Block GPL-3.0 licenses") at the design stage.

### **4.3 The TypeSpec Mandate**

A critical failure mode in V2 was the reliance on loose JSON schemas or implied TypeScript interfaces for inter-component communication. This led to "Drift," where a producer updated an API but the consumer was not updated.  
Fractal V3 mandates **TypeSpec** (formerly CADL) for all Edge definitions.

* **The Contract:** Every edge in the graph must be backed by a .tsp file defining the interface.  
* **Static Analysis:** The drafting engine uses the TypeSpec compiler to parse the Abstract Syntax Tree (AST) of the proposed interface.  
* **Semantic Diffing:** This allows the system to perform a **Semantic Diff** against the previous version. It can mathematically prove "Breaking Changes" (e.g., removing a required field) versus "Non-Breaking Changes" (e.g., adding an optional field).

This contract-first approach ensures that components drafted by different agents in different "waves" remain compatible, effectively solving the "Context-Coupling Orthogonality" problem by forcing horizontal coupling to be explicit and typed.

## **5\. The 'Tandem' Human-in-the-Loop Protocol**

The operational core of Fractal V3 is the **'Tandem' Protocol**, a formal state machine that governs the lifecycle of every architectural change. This protocol was the strategic response to the "Trust Gap"—the need to ensure that AI never executes code without explicit human ratification.

### **5.1 The Tandem State Machine**

The workflow is strictly defined by four states, mirroring the **Terraform "Plan/Apply" paradigm** but adapted for generative software engineering.

#### **State 1: INTENT (The Planning Phase)**

* **Trigger:** frctl plan "\[goal\]"  
* **System Action:** The AI Agent (acting as Architect) analyzes the current fractal.graph.json. It identifies affected nodes and decomposes the goal using ReCAP.  
* **Constraint:** It does *not* write implementation code. It generates a **Proposal Package** consisting of proposal.md (Strategic Briefing) and tasks.md (Execution Graph).  
* **Output:** A structured plan detailing the "Why," "What," and "How" of the change.

#### **State 2: REVIEW (The Alignment Phase)**

* **Trigger:** Completion of the Proposal Package.  
* **System Action:** The system locks the workspace. It displays the proposal.md alongside a **"Topological Diff"** (visualizing graph mutations) and a **"Semantic Diff"** (visualizing API contract changes).  
* **Human Action:** The developer reviews the plan. Crucially, the developer can **edit the Markdown proposal directly**. If the AI proposes "Use SQLite," the human can change it to "Use PostgreSQL" in the text. The AI must then re-plan based on this correction. This phase aligns the AI's "Hallucination" with the Human's "Intent."

#### **State 3: GATE (The Validation Phase)**

* **Trigger:** frctl approve (Cryptographic signature by the user).  
* **System Action:** The **Validation Engine** runs. It simulates the application of the proposal to the graph and enforces the "Constitution" :  
  * **Cycle Detection:** Is the graph still Acyclic? (DFS Traversal).  
  * **Breaking Change Check:** Do new TypeSpecs break existing consumers? (AST Comparison).  
  * **Policy Check:** Are new dependencies allowed by openspec/AGENTS.md?  
* **Output:** If successful, a fractal.lock file is generated, freezing the approved plan and graph state hash.

#### **State 4: EXECUTION (The Apply Phase)**

* **Trigger:** frctl apply  
* **System Action:** The AI Agent (acting as Engineer) executes the tasks.md checklist.  
* **Constraint:** Because the architectural boundaries and interfaces are already locked and validated, the AI is constrained to "filling in the blanks." It writes code to satisfy the TypeSpec contracts defined in the graph. This constraint reduces the hallucination rate to near zero.

### **5.2 Topological Drafting: The "Wave" Execution Model**

To resolve "Sibling Blindness," the execution phase utilizes **Topological Drafting**. The system executes agents in "Waves" based on the dependency graph. This forces a strict ordering of operations:

| Wave | Target Nodes | Action | Outcome |
| :---- | :---- | :---- | :---- |
| **Wave 1** | **Leafs** (e.g., Database, Utils) | Agents draft independent nodes. Define schemas. | Publish interface.md and .tsp contracts. |
| **Hoisting** | *System* | System copies contracts to **Global Registry**. | Contracts become immutable truth for dependents. |
| **Wave 2** | **Dependents** (e.g., Backend API) | Agents draft nodes depending on Wave 1\. | Prompt *injects* the authoritative Wave 1 interface. |
| **Wave 3** | **Clients** (e.g., Frontend) | Agents draft nodes depending on Wave 2\. | Prompt *injects* the authoritative Wave 2 interface. |

**Strategic Impact:** This sequential execution trades latency (Wave 2 must wait for Wave 1\) for correctness. It eliminates the **"Mocking Dilemma"** where agents guess the signatures of dependencies that don't yet exist. In Fractal V3, the dependency *always* exists and is strictly typed before the dependent is allowed to start drafting.

## **6\. Reliability Engineering: The "Sad Path" Architecture**

A distinguishing feature of Fractal V3 is its obsessive focus on the **"Sad Path"**—the inevitable failure states of distributed systems. The architecture assumes that network partitions, file system errors, and schema mismatches are normal operating conditions, not edge cases.

### **6.1 Transactional Rollback**

Since standard file systems lack the ACID (Atomicity, Consistency, Isolation, Durability) guarantees of a database, Fractal V3 implements a **Transactional Rollback** mechanism at the application layer.

* **Compensating Transaction Pattern:** Unlike database rollbacks (discarding a write-ahead log), file system operations are side effects. Fractal V3 uses compensating transactions. For every "Do" action (e.g., fs.writeFile), the system generates and pushes an "Undo" action (e.g., fs.unlink) onto a LIFO stack. This stack is strictly ordered and populated only *after* an action succeeds.  
* **Staging and Swap:** To prevent "zombie resources" (half-written files), V3 employs a **"Staging and Swap"** strategy.  
  1. **Generate:** AI writes code to a hidden staging directory (.fractal/staging/\<uuid\>/).  
  2. **Verify:** The "Ghost Compiler" validates the syntax of staged files.  
  3. **Atomic Swap:** A **Manifest-Driven Swap** occurs. Target files in src/ are moved to .fractal/history/\<uuid\>/ (Double Buffering) before being overwritten. This ensures that even if the swap fails midway (e.g., power loss), the system can fully recover from the history folder.  
* **Write-Ahead Log (WAL):** To handle "Hard Crashes" (e.g., SIGKILL) where the in-memory stack is lost, the system writes a JSON journal (fractal\_transaction.lock) to disk before starting. On recovery, the system analyzes this journal to clean up "dirty resources."

### **6.2 Drift Resolution Strategy**

**Drift** is defined as the semantic divergence between the **Local State** (TypeScript code on disk) and the **Remote State** (TypeSpec definitions or Infrastructure). V3 resolves this using **Graph-Theoretic Dependency Analysis**.

* **The Shadow Graph:** The system maintains a "Base State" (B)—a snapshot of the system from the last successful sync, persisted in .fractal/state.json.  
* **Three-Way Merge:** Drift resolution uses a three-way logic comparison: Local (L), Remote (R), and Base (B).  
* **Semantic Hashing:** To avoid false positives (e.g., whitespace changes), nodes are normalized (canonicalized, sorted, pruned of comments) before hashing. Drift is detected only when the *semantic* hash changes.  
* **Conflict Logic:** A **Sad Path Conflict** is flagged when both Local and Remote have changed relative to Base, and they differ from each other (\\Delta\_{LB} \\land \\Delta\_{RB} \\land L \\neq R).  
* **Resolution:**  
  * **Interactive:** The CLI presents a **Semantic Diff** and offers strategies like "Smart Merge" (patching AST nodes).  
  * **Automated (CI/CD):** Configuration (fractal.config.yaml) dictates strategies like strict (fail build) or force-local.

### **6.3 Loose Mode and Heuristic Inference**

**Loose Mode** is a fault-tolerant generation mode designed for the "messy reality" of brownfield development. It allows the system to ingest unstructured, "dirty" TypeScript and coerce it into valid TypeSpec.

* **Handling any:** In Strict Mode, any is an error. In Loose Mode, the system uses **Contextual Analysis**. It inspects property names (e.g., "id" implies string, "payload" implies unknown) to infer types. If inference fails, it annotates the output with @fixme.  
* **Synthetic Models:** To map TypeScript's structural typing (anonymous interfaces) to TypeSpec's nominal typing, Loose Mode hashes the anonymous structure to create deterministic **Synthetic Models** (e.g., Synthetic\_User\_Update), satisfying the requirement for named types.  
* **Self-Healing Loop:** Before committing, the system runs a **Ghost Compiler** in memory. If it detects errors (e.g., circular dependencies), it triggers a self-healing cycle, rewriting the code (e.g., injecting TypeReference) to fix the issue before the user ever sees it.

## **7\. Integration: The OpenSpec Standard**

Fractal V3 is designed not as a standalone silo but as the generative engine for the **OpenSpec** standard. OpenSpec provides the "File System Schema" that Fractal populates.  
The system outputs artifacts strictly compliant with the OpenSpec directory structure (openspec/changes/\<id\>/):

* **proposal.md:** The strategic briefing generated from the Root Node of the ReCAP tree.  
* **tasks.md:** The execution plan generated from the flattened leaf nodes.  
* **specs/**: The "Truth" source, updated via delta generation.

This standardization ensures that Fractal can integrate with existing developer tools (like Cursor, GitHub Copilot) and CI/CD pipelines. It acts as a "Ghostwriter" that produces human-readable, auditable specifications rather than opaque binary blobs. The integration with **CycloneDX** and **Backstage** (via frctl topology export) further cements its role in the platform engineering ecosystem.

## **8\. Conclusion: The Rise of Spec-Driven Development**

Fractal V3 represents the maturation of Agentic AI from a novelty to an engineering discipline. The triggers for its development—the Context Coherence Crisis, the Context-Coupling Orthogonality problem, and the Trust Gap—highlighted the inescapable reality that **probabilistic models cannot fundamentally solve deterministic problems without architectural constraints.**  
By decoupling **Planning** (ReCAP/Vertical) from **State** (Federated Graph/Horizontal), and by wrapping the stochastic LLM in the rigid safety harness of the **Tandem Protocol** and **Gated Topological Drafting**, Fractal V3 bridges the Trust Gap. It leverages the raw creativity and reasoning power of Large Language Models while constraining their execution within the immutable laws of Graph Theory and Type Systems.  
The result is an architecture where the AI is no longer a chaotic improviser, but a verifiable, reliable partner. Fractal V3 effectively provides the "Pre-frontal Cortex" for the AI developer, converting abstract desires into concrete, verified, and recoverable plans. It establishes **Spec-Driven Development (SDD)** as the necessary methodology for the future of software engineering, ensuring that as we hand over more agency to machines, we retain absolute control over the architecture they build.  
**Works Cited**

* Fractal CLI Reliability and Edge Cases  
* Fractal Technical Specification V3: Deterministic Architecture for AI-Assisted Engineering (Draft 3.0.0)  
* Tandem Architecture: Human-AI Collaboration  
* FRACTAL: A Federated Graph Architecture for Agentic Software Specification  
* Formalizing Fractal for OpenSpec Briefings  
* "Context Coherence Crisis" definition lookup  
* "Context-Coupling Orthogonality" definition lookup  
* "Trust Gap" definition lookup  
* "Sibling Blindness" definition lookup  
* "Topological Drafting" definition lookup  
* "Sad Path" definition lookup  
* ReCAP arXiv papers and benchmarks  
* ReCAP: Recursive Context-Aware Reasoning and Planning with Language Models  
* TypeSpec documentation

#### **Works cited**

1\. TypeSpec for Microsoft 365 Copilot overview, https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/overview-typespec 2\. \[2510.23822\] ReCAP: Recursive Context-Aware Reasoning and Planning for Large Language Model Agents \- arXiv, https://arxiv.org/abs/2510.23822 3\. ReCAP: Recursive Context-Aware Reasoning and Planning with Language Models \- CS 224R Deep Reinforcement Learning \- Stanford University, https://cs224r.stanford.edu/projects/pdfs/CS224R\_RECAP.pdf