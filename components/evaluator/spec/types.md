# Evaluator Types [Spec:EvaluatorTypes:1.0]

## Purpose
This document defines the types used by the Evaluator component, including AST node types, environment types, context types, and function-based template types.

## Related Documents
- [Component:Evaluator:1.0](../README.md)
- [ADR 12: Function-Based Template Model](../../../system/architecture/decisions/completed/012-function-based-templates.md)
- [ADR 6: Context Types](../../../system/architecture/decisions/006-context-types.md)

## AST Node Types

The Evaluator works with these AST node types:

```typescript
/**
 * Base AST node type
 */
type ASTNode = {
  type: string;
  [key: string]: any;
};

/**
 * Template node representing a function definition
 */
type TemplateNode = ASTNode & {
  type: 'template';
  name: string;
  params: string[];
  body: ASTNode;
  returns?: string; // Optional return type
};

/**
 * Function call node representing a function invocation
 */
type FunctionCallNode = ASTNode & {
  type: 'function_call';
  templateName: string;
  args: ArgumentNode[];
};

/**
 * Argument node representing a function argument
 */
type ArgumentNode = ASTNode & {
  type: 'argument';
  value: any; // Can be a literal or another AST node
};

/**
 * Atomic task node
 */
type AtomicNode = ASTNode & {
  type: 'atomic';
  description: string;
  inputs?: Record<string, any>;
  disableContext?: boolean;
  filePaths?: string[];
  contextManagement?: ContextManagementConfig;
  outputFormat?: OutputFormatConfig;
};

/**
 * Sequential task node
 */
type SequentialNode = ASTNode & {
  type: 'sequential';
  description: string;
  steps: ASTNode[];
  contextManagement?: ContextManagementConfig;
};

/**
 * Reduce task node
 */
type ReduceNode = ASTNode & {
  type: 'reduce';
  description: string;
  inputs: any[];
  reducer: ASTNode;
  initialValue: any;
  contextManagement?: ContextManagementConfig;
};

/**
 * Director-evaluator loop node
 */
type DirectorEvaluatorNode = ASTNode & {
  type: 'director_evaluator_loop';
  description: string;
  maxIterations: number;
  director: ASTNode;
  evaluator: ASTNode;
  scriptExecution?: ScriptExecutionConfig;
  terminationCondition?: string;
  contextManagement?: ContextManagementConfig;
};
```

## Environment Types

The Evaluator uses these environment-related types:

```typescript
/**
 * Environment type for variable scoping
 */
type Environment = {
  lookup(name: string): any;
  extend(names: string[], values: any[]): Environment;
  getParent(): Environment | null;
  getContext(): any;
  define(name: string, value: any): void;
};

/**
 * Global environment type
 */
type GlobalEnvironment = Environment & {
  registerTemplate(template: TemplateNode): void;
  lookupTemplate(name: string): TemplateNode | undefined;
  getAllTemplates(): Map<string, TemplateNode>;
};
```

## Context Types

The Evaluator uses these context-related types:

```typescript
/**
 * Context management configuration
 */
type ContextManagementConfig = {
  inheritContext?: 'full' | 'none' | 'subset';
  accumulateData?: boolean;
  accumulationFormat?: 'notes_only' | 'full_output';
  freshContext?: 'enabled' | 'disabled';
};

/**
 * Context generation input
 */
type ContextGenerationInput = {
  description: string;
  inputs?: Record<string, any>;
  disableContext?: boolean;
};

/**
 * Context frame
 */
type ContextFrame = {
  id: string;
  content: string;
  metadata?: Record<string, any>;
};
```

## Function-Based Template Types

The Evaluator implements the function-based template pattern with these types:

```typescript
/**
 * Template definition
 */
type TemplateDefinition = {
  name: string;
  params: string[];
  body: ASTNode;
  returns?: string;
  metadata?: Record<string, any>;
};

/**
 * Template registry
 */
type TemplateRegistry = Map<string, TemplateDefinition>;

/**
 * Function call
 */
type FunctionCall = {
  templateName: string;
  args: any[];
};

/**
 * Function result
 */
type FunctionResult = {
  value: any;
  type?: string;
};
```

## Task Result Types

The Evaluator uses these task result types:

```typescript
/**
 * Task status
 */
type TaskStatus = 'COMPLETE' | 'FAILED' | 'CONTINUATION';

/**
 * Task result
 */
type TaskResult = {
  content: string;
  status: TaskStatus;
  notes: Record<string, any>;
};

/**
 * Subtask request
 */
type SubtaskRequest = {
  type: string;
  description: string;
  inputs: Record<string, any>;
  template_hints?: string[];
  context_management?: ContextManagementConfig;
  max_depth?: number;
  subtype?: string;
  file_paths?: string[];
};

/**
 * Evaluation request
 */
type EvaluationRequest = {
  type: string;
  criteria: string;
  target?: string;
};
```

## Error Types

The Evaluator uses these error types:

```typescript
/**
 * Base task error
 */
type TaskError = {
  type: 'TASK_FAILURE' | 'RESOURCE_EXHAUSTION';
  reason: string;
  message: string;
  details?: Record<string, any>;
};

/**
 * Template error
 */
type TemplateError = TaskError & {
  reason: 'template_resolution_failure';
  details: {
    template: string;
    missingVariable?: string;
    partialResult?: string;
  };
};

/**
 * Output format error
 */
type OutputFormatError = TaskError & {
  reason: 'output_format_failure';
  details: {
    expectedType: string;
    actualType: string;
    content: string;
  };
};

/**
 * Subtask error
 */
type SubtaskError = TaskError & {
  reason: 'subtask_failure';
  details: {
    subtaskRequest: {
      type: string;
      description: string;
      inputs: Record<string, any>;
    };
    subtaskError: TaskError;
    nestingDepth: number;
    partialOutput?: string;
  };
};
```

## Output Format Types

The Evaluator uses these output format types:

```typescript
/**
 * Output format configuration
 */
type OutputFormatConfig = {
  type: 'json' | 'text';
  schema?: string;
};

/**
 * Parsed JSON output
 */
type ParsedJsonOutput = {
  parsedContent: any;
  originalContent: string;
};
```
