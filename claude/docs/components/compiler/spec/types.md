# Compiler Types Specification

## Purpose
This document specifies the types used by the Compiler component, including AST node types, validation result types, and error types.

## Related Documents
- [Compiler README](../README.md)
- [Compiler Interfaces](./interfaces.md)
- [ADR 12: Function-Based Template Model](../../../system/architecture/decisions/completed/012-function-based-templates.md)

## AST Structure

The Abstract Syntax Tree (AST) is a structured representation of tasks that can be processed by the Evaluator. The AST consists of nodes with specific types and properties.

### Basic Node Types

```typescript
/**
 * Base AST node interface
 */
interface ASTNode {
  type: string;
  location?: Location;
}

/**
 * Location in source
 */
interface Location {
  line: number;
  column: number;
  source: string;
}
```

### Task-Specific Node Types

```typescript
/**
 * Task node interface
 */
interface TaskNode extends ASTNode {
  type: 'task';
  taskType: 'atomic' | 'sequential' | 'parallel' | 'conditional' | 'iterative';
  description: string;
  contextManagement?: ContextManagement;
  inputs?: Record<string, any>;
  expectedOutput?: string;
  steps?: TaskNode[];
  condition?: ConditionNode;
  iterations?: number | IterationNode;
  filePaths?: string[];
}

/**
 * Context management configuration
 */
interface ContextManagement {
  inheritContext: 'full' | 'none' | 'subset';
  accumulateData: boolean;
  accumulationFormat: 'notes_only' | 'full_output';
  freshContext: 'enabled' | 'disabled';
}

/**
 * Condition node interface
 */
interface ConditionNode extends ASTNode {
  type: 'condition';
  expression: string;
}

/**
 * Iteration node interface
 */
interface IterationNode extends ASTNode {
  type: 'iteration';
  expression: string;
}
```

### Operator Node Types

```typescript
/**
 * Operator node interface
 */
interface OperatorNode extends ASTNode {
  type: 'operator';
  operatorType: OperatorType;
  arguments: ArgumentNode[];
}

/**
 * Operator type enum
 */
enum OperatorType {
  SEQUENTIAL = 'sequential',
  PARALLEL = 'parallel',
  CONDITIONAL = 'conditional',
  ITERATIVE = 'iterative',
  MAP = 'map',
  REDUCE = 'reduce',
  FILTER = 'filter',
  DIRECTOR_EVALUATOR = 'director_evaluator',
  // Add other operator types as needed
}

/**
 * Argument node interface
 */
interface ArgumentNode extends ASTNode {
  type: 'argument';
  value: string | ASTNode;
}
```

### Template-Related Node Types

```typescript
/**
 * Template node interface
 */
interface TemplateNode extends ASTNode {
  type: 'template';
  name: string;
  parameters: string[];
  body: TaskNode;
  returns?: string;
}

/**
 * Function call node interface
 */
interface FunctionCallNode extends ASTNode {
  type: 'function_call';
  templateName: string;
  arguments: ArgumentNode[];
}
```

## Node Type Definitions

### TemplateNode
The TemplateNode represents a function template definition:
- **name**: Unique template identifier
- **parameters**: Array of parameter names
- **body**: TaskNode for implementation
- **returns**: Optional type information

### FunctionCallNode
The FunctionCallNode represents a function call:
- **templateName**: Reference to registered template
- **arguments**: Array of ArgumentNodes

### ArgumentNode
The ArgumentNode represents a function argument:
- **value**: String (variable/literal) or nested AST node

## Validation Result Types

```typescript
/**
 * Validation result interface
 */
interface ValidationResult {
  valid: boolean;
  errors?: ValidationError[];
  warnings?: ValidationWarning[];
}

/**
 * Validation error interface
 */
interface ValidationError {
  code: string;
  message: string;
  location?: Location;
  context?: any;
}

/**
 * Validation warning interface
 */
interface ValidationWarning {
  code: string;
  message: string;
  location?: Location;
  context?: any;
}
```

## Error Types

```typescript
/**
 * Base compiler error interface
 */
interface CompilerError extends Error {
  code: string;
  location?: Location;
  details?: any;
}

/**
 * Syntax error interface
 */
interface SyntaxError extends CompilerError {
  code: 'SYNTAX_ERROR';
  expectedTokens?: string[];
  actualToken?: string;
}

/**
 * Reference error interface
 */
interface ReferenceError extends CompilerError {
  code: 'REFERENCE_ERROR';
  referenceName: string;
  referenceType: 'template' | 'variable' | 'function';
}

/**
 * Type error interface
 */
interface TypeError extends CompilerError {
  code: 'TYPE_ERROR';
  expectedType: string;
  actualType: string;
}

/**
 * Validation error interface
 */
interface ValidationError extends CompilerError {
  code: 'VALIDATION_ERROR';
  validationErrors: ValidationError[];
}

/**
 * Template error interface
 */
interface TemplateError extends CompilerError {
  code: 'TEMPLATE_ERROR';
  templateName: string;
}

/**
 * Function call error interface
 */
interface FunctionCallError extends CompilerError {
  code: 'FUNCTION_CALL_ERROR';
  templateName: string;
  argumentErrors?: Record<number, string>;
}
```

## Tree Traversal Requirements

The AST is designed to support specific traversal requirements:

- **Templates are registered, not traversed directly**: Templates are registered in a central registry and referenced by name during function calls.
- **Function calls trigger template lookup and execution**: When a function call node is encountered, the template is looked up in the registry and executed with the provided arguments.
- **Arguments are evaluated in caller's environment**: Function arguments are evaluated in the caller's environment before being passed to the function.

These requirements ensure proper scoping and execution semantics for the function-based template model.
