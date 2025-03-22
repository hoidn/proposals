# Task System Component

## Overview

The Task System orchestrates LLM task execution through structured XML templates and handlers. It proovides template-based task definition, resource tracking, and an XML-based interface with the LLM.

## Core Architecture

The system manages task execution through isolated Handler instances, with one Handler per task to enforce resource limits and manage LLM interactions. 

Task definitions use an XML-based template system that supports both manual and LLM-generated structures. 

## Core Interface

```typescript
interface TaskSystem {
    executeTask(
        task: string,
        context: MemorySystem,
        taskType?: TaskType
    ): Promise<TaskResult>;

    validateTemplate(template: TaskTemplate): boolean;
    
    findMatchingTasks(
        input: string,
        context: MemorySystem
    ): Promise<Array<{
        template: TaskTemplate;
        score: number;
        taskType: TaskType;
    }>>;
}
```

## Task Types and Execution

The system supports several task types for different execution patterns. Atomic tasks provide direct LLM execution with resource tracking and output validation. Sequential tasks enable ordered execution with context management between steps. Reduce tasks handle iterative data processing with accumulator management. Script tasks support external command execution with output capture and evaluation flow integration.

For all task types, the Evaluator is responsible for resolving template variables (e.g., `{{variable_name}}` placeholders) before passing fully-resolved content to the Handler for execution. This ensures consistent variable resolution across all task types and execution paths.

All task types (atomic, sequential, reduce, script) can be defined as templates and functions in the TaskLibrary. However, template matching (the process of selecting an appropriate template based on a natural language description) applies only to atomic task templates. Composite tasks can be defined directly, defined as reusable templates, or assembled from matched atomic task templates.

Each task type can specify its context management requirements and explicit file paths through XML configuration:

```xml
<task>
    <description>Task description</description>
    <context_management>
        <inherit_context>none|full|subset</inherit_context>
        <accumulate_data>true|false</accumulate_data>
        <accumulation_format>notes_only|full_output</accumulation_format>
        <fresh_context>enabled|disabled</fresh_context>
    </context_management>
    <file_paths>
        <path>./src/main.py</path>
        <path>/absolute/path/file.txt</path>
    </file_paths>
    <inputs>
        <input name="input_name" from="source_var"/>
    </inputs>
</task>
```

### Function Templates

The system supports function-based templates with explicit parameter declarations:

```xml
<template name="analyze_data" params="dataset,config">
  <task>
    <description>Analyze {{dataset}} using {{config}}</description>
  </task>
</template>
```

These templates are called with positional arguments:

```xml
<call template="analyze_data">
  <arg>weather_data</arg>
  <arg>standard_config</arg>
</call>
```

Key characteristics:

- Templates can only access explicitly passed parameters
- Arguments are evaluated in the caller's environment
- Function calls create a new lexical scope
- Template registration happens automatically during parsing

## Delegation Mechanisms

The system exposes a unified tool interface with two implementation approaches:

1. **Unified Tool Interface**: What the LLM sees and interacts with
   - Consistent invocation patterns for all operations
   - Standardized parameter schemas
   - Unified error handling

2. **Implementation Mechanisms**: How tools are executed
   - **Direct Implementation**: Synchronous Handler execution for simple operations
   - **Subtask Implementation**: Asynchronous execution via CONTINUATION

See [Pattern:ToolInterface:1.0] for complete details on this approach.

## Integration and Dependencies

The Task System integrates with several core components. It uses the Memory System for context access and management, Handler Tools for file and system operations, the Compiler for task parsing and transformation, and the Evaluator for error recovery and task decomposition. These integrations enable comprehensive task execution while maintaining clean component boundaries.

## Usage

Here's how the Task System would be instantiated:

```typescript
const taskSystem = new TaskSystem({
    provider: "anthropic",  // Default provider
    maxTurns: 10,
    maxContextWindowFraction: 0.8,
    systemPrompt: "Default system prompt"
});

// Execute a task
const result = await taskSystem.executeTask(
    "analyze data",
    memorySystem
);

// Execute with provider override
const resultWithOverride = await taskSystem.executeTask(
    "analyze data",
    memorySystem,
    { provider: "openai" }  // Override for this task
);

// Execute task with specific file paths
const resultWithFiles = await taskSystem.executeTask(
    "<task type='atomic'><description>Analyze files</description><file_paths><path>./src/main.py</path></file_paths></task>",
    memorySystem
);

// Validate a template
const validation = taskSystem.validateTemplate({
    taskPrompt: "<task>...</task>",
    systemPrompt: "System context",
    model: "claude-3-sonnet",
    isManualXML: false
});

// Register a template
const templateResult = await taskSystem.registerTemplate({
  name: "process_data",
  parameters: ["input_file", "options"],
  body: {
    type: "atomic",
    description: "Process {{input_file}} with options {{options}}",
    // Additional task properties
  }
});

// Call a template with arguments
const callResult = await taskSystem.executeCall({
  templateName: "process_data",
  arguments: ["data.csv", {format: "standard"}]
});
```

## Error Handling

The system handles several error types during execution, including resource exhaustion (for turns, context, or output), invalid output structure, XML parsing or validation errors, and general task execution failures. Each error type includes relevant context and metrics to aid in recovery and debugging. Errors will be surfaced to the Evaluator, which will use them for control flow.

## Resource Management

Resource management follows strict constraints with fixed context window sizes and limited turn counts. The system ensures clean resource release after task execution and prevents cross-Handler resource sharing. Handler configuration controls these limits:

```typescript
interface HandlerConfig {
    maxTurns: number;
    maxContextWindowFraction: number;
    defaultModel?: string;
    systemPrompt: string;
}
```

For detailed implementation specifications and patterns, refer to the component-level documentation and system contracts.
