# Context Management Architectural Decisions

## Status
Accepted

## Context
The system needs to manage task execution context efficiently while supporting composition operations. Several key decisions were needed regarding context selection, merging, and extension patterns.

## Decisions

### 1. Context Selection via LLM
- Context selection (determining minimal required context) will be handled at the LLM + prompt level
- This is NOT a system architecture concern
- Allows for more flexible and intelligent context selection
- Pushes complexity to the prompt engineering layer where it can be more easily tuned

### 2. Context Extension vs Merging
- Will use context extension patterns rather than merging
- Tasks extend from parent context rather than merging multiple contexts
- Simpler model that satisfies MVP composition requirements
- Reduces complexity in the memory system implementation

### 3. Warning Behavior
- Resource warning thresholds are purely informative
- Warnings do not affect execution flow
- Simplifies resource management behavior
- Maintains clear separation between warnings and hard limits

### 4. Memory Operation Error Handling
- Memory operations that fail should be retried (Note: A dedicated "disable context" flag is available for atomic and associative matching tasks to omit inherited context.)
- If retry fails, surface an informative error
- Provides simple but robust error handling strategy
- Gives operations a chance to recover without complex logic

### 5. Disable Context Option for Atomic and Associative Matching Tasks
- **Decision:** Atomic tasks—and by extension, associative matching tasks—may disable context entirely via a dedicated flag. When this flag is enabled, no inherited context will be passed to the task, ensuring that only its explicit inputs are used for matching.
- **Rationale:** This option provides finer control for tasks where inherited context might be unnecessary or detrimental to accurate matching.
- **Cross‑References:** See also [Context Frames](../patterns/context-frames.md) for a discussion on available context inheritance modes.

## Consequences
- Positive:
  - Simpler memory system implementation
  - Clear separation of concerns between system and LLM layers
  - Straightforward error handling model
  - Reduced complexity in context management
- Negative:
  - May need to revisit context merging for post-MVP requirements
  - More responsibility on prompt engineering for context selection
  - Limited automatic intervention on warnings

## Related
- [Component:MemorySystem:1.0]
- [Pattern:TaskExecution:1.0]
- [Contract:Resources:1.0]
