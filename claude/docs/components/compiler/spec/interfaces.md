# Compiler Interfaces Specification

## Purpose
This document specifies the internal interfaces used by the Compiler component, including the parser, validator, transformer, and error handling interfaces.

## Related Documents
- [Compiler README](../README.md)
- [Compiler API](../api/interfaces.md)
- [Compiler Types](./types.md)

## Internal Interfaces

The Compiler component uses several internal interfaces to organize its functionality:

### Core Interface

```typescript
/**
 * Core interface for the Compiler component
 */
interface ICompiler {
  /**
   * Parse natural language into an AST representation
   */
  parse(input: string): ASTNode;
  
  /**
   * Bootstrap a query into an AST representation
   */
  bootstrap(query: string): ASTNode;
  
  /**
   * Reparse a failed task with error information
   */
  reparse(failedTask: string, error: ExecutionError): ASTNode;
  
  /**
   * Translate a prompt to XML using LLM
   */
  llmTranslate(prompt: string): Element;
  
  /**
   * Parse an XML operator into an Operator object
   */
  parseOperator(xmlOperator: Element): Operator;
}
```

## Parser Interface

The Parser interface is responsible for parsing different input formats into AST representations:

```typescript
/**
 * Interface for parsing inputs into AST representations
 */
interface IParser {
  /**
   * Parse natural language into an AST representation
   */
  parseNaturalLanguage(input: string): ASTNode;
  
  /**
   * Parse XML into an AST representation
   */
  parseXML(xml: Element): ASTNode;
  
  /**
   * Parse a template definition
   */
  parseTemplate(template: Element): TemplateNode;
  
  /**
   * Parse a function call
   */
  parseFunctionCall(call: Element): FunctionCallNode;
  
  /**
   * Parse an argument
   */
  parseArgument(arg: Element): ArgumentNode;
}
```

## Validator Interface

The Validator interface is responsible for validating inputs against schemas and structural rules:

```typescript
/**
 * Interface for validating inputs
 */
interface IValidator {
  /**
   * Validate XML against the schema
   */
  validateXML(xml: Element): ValidationResult;
  
  /**
   * Validate AST structure
   */
  validateAST(ast: ASTNode): ValidationResult;
  
  /**
   * Validate a template definition
   */
  validateTemplate(template: TemplateNode): ValidationResult;
  
  /**
   * Validate a function call
   */
  validateFunctionCall(call: FunctionCallNode, templates: Record<string, TemplateNode>): ValidationResult;
  
  /**
   * Validate references in an AST
   */
  validateReferences(ast: ASTNode, env: Environment): ValidationResult;
}

/**
 * Result of validation
 */
interface ValidationResult {
  valid: boolean;
  errors?: ValidationError[];
  warnings?: ValidationWarning[];
}

/**
 * Validation error
 */
interface ValidationError {
  code: string;
  message: string;
  location?: Location;
  context?: any;
}

/**
 * Validation warning
 */
interface ValidationWarning {
  code: string;
  message: string;
  location?: Location;
  context?: any;
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

## Transformer Interface

The Transformer interface is responsible for transforming between different representations:

```typescript
/**
 * Interface for transforming between representations
 */
interface ITransformer {
  /**
   * Transform natural language to XML
   */
  naturalLanguageToXML(input: string): Element;
  
  /**
   * Transform XML to AST
   */
  xmlToAST(xml: Element): ASTNode;
  
  /**
   * Transform AST to XML
   */
  astToXML(ast: ASTNode): Element;
  
  /**
   * Transform a template to its AST representation
   */
  templateToAST(template: Element): TemplateNode;
  
  /**
   * Transform a function call to its AST representation
   */
  functionCallToAST(call: Element): FunctionCallNode;
}
```

## Error Handling Interface

The Error Handling interface is responsible for generating and managing errors:

```typescript
/**
 * Interface for error handling
 */
interface IErrorHandler {
  /**
   * Create a compiler error
   */
  createError(code: string, message: string, location?: Location, details?: any): CompilerError;
  
  /**
   * Create a validation error
   */
  createValidationError(code: string, message: string, location?: Location, context?: any): ValidationError;
  
  /**
   * Create a validation warning
   */
  createValidationWarning(code: string, message: string, location?: Location, context?: any): ValidationWarning;
  
  /**
   * Format an error for display
   */
  formatError(error: CompilerError | ValidationError | ValidationWarning): string;
  
  /**
   * Get suggestions for fixing an error
   */
  getSuggestions(error: CompilerError | ValidationError): string[];
}
```

## Template Registry Interface

The Template Registry interface is responsible for managing template definitions:

```typescript
/**
 * Interface for template registry
 */
interface ITemplateRegistry {
  /**
   * Register a template
   */
  registerTemplate(template: TemplateNode): void;
  
  /**
   * Get a template by name
   */
  getTemplate(name: string): TemplateNode | undefined;
  
  /**
   * Check if a template exists
   */
  hasTemplate(name: string): boolean;
  
  /**
   * Get all registered templates
   */
  getAllTemplates(): Record<string, TemplateNode>;
  
  /**
   * Clear all templates
   */
  clearTemplates(): void;
}
```

These internal interfaces provide a clear organization of the Compiler's functionality, with well-defined responsibilities and interactions between components.
