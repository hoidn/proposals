# Task System Types

## Core Types
```typescript
// Basic task types used across interfaces
// Used by: TaskSystem, Handler, AST processing
type TaskType = "atomic" | "sequential" | "map" | "reduce";
type AtomicTaskSubtype = "standard" | "subtask";
```

## AST Types
```typescript
// Internal representation types
// Used by: Compiler component, Task parsing
interface OperatorSpec {
    type: TaskType;
    subtype?: AtomicTaskSubtype;
    inputs: Record<string, string>;
    disableReparsing?: boolean;
}

interface ASTNode {
    type: string;
    content: string;
    children?: ASTNode[];
    metadata?: Record<string, any>;
    operatorType?: TaskType;
}
```

## Resource Types
```typescript
// System-wide resource tracking
// Used by: Handler, TaskSystem, resource monitoring
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

## Error Types
```typescript
// System-wide error representation
// Used by: All components
type TaskError = 
    | { 
        type: 'RESOURCE_EXHAUSTION';
        resource: 'turns' | 'context' | 'output';
        message: string;
        metrics?: { used: number; limit: number; };
    }
    | { 
        type: 'INVALID_OUTPUT';
        message: string;
        violations?: string[];
    }
    | { 
        type: 'VALIDATION_ERROR';
        message: string;
        path?: string;
        invalidModel?: boolean;
    }
    | { 
        type: 'XML_PARSE_ERROR';
        message: string;
        location?: string;
    };
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
```
