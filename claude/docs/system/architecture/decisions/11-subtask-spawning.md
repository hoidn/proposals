# Architecture Decision Record: Subtask Spawning Mechanism

## Status
Accepted

## Context
The system needs a standardized mechanism for tasks to dynamically spawn subtasks during execution. This capability enables adaptive task decomposition, dependency discovery, verification through testing, and dynamic workflow execution.

## Decision
Implement a standardized subtask spawning mechanism based on structured continuation requests that integrates with our three-dimensional context management model and uses direct parameter passing rather than environment variables.

## Specification

### 1. Task Result & Subtask Request Structure

```typescript
interface TaskResult {
    content: string;
    status: "CONTINUATION" | "COMPLETE" | "WAITING" | "FAILED";
    notes: {
        subtask_request?: SubtaskRequest;
        [key: string]: any;
    };
}

interface SubtaskRequest {
    type: string;           // Type of subtask
    description: string;    // Human-readable description
    inputs: Record<string, any>; // Inputs for the subtask
    template_hints?: string[]; // Optional hints for matching
    return_expectations?: string; // Expected output format
    max_depth?: number;     // Optional depth override
}
```

### 2. Context Management Integration

Subtasks fully integrate with our three-dimensional context management model:

```xml
<context_management>
    <inherit_context>full|none|subset</inherit_context>
    <accumulate_data>true|false</accumulate_data>
    <accumulation_format>notes_only|full_output</accumulation_format>
    <fresh_context>enabled|disabled</fresh_context>
</context_management>
```

**Default settings for subtasks:**
- `inherit_context`: "full"
- `accumulate_data`: "false" 
- `fresh_context`: "disabled"

### 3. Execution Flow

When a task returns with CONTINUATION status and a subtask_request:

1. TaskSystem extracts the subtask_request
2. Selects appropriate template using associative matching
3. Creates inputs for the subtask, incorporating parent task context
4. Executes the subtask with configured context management
5. Resumes the parent task with subtask results as direct inputs

```typescript
// Simplified execution flow
async function executeTask(task, inputs, depth = 0) {
    // Check depth limits
    if (depth >= (task.maxDepth || systemConfig.maxTaskDepth)) {
        return createMaxDepthError();
    }
    
    const result = await executeTaskWithLLM(task, inputs);
    
    if (result.status === "CONTINUATION" && result.notes?.subtask_request) {
        const subtaskRequest = result.notes.subtask_request;
        const subtaskTemplate = await findMatchingTemplate(subtaskRequest);
        const subtaskResult = await executeTask(subtaskTemplate, subtaskRequest.inputs, depth + 1);
        
        // Resume original task with subtask results
        return executeTask(task, {...inputs, subtask_result: subtaskResult}, depth);
    }
    
    return result;
}
```

### 4. Depth Control

- Default maximum depth: 10 levels (configurable via `maxTaskDepth`)
- Subtasks may specify an override via `max_depth` parameter
- System returns FAILED status with reason="max_depth_exceeded" when limit reached
- Cycle detection uses hash-based subtask signature tracking

### 5. Error Handling

Subtask failures follow our standard error taxonomy:

```typescript
{
  type: 'TASK_FAILURE',
  reason: 'subtask_failure', // Or other specific reason
  message: 'Subtask execution failed',
  details: {
    subtaskType: string,
    partialResults?: any,
    originalError: TaskError
  }
}
```

## Context Combinations Reference

| inherit_context | accumulate_data | fresh_context | Result |
|-----------------|-----------------|---------------|--------|
| full | false | disabled | Subtask has only parent context (DEFAULT) |
| full | false | enabled | Parent context + additional context |
| full | true | disabled | Parent context + accumulated data |
| full | true | enabled | Parent context + accumulated data + additional context |
| none | false | disabled | Minimal context (inputs only) |
| none | false | enabled | Fresh context only |
| none | true | disabled | Accumulated data only |
| none | true | enabled | Accumulated data + fresh context |
| subset | false | disabled | Relevant parent context only |
| subset | false | enabled | Relevant parent context + additional context |
| subset | true | disabled | Relevant parent context + accumulated data |
| subset | true | enabled | Relevant parent context + accumulated data + additional context |

## Relationship to Director-Evaluator Loop

These are complementary features:

- **Director-Evaluator Loop**: Specialized pattern for iterative refinement with built-in iteration management
- **Subtask Spawning**: General-purpose mechanism for dynamic, ad-hoc subtask creation

## Implementation Requirements

1. **Task System Enhancements**
   - Add CONTINUATION status processing
   - Implement template matching for subtasks
   - Add depth tracking and enforcement
   - Provide direct input/output mapping

2. **Testing Requirements**
   - Unit tests for depth control mechanisms
   - Integration tests for context inheritance
   - Verification of proper result passing
   - Error propagation tests

## Migration Guidance

1. Replace environment variable usage with direct parameter passing
2. Update subtasks to use standardized SubtaskRequest format
3. Add explicit context_management blocks
4. Implement depth tracking

## Performance Considerations

- Monitor context size in deep subtask chains
- Cache frequently used subtask templates
- Ensure proper cleanup after subtask completion
- Set appropriate depth limits based on performance testing

## Key Questions Addressed

1. **Maximum Subtask Depth**: Default 10 levels, configurable system-wide
2. **Template Selection**: Support both type-based and content-based matching
3. **Result Format**: Standardized base structure with type-specific extensions

## Related ADRs
- **Depends on**: [ADR 7: Context Management Standardization], [ADR 8: Error Taxonomy]
- **Extends**: [ADR 9: Partial Results Policy]
- **Related to**: [ADR 10: Evaluator-to-Director Feedback Flow]

## Consequences

### Positive
- Standardized mechanism for dynamic task composition
- Clear data flow between parent and subtasks
- Consistent context management across all task types
- Explicit depth control prevents runaway execution

### Negative
- Increased implementation complexity
- Additional depth tracking overhead
- More complex debugging for deep task chains
- Potential performance impact with deeply nested subtasks
