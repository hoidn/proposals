# Compiler API Interfaces

## Purpose
This document defines the public interfaces and integration points for the Compiler component, which is responsible for translating natural language or user input into structured AST or XML representations.

## Related Documents
- [Compiler README](../README.md)
- [Contract:Integration:CompilerTask:1.0](../../../system/contracts/interfaces.md)
- [Compiler Types](../spec/types.md)

## Contract Integration
The Compiler component implements the `CompilerTask` contract defined in the system contracts. This contract specifies how the Compiler interacts with other components in the system.

## Public API

```typescript
/**
 * Main interface for the Compiler component
 */
interface Compiler {
  /**
   * Parse natural language into an AST representation
   * @param input Natural language input to parse
   * @returns AST node representing the parsed task
   * @throws CompilerError if parsing fails
   */
  parse(input: string): ASTNode;
  
  /**
   * Bootstrap a query into an AST representation
   * @param query Query to bootstrap
   * @returns AST node representing the bootstrapped task
   * @throws CompilerError if bootstrapping fails
   */
  bootstrap(query: string): ASTNode;
  
  /**
   * Reparse a failed task with error information
   * @param failedTask The task that failed
   * @param error Error information from the failed execution
   * @returns AST node representing the reparsed task
   * @throws CompilerError if reparsing fails
   */
  reparse(failedTask: string, error: ExecutionError): ASTNode;
  
  /**
   * Translate a prompt to XML using LLM
   * @param prompt Prompt to translate
   * @returns XML Element representing the translated prompt
   * @throws CompilerError if translation fails
   */
  llmTranslate(prompt: string): Element;
  
  /**
   * Parse an XML operator into an Operator object
   * @param xmlOperator XML representation of an operator
   * @returns Operator object
   * @throws CompilerError if parsing fails
   */
  parseOperator(xmlOperator: Element): Operator;
  
  /**
   * Register a template for function-based calls
   * @param template Template definition
   * @throws CompilerError if template registration fails
   */
  registerTemplate(template: TemplateDefinition): void;
  
  /**
   * Validate a template against the schema
   * @param template Template to validate
   * @throws ValidationError if template is invalid
   */
  validateTemplate(template: TemplateDefinition): void;
}

/**
 * Input for compilation requests
 */
interface CompilationInput {
  query: string;
  templateContext?: Record<string, TemplateDefinition>;
  options?: CompilationOptions;
}

/**
 * Options for compilation
 */
interface CompilationOptions {
  maxDepth?: number;
  allowReparse?: boolean;
  validateOnly?: boolean;
  targetFormat?: 'xml' | 'ast';
}

/**
 * Result of compilation
 */
interface CompilationResult {
  ast?: ASTNode;
  xml?: Element;
  templates?: Record<string, TemplateDefinition>;
  errors?: CompilerError[];
  warnings?: string[];
}

/**
 * Error from compilation
 */
interface CompilerError extends Error {
  code: string;
  location?: {
    line: number;
    column: number;
    source: string;
  };
  details?: any;
}
```

## Evaluator Integration
The Compiler interfaces with the Evaluator component for reparsing and decomposition:

1. When the Evaluator encounters an error during execution, it may request a reparse through the `reparse` method.
2. The Compiler receives the failed task and error information and attempts to generate a new AST that addresses the error.
3. The new AST is returned to the Evaluator for continued execution.

This integration enables robust error recovery and dynamic task decomposition based on runtime discoveries.

## TaskSystem Integration
The Compiler interfaces with the TaskSystem component for task parsing and template validation:

1. The TaskSystem provides template context to the Compiler for validation and registration.
2. The Compiler validates templates against the schema defined in [Contract:Tasks:TemplateSchema:1.0].
3. The TaskSystem uses the Compiler to parse natural language queries into executable AST representations.

This integration ensures that tasks are properly structured and templates are correctly defined before execution.

## Integration Points
The Compiler component integrates with other components through the following interfaces:

- **Task System**: For template registration and validation
- **Evaluator**: For AST execution and reparse requests
- **Memory System**: For context retrieval during compilation (indirect through TaskSystem)

Each integration point follows the contracts defined in the system architecture to ensure consistent behavior and clear component boundaries.
