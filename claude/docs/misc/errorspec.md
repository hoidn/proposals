# Error Type Hierarchy and Handling Design

## Purpose
Define the core error types that enable control flow and task adaptation in the intelligent task execution system.

## Error Categories

### 1. Resource Exhaustion
- **Purpose**: Signal when system resource limits are exceeded
- **Characteristics**:
  - Parameterized resource type and limits (e.g., turns, context window)
  - Clear threshold for triggering
  - No partial results preserved
- **Control Flow Impact**: 
  - Signals that task requires more resources than available

### 2. Task Failure
- **Purpose**: Signal that a task cannot be completed as attempted
- **Characteristics**:
  - Generic failure mechanism
  - No internal categorization
  - No partial results preserved
- **Control Flow Impact**:
  - Task terminates
  - Control returns to parent task/evaluator

## Error Handling Principles

### 1. Separation of Concerns
- Errors purely signal failure conditions
- No recovery logic in error objects
- No state/progress tracking
- No partial results

### 2. Control Flow
- Resource Exhaustion → Task too large
- Task Failure → Termination
- No retry logic in components

### 3. Context Independence  
- Errors do not carry execution state
- No partial results in errors
- Clean separation from context management

## Integration Points

### Task System
- Detects resource exhaustion
- Signals task failures
- Handles decomposition requests

### Evaluator
- Receives error signals
- Manages control flow
- Requests decomposition when needed

### Memory System
- Preserves stable context
- No error-specific state
- No partial results

## Design Decisions & Rationale

1. Minimal Error Categories
   - Only essential control flow signals
   - Clear mapping to system behaviors
   - Simplified error handling

2. Stateless Error Design
   - Separates control flow from state
   - Clean component boundaries
   - Simplified recovery

3. No Complex Recovery
   - Decomposition as consequence not strategy
   - Simplified control flow
   - Clear system behavior

## Context Operation Failures

In scenarios where an Evaluator step calls `MemorySystem.getRelevantContextFor()` or otherwise attempts context assembly:
- We treat any failures as standard `TASK_FAILURE`.
- The error message should clarify that a context operation failed.
- **No new error category** is introduced for context issues alone.
- **Preserve partial results** if the context operation fails during a multi-step (sequential) task. These partial results can be included in the final error details or the `notes` field of the `TaskResult`.
- This approach ensures a consistent error taxonomy without branching into specialized context error types.

In short, "context operation failures" are reported as `TASK_FAILURE` (or `INVALID_OUTPUT` if the context text is invalid for the next step), and partial sub-task outputs remain available in the error state.

## Dependencies
- Task system must detect resource limits
- Evaluator must handle control flow
- Memory system must maintain context
