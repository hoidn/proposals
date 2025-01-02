# Task System Types

## Core Task Types
```typescript
// Basic task types used across interfaces
type TaskType = "atomic" | "sequential" | "map" | "reduce";
type AtomicTaskSubtype = "standard" | "subtask";

// Results and Templates
interface TaskResult {
    content: string;
    notes: {
        dataUsage: string;
    };
}

interface TaskTemplate {
    readonly taskPrompt: string;      // Maps to <instructions> in schema
    readonly systemPrompt: string;    // Maps to <system> in schema
    readonly model: string;           // Maps to <model> in schema
    readonly inputs?: Record<string, string>;
    readonly isManualXML?: boolean;   // Maps to <manual_xml> in schema
    readonly disableReparsing?: boolean; // Maps to <disable_reparsing> in schema
    readonly atomicSubtype?: AtomicTaskSubtype;
}
```

## AST Types
```typescript
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

## Memory System Types
```typescript
// Storage types for memory system
interface StorageFile {
    content: string;
    metadata: StorageMetadata;  // See Memory System documentation
}

interface WorkingFile {
    content: string;
    metadata: WorkingMetadata;  // See Memory System documentation
    sourceLocation: string;
}

interface MemorySystem {
    // Long term storage
    longTermStorage: {
        files: Map<string, StorageFile>;
        text: string;
    };
    
    // Short term working memory
    shortTermMemory: {
        files: Map<string, WorkingFile>;
        dataContext: string;
    };
}
```

## Error Types
```typescript
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

interface TemplateValidation extends ValidationResult {
    templateValid: boolean;
    modelValid: boolean;
    inputsValid: boolean;
}
```

## Cross-References
- For XML schema definitions, see [Contract:Tasks:TemplateSchema:1.0] in protocols.md
- For interface implementations, see spec/interfaces.md
- For public API surface, see api/interfaces.md

## Notes
1. All types supporting the core task system are defined here
2. Public API types are a subset of these definitions
3. Implementation details for memory system metadata types pending definition
4. All resource limits and metrics are enforced per-Handler
