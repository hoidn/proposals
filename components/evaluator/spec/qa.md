# Evaluator Q&A [Spec:EvaluatorQA:1.0]

## Purpose
This document addresses common questions about the Evaluator component, providing clarification on responsibilities, implementation details, and integration with other components.

## Related Documents
- [Component:Evaluator:1.0](../README.md)
- [Pattern:Error:1.0](../../../system/architecture/patterns/errors.md)
- [Pattern:DirectorEvaluator:1.1](../../../system/architecture/patterns/director-evaluator.md)

## General Questions

### What is the Evaluator's primary responsibility?
The Evaluator is responsible for AST processing, template variable substitution, and execution control. It walks the AST, manages lexical environments, delegates LLM execution to the Handler, and handles error recovery.

### How does the Evaluator differ from the Task System?
The Task System defines task structure, processes context management configuration, and signals the Evaluator to execute steps with the final configuration. The Evaluator handles the actual execution, including AST walking, environment management, and template variable substitution.

### How does the Evaluator differ from the Handler?
The Evaluator manages the execution flow and environment, while the Handler handles direct LLM interactions, resource tracking, and tool execution. The Evaluator is responsible for template variable substitution, while the Handler works with fully resolved content.

## Template Substitution

### Who is responsible for template variable substitution?
The Evaluator is exclusively responsible for all template variable substitution, including resolving all `{{variable_name}}` placeholders. Handlers receive fully resolved content with no remaining template variables.

### How are function templates different from standard templates?
Function templates have explicit parameter declarations and create a new lexical environment for execution. Standard templates use variables from the current environment and parent environments. Function templates provide clearer scope boundaries and dependencies.

### What happens if a template variable is not found?
If a template variable is not found in the environment, the Evaluator generates a `template_resolution_failure` error with details about the missing variable. The error includes the template string and the name of the missing variable.

### How are nested variables handled?
Nested variables (variables that contain other variables) are resolved recursively. The Evaluator first resolves the outer variable, then processes any variables in the resulting string.

## Context Management

### How does the Evaluator implement the three-dimensional context model?
The Evaluator implements the three-dimensional context model through configuration processing, context preparation, and accumulation handling. It processes the `inherit_context`, `accumulate_data`, `accumulation_format`, and `fresh_context` settings to determine how context is managed.

### What is the mutual exclusivity constraint?
The mutual exclusivity constraint states that when `inherit_context` is "full" or "subset", `fresh_context` must be "disabled". Conversely, when `fresh_context` is "enabled", `inherit_context` must be "none". This prevents potential context duplication.

### How does the Evaluator handle file paths?
The Evaluator processes specified file paths regardless of other context settings. It fetches file contents using Handler tools before task execution and integrates the contents with other context sources.

### How does context accumulation work?
When `accumulate_data` is `true`, the Evaluator accumulates previous step outputs according to the `accumulation_format` setting. If `accumulation_format` is `notes_only`, only the notes field is preserved. If it's `full_output`, both content and notes fields are preserved.

## Subtask Spawning

### How does the Evaluator implement subtask spawning?
The Evaluator implements subtask spawning through request detection, validation, and processing. It checks depth limits, detects cycles, prepares context, selects templates, and executes subtasks with proper resource tracking.

### How does the Evaluator control subtask depth?
The Evaluator tracks subtask nesting depth and enforces a maximum depth limit (default: 5). It also detects cycles in subtask spawning by tracking the subtask path and checking for repeated signatures.

### How does the Evaluator integrate with the unified tool interface?
The Evaluator integrates with the unified tool interface by transforming tool calls to subtask requests when appropriate and transforming subtask results to tool responses. This allows the LLM to interact with a consistent tool interface regardless of implementation mechanism.

### How does the Evaluator handle subtask errors?
The Evaluator wraps subtask errors with context, including the original subtask request, the specific error details, the current nesting depth, and any partial results. This enables robust recovery strategies at the parent task level.

## Error Handling

### How does the Evaluator handle resource exhaustion?
When the Handler raises a `RESOURCE_EXHAUSTION` error, the Evaluator attempts recovery through the reparse mechanism. If recovery fails, the error is propagated to the parent task with complete resource metrics and context.

### How does the Evaluator preserve partial results?
The Evaluator preserves partial results differently for different task types:
- For atomic tasks, it stores partial content in `notes.partialOutput`
- For sequential tasks, it stores step-by-step outputs in `details.partialResults`
- For reduce tasks, it stores processed input results in `details.partialResults` and the current accumulator state in `details.currentAccumulator`

### How does the Evaluator handle output format validation?
When a task specifies an output format using `<output_format type="json" schema="...">`, the Evaluator validates the output against the specified schema. If validation fails, it generates a structured error that includes the expected type, actual type, and original output.

### What recovery strategies does the Evaluator implement?
The Evaluator implements several recovery strategies:
- For resource exhaustion, it attempts task decomposition
- For failed tasks, it may try alternative templates
- For complex tasks, it may break them down into simpler subtasks
- For failed approaches, it may attempt fallback approaches

## Integration with Other Components

### How does the Evaluator interact with the Memory System?
The Evaluator interacts with the Memory System for context management, calling `memorySystem.getRelevantContextFor()` based on context management settings. It uses the Memory System for fresh context generation and associative matching.

### How does the Evaluator interact with the Handler?
The Evaluator delegates LLM execution to the Handler, passing fully resolved content with no remaining template variables. It receives execution results and resource metrics from the Handler and handles resource exhaustion errors.

### How does the Evaluator implement the Director-Evaluator pattern?
The Evaluator implements the dynamic Director-Evaluator pattern through continuation detection, evaluation request processing, and template selection. It detects when a Director task returns with a `CONTINUATION` status and an `evaluation_request`, processes the request, and executes the Evaluator subtask.

### How does the Evaluator handle script execution?
The Evaluator integrates script execution with the Director-Evaluator pattern by detecting script execution requests, delegating to the Handler for script execution, and integrating the script result with the Evaluator inputs. This enables automated testing and validation.
