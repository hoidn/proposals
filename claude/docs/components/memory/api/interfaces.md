# Memory System Interfaces [Interface:Memory:3.0]

## Overview
The Memory System provides two core capabilities:
1. Global file metadata index maintenance for associative matching

The system does not handle file content storage or retrieval.

## Core Types

/**
 * Represents metadata associated with a file
 * Stored as an unstructured string for flexibility
 */
type FileMetadata = string;

/**
 * Global index mapping file paths to their metadata
 * - Keys are absolute file paths
 * - Values are unstructured metadata strings
 */
type GlobalIndex = Map<string, FileMetadata>;
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
- Associative Matching: Uses GlobalIndex as basis for context generation in tasks
