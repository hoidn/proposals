# Handler Component [Component:Handler:1.0]

## Overview

The Handler manages LLM interactions, resource tracking, and tool execution. It serves as the direct interface to LLM providers while enforcing system constraints.

## Core Responsibilities

1. **LLM Interaction Management**
   - Execute prompts through provider-specific adapters
   - Manage conversation history and message formatting
   - Track resource usage (turns, context window)

2. **Resource Enforcement**
   - Monitor turn counts and context window usage
   - Enforce limits with appropriate error handling
   - Generate warnings at specified thresholds (80%)

3. **Tool Execution**
   - Provide unified tool interface to LLMs
   - Execute direct tools synchronously
   - Transform subtask requests into CONTINUATION signals

4. **Session Management**
   - Maintain isolated execution environments for tasks
   - Track conversation state and history
   - Ensure clean resource release after execution

## Key Interfaces

- **executePrompt**: Submit prompts to the LLM and process responses
- **registerDirectTool**: Register synchronous tools for direct execution
- **registerSubtaskTool**: Register tools implemented via subtask continuation
- **addToolResponse**: Add tool responses to conversation history

For detailed specifications, see:
- [Interface:Handler:1.0] in `/components/handler/spec/interfaces.md`
- [Pattern:ResourceManagement:1.0] in `/system/architecture/patterns/resource-management.md`
- [Pattern:ToolInterface:1.0] in `/system/architecture/patterns/tool-interface.md`

For a comprehensive map of all system documentation, see [Documentation Guide](/system/docs-guide.md).
# Handler Component

## Overview

The Handler component is responsible for managing LLM interactions, resource tracking, and tool execution. It serves as the interface between the task system and LLM providers.

## Core Responsibilities

- Managing LLM provider interactions
- Tracking resource usage (turns, context window)
- Executing direct tools
- Managing conversation sessions
- Enforcing resource limits

For detailed implementation of key patterns, see:
- Resource tracking: [Implementation:ResourceTracking:1.0] in `/components/handler/impl/resource-tracking.md`
- Tool execution: [Implementation:DirectTools:1.0] in `/components/handler/impl/tool-execution.md`
- Script execution: [Implementation:ScriptExecution:1.0] in `/components/handler/impl/script-execution.md`

## Core Interface

```typescript
interface IHandler {
  executePrompt(systemPrompt: string, userPrompt: string): Promise<TaskResult>;
  executeScript(command: string, input: string, timeout?: number): Promise<ScriptResult>;
  registerDirectTool(name: string, handler: Function): void;
  registerSubtaskTool(name: string, templateHints: string[]): void;
  addToolResponse(toolName: string, response: string): void;
  getResourceMetrics(): ResourceMetrics;
}
```

## Session Management

The Handler maintains a session for each task execution, tracking:
- Message history
- Turn counts
- Context window usage
- Resource metrics

## Tool Execution

The Handler supports two types of tools:
- Direct tools: Executed synchronously by the Handler
- Subtask tools: Implemented via CONTINUATION mechanism

## Resource Management

The Handler enforces strict resource limits:
- Turn counts (incremented for assistant messages)
- Context window size (token-based calculation)
- Warning thresholds at 80% usage
- Hard limits with error handling

## Provider Integration

The Handler abstracts away provider-specific details:
- Standardized payload construction
- Provider-agnostic interface
- Consistent error handling
- Resource tracking across providers

## Error Handling

The Handler surfaces errors with detailed metrics:
- Resource exhaustion errors
- Tool execution errors
- Provider errors
- Context overflow errors

## Usage

```typescript
// Create a handler
const handler = new Handler({
  maxTurns: 10,
  maxContextWindowFraction: 0.8,
  defaultModel: "claude-3-sonnet",
  systemPrompt: "You are a helpful assistant."
});

// Execute a prompt
const result = await handler.executePrompt(
  "You are a coding assistant.",
  "Help me write a function to calculate factorial."
);

// Register and use a direct tool
handler.registerDirectTool("readFile", async (path) => {
  return await fs.readFile(path, 'utf8');
});

// Execute a script
const scriptResult = await handler.executeScript(
  "python analyze.py",
  "input data",
  30 // timeout in seconds
);
```
