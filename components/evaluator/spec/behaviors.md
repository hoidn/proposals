# Evaluator Behaviors [Spec:EvaluatorBehaviors:1.0]

## Purpose
This document describes the runtime behaviors of the Evaluator component, focusing on template variable substitution, error handling, context management, resource coordination, and function call behavior.

## Related Documents
- [Component:Evaluator:1.0](../README.md)
- [Pattern:Error:1.0](../../../system/architecture/patterns/errors.md)
- [ADR 14: Operator Context Configuration](../../../system/architecture/decisions/completed/014-operator-ctx-config.md)

## Template Variable Substitution

The Evaluator is solely responsible for all template variable substitution:

1. **Substitution Process**:
   - Variables are identified using the `{{variable_name}}` syntax
   - Variables are resolved from the current environment
   - Substitution occurs before passing content to the Handler
   - Different resolution rules apply for function vs. standard templates

2. **Function Template Resolution**:
   - Function templates have explicit parameter declarations
   - Arguments are evaluated in the caller's environment
   - A new environment is created with parameter bindings
   - The function body is evaluated in this new environment

3. **Standard Template Resolution**:
   - Variables are resolved from the current environment
   - The environment includes all parent bindings
   - Variables not found in the environment cause resolution errors

4. **Error Handling**:
   - Missing variables generate `template_resolution_failure` errors
   - Type mismatches generate appropriate error messages
   - Partial substitution results are preserved for debugging

```mermaid
flowchart TD
    A[Template with {{variables}}] --> B{Template Type?}
    B -->|Function Template| C[Evaluate Arguments in Caller's Environment]
    B -->|Standard Template| D[Resolve Variables from Current Environment]
    C --> E[Create New Environment with Parameter Bindings]
    E --> F[Evaluate Template Body in New Environment]
    D --> G[Replace All {{variables}} with Values]
    F & G --> H[Fully Resolved Content]
    H --> I[Pass to Handler]
```

## Error Detection and Handling

The Evaluator implements comprehensive error detection and handling:

1. **Error Categories**:
   - **Resource Exhaustion**: Detected by the Handler, surfaced to the Evaluator
   - **Task Failure**: Various failure types with specific reason codes
   - **Progress Failure**: Detected when a task fails to make progress

2. **Error Detection**:
   - Resource limits are monitored during execution
   - Output validation is performed after task completion
   - Progress is tracked for iterative tasks

3. **Error Handling**:
   - **Reparse Mechanism**: For resource exhaustion, attempts task decomposition
   - **Partial Results**: Preserved for debugging and recovery
   - **Error Propagation**: Errors are propagated to parent tasks with context

4. **Recovery Strategies**:
   - **Alternative Templates**: For failed tasks, alternative templates may be tried
   - **Decomposition**: Complex tasks may be broken down into simpler subtasks
   - **Fallback Approaches**: Simpler approaches may be attempted for failed tasks

The Evaluator follows the error handling pattern defined in [Pattern:Error:1.0], ensuring consistent error behavior across the system.

## Context Management Behavior

The Evaluator implements the three-dimensional context management model:

1. **Inheritance Dimension**:
   - `full`: The Evaluator includes the complete parent context
   - `none`: The Evaluator creates a new, empty context
   - `subset`: The Evaluator includes only relevant parent context

2. **Accumulation Dimension**:
   - When `accumulate_data` is `true`, the Evaluator accumulates previous step outputs
   - The `accumulation_format` controls whether to store `notes_only` or `full_output`
   - Accumulated data is available to subsequent steps

3. **Fresh Context Dimension**:
   - When `fresh_context` is `enabled`, the Evaluator generates new context via associative matching
   - This is mutually exclusive with context inheritance

4. **File Paths Integration**:
   - The Evaluator processes specified file paths regardless of other context settings
   - Files are fetched using Handler tools before task execution
   - File contents are integrated with other context sources

The Evaluator applies different default context settings based on operator type and subtype, following the hybrid configuration approach defined in [ADR 14: Operator Context Configuration].

## Resource Coordination

The Evaluator coordinates resource tracking with the Handler:

1. **Resource Types**:
   - **Turns**: The number of LLM interactions
   - **Tokens**: The total token usage
   - **Context Window**: The context window size

2. **Resource Tracking**:
   - The Handler tracks resource usage during execution
   - The Evaluator receives resource metrics from the Handler
   - Resource limits are enforced by the Handler

3. **Resource Exhaustion Handling**:
   - When a resource limit is exceeded, the Handler raises a `RESOURCE_EXHAUSTION` error
   - The Evaluator attempts recovery through the reparse mechanism
   - If recovery fails, the error is propagated to the parent task

4. **Resource Optimization**:
   - The Evaluator optimizes resource usage through context management
   - Large outputs may be summarized to avoid context window exhaustion
   - Sequential tasks may use different context management strategies for different steps

## Function Call Behavior

The Evaluator implements function call behavior according to the function-based template pattern:

1. **Function Definition**:
   - Functions are defined as templates with explicit parameter declarations
   - Each function has its own lexical scope
   - Functions are registered in a central registry

2. **Function Lookup**:
   - Functions are looked up by name during execution
   - If a function is not found, an appropriate error is generated
   - Function lookup respects lexical scoping rules

3. **Argument Evaluation**:
   - Arguments are evaluated in the caller's environment
   - Arguments can be literals, variable references, or nested expressions
   - Argument evaluation follows the same rules as other expressions

4. **Environment Creation**:
   - A new environment is created for each function call
   - The environment includes bindings for all parameters
   - The environment has access to the caller's environment through its parent reference

5. **Function Execution**:
   - The function body is evaluated in the new environment
   - The result is returned to the caller
   - Resources used during function execution are tracked

This function call behavior ensures clear data dependencies, improved reasoning about variable scope, and better encapsulation of implementation details.
