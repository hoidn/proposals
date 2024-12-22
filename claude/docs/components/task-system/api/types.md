# Task System Types

## XML Schema Types
See [Contract:Tasks:TemplateSchema:1.0] for complete schema.

```typescript
// Task Template Types
interface TaskTemplate {
  readonly taskPrompt: string;     // Maps to <instructions> in schema
  readonly systemPrompt: string;   // Maps to <system> in schema
  readonly model: string;          // Maps to <model> in schema
  readonly inputs?: Record<string, string>;
  readonly isManualXML?: boolean;     // Maps to <manual_xml> in schema
  readonly disableReparsing?: boolean; // Maps to <disable_reparsing> in schema
}

// Operator Types
type OperatorType = "atomic" | "sequential" | "map" | "reduce";
type AtomicTaskSubtype = "standard" | "subtask";

interface OperatorSpec {
  type: OperatorType;
  subtype?: AtomicTaskSubtype;
  inputs: Record<string, string>;
  disableReparsing?: boolean;
}

// AST Types
interface ASTNode {
  type: string;
  content: string;
  children?: ASTNode[];
  metadata?: Record<string, any>;
  operatorType?: OperatorType;
}
```

## Memory System Types
```typescript
interface StorageMetadata {
  path: string;
  summary?: string;
  lastModified: Date;
  type?: string;
}

interface WorkingMetadata {
  path: string;
  summary?: string;
  loadedAt: Date;
  status: 'active' | 'stale';
}
```

## Resource Management Types
```typescript
interface HandlerConfig {
  maxTurns: number;
  maxContextWindowFraction: number;
  defaultModel?: string;
  systemPrompt: string;
}

interface ResourceMetrics {
  turns: {
    used: number;
    limit: number;
    lastTurnAt: Date;
  };
  context: {
    used: number;
    limit: number;
    peakUsage: number;
  };
}

interface ResourceLimits {
  maxTurns: number;
  maxContextWindow: number;
  warningThreshold: number;
  timeout?: number;
}
```

## Validation Types
```typescript
interface ValidationResult {
  valid: boolean;
  warnings: string[];
  errors?: string[];
  location?: string;
}

interface XMLValidation extends ValidationResult {
  xmlValid: boolean;
  schemaValid: boolean;
  parsedContent?: any;
}

interface TemplateValidation extends ValidationResult {
  templateValid: boolean;
  modelValid: boolean;
  inputsValid: boolean;
}
```