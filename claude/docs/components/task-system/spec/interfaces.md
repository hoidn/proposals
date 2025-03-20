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
    
    /**
     * findMatchingTasks
     *
     * Finds matching templates based on a provided input string.
     *
     * Note: Matching applies *only* to atomic task templates. The function evaluates the input
     * against atomic task templates using a heuristic scoring mechanism.
     * 
     * @param input - The natural language task description.
     * @param context - The MemorySystem instance providing context data.
     * @returns An array of matching candidates with their associated scores.
     */
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
    
    /**
     * Register a template in the TaskLibrary
     * 
     * @param template - The template to register
     * @returns Promise resolving to registration result
     */
    registerTemplate(template: TemplateNode): Promise<void>;
    
    /**
     * Execute a function call
     * 
     * @param call - The function call to execute
     * @param env - The environment for argument evaluation
     * @returns Promise resolving to the function result
     */
    executeCall(call: FunctionCallNode, env: Environment): Promise<TaskResult>;
export interface Environment {
    bindings: Record<string, any>;
    outer?: Environment;
    /**
     * Perform a lexical lookup for varName.
     * Returns the value if found; otherwise, throws an error.
     */
    find(varName: string): any;
    executeScriptTask(scriptTask: ScriptTask, env: Environment): Promise<ScriptTaskResult>;
    
    /**
     * Create a new child environment with additional bindings
     * 
     * @param bindings - New variable bindings to add
     * @returns A new Environment with the added bindings
     */
    extend(bindings: Record<string, any>): Environment;
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

### Example Definitions

**ContextGenerationInput Example:**
```json
{
    "taskText": "Analyze experimental data",
    "inheritedContext": "Optional inherited context from previous tasks (if not disabled)",
    "previousOutputs": "Optional string summarizing prior outputs"
}
```

**AssociativeMatchResult Example:**
```json
{
    "context": "Relevant retrieved context information",
    "matches": [
        ["fileA.txt", "metadata details"],
        ["fileB.txt", null]
    ]
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
     * Register a direct tool that will be executed by the Handler
     * @param name - Unique tool name
     * @param handler - Function that implements the tool
     */
    registerDirectTool(name: string, handler: Function): void;

    /**
     * Register a subtask tool that will be implemented via CONTINUATION
     * @param name - Unique tool name
     * @param templateHints - Hints for template selection
     */
    registerSubtaskTool(name: string, templateHints: string[]): void;

    /**
     * Callback for handling agent input requests
     * @param agentRequest - The agent's request for user input
     * @returns Promise resolving to user's input
     */
    onRequestInput: (agentRequest: string) => Promise<string>;
}
```
