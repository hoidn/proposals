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

Each task type can specify its context management requirements through XML configuration:

```xml
<task>
    <description>Task description</description>
    <context_management>
        <inherit_context>none|full|subset</inherit_context>
        <accumulate_data>true|false</accumulate_data>
        <accumulation_format>notes_only|full_output</accumulation_format>
    </context_management>
    <inputs>
        <input name="input_name" from="source_var"/>
    </inputs>
</task>
```

## Integration and Dependencies

The Task System integrates with several core components. It uses the Memory System for context access and management, Handler Tools for file and system operations, the Compiler for task parsing and transformation, and the Evaluator for error recovery and task decomposition. These integrations enable comprehensive task execution while maintaining clean component boundaries.

## Usage

Here's how the Task System would be instantiated:

```typescript
const taskSystem = new TaskSystem({
    maxTurns: 10,
    maxContextWindowFraction: 0.8,
    systemPrompt: "Default system prompt"
});

// Execute a task
const result = await taskSystem.executeTask(
    "analyze data",
    memorySystem
);

// Validate a template
const validation = taskSystem.validateTemplate({
    taskPrompt: "<task>...</task>",
    systemPrompt: "System context",
    model: "claude-3-sonnet",
    isManualXML: false
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
