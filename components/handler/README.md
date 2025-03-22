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
# Handler Component [Component:Handler:1.0]

## Purpose

The Handler component is responsible for LLM interface management and resource tracking. It serves as the bridge between the Task System and various LLM providers, ensuring consistent interaction patterns and resource usage monitoring.

## Related Documents

- [Pattern:ResourceManagement:1.0](../../system/architecture/patterns/resource-management.md)
- [Pattern:ToolInterface:1.0](../../system/architecture/patterns/tool-interface.md)
- [Contract:LLMInteraction:1.0](../../system/contracts/protocols.md)

## Component Overview

The Handler component:

- Performs ALL file I/O operations (reading, writing, deletion)
- Supports multiple LLM providers with appropriate tool configurations
- Abstracts provider-specific implementation details while maintaining consistent capabilities
- Manages resource usage tracking (turns, tokens)
- Handles LLM interactions and session management
- Works with fully resolved content (no template variable substitution)

## Directory Structure

- `api/`: Public interfaces for external components
- `impl/`: Implementation details for resource tracking, tool execution, etc.
- `spec/`: Specifications for behaviors, interfaces, and types

## Integration Points

- **Task System**: Creates Handler instances with configuration
- **Evaluator**: Provides fully resolved content for LLM interaction
- **Memory System**: Provides context that Handler presents to LLMs

## Resource Management

The Handler implements resource tracking according to [Pattern:ResourceManagement:1.0]:

- One Handler per task execution
- Isolated resource tracking per session
- Clear limit enforcement
- Warning thresholds at 80%
- Clean termination on exhaustion

For implementation details, see [Implementation:ResourceTracking:1.0](./impl/resource-tracking.md).

## Tool Interface

The Handler provides a unified tool interface according to [Pattern:ToolInterface:1.0]:

- Direct tools for synchronous operations
- User input request tools for interactive sessions
- Tool response handling for subtask results

For implementation details, see [Implementation:DirectTools:1.0](./impl/tool-execution.md) and [Implementation:UserInputTools:1.0](./impl/tool-execution.md).

## Script Execution

The Handler supports script execution for the Director-Evaluator pattern:

- Command execution with input/output handling
- Timeout enforcement
- Error handling and result formatting

For implementation details, see [Implementation:ScriptExecution:1.0](./impl/script-execution.md).
