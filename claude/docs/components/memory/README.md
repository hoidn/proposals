# Memory System Component [Version 3.0]

## Overview

The Memory System provides context management and associative matching services for task execution. It maintains a global metadata index to support context retrieval while delegating actual file operations to Handler tools. The system focuses purely on metadata management and context retrieval - it does not store file content, perform file operations, track resources, or rank matches.

## Core Interface

```typescript
interface MemorySystem {
    // Retrieve global file metadata index
    getGlobalIndex(): Promise<GlobalIndex>;
    
    // Update global metadata index (bulk operation)
    updateGlobalIndex(index: GlobalIndex): Promise<void>;
    
    // Get relevant context for task execution
    getRelevantContextFor(input: ContextGenerationInput): Promise<AssociativeMatchResult>;
}
```

The system works with a simple but flexible type system. File metadata is stored as unstructured strings, with a global index mapping absolute file paths to their metadata. When performing associative matching, the system returns both relevant context and a list of matching files.

## Usage

The Memory System is typically used for two main purposes: managing the global metadata index and retrieving context for task execution. Here's a typical usage pattern:

```typescript
// Initialize and update index
const memory = new MemorySystem();
await memory.updateGlobalIndex(new Map([
    ['data.txt', 'Experimental results from 2024-02'],
    ['config.json', 'System configuration parameters']
]));

// Request context for task execution
const result = await memory.getRelevantContextFor({
    taskText: "Analyze recent experimental results",
    inheritedContext: "Previous analysis focused on temperature variance",
    previousOutputs: "Initial data validation complete"
});
```

## Integration Points

The Memory System integrates with other components through clear boundaries. It provides context and metadata to the Task System and Evaluator while relying on Handler tools for any actual file operations. The system maintains a read-only approach to context management, with updates happening through bulk operations on the metadata index.

All file operations go through Handler tools rather than the Memory System itself. This separation ensures clean resource management and clear responsibility boundaries. Error handling follows a simple pattern - all failures map to standard TASK_FAILURE errors with clear messages.

## Resource Management

The system takes a conservative approach to resource management. Index updates are bulk operations that replace the entire index, avoiding complexities of partial updates or hierarchical organization. Context is never preserved between tasks, and all updates happen through clean extensions rather than merging.

## Implementation Guidelines

When implementing against the Memory System, keep these principles in mind:

```typescript
// Context generation requires structured input
const input: ContextGenerationInput = {
    taskText: "Required task description",
    inheritedContext: "Optional parent context",
    previousOutputs: "Optional step outputs"
};

// Index management uses absolute paths
const index: GlobalIndex = new Map([
    ['/absolute/path/to/file', 'Metadata string']
]);
```

Use descriptive but concise metadata strings, maintain consistent formats, and handle all error cases explicitly. Always access file content through Handler tools rather than trying to store it in the Memory System.

## Version History

The current Version 3.0 removed the updateContext capability and enforces a read-only context model with simplified state management. This follows from architecture decisions documented in [ADR:Memory:1.0] and interface specifications in [Interface:Memory:3.0].

For detailed implementation specifications and patterns, refer to [Contract:Integration:TaskMemory:1.0] and [Pattern:ContextFrame:1.0].
