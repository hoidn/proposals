# Context Frame Pattern [Pattern:ContextFrame:1.0]

## Related Documents
- Memory System ADR in [ADR:Memory:1.0]
- Memory component in [Component:Memory:1.0]
- Resource Management Pattern in [Pattern:ResourceManagement:1.0]

## Context Frame Operations

### Operator Default Settings

Each operator type has specific default context management settings:

| Operator Type | inherit_context | accumulate_data | accumulation_format | fresh_context |
|---------------|-----------------|-----------------|---------------------|---------------|
| atomic        | full            | false           | notes_only          | disabled      |
| sequential    | full            | true            | notes_only          | disabled      |
| reduce        | none            | true            | notes_only          | enabled       |
| script        | full            | false           | notes_only          | disabled      |
| director_evaluator_loop | none  | true            | notes_only          | enabled       |

### Context Management Constraints

To simplify the system and prevent potential content duplication, the following constraint is enforced:

- **Mutual Exclusivity**: `fresh_context="enabled"` and `inherit_context` being "full" or "subset" are mutually exclusive
  - When a task inherits context (fully or partially), it should not generate fresh context
  - When a task generates fresh context, it should not inherit context from its parent

These defaults apply when no explicit context_management block is provided. When present, the explicit settings override the defaults:

```xml
<context_management>
    <inherit_context>full|none|subset</inherit_context>
    <accumulate_data>true|false</accumulate_data>
    <accumulation_format>notes_only|full_output</accumulation_format>
    <fresh_context>enabled|disabled</fresh_context>
</context_management>
```

Settings are merged during template loading, with explicit settings taking precedence over defaults.

### Context Inheritance Modes

The system supports three context inheritance modes:
- **full**: Complete inheritance of parent context
- **subset**: Selective inheritance of specific context elements
- **none**: No context inheritance

When the "disable context" flag is active, the inherited context is completely omitted from the ContextGenerationInput.

```mermaid
flowchart TD
    A[Task Start] --> B{Context Mode?}
    B -->|Full| C[Use Parent Context]
    B -->|Subset| D[Use Selected Context]
    B -->|None| E[No Inherited Context]
    C --> F[Execute Task]
    D --> F
    E --> F
```

```mermaid
flowchart TD
    A[Atomic Task Begins] --> B[Check "Disable Context" Flag]
    B -- Yes --> C[Omit inheritedContext in ContextGenerationInput]
    B -- No --> D[Include parent context]
    C --> E[Pass to MemorySystem.getRelevantContextFor]
    D --> E
    E --> F[Heuristic Matching & Candidate Scoring]
    F --> G[Select Highest-scoring Template]
```

## Formal Definitions

Example ContextGenerationInput:
```json
{
  "taskText": "analyze experimental data",
  "inheritedContext": "context string if available",
  "previousOutputs": "summarized outputs if any"
}
```

Example AssociativeMatchResult:
```json
{
  "context": "retrieved relevant context",
  "matches": [
    ["fileA.txt", "metadata info"],
    ["fileB.txt", null]
  ]
}
```

See also:
- [ADR:002-context-management]
- [ADR:005-context-handling]

### Frame Creation and Extension
```typescript
interface ContextFrame {
    // Based on Memory System design (see [ADR:Memory:1.0])
    bindings: Map<string, any>;    // Current variable bindings
    context: Map<string, any>;     // Working memory context
    
    extend(bindings: Map<string, any>): ContextFrame;
    cleanup(): void;
}

---
**Related Decisions:** For higher‑level context management decisions, see [decisions/002-context-management.md](../decisions/002-context-management.md) and [decisions/005-context-handling.md](../decisions/005-context-handling.md).
```

## EnvironmentFrame Interface

To support argument passing during task evaluation, we introduce a new interface:

```typescript
interface EnvironmentFrame {
    bindings: Map<string, any>;    // Arguments bound to this scope
    parent?: EnvironmentFrame;     // Parent scope for lookup chain
    context: Record<string, any>;    // Task execution context (separate from bindings)
}
```

This `EnvironmentFrame` is created at the start of each task execution (using the new `createFrame` method) and is chained to any existing parent frame. Its purpose is to maintain a clear separation between argument bindings and the overall task context.

### Frame Immutability
- No modification of existing frames
- New frames created through extension
- Clear task isolation boundaries
- Minimal required context principle

### Memory System Integration
- Associative memory system mediates between long-term and working memory
- Working memory instantiated from long-term storage using associative retrieval
- Context updates managed through frame extension
- Resource tracking delegated to Handler

## Implementation Examples

### Frame Creation
```typescript
// Example based on [Component:Memory:1.0] implementation
class ContextFrame implements IContextFrame {
    private bindings: Map<string, any>;
    private context: Map<string, any>;
    
    extend(newBindings: Map<string, any>): ContextFrame {
        const frame = new ContextFrame();
        frame.bindings = new Map([...this.bindings, ...newBindings]);
        frame.context = this.context;  // Shared context reference
        return frame;
    }
    
    cleanup(): void {
        // Resource cleanup handled by Handler
        this.bindings.clear();
        this.context = null;
    }
}
