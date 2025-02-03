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

In scenarios where a task step calls `MemorySystem.getRelevantContextFor()` (or otherwise attempts context assembly), any failure is reported as a standard `TASK_FAILURE` (or, if output is invalid, as `INVALID_OUTPUT`).
Partial results from previous steps (if any) may be attached in the `notes` field. No separate "context-generation" error type is defined.

In short, "context operation failures" are reported as `TASK_FAILURE` (or `INVALID_OUTPUT` if the context text is invalid for the next step), and partial sub-task outputs remain available in the error state.

## Dependencies
- Task system must detect resource limits
- Evaluator must handle control flow
- Memory system must maintain context
