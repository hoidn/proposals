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

A mapping of file paths to their associated metadata strings. **Note:** The Memory System is responsible only for providing file metadata (including file paths and unstructured metadata strings). All file I/O operations (reading, writing, deletion) are delegated to Handler tools. The index serves as a bootstrap mechanism for associative matching when full content scanning is not feasible.

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
Retrieves the complete global file metadata index. The GlobalIndex should now support the needs of the TaskLibrary and nested environment model. Any changes to the GlobalIndex structure must allow associative matching in the context of nested task environments. Keys remain absolute file paths and values remain unstructured metadata but remain useful for task context extraction.

#### updateGlobalIndex(index: GlobalIndex)
```typescript
updateGlobalIndex(index: GlobalIndex): Promise<void>
```
Performs a bulk update of the global file metadata index. Replaces the entire existing index.


/**
 * Retrieve context using associative matching.
 * 
 * The Memory System does NOT perform ranking or prioritization of matches.
 * It only provides associative matching based on the input structure.
 *
 * @param input - The ContextGenerationInput containing task context
 * @returns A promise resolving to an AssociativeMatchResult object containing:
 *   - `context`: Unstructured text data relevant to the query
 *   - `matches`: An unordered list of file paths (and optional metadata) relevant to the query
 * @throws {INVALID_INPUT} If the input structure is malformed or missing required fields
 */
declare function getRelevantContextFor(input: ContextGenerationInput): Promise<AssociativeMatchResult>;

## Integration Points
- Handler: Uses file paths from AssociativeMatchResult to read files via tools
- Associative Matching: Uses GlobalIndex as basis for context generation in tasks
