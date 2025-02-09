# Task System Types

// Core task types used across the Task System.
export type TaskType = "atomic" | "sequential" | "reduce" | "script";
export type AtomicTaskSubtype = "standard" | "subtask";

// Task execution status.
export type ReturnStatus = "COMPLETE" | "CONTINUATION" | "FAILED";

// Core interfaces:

export interface TaskResult {
    content: string;
    status: ReturnStatus;
    /**
     * Optional free-form description used for dynamic evaluation template selection.
     */
    criteria?: string;
    /**
     * Additional notes from task execution. May include extra metadata,
     * such as an optional success score (e.g., `successScore?: number`) for future adaptive template matching.
     */
    notes: {
        dataUsage: string;
        successScore?: number;
        [key: string]: any;
    };
}

/**
 * Represents a sequential task which has its own context management block
 * and multiple steps of subtasks.
 */
interface SequentialTask extends BaseTask {
    type: 'sequential';
    contextManagement: ContextManagement;
    steps: Task[];
}

/**
 * A general-purpose task result, now updated to store optional string notes
 * or structured data. This may override or augment the existing TaskResult
 * if needed, but is shown here as the revision plan states.
 */
interface RevisedTaskResult {
    content: string;
    notes: string;
}

/**
 * Defines context inheritance and accumulation policies for tasks.
 * The new model replaces a boolean inheritContext flag with an enumeration:
 *   - "full" for complete inheritance,
 *   - "none" for no inheritance, and
 *   - "subset" for selective inheritance.
 */
export interface ContextManagement {
    inheritContext: 'full' | 'none' | 'subset';
    accumulateData: boolean;
    accumulationFormat: 'full_output' | 'notes_only';
}

/**
 * Input structure for Memory System context requests
 */
interface ContextGenerationInput {
    previousOutputs?: string;   // Outputs accumulated from previous steps
    inheritedContext?: string;  // Context inherited from parent tasks
    taskText: string;          // The primary task description or request
}

/**
 * Note: Only atomic tasks have their own templates.
 * Composite tasks are constructed by combining multiple atomic task templates.
 */
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

export interface FunctionCall extends ASTNode {
    funcName: string;
    args: ASTNode[];
}
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

export interface EvaluationResult {
    success: boolean;
    feedback?: string;
}

export interface DirectorEnv extends Environment {
    last_evaluator_output: string | null;
    // Other variables are cleared on continuation
}

export interface Environment {
    bindings: Record<string, any>;
    outer?: Environment;
    /**
     * Perform a lexical lookup for varName.
     * Returns the value if found; otherwise, throws an error.
     */
    find(varName: string): any;
}

function prepareContinuationEnv(currentEnv: Environment): Environment {
    return new Environment({
        last_evaluator_output: currentEnv.get('last_evaluator_output')
    });
}

function storeEvaluatorResult(result: TaskResult, env: Environment): void {
    env.set('last_evaluator_output', result.content);
    env.clearExcept(['last_evaluator_output']);
}

## Resource Management Types

export interface TaskDefinition {
    name: string;                     // Unique task identifier
    isatomic: boolean;
    type: TaskType;                   // e.g., "atomic" or "sequential"
    subtype?: string;                 // Optional subtype, e.g., "director", "evaluator", etc.
    metadata?: Record<string, any>;   // Parameter schemas, return specs, etc.
    astNode: ASTNode;                 // Parsed AST for the task
}

export class TaskLibrary {
    private tasks: Map<string, TaskDefinition>;

    constructor() {
        this.tasks = new Map();
    }

    public registerTask(taskDef: TaskDefinition): void {
        if (this.tasks.has(taskDef.name)) {
            throw new Error(`Task ${taskDef.name} is already registered.`);
        }
        this.tasks.set(taskDef.name, taskDef);
    }

    public getTask(name: string): TaskDefinition {
        const taskDef = this.tasks.get(name);
        if (!taskDef) {
            throw new Error(`Task ${name} not found in TaskLibrary.`);
        }
        return taskDef;
    }
}
```typescript
interface HandlerConfig {
    maxTurns: number;
    maxContextWindowFraction: number;
    defaultModel?: string;
    systemPrompt: string;
}

/**
 * Represents the result of executing a script task.
 */
interface ScriptTaskResult extends TaskResult {
    stdout: string;
    stderr: string;
    exitCode: number;
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

/**
 * EvaluationInput interface clarifies that target_content refers to the original output from the Director task.
 * The raw outputs from the script (stdout, stderr, exit_code) are passed directly without preprocessing.
 */
interface EvaluationInput {
    target_content: string; // The original output from the Director task.
    stdout?: string;        // Raw standard output from the script.
    stderr?: string;        // Raw standard error output from the script.
    exit_code?: number;     // Script exit code (non-zero exit codes do not block evaluation but inform decision-making).
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
