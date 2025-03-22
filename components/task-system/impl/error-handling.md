# Error Handling Implementation

This document provides implementation details for error handling patterns defined in [Pattern:Error:1.0].

## Error Type Implementation [Implementation:ErrorTypes:1.0]

```typescript
// Resource Exhaustion Error
function createResourceExhaustionError(resource: 'turns' | 'context', metrics: any): TaskError {
  return {
    type: 'RESOURCE_EXHAUSTION',
    resource,
    message: `${resource.charAt(0).toUpperCase() + resource.slice(1)} limit exceeded`,
    metrics
  };
}

// Task Failure Error
function createTaskFailureError(
  reason: TaskFailureReason, 
  message: string, 
  details?: any
): TaskError {
  return {
    type: 'TASK_FAILURE',
    reason,
    message,
    details
  };
}

// Output Format Error
function createOutputFormatError(expectedType: string, actualType: string, content: string): TaskError {
  return {
    type: 'TASK_FAILURE',
    reason: 'output_format_failure',
    message: `Expected output of type "${expectedType}" but got "${actualType}"`,
    details: {
      expectedType,
      actualType,
      content
    }
  };
}
```

## Error Recovery Implementation [Implementation:ErrorRecovery:1.0]

```typescript
class Evaluator {
  async recoverFromError(error: TaskError, task: Task): Promise<TaskResult | null> {
    // Resource exhaustion handling
    if (error.type === 'RESOURCE_EXHAUSTION') {
      return this.attemptTaskDecomposition(task, error);
    }
    
    // Task failure handling
    if (error.type === 'TASK_FAILURE') {
      switch (error.reason) {
        case 'context_retrieval_failure':
          return this.recoverFromContextFailure(task, error);
          
        case 'output_format_failure':
          return this.recoverFromFormatFailure(task, error);
          
        case 'subtask_failure':
          return this.recoverFromSubtaskFailure(task, error);
          
        default:
          // No recovery strategy for other failure types
          return null;
      }
    }
    
    // No recovery strategy for other error types
    return null;
  }
  
  private async attemptTaskDecomposition(task: Task, error: TaskError): Promise<TaskResult | null> {
    // Implementation details for task decomposition
    // ...
  }
  
  private async recoverFromContextFailure(task: Task, error: TaskError): Promise<TaskResult | null> {
    // Implementation details for context failure recovery
    // ...
  }
  
  private async recoverFromFormatFailure(task: Task, error: TaskError): Promise<TaskResult | null> {
    // Implementation details for format failure recovery
    // ...
  }
  
  private async recoverFromSubtaskFailure(task: Task, error: TaskError): Promise<TaskResult | null> {
    // Implementation details for subtask failure recovery
    // ...
  }
}
```

## Error Handling Examples [Implementation:ErrorExamples:1.0]

### Sequential Task Failure Example

```typescript
try {
  const result = await taskSystem.executeTask(sequentialTask, memorySystem);
  console.log("Task completed successfully:", result.content);
} catch (error) {
  if (error.type === 'TASK_FAILURE' && error.reason === 'subtask_failure') {
    console.log(`Sequential task failed at step ${error.details.failedStep}`);
    
    // Access partial results from completed steps
    if (error.details.partialResults) {
      error.details.partialResults.forEach(result => {
        console.log(`Step ${result.stepIndex} output: ${result.content}`);
      });
    }
    
    // Potentially recover using partial results
    const recoveryResult = await evaluator.recoverWithPartialResults(error);
    if (recoveryResult) {
      console.log("Recovery succeeded:", recoveryResult.content);
    }
  }
}
```

### Resource Exhaustion Example

```typescript
try {
  const result = await taskSystem.executeTask(complexTask, memorySystem);
  console.log("Task completed successfully:", result.content);
} catch (error) {
  if (error.type === 'RESOURCE_EXHAUSTION') {
    console.log(`Resource limit exceeded: ${error.resource}`);
    console.log(`Used: ${error.metrics.used}, Limit: ${error.metrics.limit}`);
    
    // Attempt decomposition with reparse template
    const decomposedResult = await taskSystem.executeTask(
      createReparseTemplate(complexTask, error),
      memorySystem
    );
    
    console.log("Decomposed execution result:", decomposedResult.content);
  }
}
```

For additional details on error patterns, see [Pattern:Error:1.0].
