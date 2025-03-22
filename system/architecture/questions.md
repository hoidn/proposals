# Architecture Questions

This document captures open questions and unresolved architectural issues that require further discussion or decisions.

## Unresolved Questions

1. **Context Window Management**: How should we handle context window size limits across different LLM providers?

2. **Template Versioning**: What versioning scheme should we use for task templates to ensure backward compatibility?

*Integrated from `/inconsistencies.md`:*

3. **Documentation Priority**: Should we prioritize architectural clarity or implementation details in the main documentation?

4. **Error Taxonomy Boundaries**: Where should we draw the line between specific error types and generic errors with reason codes?

5. **Context Management Model Extensibility**: How should we handle future extensions to the three-dimensional context model without breaking existing implementations?

6. **Handler Tool Registration Mechanism**: Should tool registration be dynamic at runtime or static at initialization time?

7. **Resource Calculation Trade-offs**: How should we balance accurate resource tracking against performance overhead?

## Resolved Questions

1. **Context Management Model**: Should we use a three-dimensional model (inherit, accumulate, fresh) or a simpler two-dimensional model?
   - **Decision**: Use the three-dimensional model with explicit settings for each dimension
   - **Rationale**: Provides more flexibility while maintaining clear defaults
   - **Reference**: ADR 14 - Operator Context Configuration

2. **Subtask Spawning Mechanism**: Should subtasks use continuation-based or callback-based execution?
   - **Decision**: Use continuation-based execution with standardized subtask_request structure
   - **Rationale**: Simplifies implementation and maintains clear execution flow
   - **Reference**: ADR 11 - Subtask Spawning
