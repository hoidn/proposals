# Session Management Implementation

## Purpose

This document provides implementation details for the Handler session management, including conversation state tracking, payload construction, and error handling.

## Related Documents

- [Pattern:ResourceManagement:1.0](../../../system/architecture/patterns/resource-management.md)
- [Handler Types](../spec/types.md)
- [Handler Behaviors](../spec/behaviors.md)

## Session Management Strategy

```typescript
class HandlerSession {
  private systemPrompt: string;
  private messages: Message[] = [];
  private turnCounter: TurnCounter;
  private contextManager: ContextManager;
  private tools: Map<string, ToolDefinition> = new Map();
  private isActive: boolean = true;
  
  constructor(config: HandlerConfig) {
    this.systemPrompt = config.systemPrompt;
    this.turnCounter = new TurnCounter(config.maxTurns);
    this.contextManager = new ContextManager(
      config.maxContextWindowFraction,
      config.provider,
      config.defaultModel
    );
    
    // Register standard tools
    this.registerStandardTools();
  }
  
  addUserMessage(content: string): void {
    if (!this.isActive) {
      throw new Error("Session is no longer active");
    }
    
    const message = {
      role: "user",
      content,
      timestamp: new Date()
    };
    
    this.messages.push(message);
    this.contextManager.addContent(content);
  }
  
  addAssistantMessage(content: string): void {
    if (!this.isActive) {
      throw new Error("Session is no longer active");
    }
    
    const message = {
      role: "assistant",
      content,
      timestamp: new Date()
    };
    
    this.messages.push(message);
    this.contextManager.addContent(content);
    this.turnCounter.increment();
  }
  
  addToolResponse(toolName: string, content: string): void {
    if (!this.isActive) {
      throw new Error("Session is no longer active");
    }
    
    const message = {
      role: "tool",
      toolName,
      content,
      timestamp: new Date()
    };
    
    this.messages.push(message);
    this.contextManager.addContent(content);
    // Tool responses don't increment turn counter
  }
  
  registerTool(tool: ToolDefinition): void {
    if (this.tools.has(tool.name)) {
      throw new Error(`Tool '${tool.name}' is already registered`);
    }
    
    this.tools.set(tool.name, tool);
  }
  
  cleanup(): void {
    // Log final resource usage
    const metrics = this.getResourceMetrics();
    console.log("Session cleanup - Final metrics:", metrics);
    
    // Clear message history
    this.messages = [];
    
    // Mark session as inactive
    this.isActive = false;
  }
  
  getResourceMetrics(): ResourceMetrics {
    return {
      turns: this.turnCounter.getMetrics(),
      context: this.contextManager.getMetrics()
    };
  }
  
  private registerStandardTools(): void {
    // Register standard tools like user input request
    // ...
  }
}
```

## Payload Construction

```typescript
class HandlerSession {
  // Other methods...
  
  constructPayload(taskPrompt: string): HandlerPayload {
    if (!this.isActive) {
      throw new Error("Session is no longer active");
    }
    
    // Check resource limits before constructing payload
    const metrics = this.getResourceMetrics();
    if (metrics.turns.used >= metrics.turns.limit) {
      throw new ResourceExhaustionError('turns', metrics.turns);
    }
    
    // Estimate tokens for the new prompt
    this.contextManager.checkContentAddition(taskPrompt);
    
    return {
      systemPrompt: this.systemPrompt,
      messages: [
        ...this.messages,
        {
          role: "user",
          content: taskPrompt,
          timestamp: new Date()
        }
      ],
      context: this.context,
      tools: Array.from(this.tools.values()),
      metadata: {
        model: this.config.defaultModel,
        temperature: this.config.temperature,
        resourceUsage: metrics
      }
    };
  }
}
```

## Interactive Session Support

```typescript
class Handler implements IHandler {
  private session: HandlerSession;
  private onRequestInput?: (prompt: string) => Promise<string>;
  
  constructor(config: HandlerConfig) {
    this.session = new HandlerSession(config);
    
    // Register user input tool
    this.registerDirectTool("requestUserInput", this.handleUserInputRequest.bind(this));
  }
  
  setRequestInputCallback(callback: (prompt: string) => Promise<string>): void {
    this.onRequestInput = callback;
  }
  
  private async handleUserInputRequest(params: {prompt: string}): Promise<{userInput: string}> {
    if (!this.onRequestInput) {
      throw new Error("No input request handler registered");
    }
    
    try {
      const userInput = await this.onRequestInput(params.prompt);
      this.session.addUserMessage(userInput);
      
      return { userInput };
    } catch (error) {
      throw {
        type: 'TOOL_EXECUTION_ERROR',
        tool: 'requestUserInput',
        message: error.message,
        details: error
      };
    }
  }
}
```

## Error Propagation Design

```typescript
class Handler implements IHandler {
  // Other methods...
  
  async executePrompt(systemPrompt: string, taskPrompt: string): Promise<string> {
    try {
      // Construct payload
      const payload = this.session.constructPayload(taskPrompt);
      
      // Call LLM provider
      const response = await this.provider.generateResponse(payload);
      
      // Process response
      const processedResponse = this.processLLMResponse(response);
      
      // Add assistant message to session
      this.session.addAssistantMessage(processedResponse);
      
      return processedResponse;
    } catch (error) {
      // Handle resource exhaustion
      if (error.type === 'RESOURCE_EXHAUSTION') {
        // Clean up session
        this.session.cleanup();
        
        // Rethrow with complete metrics
        throw {
          type: 'RESOURCE_EXHAUSTION',
          resource: error.resource,
          message: `${error.resource} limit exceeded`,
          metrics: error.metrics
        };
      }
      
      // Handle other errors
      throw {
        type: 'EXECUTION_ERROR',
        message: error.message,
        details: error
      };
    }
  }
  
  private processLLMResponse(response: any): string {
    // Process provider-specific response format
    // Handle tool calls if present
    // ...
    
    return response.content;
  }
}
```

This implementation follows the principles outlined in [Pattern:ResourceManagement:1.0] and ensures proper session management, resource tracking, and error handling.
