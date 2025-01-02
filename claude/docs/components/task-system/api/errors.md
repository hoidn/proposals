# Task System Error Types

## Error Type Definitions
```typescript
type TaskError = 
  | { 
      type: 'RESOURCE_EXHAUSTION';
      resource: 'turns' | 'context' | 'output';
      message: string;
      metrics?: { used: number; limit: number; };
    }
  | { 
      type: 'INVALID_OUTPUT';
      message: string;
      violations?: string[];
    }
  | { 
      type: 'VALIDATION_ERROR';
      message: string;
      path?: string;
      invalidModel?: boolean;
    }
  | { 
      type: 'XML_PARSE_ERROR';
      message: string;
      location?: string;
    };
```

## Error Detection and Response

### Resource Exhaustion
- Handler detects limit violations
- Immediate task termination
- Surfaces through standard error type
- Resource accounting completion
- Clean Handler termination
- No retry attempts

### Invalid Output
- Structural validation failure
- Format validation errors
- No semantic validation
- Preserves partial outputs when useful
- Returns both output and notes sections
- May trigger reparse task

### Progress Failure
- Handler detects stalled execution
- Task-specific progress indicators
- No internal progress tracking
- May trigger alternative approach
- State preserved in error response
- No automatic retry

### XML Validation
- Immediate failure on invalid structure
- No warning collection
- Clear error messages
- Location information when available
- May trigger reparse if not disabled

## Error Response
### Error Surfacing
- Uses standard error type system
- Includes relevant task notes
- Preserves partial outputs when useful
- Includes resource metrics where applicable
- Clear error messages and locations

### Handler Cleanup
- Clean termination of LLM session
- Resource accounting completion
- No state preservation
- Context window cleanup
- Turn counter finalization

### Recovery Delegation
- No retry attempts
- No state maintenance
- Delegates to evaluator
- Provides complete error context
- Includes notes for recovery guidance