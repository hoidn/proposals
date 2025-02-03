# Open Architecture Questions

## Critical (Required for MVP)

### Resource Management
1. How should warning thresholds affect task execution?
   - DECIDED: Warnings are purely informative and do not affect execution flow
   - Continue normally until hard limits
   - Basic metrics preserved for monitoring

2. What is the exact protocol for minimal context selection?
   - DECIDED: Handled at LLM + prompt level
   - Selection performed by LLM based on task requirements
   - Not a system architecture concern

3. What cleanup guarantees are needed between tasks?
   - What must be cleaned up vs what can persist?
   - How are resources released?
   - What happens to in-progress operations?

### Error Handling
1. How should resource exhaustion errors be handled?
   - What context needs to be preserved?
   - Should partial results be kept?
   - What recovery options should be available?

2. What error conditions require task termination vs continuation?
   - Which errors are recoverable?
   - When should tasks be restarted vs continued?
   - How are errors propagated?

## Important (Needed Soon After MVP)

### Memory System
1. How should memory system operations be metered?
   - Do we need limits on memory operations?
   - DECIDED: Failed operations retry once, then surface error
   - What metrics should be tracked?

2. What is the associative memory matching protocol?
   - DECIDED: Handled at LLM + prompt level
   - Not a system architecture concern

### Task Execution
1. How should task transitions be managed?
   - What state needs to be preserved?
   - How are resources transferred?
   - What cleanup is required?

2. When should tasks be allowed to merge contexts?
   - DECIDED: No context merging in MVP
   - Using extension patterns instead
   - May revisit post-MVP

## Future Considerations

### Optimization
1. Are there cases where resource sharing could be beneficial?
2. Should we allow resource reservation for known upcoming needs?
3. How do we handle peak load conditions?

### Context Management
1. Should we track context usage patterns?
2. Do we need context versioning?
3. Should we cache frequent contexts?

### Monitoring
1. What metrics need to be exposed for system health?
2. How should resource usage be tracked over time?
3. What alerting is needed?

## Notes
- Questions are ordered by dependency (what blocks what) and impact on MVP functionality
- Focus areas derived from current documentation gaps
- Some questions may be answerable through implementation experience rather than up-front design
- Security considerations may raise additional questions that need to be prioritized

## Argument Passing Open Questions

1. **Missing Required Arguments:** If a task's required input is not found in the environment frame chain, should the task immediately fail?
   - *Current Decision (MVP):* Yes, the evaluator will return a `TASK_FAILURE` error.

2. **Extra Arguments:** What should be done if extra (non‐defined) arguments are provided?
   - *Current Decision (MVP):* Extra arguments are allowed but only required arguments are validated.

3. **Argument Immutability:** Should task arguments be immutable?
   - *Decision:* Yes, once bound, argument values cannot be modified.
