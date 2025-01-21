# Implementation Plan

This document describes a phased approach to completing the outstanding TODO items and aligning the Task System, Memory System, and Handler interfaces with the intended architecture.

---

## Phase 1: Interface Consolidation and Version Alignment

### Goals
1. **Unify Memory System interface references** to a single version (decide on `Memory:2.0` **or** `Memory:3.0`).
2. **Remove old or conflicting memory structure references** in the Task System.
3. **Harmonize** cross-references in the documentation (ADR files, architecture patterns, and the `task-system/spec` directory).

### Steps

1. **Pick a Single Memory Interface Version**  
   - Decide whether to standardize on `[Interface:Memory:3.0]` or revert to `[Interface:Memory:2.0]`.  
   - Whichever is chosen, rename references and ensure references to the other version are removed or updated.

2. **Clean Up Task System References**  
   - In `components/task-system/spec/interfaces.md`, ensure that the `MemorySystem` type is imported consistently.  
   - Remove any leftover legacy fields such as `getContext()` or “manual partial context” if they conflict with the final design.  
   - Verify that only the **metadata** and **bulk index** capabilities remain under `MemorySystem`.

3. **Update Handler Tool Interfaces**  
   - Confirm whether you need `writeFile`, or if read-only is sufficient.  
   - If you need additional methods (e.g., `listFiles`, `deleteFile`), define them under `Handler.tools` or propose them as optional future expansions.

4. **Validate Documentation References**  
   - Search for `[Interface:Memory:2.0]` and `[Interface:Memory:3.0]` across all `.md` files in `system/` and `components/`.  
   - Remove or update references that point to the outdated version.  

### Example Code Snippet

```typescript
// In components/task-system/spec/interfaces.ts (example):
import { MemorySystem } from '../../memory/api/interfaces'; // must match final chosen version

interface TaskSystem {
  executeTask(
    task: string,
    memory: MemorySystem, // Unified usage
    taskType?: TaskType
  ): Promise<TaskResult>;
  ...
}
Completion Criteria
No stale references to the unused interface version.
TaskSystem references to MemorySystem are consistent.
Handler’s tools property is clear on read-only vs. read/write.
Phase 2: Expanded Context Management
Goals
Ensure environment has three layers (MemorySystem instance, sequential data accumulation, associatively retrieved data).
Extend inherit_context usage to sequential, map, and reduce operators.
Define partial-result handling when context generation fails or is incomplete.
Steps
Revise Operator Specs

In misc/operators.md (or your operators specification), ensure each operator (sequential, reduce, map) can optionally include <inherit_context>true</inherit_context>.
Document how partial contexts propagate. For instance, if a map sub-task fails partially, do you keep partial results or discard them?
Enhance Environment Structure

Introduce an interface Environment in the code that includes:
typescript
Copy
interface Environment {
  memorySystem: MemorySystem; 
  sequentialData?: Record<string, any>; 
  workingMemory?: Record<string, any>; 
}
Pass this Environment object around so that tasks can reference the needed contexts.
Partial-Result Handling

Decide if context-generation failures produce a new error type (e.g., CONTEXT_GENERATION_FAILURE) or if they remain a generic TASK_FAILURE.
If partial results are important, preserve them under a notes.partialResults or a similar field in the TaskResult.
Update Error Taxonomy

If you do introduce a new error type for context issues, define it in errorspec.md or your main TaskError union.
Clarify in your documentation whether you retry automatically or require a “reparse” approach.
Example Code Snippet
xml
Copy
```xml
<task type="map">
  <description>Analyze each file in parallel</description>
  <inherit_context>true</inherit_context>
  <steps>
    <task>
      <description>Process data</description>
      <inputs>
        <input name="file_path">/absolute/path/file1.txt</input>
      </inputs>
    </task>
    <task>
      <description>Process data</description>
      <inputs>
        <input name="file_path">/absolute/path/file2.txt</input>
      </inputs>
    </task>
  </steps>
</task>
```

The environment for each sub-task automatically includes shared memory or sequential data when `inherit_context="true"`.

### Completion Criteria
- Operators consistently accept or ignore inherit_context
- New environment structure is used in at least one example operator chain
- Decision on partial results is documented and implemented

## Phase 3: Task Execution Enhancements
Goals
Implement “rebuild-memory” or “clear-memory” flags for tasks that need a fresh context.
Support multi-step or “continuation” protocols for tasks that require multiple interactions without losing context state.
Add summary output or additional logging in the evaluator for advanced debugging.
Steps
Add rebuild_memory Flag

In your XML schemas or DSL, define an optional rebuild_memory boolean.
If true, your environment creation logic can skip copying any existing memory or context from the parent environment.
Continuation Protocol

Provide a structured way to re-enter an ongoing task.
Could be as simple as a “session ID” recognized by the TaskSystem, or an explicit “continuation step” operator.
Evaluator Enhancements

For tasks that produce extensive logs or partial results, store that data in a new notes.debugLogs or notes.summary field.
Decide how (or if) you re-inject that information in subsequent tasks.
Example Code Snippet
xml
Copy
<task type="sequential">
  <description>Clear memory, then do two steps</description>
  <rebuild_memory>true</rebuild_memory>
  <steps>
    <task>
      <description>Load fresh environment</description>
    </task>
    <task>
      <description>Perform main analysis in a cleaned environment</description>
    </task>
  </steps>
</task>
Completion Criteria
rebuild_memory or clear_memory recognized by the environment code.
Capability to do multi-step tasks without losing required state, or documented reasoning why that is out of scope.
Phase 4: Agent Features (Optional / Future)
Goals
Add agent-oriented features (storing conversation history across tasks, REPL-like interactions, multi-LLM backends).
Extend Handler or spin off a new module for advanced agent logic.
Steps
Conversation History

Decide if the conversation timeline is maintained entirely by the Handler or if you store a rolling log outside.
Potentially add an “agent memory” object to combine short text history with the rest of the environment.
Multi-LLM or REPL Support

Abstract the Handler.executePrompt method to accept different underlying LLMs.
Provide a REPL where developers can step through tasks and respond to onRequestInput hooks in real time.
Testing & Monitoring

Because agent interactions can be tricky, add extra instrumentation to track turn usage, partial completions, and user overrides.
Example Code Snippet
typescript
Copy
// Handler with multi-LLM support
class MultiLLMHandler implements Handler {
  constructor(private config: HandlerConfig) {}
  
  async executePrompt(systemPrompt: string, taskPrompt: string): Promise<string> {
    if (this.config.defaultModel === 'modelA') {
      return modelACall(systemPrompt, taskPrompt);
    } else {
      return modelBCall(systemPrompt, taskPrompt);
    }
  }

  onRequestInput(agentRequest: string): Promise<string> {
    // Developer or user-defined logic here
    return Promise.resolve("User typed input here");
  }

  tools = {
    readFile: async (path: string) => { ... }
  }
}
Completion Criteria
Agent’s conversation context stored and re-used in a stable manner.
REPL or multi-LLM integration thoroughly tested or demoed.
Documented guidelines for ongoing conversation boundaries.
Additional Notes & Guidance
Documentation Sync

Each phase should be accompanied by doc updates in system/architecture/, components/task-system/, and components/memory/.
Once you finalize each stage, run a final cross-reference check to avoid stale references.
Testing Strategy

For each phased milestone, implement integration tests (especially around resource exhaustion, partial results, and context inheritance).
Consider adding a “mock memory system” or “mock handler” for robust unit tests without real LLM calls.
Partial Results

If you decide partial results must be saved, store them in TaskResult.notes.partialResults or a similar field.
Clearly document any distinction between partial failure (some subtasks succeeded) and total task failure.
Versioning

When you make backward-incompatible changes to the Memory interface or TaskSystem interface, increment the major version and update references accordingly.
Keep a consolidated changelog in the repository root to track these changes.

