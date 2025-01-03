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
    readonly atomicSubtype?: AtomicTaskSubtype;  // From [Type:TaskSystem:AtomicTaskSubtype:1.0]
}

/**
 * Core task execution interface
 * Uses [Type:TaskSystem:TaskType:1.0] defined in types.md
 * Uses [Type:TaskSystem:TaskError:1.0] defined in errors.md
 */
interface TaskSystem {
    // Execute a single task with the given context
    executeTask(
        task: string,
        context: MemorySystem,  // Now uses updated MemorySystem interface [Interface:Memory:2.0]
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

### Memory System Interface [Interface:Memory:2.0]
```typescript
/**
 * Memory management interface
 */
type GlobalIndex = Map<string, string>;

type FileMatch = [string, string | undefined];

interface MemorySystem {
    // Get current data context
    getContext(): Promise<string>;
    
    // Update data context
    updateContext(context: string): Promise<void>;

    // Get global file index
    getGlobalIndex(): Promise<GlobalIndex>;

    // Bulk update to global index
    updateGlobalIndex(index: GlobalIndex): Promise<void>;
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
 * Uses [Type:TaskSystem:ResourceMetrics:1.0], [Type:TaskSystem:ResourceLimits:1.0]
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

    /**
     * File access tools for LLM
     */
    tools: {
        readFile(path: string): Promise<string>;
    };
}
```