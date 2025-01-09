# Resource Management Implementation

## Core Principles
- No resource usage prediction
- No task decomposition optimization
- Handler-based resource tracking
- Clear resource ownership boundaries

## Turn Counter Management

### Implementation Details
- Per-Handler turn tracking
- Atomic increment operations
- Strict limit enforcement
- No cross-Handler pooling

### Turn Management Rules
- Turn tracking owned by Handler instance
- Turn limit passed during Handler initialization
- Interactive sessions count against turn limits

### Usage Tracking
```typescript
// Using canonical ResourceMetrics definition from spec/types.md
// See [Type:ResourceMetrics:1.0]

class TurnCounter {
  private metrics: ResourceMetrics['turns'];
  
  increment(): void {
    if (this.metrics.used >= this.metrics.limit) {
      throw new ResourceExhaustionError('turns');
    }
    this.metrics.used++;
    this.metrics.lastTurnAt = new Date();
  }
}
```

### Configuration
- Default turn limits from config
- Per-task limit overrides
- Warning at 80% threshold
- Error at limit reached

## Context Window Management

### Size Tracking
- Token-based calculation
- Window size monitoring
- Fraction-based limits
- No content optimization

### Implementation
```typescript
// Using canonical ResourceMetrics definition from spec/types.md
// See [Type:ResourceMetrics:1.0]

class ContextManager {
  private metrics: ResourceMetrics['context'];
  
  addContent(content: string): void {
    const tokens = this.countTokens(content);
    if (this.metrics.used + tokens > this.metrics.limit) {
      throw new ResourceExhaustionError('context');
    }
    this.metrics.used += tokens;
    this.metrics.peakUsage = Math.max(this.metrics.peakUsage, this.metrics.used);
  }
}
```

### Monitoring
- Continuous token tracking
- Peak usage recording
- Threshold warnings
- Limit enforcement

## Resource Cleanup

### Handler Termination
- Clean session shutdown
- Resource accounting completion
- Metric collection
- No state preservation

### Memory Management
- Context cleanup
- Reference clearing
- Memory release
- State invalidation

## Integration Points

### Handler Integration
- Resource initialization
- Usage monitoring
- Limit enforcement
- Cleanup coordination

### Memory System
- Read-only access
- No state maintenance
- Direct interface usage
- Context boundaries

### Error Handling
- Resource exhaustion detection
- Clean termination
- Metric reporting
- State cleanup
