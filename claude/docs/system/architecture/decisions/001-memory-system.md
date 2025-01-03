# Architecture Decision Record: Memory System Design

## Context

The memory system needs to manage multiple types of memory and context while integrating with task execution and handlers. This ADR captures key decisions about responsibilities and interfaces.

## Related Documents
- See [Component:Memory:1.0] in components/memory/README.md for component specification
- See [Component:TaskSystem:1.0] in components/task-system/README.md for task execution details
- See [Interface:Handler:ResourceMonitoring:1.0] in components/task-system/spec/interfaces.md for Handler resource management
- See Sequential and Reduce operator specifications in components/task-system/spec/operators.md
- See [Pattern:ResourceManagement:1.0] in system/architecture/patterns/resource-management.md

## Decisions

### Memory System Scope

1. **Component Ownership**
   - Owns associative matching mechanism through specialized tasks (see Memory Task Example in components/task-system/impl/examples.md)
   - Stores but doesn't manage system prompts and templates (see [Contract:Tasks:TemplateSchema:1.0] in system/contracts/protocols.md)
   - Delegates context window tracking to Handler (see [Interface:Handler:ResourceMonitoring:1.0])
   - Delegates chat history management to Handler

2. **Memory Organization**
   - Working Memory includes:
     * Data context (from associative matching)
     * Chat component (LLM-handler interaction)
     * System prompt
     * Populated prompt template
   - Context specifically refers to data context
   - Clear separation between storage and management responsibilities
   - See Memory System Types in components/task-system/spec/types.md

### Context Management

1. **Context Sources**
   - Data context can come from:
     * Parent task inheritance
     * Predecessor task (for map/sequence operations, see operator specifications)
     * Associative matching against long-term memory
   - See [Pattern:ContextFrame:1.0] in system/architecture/patterns/context-frames.md
   
2. **Context Control**
   - Context source controlled by task library entries
   - Specified through operator XML syntax
   - Not a substitutable template parameter
   - Prior task notes can influence associative matching
   - See Task Template Schema [Contract:Tasks:TemplateSchema:1.0]

### Interface Design

1. **XML Schema**
   - Add optional inherit_context attribute to task elements
   - Default behavior can vary by operator type
   - Part of operator XML structure, not template parameters
   - See operator specifications in components/task-system/spec/operators.md

2. **TaskResult**
   - Simplify notes to unstructured string
   - Remove structured dataUsage field
   - Allows flexible note content for associative matching
   - See TaskResult interface in components/task-system/api/interfaces.md

## Consequences

1. **Positive**
   - Clear separation of concerns between components (follows [Pattern:ResourceManagement:1.0])
   - Flexible context management
   - Simple, unstructured note passing
   - XML-driven context control

2. **Negative**
   - More complex task library entries
   - Potential for inconsistent defaults across operators
   - Less structured task result notes

## Implementation Notes

1. Update operator XML schemas to include inherit_context attribute (see [Contract:Tasks:TemplateSchema:1.0])
2. Modify TaskResult interface to simplify notes field (see components/task-system/api/interfaces.md)
3. Ensure Handler properly manages delegated responsibilities (see [Interface:Handler:ResourceMonitoring:1.0])
4. Update task library processing for context control