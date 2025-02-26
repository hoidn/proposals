# Architecture Decision Record: Sequential Context Management

## Status
Proposed

## Context
We need to separate context inheritance from data accumulation and provide a robust mechanism for step-by-step history tracking.

Currently, tasks either share context automatically or produce data that might or might not propagate. This leads to confusion when partial outputs are produced but we do not have a consistent mechanism to feed them into subsequent steps. Also, memory consumption can balloon if every subtask blindly appends data. 

## Decision
1. **Introduce `<context_management>`** for controlling context inheritance and accumulation in sequential tasks.  
2. **Add explicit outputtracking** in the Evaluator for each step of a sequential task.  
3. **Provide structured ways** to use task history in associative matching or subsequent steps.  
4. **Include step outputs** in error results for failed sequences.  
5. **Enforce resource limits** on total stored step data.

## Consequences
- **Cleaner separation of concerns** between inheritance and accumulation  
- **More flexible context management** through distinct modes (`inherit_context`, `accumulate_data`, etc.)  
- **Better step-by-step tracking** for partial outputs  
- **Predictable error output**: if step N fails, steps 1..N-1 remain visible  
- **Clear resource usage capping** for historical data

## Implementation Notes
1. The new `<context_management>` block in the `sequential` task schema.  
2. The Evaluator stores subtask outputs in a local structure (`SequentialHistory`).  
3. On subtask completion (whether success or error), the Evaluator updates the history.  
4. If `accumulate_data` is `true`, the next subtask can optionally see prior outputs (the system uses these to fill in an associative matching context or a merged notes field).  
5. If `accumulation_format` is `notes_only`, we store only minimal text from each step in the history. If `full_output`, we store the entire subtask result.  
6. The plan accounts for partial failures by storing partial results in the final error. 

## Alternatives Considered
- **Context merging** in each step: Rejected due to complexity and risk of indefinite growth.  
- **Forcing every step to have fresh context**: Would break certain use cases that require incremental data usage.  
- **Implicit partial output usage**: Proposed approach is more explicit, ensuring developers set `accumulate_data` if they need it.

## Related
- [Pattern:SequentialTask:2.0] in system/architecture/overview.md  
- [misc/operators.md] for structural usage  
- [system/contracts/protocols.md] for updated XSD schema  
- [components/task-system/impl/examples.md] for a usage example
