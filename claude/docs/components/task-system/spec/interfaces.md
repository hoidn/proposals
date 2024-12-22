# Task System Interfaces

## Types

### Task Results
```typescript
interface TaskResult {
    content: string;
    notes: {
        dataUsage: string;
    };
}
```

### Task Types
```typescript
type TaskType = "atomic" | "sequential" | "map" | "reduce";
type AtomicTaskSubtype = "standard" | "subtask";

// Core types with documentation
interface TaskTemplate {
    readonly taskPrompt: string;     // Maps to <instructions> in schema
    readonly systemPrompt: string;   // Maps to <system> in schema
    readonly model: string;          // Maps to <model> in schema
    readonly inputs?: Record<string, string>;
    readonly isManualXML?: boolean;     // Maps to <manual_xml> in schema
    readonly disableReparsing?: boolean; // Maps to <disable_reparsing> in schema
    readonly atomicSubtype?: AtomicTaskSubtype;  // Only for atomic tasks
}
```

### Error Types
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

### Memory System Types
```typescript
interface StorageFile {
    content: string;
    metadata: StorageMetadata;
}

interface WorkingFile {
    content: string;
    metadata: WorkingMetadata;
    sourceLocation: string;
}

interface MemorySystem {
    longTermStorage: {
        files: Map<string, StorageFile>;
        text: string;
    };
    shortTermMemory: {
        files: Map<string, WorkingFile>;
        dataContext: string;
    };
}
```

## Public Interfaces

### TaskSystem
```typescript
interface TaskSystem {
    // Task Execution
    executeTask(
        task: string,
        context: MemorySystem,
        taskType?: TaskType
    ): Promise<TaskResult>;

    // Template Management
    validateTemplate(template: TaskTemplate): boolean;
    
    // Task Matching
    findMatchingTasks(
        input: string,
        context: MemorySystem
    ): Promise<Array<{
        template: TaskTemplate;
        score: number;
        taskType: TaskType;
    }>>;
}
```

### Handler
```typescript
interface Handler {
    /**
     * Execute a prompt with the LLM
     * @param systemPrompt - System-level context and instructions
     * @param taskPrompt - Task-specific input
     * @returns Promise resolving to LLM response
     */
    executePrompt(
        systemPrompt: string,
        taskPrompt: string
    ): Promise<string>;

    /**
     * Callback for handling agent input requests
     * @param agentRequest - The agent's request for user input
     * @returns Promise resolving to user's input
     */
    onRequestInput: (agentRequest: string) => Promise<string>;
}
```
