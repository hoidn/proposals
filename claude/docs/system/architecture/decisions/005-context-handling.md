# Architecture Decision Record: Context Generation Clarifications

## Status
Accepted

## Context
Recent feedback provided several important clarifications about context generation and associative matching that were either unclear or inconsistent in existing documentation.
The system needs clear policies for how context inheritance and accumulation work across different operator types. This includes sequential tasks, reduce operations, and potential future parallel tasks. We need to define both the inheritance rules and error handling approaches.

## Key Clarifications

### 1. Input Structure for Associative Matching
**Surprise:** The input to getRelevantContextFor() has a specific XML structure with three potential fields:
- Previous outputs (if applicable)
- Inherited context (if applicable)
- Task text
Each with standardized headings from system configuration.

Current documentation does not mention this structure at all.

### 2. Dual Context Components
**Surprise:** When both inheritance and accumulation are active, the system maintains two distinct context components:
- 'Regular' inherited context
- 'Accumulation' context from prior steps
These are tracked separately but can be concatenated for use.

Current documentation suggests a simpler single-context model.

### 3. Resource Allocation Clarification
**Surprise:** The concept of "resource allocation" in relation to context generation timing is irrelevant - the system only signals exhaustion without actual allocation operations.

Current documentation contains references to resource allocation that may be misleading.

### 4. Memory System Scope
**Surprise:** The Memory System does not perform any ranking or prioritization of matched files - this responsibility is explicitly not part of its scope.

Current documentation is ambiguous about this limitation.

## Decision
Update architecture documentation to reflect these clarifications, particularly:
1. The structured XML format for getRelevantContextFor() input
2. The dual-context tracking mechanism
3. Remove references to resource "allocation"
4. Clarify Memory System scope limitations

## Consequences
- Clearer component responsibilities
- More precise context management specification
- Removal of ambiguous resource management concepts
- Better defined Memory System boundaries


# more decisions
### 1. Context Support by Operator Type

- **Sequential Tasks**: Full support for both inheritance and accumulation via `context_management` block
- **Reduce Tasks**: Support context inheritance only (no accumulation)
- **Parallel Execution**: Not implemented in MVP

### 2. Context Management Configuration
- Context management settings (`inherit_context`, `accumulate_data`) are fixed at template definition time
- No dynamic modification during task execution
- Settings remain consistent within a task/sequence

### 3. Reduce Task Context Flow
- Inner task results automatically influence reduction_task context
- Reduction task has access to:
  * Inherited context (if enabled)
  * Results from inner task execution

### 4. Error Handling
- No custom error handling for context failures in MVP
- All context failures map to standard `TASK_FAILURE`
- Future versions may support advanced context handling (e.g., input data reduction)
- No operator-specific error handling mechanisms

## Consequences

### Positive
- Clear, consistent context management model
- Simpler implementation without parallel execution concerns
- Predictable behavior with fixed settings
- Standard error handling reduces complexity
- Clear development path for future enhancements

### Negative
- Less flexibility in dynamic context management
- May require template changes for different context needs
- No operator-specific error handling in MVP
- Must handle all errors through standard `TASK_FAILURE`

## Related
- [Pattern:SequentialTask:2.0]
- [Interface:Memory:3.0]
- Task System operator specifications
