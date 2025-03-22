# Error Handling and Recovery Pattern [Pattern:Error:1.0]

**Intended Focus:** This document covers overall error detection, classification, and recovery strategies. For resource‑related cleanup details, see the "Resource Cleanup" subsection below. (For low‑level resource metrics, refer to [Handler Resource Tracking](../decisions/001-memory-system.md) and related docs.)

## 1. Pattern Definition

### 1.1 Purpose
Error handling pattern for the task execution system, focusing on three key concerns:
- Resource exhaustion detection and recovery
- Invalid output handling
- Progress failure management

### 1.2 Context
This pattern is used by:
- [Component:TaskSystem:1.0] for error detection
- [Component:Evaluator:1.0] for error recovery
- [Component:Handler:1.0] for resource monitoring

### 1.3 Core Elements
- Error Type System: See [Type:TaskSystem:TaskError:1.0]
- Recovery Protocols: See [Protocol:Tasks:Reparse:1.0]
- Resource Contracts: See [Contract:Resources:1.0]

## 2. Error Categories

### 2.1 Resource Exhaustion
Handled by [Protocol:Tasks:Reparse:1.0]

Resource exhaustion occurs when a task exceeds allocated system resources:
- **Type**: 'RESOURCE_EXHAUSTION'
- **Resources**: 'turns' | 'context' | 'output'
- **Metrics**: Contains usage and limit values
- **Recovery**: Attempt task decomposition

### 2.2 Task Failure
Related to [Contract:Tasks:TemplateSchema:1.0]

Task failures now include a standardized `reason` field for more specific categorization:

- 'context_retrieval_failure': Failure to retrieve context data
- 'context_matching_failure': Failure in associative matching algorithm 
- 'context_parsing_failure': Failure to parse or process retrieved context
- 'xml_validation_failure': Output doesn't conform to expected XML schema
- 'output_format_failure': Output doesn't meet format requirements
- 'execution_timeout': Task execution exceeded time limits
- 'execution_halted': Task execution was deliberately terminated
- 'subtask_failure': A subtask failed, causing parent task failure
- 'input_validation_failure': Input data didn't meet requirements
- 'unexpected_error': Catch-all for truly unexpected errors

Task failures also include a structured details object that may contain error-specific information such as:
- partial_context: Any partial context that was retrieved before failure
- context_metrics: Metrics related to context retrieval
- violations: Specific validation rule violations
- partialResults: Results from steps that completed before failure
- failedStep: Index of the step that failed in a sequential task

For implementation details of error type structures, see [Implementation:ErrorTypes:1.0] in `/components/task-system/impl/error-handling.md`.

### 2.3 Failure to Make Progress
Progress failures occur when a task cannot advance despite resources being available:
- **Type**: 'TASK_FAILURE'
- **Reason**: 'execution_halted'
- **Indicators**: Multiple rounds with no state change
- **Recovery**: Alternative approach or termination

### 2.4 Partial Results Handling

The system maintains a standardized approach for preserving partial results when multi-step operations fail:

### Error Output Structure

#### Atomic Tasks
Task status (`COMPLETE` vs `FAILED`) indicates whether content is complete or partial.

#### Sequential Tasks
When a sequential task fails, the error includes details about which step failed and preserves the results from completed steps.

#### Reduce Tasks
For reduce tasks, the error includes information about which input failed processing, the current accumulator state, and results from successfully processed inputs.

#### Storage Format Control
The format of preserved partial results depends on the task's `accumulation_format` setting:
- `notes_only`: Only the notes field is preserved (default for memory efficiency)
- `full_output`: Both content and notes fields are preserved (with size limits)

Each operator type has specific default settings for context management. For sequential tasks, the default `accumulation_format` is `minimal`. These defaults apply when the `context_management` block is omitted. When present, explicit settings override the defaults, following the hybrid configuration approach.

#### Size Management
To prevent memory issues:
- Individual step outputs are kept reasonably sized
- When accumulated data becomes too large, older results may be summarized or truncated
- The system indicates when truncation has occurred

### 2.5 Output Format Validation

When a task specifies an output format using `<output_format type="json" schema="...">`, validation failures result in a structured error that includes the expected type, actual type, and original output.

This error occurs when:
1. The task specifies an output format with `type="json"`
2. The output is successfully parsed as JSON
3. The parsed content doesn't match the specified schema type

The original output is preserved in the `partialOutput` field to allow for potential recovery or manual parsing. The error includes both the expected and actual types to aid in debugging and recovery.

## 3. Recovery Process

### 3.1 Detection Phase
See [Interface:Handler:ResourceMonitoring:1.0]

Error detection now includes identifying:
- Context retrieval failures
- Context matching failures
- Context parsing failures
- Output format validation failures

### 3.2 Planning Phase
See [Component:Evaluator:1.0] for error handling.

Based on error type and reason, the system will surface appropriate error information:
- **Resource Exhaustion**: Complete resource metrics and context
- **Context Failures**: Context-related error details
- **Validation Errors**: Validation failure specifics
- **Subtask Failures**: Error details including partial execution data

### 3.3 Execution Phase
See [Protocol:Tasks:Reparse:1.0] for execution details.

Error handling involves:
- Preparing complete error context
- Including relevant partial execution data
- Surfacing errors through standard error flow
- Providing detailed diagnostics

- **Associative Matching Failures:** If an associative matching task encounters an error—such as insufficient context or partial output—it will automatically trigger a retry. These errors will include any partial output and, if available, an optional success score (recorded in the task's `notes` field) to support future adaptive behavior.

#### Error Recovery Flow for Associative Matching

```mermaid
flowchart TD
    A[Associative Matching Task Initiated] --> B{Error Detected?}
    B -- Yes --> C[Trigger Automatic Retry]
    C --> D[Capture Partial Output & Success Score]
    D --> E[Reattempt Associative Matching]
    B -- No --> F[Proceed with Normal Execution]
```

### Subtask Failure Handling

When a subtask fails, the system provides a standardized error structure that preserves context and enables recovery. This standardized structure provides several benefits:
1. Complete error context preservation
2. Clear indication of which subtask failed
3. Access to the original subtask request for potential retry
4. Preservation of partial results for recovery

For implementation details of error recovery mechanisms, see [Implementation:ErrorRecovery:1.0] in `/components/task-system/impl/error-handling.md`.

### 3.4 Validation Phase
Recovery validation includes:
- Verifying resource usage of recovery approach
- Ensuring progress is made
- Validating output structure and format
- Limiting recovery depth to prevent infinite loops

## 4. Pattern Examples
See components/task-system/impl/examples.md for concrete examples.

### Context Retrieval Failure Example
When the Memory System's file index is corrupted or unavailable, recovery involves alternative context strategy.

### Sequential Task Failure Example
When a sequential task fails, the system provides access to partial results from completed steps, which can be used for recovery.

For concrete implementation examples, see [Implementation:ErrorExamples:1.0] in `/components/task-system/impl/error-handling.md`.

## 5. Known Limitations
- **Recovery Depth**: Limited to prevent infinite loops
- **Partial Result Size**: May be truncated for very large outputs
- **Stateful Recovery**: Not supported across sessions
- **Complex Dependencies**: Recovery may not work for deeply nested failures

## 6. Related Patterns
- [Pattern:ResourceManagement:1.0]
- [Pattern:TaskExecution:2.0]
