# Evaluator Interfaces [Spec:EvaluatorInterfaces:1.0]

## Purpose
This document defines the internal interfaces used by the Evaluator component, including the Environment interface, TaskResult structure, and output formats.

## Related Documents
- [Component:Evaluator:1.0](../README.md)
- [Interface:Evaluator:1.0](../api/interfaces.md)
- [ADR 15: Notes Field Standardization](../../../system/architecture/decisions/completed/015-notes-field-standardization.md)
- [ADR 16: Output Structure Simplification](../../../system/architecture/decisions/completed/016-output-structure-simplification.md)

## Internal Interfaces

### AST Node Interface

```typescript
/**
 * Base interface for all AST nodes
 */
interface ASTNode {
  /**
   * The type of node
   */
  type: string;
  
  /**
   * Optional node metadata
   */
  metadata?: Record<string, any>;
  
  /**
   * Optional context management configuration
   */
  contextManagement?: ContextManagementConfig;
}

/**
 * Template node representing a function definition
 */
interface TemplateNode extends ASTNode {
  type: 'template';
  name: string;
  params: string[];
  body: ASTNode;
}

/**
 * Function call node representing a function invocation
 */
interface FunctionCallNode extends ASTNode {
  type: 'function_call';
  templateName: string;
  args: ArgumentNode[];
}

/**
 * Atomic task node
 */
interface AtomicNode extends ASTNode {
  type: 'atomic';
  description: string;
  inputs?: Record<string, any>;
  disableContext?: boolean;
  filePaths?: string[];
}

/**
 * Sequential task node
 */
interface SequentialNode extends ASTNode {
  type: 'sequential';
  description: string;
  steps: ASTNode[];
}

/**
 * Reduce task node
 */
interface ReduceNode extends ASTNode {
  type: 'reduce';
  description: string;
  inputs: any[];
  reducer: ASTNode;
  initialValue: any;
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

### Context Management Interface

```typescript
/**
 * Context management configuration
 */
interface ContextManagementConfig {
  /**
   * Controls parent context inheritance
   */
  inheritContext?: 'full' | 'none' | 'subset';
  
  /**
   * Controls whether previous step outputs are accumulated
   */
  accumulateData?: boolean;
  
  /**
   * Controls the format of accumulated data
   */
  accumulationFormat?: 'notes_only' | 'full_output';
  
  /**
   * Controls whether new context is generated via associative matching
   */
  freshContext?: 'enabled' | 'disabled';
}
```

## TaskResult Structure

The Evaluator uses a simplified output structure as defined in [ADR 16: Output Structure Simplification]:

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

### Atomic Tasks
For atomic tasks, the structure is straightforward:
- `content`: Contains all output (complete or partial)
- `notes`: Contains only metadata (never content)
- `status` indicates completion:
  * `COMPLETE`: Content is final
  * `FAILED`: Content may be partial
  * `CONTINUATION`: Content is intermediate

### Sequential Tasks
For sequential tasks, the structure preserves step outputs with proper separation:
```typescript
notes: {
  partialResults: [
    {
      stepIndex: number,
      content: string,      // Step output
      metadata: {           // Step metadata
        status: string,
        [key: string]: any
      }
    }
  ]
}
```

### Reduce Tasks
For reduce tasks, the structure preserves processed inputs with proper separation:
```typescript
notes: {
  processedResults: [
    {
      inputIndex: number,
      content: string,      // Processing output
      metadata: {           // Processing metadata
        status: string,
        [key: string]: any
      }
    }
  ]
}
```

## Output Formats

The Evaluator supports different output formats through the `output_format` element:

1. **Format Declaration**:
   - Format is declared via `<output_format>` element with required `type` attribute
   - Supported format types:
     * "json" - Structured JSON data
     * "text" - Plain text (default)
   - Optional `schema` attribute for type validation:
     * "object" - JSON object
     * "array" or "[]" - JSON array
     * "string[]" - Array of strings
     * "number" - Numeric value
     * "boolean" - Boolean value

2. **JSON Detection**:
   - When `type="json"`, the Evaluator attempts to parse content as JSON
   - Parsed content is added to TaskResult as `parsedContent` property
   - If parsing fails, the Evaluator falls back to original string content

3. **Type Validation**:
   - The Evaluator validates parsed content against the `schema` attribute
   - If there's a type mismatch, an `output_format_failure` error is generated
   - The original content is preserved in the error details

4. **Function Return Type Validation**:
   - Function templates can specify return types via `returns` attribute
   - Return types are validated against actual output
   - Type mismatches generate validation errors

Example error structure for output_format_failure:
```typescript
{
  type: 'TASK_FAILURE',
  reason: 'output_format_failure',
  message: 'Expected output of type "array" but got "object"',
  details: {
    expectedType: "array",
    actualType: "object",
    content: "..." // The original output is now in content field
  }
}
```
