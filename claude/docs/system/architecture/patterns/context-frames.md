# Context Frame Pattern [Pattern:ContextFrame:1.0]

## Related Documents
- Memory System ADR in [ADR:Memory:1.0]
- Memory component in [Component:Memory:1.0]
- Resource Management Pattern in [Pattern:ResourceManagement:1.0]

## Context Frame Operations

### Frame Creation and Extension
```typescript
interface ContextFrame {
    // Based on Memory System design (see [ADR:Memory:1.0])
    bindings: Map<string, any>;    // Current variable bindings
    context: Map<string, any>;     // Working memory context
    
    extend(bindings: Map<string, any>): ContextFrame;
    cleanup(): void;
}
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
