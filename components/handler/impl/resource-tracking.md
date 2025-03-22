# Resource Tracking Implementation

## Turn Counting

```typescript
class TurnCounter {
  private used: number = 0;
  private limit: number;
  private lastTurnAt?: Date;
  
  constructor(limit: number) {
    this.limit = limit;
  }
  
  increment(): void {
    if (this.used >= this.limit) {
      throw new ResourceExhaustionError('turns', {
        used: this.used,
        limit: this.limit
      });
    }
    
    this.used++;
    this.lastTurnAt = new Date();
  }
  
  getMetrics(): TurnMetrics {
    return {
      used: this.used,
      limit: this.limit,
      lastTurnAt: this.lastTurnAt
    };
  }
}
```

## Context Window Management

```typescript
class ContextManager {
  private used: number = 0;
  private limit: number;
  private provider: ProviderAdapter;
  
  constructor(maxFraction: number, provider: ProviderAdapter, model: string) {
    const modelLimit = provider.getModelContextLimit(model);
    this.limit = Math.floor(modelLimit * maxFraction);
    this.provider = provider;
  }
  
  addContent(content: string): void {
    const tokens = this.provider.estimateTokens(content);
    
    if (this.used + tokens > this.limit) {
      throw new ResourceExhaustionError('context', {
        used: this.used,
        limit: this.limit
      });
    }
    
    this.used += tokens;
    
    if (this.used >= this.limit * 0.8) {
      // Emit warning at 80% usage
    }
  }
  
  getMetrics(): ContextMetrics {
    return {
      used: this.used,
      limit: this.limit
    };
  }
}
```

## Integration with HandlerSession

The HandlerSession integrates both tracking mechanisms:

1. **Turn Tracking**
   - Incremented in addAssistantMessage method
   - Not affected by user messages or tool responses
   - Checked before each LLM call

2. **Context Tracking**
   - Updated for all messages regardless of type
   - Includes system prompt and context
   - Checked before constructing payload

See [Pattern:ResourceManagement:1.0] for underlying principles.
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
