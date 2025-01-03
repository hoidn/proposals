# Memory System Interfaces [Interface:Memory:2.0]

## Overview
The Memory System provides two core capabilities:
1. Short-term task data context management
2. Global file metadata index maintenance

The system does not handle file content storage or retrieval.

## Core Types

### GlobalIndex
```typescript
type GlobalIndex = Map<string, string>;
```

A mapping of file paths to their associated metadata strings. The index serves as a bootstrap mechanism for associative matching when full content scanning is not feasible.

Key characteristics:
- Keys are absolute file paths
- Values are unstructured metadata strings
- No hierarchical organization
- Updated in bulk operations only

### FileMatch
```typescript
type FileMatch = [string, string | undefined];
```

Represents a relevant file match from associative matching:
- First element: Absolute file path
- Second element: Optional metadata string providing context for this specific match

### AssociativeMatchResult
```typescript
interface AssociativeMatchResult {
    context: string;      // Unstructured data context
    matches: FileMatch[]; // Relevant file matches
}
```

The complete result of associative matching, containing:
- Unstructured context data relevant to the current task
- List of potentially relevant files with optional per-file context

## Interface Methods

### Context Management

#### getContext()
```typescript
getContext(): Promise<string>
```
Retrieves the current task data context.

#### updateContext(context: string)
```typescript
updateContext(context: string): Promise<void>
```
Updates the current task data context with new content.

### Index Management

#### getGlobalIndex()
```typescript
getGlobalIndex(): Promise<GlobalIndex>
```
Retrieves the complete global file metadata index.

#### updateGlobalIndex(index: GlobalIndex)
```typescript
updateGlobalIndex(index: GlobalIndex): Promise<void>
```
Performs a bulk update of the global file metadata index. Replaces the entire existing index.

## Integration Points
- Handler: Uses file paths from AssociativeMatchResult to read files via tools
- Associative Matching Task: Uses GlobalIndex for initial file filtering