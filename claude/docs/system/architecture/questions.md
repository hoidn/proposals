# Open Architecture Questions

This document now lists only *unresolved* questions. Many items previously listed have been answered in the ADRs or clarified in the patterns.

## Unresolved Questions

1. **Context Generation Failures:** When associative matching fails, should partial outputs be preserved for re‑try? (See ADRs 002 and 005 for related discussion.)

2. **Operator Inheritance for Reduce/Map:** Should the `inherit_context` attribute be extended to reduce and parallel operators, and if so, how should it interact with accumulation?

3. **Subtask Spawning Mechanism:** How exactly should subtasks be created dynamically (beyond the Director‑Evaluator pattern)? This remains an open design area.

For additional background, see also [decisions/005-context-handling.md](decisions/005-context-handling.md) and [questions.md](questions.md) in previous revisions.

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
