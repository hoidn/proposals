# Evaluator Component

## Overview

The **Evaluator** is the unified task-execution component of the system. It is responsible for:

1. **Controlling AST processing and execution**  
2. **Managing failure recovery** via standard task return statuses (`COMPLETE`, `CONTINUATION`, `FAILED`)
3. **Tracking resource usage** (in coordination with Handlers)
4. **Handling reparse/decomposition requests** when tasks fail (e.g. due to resource exhaustion or invalid output)

### References in Existing Documentation

- **System-Level References**  
  - *System README (`system/README.md`)* and *Architecture Overview (`system/architecture/overview.md`)* list the Evaluator as a core component, describing it as the manager for AST execution, resource tracking, and reparse/error handling.  
  - *Contracts & Interfaces (`system/contracts/interfaces.md`)* references "[Contract:Integration:EvaluatorTask:1.0]," tying the Evaluator to tasks and describing the need for an integration interface (though that interface is not yet fully elaborated).  
  - The *"Metacircular Evaluator"* concept is mentioned in `misc/textonly.tex.md`, demonstrating an evaluator that calls LLM operations as part of `apply-proc` and `eval-task`. This underscores that the Evaluator runs tasks by leveraging LLM-based primitives (for decomposition, atomic calls, or re-checking).  

- **Error Handling**  
  - The Evaluator is mentioned repeatedly (e.g., `misc/errorspec.md`, `system/architecture/patterns/errors.md`) as the component receiving error signals from tasks or sub-operations. It manages or coordinates the "control flow" when resource exhaustion or invalid outputs appear.  
  - Errors of type `RESOURCE_EXHAUSTION` or `TASK_FAILURE` can cause the Evaluator to request "reparse" or "decomposition."  

- **Implementation Plan**  
  - *Phase 2: Expanded Context Management* mentions extending environment usage so that sub-tasks may inherit or manage context. The Evaluator is implicitly involved in ensuring tasks have the right environment or partial results.  
  - *Phase 3: Task Execution Enhancements* explicitly names the Evaluator as a place to add "summary output or additional logging" for advanced debugging. The same phase also suggests new flags like `rebuild_memory` or `clear_memory` that the Evaluator would honor when building or discarding context.  

In many existing code examples (both TypeScript-like and Scheme-like), the system calls an `eval` or `apply` function that effectively belongs to the Evaluator domain. When direct execution fails, a decomposition or reparse step is triggered, also under the Evaluator's responsibility.

## 3.1 Nested Environment Model Integration

The Environment class supports nested scopes via an "outer" reference. The Evaluator creates a global environment (globalEnv) that includes built-in variables along with an instance of TaskLibrary (e.g., globalEnv.bindings["taskLibrary"] = taskLibrary). A new child environment is created for each task or function call.

```typescript
// Example Environment implementation
class Env implements Environment {
    constructor(public bindings: Record<string, any> = {}, public outer?: Environment) {}
    find(varName: string): any {
        return (varName in this.bindings)
            ? this.bindings[varName]
            : this.outer ? this.outer.find(varName) : throw new Error(`Variable ${varName} not found`);
    }
}
```

## Responsibilities and Role

1. **AST Execution Controller**  
   - Orchestrates the step-by-step or operator-by-operator execution of tasks represented as an AST.
   - Calls out to the Handler for LLM-specific interactions and resource tracking (e.g. turn counts, context window checks).
   - Interacts with the Compiler when re-parsing or decomposition is required.

2. **Failure Recovery**  
   - Detects or receives error signals when tasks fail or exceed resources.  
   - Initiates "reparse" tasks or alternative decomposition approaches if the system's policies allow.  
   - Surfaces errors back to the Task System or parent contexts (e.g., "resource exhaustion," "invalid output").  

3. **Resource Usage Coordination**  
   - Not purely "owns" resource tracking (that's part of the Handler), but integrates with it. The Evaluator is aware of usage or limit errors and decides whether to attempt decomposition or fail outright.  

4. **Context and Environment Handling**  
   - In multi-step or operator-based tasks (sequential, reduce, etc.), the Evaluator ensures the proper propagation of the environment and partial context. Every new task or function call execution uses a child environment (based on the parent environment or the global environment, depending on the XML attribute `inherit_context`), thereby ensuring that the TaskLibrary and any built-in variables remain accessible through the environment chain.
   - The Evaluator leverages the Memory System for associative context retrieval but does not manage file content directly.  

5. **Integration with Task System**  
   - The Task System may call the Evaluator with a structured or partially structured task. The Evaluator then "executes" it by walking its representation (e.g., an AST or an XML-based operator chain).  
   - On error or partial success, the Evaluator can signal the Task System to orchestrate higher-level recovery or store partial results.  

## 3.3 FunctionCall AST Node for DSL Function Calling

The FunctionCall node is used to invoke a task functionally by looking up its definition in the TaskLibrary. When a FunctionCall is evaluated, the Evaluator:
- Uses env.find("taskLibrary") to retrieve the registry;
- Looks up the task by its funcName;
- Creates a child environment (e.g., new Env({}, env));
- Binds the parameters from task_def.metadata to the evaluated arguments;
- And finally calls taskDef.astNode.eval(newEnv) to get the result.

```typescript
// Example FunctionCall evaluation
class FunctionCallNode implements FunctionCall {
    constructor(public funcName: string, public args: ASTNode[]) {}
    async eval(env: Environment): Promise<any> {
        const taskLibrary = env.find("taskLibrary")["taskLibrary"];
        const taskDef = taskLibrary.getTask(this.funcName);
        const funcEnv = new Env({}, env);
        const parameters: string[] = taskDef.metadata?.parameters || [];
        for (let i = 0; i < parameters.length && i < this.args.length; i++) {
            funcEnv.bindings[parameters[i]] = await this.args[i].eval(env);
        }
        return await taskDef.astNode.eval(funcEnv);
    }
}
```

## Metacircular Approach

Documentation (especially in `misc/textonly.tex.md`) sometimes refers to the system's evaluator as a "metacircular evaluator," meaning:
> The interpreter (Evaluator) uses LLM-based operations as its basic building blocks, while the LLM also uses the DSL or AST from the evaluator for self-decomposition tasks.

In practice, this means:  
- The Evaluator calls an LLM to run "atomic" tasks or to do "decomposition."  
- The LLM might generate or refine structured XML tasks that, in turn, the Evaluator must interpret again.  
- This cycle repeats until the tasks can be successfully executed without exceeding resource or output constraints.

Because of this, the Evaluator is partially "self-hosting": it leverages the same LLM to break down tasks that can't be executed directly.  

---

## Potential Future Enhancements

The existing plan outlines several optional or future features that involve the Evaluator:

1. **Advanced Debug Logging** (Phase 3 in the Implementation Plan)  
   - Collecting or storing extensive logs in `notes.debugLogs` or similar.  
   - Exposing partial steps or re-try decisions for advanced debugging.  

2. **`rebuild_memory` or `clear_memory` Flags**  
   - When tasks specify these, the Evaluator would create or discard certain environment data at the start of a sub-task.  
   - This is relevant for tasks that explicitly want a fresh context (e.g., ignoring prior steps' context).  

3. **Multi-Step or "Continuation" Protocol**  
   - The Evaluator might support tasks that require multiple interactions or "continuation steps" without losing context.  
   - This could involve storing partial states or sub-results in the environment and continuing in a new iteration.  

4. **Agent Features** (Phase 4 in some documents)  
   - The Evaluator could handle conversation-like tasks with a "REPL" approach, or coordinate multiple LLM backends.  
   - This is out of scope for the MVP, but recognized as an extension point.

---

## Known Open Questions

1. **Partial Results**  
   - Some references (e.g., "Phase 2: Expanded Context Management") mention partial-result handling if sub-tasks fail mid-operator. It is not yet finalized how the Evaluator will pass partial data up or whether to discard it.  

2. **Context Generation Errors**  
   - The error taxonomy may or may not include a dedicated "CONTEXT_GENERATION_FAILURE." Currently, the Evaluator might treat it as a generic `TASK_FAILURE` or trigger reparse.  

3. **Inheritance on Map/Reduce**  
   - It is hinted that "inherit_context" might become relevant for parallel or reduce operators. The Evaluator's role in distributing or discarding environment data for sub-tasks is still being discussed.

---

## Summary

The Evaluator coordinates the execution of tasks—represented in AST or XML-based form—by calling LLM operations, handling resource usage signals, managing sub-task context, and recovering from errors. It serves as the system's "control loop" for deciding whether tasks can be executed directly or require alternative approaches (like decomposition).  

*For further details:*  
- **System-Level Descriptions:** See `system/architecture/overview.md`  
- **Error Patterns & Recovery:** See `system/architecture/patterns/errors.md`, `misc/errorspec.md`  
- **Metacircular Evaluator Examples:** See the "Evaluator" sketches in `misc/textonly.tex.md`  
- **Future Expansions:** Refer to Implementation Plan phases in `implementation.md` (root-level or system docs).

## Dual Context Tracking

The Evaluator maintains two distinct types of context when both inheritance and accumulation are enabled:

1. **Inherited Context**: The parent task's context that is passed down unchanged
2. **Accumulated Data**: The step-by-step outputs collected during sequential execution

When both `inheritContext` and `accumulateData` are true, these contexts remain separate internally but can be combined during task execution. The Evaluator:

1. Maintains the parent's inherited context unchanged throughout execution
2. Separately tracks accumulated outputs from previous steps
3. Calls `getRelevantContextFor()` with both contexts when needed:
   ```typescript
   const contextInput: ContextGenerationInput = {
       previousOutputs: accumulatedData,    // From sequential history
       inheritedContext: parentContext,     // From parent task
       taskText: currentTaskDescription     // Current step
   };
   const matchResult = await getRelevantContextFor(contextInput);
   ```
4. Uses the returned context and matches during prompt generation

## Associative Matching Invocation

When executing a sequential task step with `<inherit_context>false</inherit_context>` **but** `<accumulate_data>true</accumulate_data>`, the Evaluator:
1. Calls `MemorySystem.getRelevantContextFor()` with prior steps' partial results
2. Merges the returned `AssociativeMatchResult` into the next step's environment
3. Maintains complete separation from the Handler's resource management

### Evaluator Responsibilities for Associative Matching

* **Initiation**: The Evaluator is the *sole* caller of `MemorySystem.getRelevantContextFor()`.
* **Sequential History**: It retrieves partial outputs from `SequentialHistory` (the step-by-step data structure it maintains).
* **Context Merging**: If the step is configured for accumulation, the Evaluator incorporates the match results into the upcoming step's environment.
* **Error Handling**: Any failure to retrieve context (e.g., a memory system error) is handled through the existing `TASK_FAILURE` or resource-related error flow. No new error category is introduced.
* **No Handler Involvement**: The Handler does not participate in the retrieval or assembly of this context data, beyond tracking resource usage at a high level.

This design ensures that only the Evaluator initiates associative matching, preventing confusion about which component is responsible for cross-step data retrieval. The Memory System remains a service that simply provides matches upon request.

---

---

## Sequential Task History

When evaluating a **sequential** task (type="sequential"), the Evaluator maintains a **step-by-step output history**:

### Output Tracking
1. **History per sequence**: Each sequential task run has a dedicated list (or array) of step outputs.
2. **Preservation**: All step outputs remain available until the task completes (success or error).
3. **Failure case**: If a step fails, the partial results from prior steps are included in the final error notes.
4. **Resource awareness**: The evaluator must keep track of the size of stored outputs, possibly truncating or summarizing them to prevent memory or token overflow.

### History Structure (example)
```typescript
interface SequentialHistory {
    outputs: TaskOutput[];
    metadata: {
        startTime: Date;
        currentStep: number;
        resourceUsage: ResourceMetrics;
    };
}

interface TaskOutput {
    stepId: string;       // or step index
    output: string;       // The main content from that step
    notes: string;        // Additional or partial notes
    timestamp: Date;
}
```

### Lifecycle Management
1. **Creation**: On the first step of a sequential task, the Evaluator initializes a new `SequentialHistory`.
2. **Updates**: After each step completes, the Evaluator appends a `TaskOutput` object to `SequentialHistory.outputs`.
3. **Clearing**: Once the entire sequence finishes (success or error), the Evaluator discards the stored step outputs to reclaim resources.
4. **Error Handling**: If a step fails, the last known `SequentialHistory` object is packaged with the error output, so that partial results can be surfaced if needed.

### Static Pattern Execution
The Evaluator now supports a static Director-Evaluator variant. In this mode, after the Director task generates the initial output, a script execution task (of type "script") is automatically invoked. The Evaluator captures the script's output—including stdout, stderr, and exit code—and feeds it into the subsequent evaluation step, ensuring a predictable, pre-compiled control flow.

### Usage Example
When a multi-step sequence is run, each subtask is executed in turn. The Evaluator:
1. Sets up a new `SequentialHistory` with `currentStep=0`.
2. Executes the first subtask, storing its `TaskOutput` in `outputs[0]`.
3. Moves on to the second subtask, incrementing `currentStep`. If it fails, the Evaluator includes `outputs[0]` data in the final error's notes, to assist debugging or partial re-usage.
4. If steps continue successfully, the final result merges all step outputs or final subtask output as the overall `TaskResult`.

The evaluator now produces an EvaluationResult (with success and optional feedback) for each task. Only the last evaluator output is stored in the environment variable last_evaluator_output; all other variables are cleared on continuation.

Example task definitions:
```xml
<task type="director">
    <output_slot>last_evaluator_output</output_slot>
</task>

<task type="evaluator">
    <input_source>last_evaluator_output</input_source>
</task>
```

**Important**: Because subtask outputs can be large, the system should either store them as short notes or partial references. The data accumulation approach can be toggled with `accumulateData` (in `ContextManagement`), plus an `accumulationFormat` indicating whether to store full outputs or only summary notes.
