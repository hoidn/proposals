# ADR 7: Context Management Standardization

## Status
Accepted and Implemented

## Context
The system needed a standardized approach to context management across different task types. Previously, context handling was inconsistent, with different mechanisms for inheritance and accumulation.

## Decision
Implement a standardized three-dimensional context management model with the following dimensions:

1. **inherit_context**: Controls parent context inheritance
   - "full" - complete inheritance of parent context
   - "none" - no inheritance from parent
   - "subset" - selective inheritance based on relevance

2. **accumulate_data**: Controls whether outputs from prior steps are accumulated (true/false)

3. **accumulation_format**: When accumulating data, specifies storage format
   - "notes_only" - only summary information is preserved
   - "full_output" - complete step outputs are preserved

4. **fresh_context**: Controls whether new context is generated via associative matching
   - "enabled" - fresh context is generated
   - "disabled" - no fresh context is generated

This model is configured through a standardized XML structure:
```xml
<context_management>
    <inherit_context>full|none|subset</inherit_context>
    <accumulate_data>true|false</accumulate_data>
    <accumulation_format>notes_only|full_output</accumulation_format>
    <fresh_context>enabled|disabled</fresh_context>
</context_management>
```

## Consequences
- Consistent context management across all task types
- Clear separation of inheritance, accumulation, and fresh context generation
- Simplified implementation in the Evaluator component
- Better control over context window usage
- Standardized XML structure for configuration

## Related Documents
- Full ADR moved to archive for space efficiency
- See implementation in Evaluator and Task System components
