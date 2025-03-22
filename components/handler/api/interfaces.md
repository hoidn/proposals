# Handler API Interfaces

## Purpose

This document defines the public interfaces exposed by the Handler component for use by other system components.

## Related Documents

- [Pattern:ToolInterface:1.0](../../../system/architecture/patterns/tool-interface.md)
- [Contract:LLMInteraction:1.0](../../../system/contracts/protocols.md)
- [Handler Types](../spec/types.md)

## Handler Interface

```typescript
/**
 * LLM interaction interface
 * Uses [Type:TaskSystem:ResourceMetrics:1.0], [Type:TaskSystem:ResourceLimits:1.0]
 */
interface Handler {
    /**
     * Execute a prompt with the LLM
     * Note: All template substitution should be performed by the Evaluator before calling
     * @param systemPrompt - System-level context and instructions (fully resolved)
     * @param taskPrompt - Task-specific input (fully resolved)
     * @returns Promise resolving to LLM response
     */
    executePrompt(
        systemPrompt: string,
        taskPrompt: string
    ): Promise<string>;

    /**
     * Register a direct tool that will be executed by the Handler
     * @param name - Unique tool name
     * @param handler - Function that implements the tool
     */
    registerDirectTool(name: string, handler: Function): void;

    /**
     * Register a subtask tool that will be implemented via CONTINUATION
     * @param name - Unique tool name
     * @param templateHints - Hints for template selection
     */
    registerSubtaskTool(name: string, templateHints: string[]): void;

    /**
     * Add a tool response to the session
     * Used for adding subtask results to parent tasks
     * @param toolName - Name of the tool that produced the response
     * @param response - The tool response content
     */
    addToolResponse(toolName: string, response: string): void;

    /**
     * Execute a script with input and timeout
     * @param command - The command to execute
     * @param input - Input to provide to the script
     * @param timeout - Maximum execution time in seconds
     * @returns Promise resolving to script execution result
     */
    executeScript(
        command: string,
        input: string,
        timeout?: number
    ): Promise<ScriptResult>;

    /**
     * Callback for handling agent input requests
     * @param agentRequest - The agent's request for user input
     * @returns Promise resolving to user's input
     */
    onRequestInput: (agentRequest: string) => Promise<string>;
}
```

## HandlerPayload Interface

```typescript
/**
 * Standardized payload structure for LLM interactions
 */
interface HandlerPayload {
  systemPrompt: string;
  messages: Array<{
    role: "user" | "assistant" | "system";
    content: string;
    timestamp?: Date;
  }>;
  context?: string;        // Context from Memory System
  tools?: ToolDefinition[]; // Available tools
  metadata?: {
    model: string;
    temperature?: number;
    maxTokens?: number;
    resourceUsage: ResourceMetrics;
  };
}
```

## LLM Interaction Protocol

The Handler-LLM interaction follows a standardized protocol:

1. The Task System creates a Handler instance with configuration
2. The Handler creates a HandlerSession to manage conversation state
3. The Evaluator ensures all placeholders are substituted
4. The Handler constructs a HandlerPayload via session.constructPayload()
5. Provider-specific adapters transform the payload to appropriate formats
6. LLM response is processed via handler.processLLMResponse()
7. Tool calls (including user input requests) are handled
8. Session state is updated with new messages
9. Resource usage is tracked and limits enforced

This standardized protocol ensures consistent handling of LLM interactions across different providers while maintaining proper conversation tracking and resource management.
