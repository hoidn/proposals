# Evaluator API Interfaces [Interface:Evaluator:1.0]

## Purpose
This document defines the public interfaces for the Evaluator component, which is responsible for AST processing, template variable substitution, and execution control.

## Related Documents
- [Component:Evaluator:1.0](../README.md)
- [Contract:Integration:EvaluatorTask:1.0](../../../system/contracts/interfaces.md)
- [Pattern:TaskExecution:2.0](../../../system/architecture/patterns/task-execution.md)

## Public Interfaces

### Evaluator Interface

```typescript
/**
 * Main Evaluator interface for AST processing and execution
 */
interface Evaluator {
  /**
   * Evaluates an AST node in the given environment
   * @param node The AST node to evaluate
   * @param env The environment to evaluate in
   * @param reparse_depth Current reparse depth (for error recovery)
   * @returns The evaluation result
   */
  eval(node: ASTNode, env: Environment, reparse_depth?: number): any;
  
  /**
   * Handles reparse requests for error recovery
   * @param node The node that failed
   * @param env The environment
   * @param depth Current reparse depth
   * @returns The recovery result
   */
  handle_reparse(node: ASTNode, env: Environment, depth: number): any;
  
  /**
   * Determines if an operator is atomic
   * @param operator The operator to check
   * @returns True if the operator is atomic
   */
  is_atomic(operator: any): boolean;
  
  /**
   * Executes an LLM call for an atomic task
   * @param operator The operator to execute
   * @param env The environment
   * @returns The LLM execution result
   */
  execute_llm(operator: any, env: Environment): any;
  
  /**
   * Applies an operator to arguments in the given environment
   * @param operator The operator to apply
   * @param args The arguments to apply
   * @param env The environment
   * @returns The application result
   */
  apply(operator: any, args: any[], env: Environment): any;
  
  /**
   * Substitutes template variables in a string
   * @param template The template string
   * @param env The environment
   * @returns The resolved string
   */
  evaluateTemplateVariables(template: string, env: Environment): string;
}
```

### Environment Interface

```typescript
/**
 * Lexical environment for variable scoping and context management
 */
interface Environment {
  /**
   * Looks up a variable in the environment
   * @param name The variable name
   * @returns The variable value or undefined
   */
  lookup(name: string): any;
  
  /**
   * Extends the environment with new bindings
   * @param names Parameter names
   * @param values Parameter values
   * @returns A new environment with the bindings
   */
  extend(names: string[], values: any[]): Environment;
  
  /**
   * Gets the parent environment
   * @returns The parent environment or null
   */
  getParent(): Environment | null;
  
  /**
   * Gets the context associated with this environment
   * @returns The context object
   */
  getContext(): any;
  
  /**
   * Sets a variable in the current environment
   * @param name The variable name
   * @param value The variable value
   */
  define(name: string, value: any): void;
}
```

### TaskResult Interface

```typescript
/**
 * Result of a task execution
 */
interface TaskResult {
  /**
   * The main output content
   */
  content: string;
  
  /**
   * Execution status
   */
  status: 'COMPLETE' | 'FAILED' | 'CONTINUATION';
  
  /**
   * Metadata and notes about the execution
   */
  notes: {
    /**
     * Optional subtask request for CONTINUATION status
     */
    subtask_request?: SubtaskRequest;
    
    /**
     * Optional evaluation request for CONTINUATION status
     */
    evaluation_request?: EvaluationRequest;
    
    /**
     * Optional partial output for FAILED status
     */
    partialOutput?: string;
    
    /**
     * Optional error details for FAILED status
     */
    error?: TaskError;
    
    /**
     * Optional success score for completed tasks
     */
    success_score?: number;
    
    [key: string]: any;
  };
}
```

### Resource Tracking Interface

```typescript
/**
 * Interface for resource tracking during evaluation
 */
interface ResourceTracker {
  /**
   * Tracks resource usage for an operation
   * @param resourceType The type of resource
   * @param amount The amount used
   */
  trackUsage(resourceType: 'turns' | 'tokens' | 'context', amount: number): void;
  
  /**
   * Checks if a resource limit has been exceeded
   * @param resourceType The type of resource
   * @returns True if the limit is exceeded
   */
  isLimitExceeded(resourceType: 'turns' | 'tokens' | 'context'): boolean;
  
  /**
   * Gets current resource usage metrics
   * @returns Object with resource usage metrics
   */
  getMetrics(): ResourceMetrics;
}
```

## Integration Points

### Compiler Integration
The Evaluator receives AST nodes from the Compiler and processes them according to their type.

### Handler Integration
The Evaluator delegates LLM execution to the Handler and receives execution results.

### Memory System Integration
The Evaluator interacts with the Memory System for context management according to task configuration.

### Task System Integration
The Evaluator implements the execution logic for various task types defined by the Task System.
