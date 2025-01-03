# Resource Management Q&A

## Memory Types & Organization

Q: What types of memory need to be managed?
A: The system has a hierarchical memory design:
- Long-term memory for data and procedures
- Working memory for active computations
- Context frames that capture execution environments (including working memory)
- Variable bindings within environments

Q: How is context organized and managed?
A: Through Environment objects that combine:
- Variable bindings (local scope)
- Working memory context
- Context frames are passed and extended through task execution

## Resource Ownership & Isolation

Q: Who owns and tracks resources?
A: Per existing documentation:
- Handler-based resource tracking
- One Handler per task execution
- No cross-Handler resource pooling
- Per-session resource isolation

Q: How are resources allocated and released?
A: As documented:
- Clean resource release on completion
- Turn limit passed during Handler initialization
- Default resource limits from config
- Per-task limit overrides possible

## Context Window Management

Q: How is the context window managed?
A: Through explicit tracking:
- Token-based calculation
- Window size monitoring
- Fraction-based limits
- No content optimization
- Warning at 80% threshold
- Error at limit reached

Q: How does context preservation work between tasks?
A: Through the Environment system:
- Context frames capture complete execution environments
- Each task receives minimal required context
- Associative memory system mediates between long-term and working memory
- Environment.extend() creates new contexts with additional bindings

## Resource Metrics & Limits

Q: What resource metrics are tracked?
A: Currently documented:
- Turn counts
- Context window size
- Token usage
- Peak usage statistics

Q: How are resource limits handled?
A: As specified:
- Default limits from config
- Per-task overrides possible
- Warning thresholds (80%)
- Hard limits with error handling
- Clean termination on limit violation