# Resource Tracking Implementation [Implementation:ResourceTracking:1.0]

## Purpose

This document provides implementation details for the Resource Management Pattern defined in [Pattern:ResourceManagement:1.0].

## Related Documents

- [Pattern:ResourceManagement:1.0](../../../system/architecture/patterns/resource-management.md)
- [Handler Types](../spec/types.md)
- [Handler Behaviors](../spec/behaviors.md)

## Turn Counter Implementation

```typescript
class TurnCounter {
  private metrics: ResourceMetrics['turns'];
  
  constructor(limit: number) {
    this.metrics = {
      used: 0,
      limit,
      lastTurnAt: new Date()
    };
  }
  
  increment(): void {
    if (this.metrics.used >= this.metrics.limit) {
      throw new ResourceExhaustionError('turns', this.metrics);
    }
    this.metrics.used++;
    this.metrics.lastTurnAt = new Date();
  }
  
  getMetrics(): ResourceMetrics['turns'] {
    return { ...this.metrics };
  }
}
```

## Context Window Management [Implementation:ContextWindow:1.0]

```typescript
class ContextManager {
  private metrics: ResourceMetrics['context'];
  private provider: ProviderAdapter;
  
  constructor(maxFraction: number, provider: ProviderAdapter, model: string) {
    const modelLimit = provider.getModelContextLimit(model);
    this.metrics = {
      used: 0,
      limit: Math.floor(modelLimit * maxFraction),
      peakUsage: 0
    };
    this.provider = provider;
  }
  
  addContent(content: string): void {
    const tokens = this.estimateTokens(content);
    
    if (this.metrics.used + tokens > this.metrics.limit) {
      throw new ResourceExhaustionError('context', this.metrics);
    }
    
    this.metrics.used += tokens;
    this.metrics.peakUsage = Math.max(this.metrics.peakUsage, this.metrics.used);
    
    if (this.metrics.used >= this.metrics.limit * 0.8) {
      this.emitWarning('RESOURCE_WARNING', 'context', this.metrics);
    }
  }
  
  private estimateTokens(text: string): number {
    return this.provider.estimateTokens(text);
  }
  
  getMetrics(): ResourceMetrics['context'] {
    return { ...this.metrics };
  }
}
```

## Resource Cleanup Implementation [Implementation:ResourceCleanup:1.0]

```typescript
class HandlerSession {
  // Other properties and methods...
  
  cleanup(): void {
    // Complete resource accounting
    const finalMetrics = {
      turns: this.turnCounter.getMetrics(),
      context: this.contextManager.getMetrics()
    };
    
    // Log final resource usage
    this.logResourceUsage(finalMetrics);
    
    // Clear message history
    this.messages = [];
    
    // Clear any cached data
    this.cachedPayload = null;
    
    // Signal completion
    this.isActive = false;
  }
}
```

## Integration with HandlerSession

The HandlerSession integrates both tracking mechanisms:

```typescript
class HandlerSession {
  private systemPrompt: string;
  private messages: Message[] = [];
  private turnCounter: TurnCounter;
  private contextManager: ContextManager;
  private config: HandlerConfig;
  
  constructor(config: HandlerConfig) {
    this.config = config;
    this.systemPrompt = config.systemPrompt;
    this.turnCounter = new TurnCounter({
      limit: config.maxTurns,
      used: 0,
      lastTurnAt: new Date()
    });
    this.contextManager = new ContextManager({
      limit: Math.floor(config.maxContextWindowFraction * this.getModelMaxTokens(config.defaultModel)),
      used: 0,
      peakUsage: 0
    });
  }
  
  addUserMessage(content: string): void {
    this.messages.push({ 
      role: "user", 
      content, 
      timestamp: new Date() 
    });
    this.contextManager.addContent(content);
    // No turn increment for user messages
  }
  
  addAssistantMessage(content: string): void {
    this.messages.push({ 
      role: "assistant", 
      content, 
      timestamp: new Date() 
    });
    this.contextManager.addContent(content);
    this.turnCounter.increment(); // Increment turn counter for assistant responses
  }
  
  /**
   * Constructs a payload for the LLM using fully resolved content
   * @param task The resolved task template with all variables already substituted
   * @returns A complete HandlerPayload ready for LLM submission
   */
  constructPayload(task: TaskTemplate): HandlerPayload {
    // Note: All template variables should already be resolved by the Evaluator
    return {
      systemPrompt: this.systemPrompt,
      messages: [...this.messages, { 
        role: "user", 
        content: task.taskPrompt, // Already fully resolved
        timestamp: new Date()
      }],
      context: this.contextManager.getCurrentContext(),
      tools: this.getAvailableTools(),
      metadata: {
        model: this.config.defaultModel,
        resourceUsage: this.getResourceMetrics()
      }
    };
  }
  
  getResourceMetrics(): ResourceMetrics {
    return {
      turns: this.turnCounter.getMetrics(),
      context: this.contextManager.getMetrics()
    };
  }
  
  private getModelMaxTokens(model: string): number {
    // Return model-specific token limits
    const modelTokenLimits = {
      "claude-3-opus": 200000,
      "claude-3-sonnet": 180000,
      "claude-3-haiku": 150000,
      "gpt-4": 128000,
      "gpt-4-turbo": 128000,
      "gpt-3.5-turbo": 16000
    };
    
    return modelTokenLimits[model] || 100000; // Default fallback
  }
  
  private getAvailableTools(): ToolDefinition[] {
    // Return registered tools
    return this.registeredTools;
  }
}
```

The implementation follows these principles from [Pattern:ResourceManagement:1.0]:
- One Handler per task execution
- Isolated resource tracking per session
- Clear limit enforcement
- Warning thresholds at 80%
- Clean termination on exhaustion
# Resource Tracking Implementation [Implementation:ResourceTracking:1.0]

This document provides implementation details for the Resource Management Pattern defined in [Pattern:ResourceManagement:1.0].

## Turn Counter Implementation

```typescript
class TurnCounter {
  private metrics: ResourceMetrics['turns'];
  
  constructor(limit: number) {
    this.metrics = {
      used: 0,
      limit,
      lastTurnAt: new Date()
    };
  }
  
  increment(): void {
    if (this.metrics.used >= this.metrics.limit) {
      throw new ResourceExhaustionError('turns', this.metrics);
    }
    this.metrics.used++;
    this.metrics.lastTurnAt = new Date();
  }
  
  getMetrics(): ResourceMetrics['turns'] {
    return { ...this.metrics };
  }
}
```

## Context Window Management [Implementation:ContextWindow:1.0]

```typescript
class ContextManager {
  private metrics: ResourceMetrics['context'];
  private provider: ProviderAdapter;
  
  constructor(maxFraction: number, provider: ProviderAdapter, model: string) {
    const modelLimit = provider.getModelContextLimit(model);
    this.metrics = {
      used: 0,
      limit: Math.floor(modelLimit * maxFraction)
    };
    this.provider = provider;
  }
  
  addContent(content: string): void {
    const tokens = this.estimateTokens(content);
    
    if (this.metrics.used + tokens > this.metrics.limit) {
      throw new ResourceExhaustionError('context', this.metrics);
    }
    
    this.metrics.used += tokens;
    
    if (this.metrics.used >= this.metrics.limit * 0.8) {
      this.emitWarning('RESOURCE_WARNING', 'context', this.metrics);
    }
  }
  
  private estimateTokens(text: string): number {
    return this.provider.estimateTokens(text);
  }
  
  getMetrics(): ResourceMetrics['context'] {
    return { ...this.metrics };
  }
}
```

## Resource Cleanup Implementation [Implementation:ResourceCleanup:1.0]

```typescript
class HandlerSession {
  // Other properties and methods...
  
  cleanup(): void {
    // Complete resource accounting
    const finalMetrics = {
      turns: this.turnCounter.getMetrics(),
      context: this.contextManager.getMetrics()
    };
    
    // Log final resource usage
    this.logResourceUsage(finalMetrics);
    
    // Clear message history
    this.messages = [];
    
    // Clear any cached data
    this.cachedPayload = null;
    
    // Signal completion
    this.isActive = false;
  }
}
```

The implementation follows these principles from [Pattern:ResourceManagement:1.0]:
- One Handler per task execution
- Isolated resource tracking per session
- Clear limit enforcement
- Warning thresholds at 80%
- Clean termination on exhaustion
