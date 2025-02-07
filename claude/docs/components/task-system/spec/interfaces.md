# Task System Interfaces

// For core type definitions (e.g. TaskResult, TaskTemplate, TaskType, AtomicTaskSubtype),
// please refer to components/task-system/spec/types.md.

import { MemorySystem } from "../../memory/api/interfaces";

/**
 * TaskSystem Interface
 * 
 * Provides methods to execute tasks, validate templates, and find matching templates.
 */
export interface TaskSystem {
    executeTask(
        task: string,
        memory: MemorySystem,
        taskType?: "atomic" | "sequential" | "reduce" | "script"
    ): Promise<TaskResult>;

    validateTemplate(template: TaskTemplate): boolean;
    
    findMatchingTasks(
        input: string,
        context: MemorySystem
    ): Promise<Array<{
        template: TaskTemplate;
        score: number;
        taskType: "atomic" | "sequential" | "reduce" | "script";
    }>>;
    registerTask(taskDef: TaskDefinition): void;
    executeFunctionCall(funcCall: FunctionCall, env: Environment): Promise<any>;
export interface Environment {
    bindings: Record<string, any>;
    outer?: Environment;
    /**
     * Perform a lexical lookup for varName.
     * Returns the value if found; otherwise, throws an error.
     */
    find(varName: string): any;
    executeScriptTask(scriptTask: ScriptTask, env: Environment): Promise<ScriptTaskResult>;
}

// Handler interface details are maintained in external documentation.
 * Memory management interface focused on metadata
 */
type FileMetadata = string;

type GlobalIndex = Map<string, FileMetadata>;

type FileMatch = [string, string | undefined];

interface AssociativeMatchResult {
    context: string;      // Unstructured data context
    matches: FileMatch[]; // Relevant file matches
}

interface MemorySystem {
    // Get global file metadata index
    getGlobalIndex(): Promise<GlobalIndex>;
    
    // Update global file metadata index
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
}
```
