# Evaluator Component

## Overview

The **Evaluator** is the unified task-execution component of the system. It is responsible for:

1. **Controlling AST processing and execution**  
2. **Managing failure recovery** via standard task return statuses (`COMPLETE`, `CONTINUATION`, `FAILED`)
3. **Tracking resource usage** (in coordination with Handlers)
4. **Handling reparse/decomposition requests** when tasks fail (e.g. due to resource exhaustion or invalid output)

### References in Existing Documentation

- **System-Level References**  
  - *System README (`system/README.md`)* and *Architecture Overview (`system/architecture/overview.md`)* list the Evaluator as a core component, describing it as the manager for AST execution, resource tracking, and reparse/error handling.  
  - *Contracts & Interfaces (`system/contracts/interfaces.md`)* references "[Contract:Integration:EvaluatorTask:1.0]," tying the Evaluator to tasks and describing the need for an integration interface (though that interface is not yet fully elaborated).  
  - The *"Metacircular Evaluator"* concept is mentioned in `misc/textonly.tex.md`, demonstrating an evaluator that calls LLM operations as part of `apply-proc` and `eval-task`. This underscores that the Evaluator runs tasks by leveraging LLM-based primitives (for decomposition, atomic calls, or re-checking).  

- **Error Handling**  
  - The Evaluator is mentioned repeatedly (e.g., `misc/errorspec.md`, `system/architecture/patterns/errors.md`) as the component receiving error signals from tasks or sub-operations. It manages or coordinates the "control flow" when resource exhaustion or invalid outputs appear.  
  - Errors of type `RESOURCE_EXHAUSTION` or `TASK_FAILURE` can cause the Evaluator to request "reparse" or "decomposition."  

- **Implementation Plan**  
  - *Phase 2: Expanded Context Management* mentions extending environment usage so that sub-tasks may inherit or manage context. The Evaluator is implicitly involved in ensuring tasks have the right environment or partial results.  
  - *Phase 3: Task Execution Enhancements* explicitly names the Evaluator as a place to add "summary output or additional logging" for advanced debugging. The same phase also suggests new flags like `rebuild_memory` or `clear_memory` that the Evaluator would honor when building or discarding context.  

In many existing code examples (both TypeScript-like and Scheme-like), the system calls an `eval` or `apply` function that effectively belongs to the Evaluator domain. When direct execution fails, a decomposition or reparse step is triggered, also under the Evaluator's responsibility.

## Responsibilities and Role

1. **AST Execution Controller**  
   - Orchestrates the step-by-step or operator-by-operator execution of tasks represented as an AST.
   - Calls out to the Handler for LLM-specific interactions and resource tracking (e.g. turn counts, context window checks).
   - Interacts with the Compiler when re-parsing or decomposition is required.

For detailed implementation of key patterns, see:
- Director-Evaluator: [Implementation:DynamicDirectorEvaluator:1.0] in `/components/evaluator/impl/director-evaluator.md`

2. **Failure Recovery**  
   - Detects or receives error signals when tasks fail or exceed resources.  
   - Initiates "reparse" tasks or alternative decomposition approaches if the system's policies allow.  
   - Surfaces errors back to the Task System or parent contexts (e.g., "resource exhaustion," "invalid output").  

3. **Resource Usage Coordination**  
   - Not purely "owns" resource tracking (that's part of the Handler), but integrates with it. The Evaluator is aware of usage or limit errors and decides whether to attempt decomposition or fail outright.  

4. **Context and Environment Handling**  
   - In multi-step or operator-based tasks (sequential, reduce, etc.), the Evaluator ensures the proper propagation of parameters and context. Every new task or function call execution uses direct parameter passing between tasks rather than relying on environment variables. The Evaluator leverages Memory System 3.0 for associative context retrieval (following its read-only context model) but does not manage file content directly.

5. **Integration with Task System**  
   - The Task System may call the Evaluator with a structured or partially structured task. The Evaluator then "executes" it by walking its representation (e.g., an AST or an XML-based operator chain).  
   - On error or partial success, the Evaluator can signal the Task System to orchestrate higher-level recovery or store partial results.  

## Lexical Environment Model

The Environment class implements lexical scoping for DSL variables through nested environments. This is strictly for variable binding and lookup - completely separate from template matching or context management:

- Maintains variable bindings at each scope level via `bindings` map
- Supports variable lookup through parent scopes via `outer` reference
- Creates child scopes with additional bindings via `extend` method
- Resolves variables through lexical chain with `find` method

## Function Call Processing

Function calls use direct parameter passing with lexical isolation:

1. **Template Lookup**: Retrieve template by name from TaskLibrary
2. **Argument Resolution**: For each argument in the caller's environment:
   - For string values: Try variable lookup first, fallback to literal value
   - For AST nodes: Recursively evaluate in caller's environment
3. **Fresh Environment Creation**: Create new environment with parameter bindings
   - Parameters explicitly bound to evaluated argument values
   - No implicit access to caller's variables
4. **Isolated Execution**: Execute template in this clean environment

This ensures templates can only access explicitly passed parameters, maintaining clear boundaries between caller and template scopes.

This process maintains clean scope boundaries, preventing unintended variable access.

## Template Substitution

The Evaluator is solely responsible for resolving all template variables before passing tasks to the Handler. This template substitution phase occurs after task selection but before execution.

The Evaluator ensures that all placeholder substitutions (e.g., `{{variable_name}}`) are completed before dispatching to the Handler, ensuring all execution happens with fully resolved inputs. This includes resolving variables in both direct templates and function templates, with different resolution rules for each type. Associative matching tasks operate on the final, substituted task description.

Furthermore, the Evaluator extracts an optional success score from the task result's `notes` field. This score, if present, is intended to support future adaptive matching and error-handling strategies.

For more details on context handling and the disable context option implemented for atomic tasks, see [ADR 002 - Context Management](../../system/architecture/decisions/002-context-management.md) and [ADR 005 - Context Handling](../../system/architecture/decisions/005-context-handling.md).

## Context Management Implementation

The Evaluator manages all dimensions of the context management model:

### Standard Three-Dimensional Model
1. **Inherited Context**: The parent task's context, controlled by `inherit_context` setting ("full", "none", or "subset").
2. **Accumulated Data**: The step-by-step outputs collected during sequential execution, controlled by `accumulate_data` setting.
3. **Fresh Context**: New context generated via associative matching, controlled by `fresh_context` setting.

### Explicit File Inclusion
In addition to the standard model, the Evaluator supports explicit file inclusion through the `file_paths` feature:
- Files specified via `file_paths` are always included in context
- This operates orthogonally to the three-dimensional model
- File retrieval is delegated to Handler tools
- File content is formatted with XML tags indicating source paths

These dimensions are configured through the standardized context management XML structure:
```xml
<context_management>
    <inherit_context>full|none|subset</inherit_context>
    <accumulate_data>true|false</accumulate_data>
    <accumulation_format>notes_only|full_output</accumulation_format>
    <fresh_context>enabled|disabled</fresh_context>
</context_management>
```

When contexts are needed, the Evaluator decides which dimensions to include based on these settings.

## Associative Matching Invocation

When executing a sequential task step with `<inherit_context>none</inherit_context>` but `<accumulate_data>true</accumulate_data>` and `<fresh_context>enabled</fresh_context>`, the Evaluator:
1. Calls `MemorySystem.getRelevantContextFor()` with prior steps' partial results
2. Merges the returned `AssociativeMatchResult` into the next step's environment
3. Maintains complete separation from the Handler's resource management

### Evaluator Responsibilities for Associative Matching

* **Initiation**: The Evaluator is the *sole* caller of `MemorySystem.getRelevantContextFor()`.
* **Sequential History**: It retrieves partial outputs from `SequentialHistory` (the step-by-step data structure it maintains).
* **Context Merging**: If the step is configured for accumulation, the Evaluator incorporates the match results into the upcoming step's environment.
* **Error Handling**: Any failure to retrieve context (e.g., a memory system error) is handled through the existing `TASK_FAILURE` or resource-related error flow. No new error category is introduced.
* **No Handler Involvement**: The Handler does not participate in the retrieval or assembly of this context data, beyond tracking resource usage at a high level.

This design ensures that only the Evaluator initiates associative matching, preventing confusion about which component is responsible for cross-step data retrieval. The Memory System remains a service that simply provides matches upon request.

## Sequential Task History

When evaluating sequential tasks, the Evaluator implements the Sequential Task Management pattern [Pattern:SequentialTask:2.0] as defined in the system architecture. This includes:

- Maintaining explicit task history for each sequential operation
- Preserving step outputs until task completion or failure
- Implementing resource-aware storage with potential summarization
- Including partial results in error responses for failed sequences

The Evaluator is responsible for tracking this history independent of the Handler's resource management and implementing the appropriate accumulation behavior based on the task's context_management configuration.

For the complete specification of the Sequential Task Management pattern, including output tracking, preservation policies, and resource considerations, see `system/architecture/overview.md`.

## Subtask Spawning Implementation

The Evaluator implements the subtask tool mechanism as defined in [Pattern:ToolInterface:1.0], using the CONTINUATION status internally. From the LLM's perspective, these appear as tools but are implemented using the subtask spawning protocol.

Key responsibilities of the Evaluator in this pattern:
- Handling CONTINUATION requests from subtask tool calls
- Managing context according to the specified configuration
- Coordinating script execution when required
- Passing evaluation results back to the Director

When creating subtasks with explicit file paths, the Evaluator ensures these files are fetched and included in the subtask's context before execution.

## Tool Interface Integration

When the LLM invokes a subtask-based tool:
1. The Handler transforms this into a CONTINUATION with SubtaskRequest
2. The Evaluator receives and processes this request
3. Template selection occurs via associative matching
4. Execution follows the subtask spawning protocol
5. Results are returned to the parent task
