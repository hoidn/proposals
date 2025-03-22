# Task System Type Definitions

This document defines the core data structures and types used by the Task System.

## Task Types

```typescript
/**
 * Defines the type of task to be executed.
 */
export type TaskType = "atomic" | "sequential" | "reduce" | "script" | "director_evaluator_loop";

/**
 * Subtypes for atomic tasks providing specialized functionality.
 */
export type AtomicTaskSubtype = "standard" | "subtask" | "director" | "evaluator";
```

## Atomic Task Subtype Hierarchy
*Integrated from `/plans/atomic_task_subtypes.md`*

Atomic tasks support the following subtypes, implemented as a type hierarchy:

```typescript
/**
 * Subtypes for atomic tasks providing specialized functionality.
 */
export type AtomicTaskSubtype = "standard" | "subtask" | "director" | "evaluator";
```

### XML Implementation

The subtypes are implemented in XML using the `subtype` attribute:

```xml
<task type="atomic" subtype="director">
    <continuation_policy>latest-only</continuation_policy>
    <output_slot>last_eval_input</output_slot>
</task>

<task type="atomic" subtype="evaluator">
    <input_source>last_eval_input</input_source>
    <validation_rules>strict</validation_rules>
</task>
```

### Advantages of Atomic Subtyping

| Aspect | Benefit |
|--------|---------|
| Execution Flow | Inherits standard atomic task lifecycle (init → execute → cleanup) |
| Error Handling | Uses existing atomic error recovery patterns |
| Resource Tracking | Leverages atomic task's turn counting & context management |
| Template Matching | Works with current associative matching system |

### Context Management By Subtype

The `AtomicTaskSubtype` influences default context management settings:

| Subtype | inherit_context | fresh_context | Description |
|---------|-----------------|---------------|-------------|
| standard | full | disabled | Regular atomic tasks inherit context |
| subtask | none | enabled | Subtasks use fresh context |
| director | full | disabled | Directors inherit context |
| evaluator | subset | enabled | Evaluators use relevant context |

## Task Definition

```typescript
/**
 * Core task definition structure.
 */
export interface TaskDefinition {
  type: TaskType;
  subtype?: AtomicTaskSubtype;
  description: string;
  provider?: string;
  model?: string;
  inputs?: Record<string, any>;
  context_management?: ContextManagementConfig;
  file_paths?: string[];
  isManualXML?: boolean;
  disableReparsing?: boolean;
}
```

## Context Management

```typescript
/**
 * Configuration for context management during task execution.
 */
export interface ContextManagementConfig {
  inherit_context: "full" | "none" | "subset";
  accumulate_data: boolean;
  accumulation_format: "notes_only" | "full_output";
  fresh_context: "enabled" | "disabled";
}
```

## Task Results

```typescript
/**
 * Result of a task execution.
 */
export interface TaskResult {
  content: string;
  status: "COMPLETE" | "CONTINUATION" | "ERROR";
  notes?: Record<string, any>;
  parsedContent?: any;
  wasXMLParsed?: boolean;
}
```

## Task Template

```typescript
/**
 * Template for task execution.
 */
export interface TaskTemplate {
  taskPrompt: string;
  systemPrompt?: string;
  model?: string;
  isManualXML?: boolean;
  disableReparsing?: boolean;
}
```

## Resource Metrics

```typescript
/**
 * Metrics for resource usage during task execution.
 */
export interface ResourceMetrics {
  turnsUsed: number;
  maxTurns: number;
  tokensUsed?: number;
  contextWindowUsage?: number;
  maxContextWindowFraction?: number;
}
```

## Task Errors

```typescript
/**
 * Error types for task execution failures.
 */
export type TaskErrorType = "RESOURCE_EXHAUSTION" | "TASK_FAILURE";

/**
 * Detailed error information for task failures.
 */
export interface TaskError {
  type: TaskErrorType;
  message: string;
  resource?: string;
  reason?: string;
  details?: Record<string, any>;
  metrics?: ResourceMetrics;
}
```

## Subtask Request

```typescript
/**
 * Request structure for spawning subtasks.
 */
export interface SubtaskRequest {
  type: TaskType;
  description: string;
  inputs: Record<string, any>;
  template_hints?: string[];
  context_management?: Partial<ContextManagementConfig>;
  max_depth?: number;
  subtype?: AtomicTaskSubtype;
  file_paths?: string[];
}
```

## Function Templates

```typescript
/**
 * Function-style template definition.
 */
export interface FunctionTemplate {
  name: string;
  parameters: string[];
  returns?: string;
  body: TaskDefinition;
}

/**
 * Function call structure.
 */
export interface FunctionCall {
  templateName: string;
  arguments: any[];
}
```
