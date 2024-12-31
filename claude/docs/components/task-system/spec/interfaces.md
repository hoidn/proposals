# Task System Interfaces

## Public Interfaces

### TaskSystem Interface
```typescript
/**
 * Types specific to TaskSystem interface
 */
interface TaskResult {
    content: string;
    notes: {
        dataUsage: string;
    };
}

interface TaskTemplate { 
    readonly taskPrompt: string;     // Maps to <instructions> in schema
    readonly systemPrompt: string;   // Maps to <s> in schema
    readonly model: string;          // Maps to <model> in schema
    readonly inputs?: Record<string, string>;
    readonly isManualXML?: boolean;     // Maps to <manual_xml> in schema
    readonly disableReparsing?: boolean; // Maps to <disable_reparsing> in schema
    readonly atomicSubtype?: AtomicTaskSubtype;  // From types.md
}

/**
 * Core task execution interface
 * Uses TaskType, TaskError from types.md
 */
interface TaskSystem {
    // Execute a single task with the given context
    executeTask(
        task: string,
        context: MemorySystem,
        taskType?: TaskType
    ): Promise<TaskResult>;

    // Validate a task template
    validateTemplate(template: TaskTemplate): boolean;
    
    // Find matching task templates for input
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

### Memory System Interface
```typescript
/**
 * Types specific to Memory interface
 */
interface StorageFile {
    content: string;
    metadata: StorageMetadata;  // TODO: Define this type
}

interface WorkingFile {
    content: string;
    metadata: WorkingMetadata;  // TODO: Define this type
    sourceLocation: string;
}

/**
 * Memory management interface
 * Handles persistent and temporary storage
 */
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

### Handler Interface
```typescript
/**
 * Types specific to Handler interface
 */
interface HandlerConfig {
    maxTurns: number;
    maxContextWindowFraction: number;
    defaultModel?: string;
    systemPrompt: string;
}

/**
 * LLM interaction interface
 * Uses ResourceMetrics, ResourceLimits from types.md
 */
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
