# Task System Interfaces

import { MemorySystem, FileMatch } from "../../memory/api/interfaces";

## References

- Core Types: See [Type:TaskSystem:1.0] (`/components/task-system/spec/types.md`)
- XML Schema: See [Contract:Tasks:TemplateSchema:1.0] (`/system/contracts/protocols.md`)

## Public Interfaces

### TaskSystem Interface
```typescript
/**
 * Core task execution interface
 * Uses types defined in [Type:TaskSystem:1.0]:
 * - TaskResult
 * - TaskTemplate
 * - TaskType
 * - AtomicTaskSubtype
 */
interface TaskSystem {
    executeTask(
        task: string,
        memory: MemorySystem,
        taskType?: TaskType // Supports "atomic", "sequential", "reduce", and "script" tasks.
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
        taskType: TaskType;    // Now limited to atomic, sequence, reduce
    }>>;
    
    /**
     * Parse and validate task output against declared format
     * @param output - Raw task output
     * @param format - Optional output format specification
     * @returns Parsed output or the original if parsing fails
     */
    parseTaskOutput(output: string, format?: {
        type: "json" | "text";
        schema?: string;
    }): { isParsed: boolean; value: any };
}
```

### Memory System Interface [Interface:Memory:3.0]
```typescript
/**
 * Memory System Interface [Interface:Memory:3.0]
 * Focused on metadata management and context retrieval
 */
interface MemorySystem {
    /**
     * Get global file metadata index
     * @returns Promise resolving to the global index
     */
    getGlobalIndex(): Promise<GlobalIndex>;
    
    /**
     * Update global file metadata index
     * @param index New index to set
     * @returns Promise resolving when update is complete
     */
    updateGlobalIndex(index: GlobalIndex): Promise<void>;
    
    /**
     * Get relevant context for a task
     * @param input Context generation input
     * @returns Promise resolving to associative match result
     */
    getRelevantContextFor(input: ContextGenerationInput): Promise<AssociativeMatchResult>;
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
}
```
