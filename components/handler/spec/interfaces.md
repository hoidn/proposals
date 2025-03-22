# Handler Interfaces [Interface:Handler:1.0]

```typescript
/**
 * Primary Handler interface
 */
export interface Handler {
    /**
     * Execute a prompt with the LLM
     * Note: All template variables should be resolved before calling
     * 
     * @param systemPrompt - System-level instructions (fully resolved)
     * @param taskPrompt - Task-specific input (fully resolved)
     * @returns Promise resolving to TaskResult
     */
    executePrompt(
        systemPrompt: string,
        taskPrompt: string
    ): Promise<TaskResult>;

    /**
     * Register a direct tool that will be executed by the Handler
     * 
     * @param name - Unique tool name
     * @param handler - Function that implements the tool
     */
    registerDirectTool(name: string, handler: Function): void;

    /**
     * Register a subtask tool that will be implemented via CONTINUATION
     * 
     * @param name - Unique tool name
     * @param templateHints - Hints for template selection
     */
    registerSubtaskTool(name: string, templateHints: string[]): void;

    /**
     * Add a tool response to the session
     * Used for adding subtask results to parent tasks
     * 
     * @param toolName - Name of the tool that produced the response
     * @param response - The tool response content
     */
    addToolResponse(toolName: string, response: string): void;

    /**
     * Get current resource metrics
     * 
     * @returns ResourceMetrics object with current usage
     */
    getResourceMetrics(): ResourceMetrics;

    /**
     * Set callback for handling user input requests
     * 
     * @param callback - Function to call when user input is requested
     */
    onRequestInput(callback: (prompt: string) => Promise<string>): void;
}

/**
 * Session management interface
 */
export interface HandlerSession {
    /**
     * Add a user message to the conversation
     * 
     * @param content - Message content
     */
    addUserMessage(content: string): void;
    
    /**
     * Add an assistant message to the conversation
     * Increments turn counter
     * 
     * @param content - Message content
     */
    addAssistantMessage(content: string): void;
    
    /**
     * Add a tool response to the conversation
     * Does not increment turn counter
     * 
     * @param toolName - Name of tool that generated the response
     * @param content - Tool response content
     */
    addToolResponse(toolName: string, content: string): void;
    
    /**
     * Construct payload for LLM request
     * 
     * @returns HandlerPayload object
     */
    constructPayload(): HandlerPayload;
    
    /**
     * Get current resource metrics
     * 
     * @returns ResourceMetrics object with current usage
     */
    getResourceMetrics(): ResourceMetrics;
}
```

For other relevant interfaces, see:
- [Type:Handler:1.0] for handler-specific type definitions
- [Type:TaskSystem:TaskResult:1.0] for the TaskResult structure
- [Pattern:ToolInterface:1.0] for tool interface patterns
# Handler Internal Interfaces

## Purpose

This document defines the internal interfaces used within the Handler component. For public interfaces exposed to other components, see [Handler API Interfaces](../api/interfaces.md).

## Related Documents

- [Handler Types](./types.md)
- [Handler Behaviors](./behaviors.md)
- [Pattern:ResourceManagement:1.0](../../../system/architecture/patterns/resource-management.md)

## HandlerSession Interface

```typescript
/**
 * Handler session interface for managing conversation state
 */
interface HandlerSession {
  /**
   * Add a user message to the session
   * @param content - Message content
   */
  addUserMessage(content: string): void;
  
  /**
   * Add an assistant message to the session
   * Increments turn counter
   * @param content - Message content
   */
  addAssistantMessage(content: string): void;
  
  /**
   * Add a tool response to the session
   * Used for adding subtask results as tool responses
   * @param toolName - Name of the tool that produced the response
   * @param content - Tool response content
   */
  addToolResponse(toolName: string, content: string): void;
  
  /**
   * Register a tool with the session
   * @param tool - Tool definition
   */
  registerTool(tool: ToolDefinition): void;
  
  /**
   * Construct a payload for the LLM with current session state
   * @param taskPrompt - Task prompt to include in the payload
   * @returns HandlerPayload ready for LLM submission
   */
  constructPayload(taskPrompt: string): HandlerPayload;
  
  /**
   * Get resource metrics for the session
   * @returns Current resource usage metrics
   */
  getResourceMetrics(): ResourceMetrics;
  
  /**
   * Clean up session resources
   */
  cleanup(): void;
}
```

## TurnCounter Interface

```typescript
/**
 * Turn counter interface for tracking conversation turns
 */
interface TurnCounter {
  /**
   * Increment the turn counter
   * @throws ResourceExhaustionError if limit is exceeded
   */
  increment(): void;
  
  /**
   * Get current turn metrics
   * @returns Turn usage metrics
   */
  getMetrics(): ResourceMetrics['turns'];
}
```

## ContextManager Interface

```typescript
/**
 * Context manager interface for tracking context window usage
 */
interface ContextManager {
  /**
   * Add content to the context window
   * @param content - Content to add
   * @throws ResourceExhaustionError if limit is exceeded
   */
  addContent(content: string): void;
  
  /**
   * Check if adding content would exceed limits
   * @param content - Content to check
   * @throws ResourceExhaustionError if limit would be exceeded
   */
  checkContentAddition(content: string): void;
  
  /**
   * Get current context window metrics
   * @returns Context usage metrics
   */
  getMetrics(): ResourceMetrics['context'];
  
  /**
   * Get current context for LLM payload
   * @returns Formatted context string
   */
  getCurrentContext(): string;
}
```

## ProviderAdapter Interface

```typescript
/**
 * Provider adapter interface for LLM-specific implementations
 */
interface ProviderAdapter {
  /**
   * Generate a response from the LLM
   * @param payload - Handler payload
   * @returns LLM response
   */
  generateResponse(payload: HandlerPayload): Promise<LLMResponse>;
  
  /**
   * Estimate token count for text
   * @param text - Text to estimate
   * @returns Estimated token count
   */
  estimateTokens(text: string): number;
  
  /**
   * Get context window limit for model
   * @param model - Model identifier
   * @returns Maximum context window size in tokens
   */
  getModelContextLimit(model: string): number;
  
  /**
   * Transform tool definitions to provider format
   * @param tools - Tool definitions
   * @returns Provider-specific tool format
   */
  transformTools(tools: ToolDefinition[]): any;
}
```

## ToolHandler Interface

```typescript
/**
 * Tool handler interface for executing tools
 */
interface ToolHandler {
  /**
   * Execute a tool
   * @param name - Tool name
   * @param params - Tool parameters
   * @returns Tool execution result
   */
  executeTool(name: string, params: any): Promise<any>;
  
  /**
   * Register a tool handler
   * @param name - Tool name
   * @param handler - Tool implementation function
   */
  registerToolHandler(name: string, handler: Function): void;
}
```

These interfaces define the internal structure of the Handler component and how its various parts interact. They are not exposed directly to other components but are used to implement the public interfaces defined in [Handler API Interfaces](../api/interfaces.md).
