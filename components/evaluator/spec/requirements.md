# Evaluator Requirements [Spec:EvaluatorRequirements:1.0]

## Purpose
This document defines the requirements for the Evaluator component, including core requirements, template substitution requirements, context management requirements, subtask spawning requirements, and error handling requirements.

## Related Documents
- [Component:Evaluator:1.0](../README.md)
- [ADR 11: Subtask Spawning Mechanism](../../../system/architecture/decisions/completed/011-subtask-spawning.md)
- [ADR 14: Operator Context Configuration](../../../system/architecture/decisions/completed/014-operator-ctx-config.md)

## Core Requirements

### Functional Requirements

1. **AST Processing**
   - The Evaluator MUST process AST nodes according to their type
   - The Evaluator MUST support all defined node types (atomic, sequential, reduce, etc.)
   - The Evaluator MUST handle nested node structures of arbitrary depth

2. **Environment Management**
   - The Evaluator MUST implement a lexical environment model for variable scoping
   - The Evaluator MUST support environment extension for function calls
   - The Evaluator MUST maintain proper variable bindings throughout execution

3. **Execution Control**
   - The Evaluator MUST delegate LLM execution to the Handler
   - The Evaluator MUST track resource usage during execution
   - The Evaluator MUST handle execution errors and attempt recovery

4. **Result Processing**
   - The Evaluator MUST return results in the standardized TaskResult format
   - The Evaluator MUST include appropriate metadata in the notes field
   - The Evaluator MUST handle partial results for failed tasks

### Non-Functional Requirements

1. **Performance**
   - The Evaluator MUST optimize resource usage through context management
   - The Evaluator SHOULD minimize unnecessary LLM calls

2. **Reliability**
   - The Evaluator MUST handle errors gracefully and attempt recovery
   - The Evaluator MUST preserve partial results for failed tasks

3. **Maintainability**
   - The Evaluator MUST follow a clean, modular design
   - The Evaluator MUST separate concerns appropriately

4. **Extensibility**
   - The Evaluator MUST support adding new node types
   - The Evaluator MUST support adding new execution strategies

## Template Substitution Requirements

1. **Variable Resolution**
   - The Evaluator MUST resolve all template variables before passing content to the Handler
   - The Evaluator MUST support the `{{variable_name}}` syntax for variable references
   - The Evaluator MUST look up variables in the current environment and parent environments

2. **Function Templates**
   - The Evaluator MUST support function templates with explicit parameter declarations
   - The Evaluator MUST evaluate arguments in the caller's environment
   - The Evaluator MUST create a new environment with parameter bindings for function calls
   - The Evaluator MUST evaluate the function body in the new environment

3. **Error Handling**
   - The Evaluator MUST detect and report missing variables
   - The Evaluator MUST detect and report type mismatches
   - The Evaluator MUST preserve partial substitution results for debugging

4. **Type Validation**
   - The Evaluator MUST validate output types against declared return types
   - The Evaluator MUST generate appropriate errors for type mismatches

## Context Management Requirements

1. **Three-Dimensional Model**
   - The Evaluator MUST implement the three-dimensional context management model
   - The Evaluator MUST support all values for `inherit_context`, `accumulate_data`, and `fresh_context`
   - The Evaluator MUST enforce the mutual exclusivity constraint between `inherit_context` and `fresh_context`

2. **Default Settings**
   - The Evaluator MUST apply operator-specific default context settings
   - The Evaluator MUST override defaults with explicit configuration when present

3. **Context Preparation**
   - The Evaluator MUST prepare context according to the configuration
   - The Evaluator MUST handle inheritance, accumulation, and fresh context generation

4. **File Paths Integration**
   - The Evaluator MUST process specified file paths regardless of other context settings
   - The Evaluator MUST fetch file contents using Handler tools
   - The Evaluator MUST integrate file contents with other context sources

## Subtask Spawning Requirements

As defined in [ADR 11: Subtask Spawning Mechanism], the Evaluator must implement these requirements:

1. **Request Processing**
   - The Evaluator MUST detect and validate subtask requests
   - The Evaluator MUST check depth limits and detect cycles
   - The Evaluator MUST prepare context according to the request configuration
   - The Evaluator MUST select an appropriate template for the subtask
   - The Evaluator MUST execute the subtask with proper resource tracking

2. **Context Management**
   - The Evaluator MUST apply default context settings for subtasks
   - The Evaluator MUST override defaults with explicit configuration when present
   - The Evaluator MUST prepare context based on the configuration
   - The Evaluator MUST create a new environment with the prepared context and inputs

3. **Depth Control**
   - The Evaluator MUST track subtask nesting depth
   - The Evaluator MUST enforce a maximum depth limit
   - The Evaluator MUST detect and prevent cycles in subtask spawning

4. **Tool Integration**
   - The Evaluator MUST integrate with the unified tool interface
   - The Evaluator MUST transform tool calls to subtask requests when appropriate
   - The Evaluator MUST transform subtask results to tool responses

5. **Error Handling**
   - The Evaluator MUST wrap subtask errors with context
   - The Evaluator MUST preserve partial results for failed subtasks
   - The Evaluator MUST propagate errors to the parent task

## Error Handling Requirements

1. **Error Detection**
   - The Evaluator MUST detect resource exhaustion errors from the Handler
   - The Evaluator MUST detect task failures of various types
   - The Evaluator MUST detect progress failures

2. **Error Handling**
   - The Evaluator MUST implement the reparse mechanism for resource exhaustion
   - The Evaluator MUST preserve partial results for debugging and recovery
   - The Evaluator MUST propagate errors to parent tasks with context

3. **Recovery Strategies**
   - The Evaluator SHOULD attempt alternative templates for failed tasks
   - The Evaluator SHOULD break down complex tasks into simpler subtasks
   - The Evaluator SHOULD attempt fallback approaches for failed tasks

4. **Error Reporting**
   - The Evaluator MUST include detailed error information in the TaskResult
   - The Evaluator MUST include the error type, reason, and message
   - The Evaluator MUST include relevant details for debugging
