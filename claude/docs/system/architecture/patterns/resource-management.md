# Resource Management Pattern [Pattern:ResourceManagement:1.0]

## Purpose & Constraints
Defines the resource management strategy for the task execution system focusing on:
- Memory hierarchy management
- Resource allocation and tracking
- Context preservation and isolation
- Limit enforcement

## Core Components

### Memory Hierarchy
1. Long-term Memory
   - Stores data and procedures
   - Accessed via associative memory system
   - Read-only during task execution
   - Managed by Memory System component

2. Working Memory
   - Active computation space
   - Task-specific context
   - Managed through Environment objects
   - Cleared after task completion

3. Context Frames
   - Capture complete execution environments
   - Include variable bindings and working memory
   - Extended through Environment.extend()
   - Minimal context principle applied

### Resource Tracking

#### Handler Responsibility
- One Handler per task execution
- Tracks resource usage:
  * Turn counts
  * Context window size
  * Token usage
  * Peak usage statistics
- Enforces resource limits
- Manages clean termination

#### Isolation Requirements
- No cross-Handler resource pooling
- Per-session resource isolation
- Clean resource release on completion
- Independent Handler execution

### Context Management

#### Window Management
- Token-based calculation
- Explicit size monitoring
- Fraction-based limits
- No content optimization
- Warning thresholds at 80%
- Hard limits with error handling

#### Context Preservation
- Context frames capture environments
- Minimal required context per task
- Associative memory mediation
- Clean extension mechanism

## Resource Configuration

### Default Configuration
- Base resource limits
- Warning thresholds
- Default turn counts
- Context window limits

### Per-Task Overrides
- Task-specific limits
- Custom thresholds
- Resource constraints
- Performance targets

## Interactions

### With Memory System [Component:MemorySystem:1.0]
- Provides long-term storage
- Manages context persistence
- Handles file operations
- Maintains memory hierarchy

### With Task System [Component:TaskSystem:1.0]
- Creates/manages Handlers
- Enforces resource limits
- Manages task execution
- Handles resource errors

### With Handler [Component:Handler:1.0]
- Tracks resource usage
- Enforces limits
- Manages session lifecycle
- Reports resource metrics

## Implementation Requirements

### Resource Tracking
```typescript
// Resource metrics definition moved to spec/types.md
// See [Type:ResourceMetrics:1.0] for the complete interface
```

### Handler Configuration
```typescript
interface HandlerConfig {
    maxTurns: number;
    maxContextWindowFraction: number;
    warningThreshold: number;
    defaultModel?: string;
    systemPrompt: string;
}
```

## Error Handling

### Resource Exhaustion
- Immediate task termination
- Clean resource release
- Error surfacing with metrics
- No automatic retry

### Context Overflow
- Token limit enforcement
- Warning at threshold
- Clean termination
- Context metrics reported

### Progress Failure
- Resource accounting completion
- State cleanup
- Error propagation
- Recovery guidance

### Sequential Task Resources

For **sequential** tasks, the Evaluator maintains a step-by-step record of partial results and history, often called `SequentialHistory`. This history is **not** tracked against the Handler's context window limits. Instead:

- **Evaluator** owns the entire sequential history for multi-step tasks.
- **Handler** continues to track standard resource usage (turns, tokens).
- Because the sequential history is purely textual or metadata that the Evaluator stores separately, it does not consume the Handler's context window.
- If the task is configured to accumulate data (`<accumulate_data>true</accumulate_data>`), the Evaluator may pass prior step outputs into `MemorySystem.getRelevantContextFor()`.
- This separation ensures Handler resource metrics stay consistent and the Evaluator can keep any relevant partial outputs for as long as needed.
- Once the sequential task completes (success or failure), the Evaluator discards (or archives) the sequential history to free memory.

This design ensures a clean boundary between higher-level multi-step results (owned by the Evaluator) and resource usage constraints (handled by the Handler).

## Related Patterns
- [Pattern:Error:1.0] - Error handling strategy
- [Pattern:TaskExecution:1.0] - Task execution flow
