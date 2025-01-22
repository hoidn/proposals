# Architecture Decision Record: Context Generation Clarifications

## Status
Accepted

## Context
Recent feedback provided several important clarifications about context generation and associative matching that were either unclear or inconsistent in existing documentation.

## Key Clarifications

### 1. Input Structure for Associative Matching
**Surprise:** The input to getRelevantContextFor() has a specific XML structure with three potential fields:
- Previous outputs (if applicable)
- Inherited context (if applicable)
- Task text
Each with standardized headings from system configuration.

Current documentation does not mention this structure at all.

### 2. Dual Context Components
**Surprise:** When both inheritance and accumulation are active, the system maintains two distinct context components:
- 'Regular' inherited context
- 'Accumulation' context from prior steps
These are tracked separately but can be concatenated for use.

Current documentation suggests a simpler single-context model.

### 3. Resource Allocation Clarification
**Surprise:** The concept of "resource allocation" in relation to context generation timing is irrelevant - the system only signals exhaustion without actual allocation operations.

Current documentation contains references to resource allocation that may be misleading.

### 4. Memory System Scope
**Surprise:** The Memory System does not perform any ranking or prioritization of matched files - this responsibility is explicitly not part of its scope.

Current documentation is ambiguous about this limitation.

## Decision
Update architecture documentation to reflect these clarifications, particularly:
1. The structured XML format for getRelevantContextFor() input
2. The dual-context tracking mechanism
3. Remove references to resource "allocation"
4. Clarify Memory System scope limitations

## Consequences
- Clearer component responsibilities
- More precise context management specification
- Removal of ambiguous resource management concepts
- Better defined Memory System boundaries
