# Handler Types [Type:Handler:1.0]

```typescript
/**
 * Handler configuration parameters
 */
export interface HandlerConfig {
    maxTurns: number;             // Maximum turns allowed for this Handler
    maxContextWindowFraction: number; // Fraction of model's context window to use
    defaultModel?: string;        // Default LLM model to use
    systemPrompt: string;         // Default system prompt
}

/**
 * Payload sent to LLM provider
 */
export interface HandlerPayload {
    systemPrompt: string;         // System-level instructions
    messages: Array<{             // Conversation history
        role: "user" | "assistant" | "system";
        content: string;
        timestamp?: Date;
    }>;
    context?: string;             // Context from Memory System
    tools?: ToolDefinition[];     // Available tools
    metadata?: {
        model: string;
        temperature?: number;
        maxTokens?: number;
        resourceUsage: ResourceMetrics;
    };
}

/**
 * Tool definition for LLM
 */
export interface ToolDefinition {
    name: string;
    description: string;
    parameters: {
        type: "object";
        properties: Record<string, {
            type: string;
            description: string;
        }>;
        required?: string[];
    };
}

/**
 * Resource metrics tracked by Handler
 */
export interface ResourceMetrics {
    turns: {
        used: number;
        limit: number;
        lastTurnAt: Date;
    };
    context: {
        used: number;
        limit: number;
    };
}
```

For related resource management patterns, see [Pattern:ResourceManagement:1.0].
# Handler Types

## Purpose

This document defines the type definitions used by the Handler component.

## Related Documents

- [Handler Interfaces](./interfaces.md)
- [Handler Behaviors](./behaviors.md)
- [Pattern:ResourceManagement:1.0](../../../system/architecture/patterns/resource-management.md)

## Configuration Types

```typescript
/**
 * Handler configuration
 */
interface HandlerConfig {
  /**
   * Maximum number of turns allowed in a conversation
   */
  maxTurns: number;
  
  /**
   * Maximum fraction of model's context window to use
   * Value between 0 and 1, typically 0.8 or 0.9
   */
  maxContextWindowFraction: number;
  
  /**
   * Default model to use if not specified in task
   */
  defaultModel?: string;
  
  /**
   * System prompt to use for all conversations
   */
  systemPrompt: string;
  
  /**
   * Temperature setting for LLM (0-1)
   */
  temperature?: number;
  
  /**
   * Provider adapter for LLM-specific implementations
   */
  provider: ProviderAdapter;
}
```

## Message Types

```typescript
/**
 * Message role in conversation
 */
type MessageRole = "user" | "assistant" | "system" | "tool";

/**
 * Message in conversation history
 */
interface Message {
  /**
   * Role of the message sender
   */
  role: MessageRole;
  
  /**
   * Message content
   */
  content: string;
  
  /**
   * Timestamp when message was created
   */
  timestamp: Date;
  
  /**
   * Tool name if role is "tool"
   */
  toolName?: string;
}
```

## Resource Metrics Types

```typescript
/**
 * Resource metrics for tracking usage
 */
interface ResourceMetrics {
  /**
   * Turn usage metrics
   */
  turns: {
    /**
     * Number of turns used
     */
    used: number;
    
    /**
     * Maximum number of turns allowed
     */
    limit: number;
    
    /**
     * Timestamp of last turn
     */
    lastTurnAt: Date;
  };
  
  /**
   * Context window usage metrics
   */
  context: {
    /**
     * Number of tokens used
     */
    used: number;
    
    /**
     * Maximum number of tokens allowed
     */
    limit: number;
    
    /**
     * Peak token usage in this session
     */
    peakUsage: number;
  };
}
```

## Tool Types

```typescript
/**
 * Tool definition for LLM
 */
interface ToolDefinition {
  /**
   * Unique tool name
   */
  name: string;
  
  /**
   * Tool description for LLM
   */
  description: string;
  
  /**
   * Tool parameters schema
   */
  parameters: {
    /**
     * Parameter type (typically "object")
     */
    type: string;
    
    /**
     * Parameter properties
     */
    properties: Record<string, {
      /**
       * Property type
       */
      type: string;
      
      /**
       * Property description
       */
      description: string;
      
      /**
       * Optional enum values
       */
      enum?: string[];
    }>;
    
    /**
     * Required properties
     */
    required: string[];
  };
}

/**
 * Tool call from LLM
 */
interface ToolCall {
  /**
   * Tool name
   */
  name: string;
  
  /**
   * Tool parameters
   */
  parameters: Record<string, any>;
}
```

## LLM Interaction Types

```typescript
/**
 * Handler payload for LLM request
 */
interface HandlerPayload {
  /**
   * System prompt
   */
  systemPrompt: string;
  
  /**
   * Conversation messages
   */
  messages: Message[];
  
  /**
   * Context from Memory System
   */
  context?: string;
  
  /**
   * Available tools
   */
  tools?: ToolDefinition[];
  
  /**
   * Request metadata
   */
  metadata?: {
    /**
     * Model identifier
     */
    model: string;
    
    /**
     * Temperature setting (0-1)
     */
    temperature?: number;
    
    /**
     * Maximum tokens to generate
     */
    maxTokens?: number;
    
    /**
     * Resource usage metrics
     */
    resourceUsage: ResourceMetrics;
  };
}

/**
 * LLM response
 */
interface LLMResponse {
  /**
   * Response content
   */
  content: string;
  
  /**
   * Tool calls if any
   */
  toolCalls?: ToolCall[];
  
  /**
   * Usage metrics from provider
   */
  usage?: {
    /**
     * Prompt tokens
     */
    promptTokens: number;
    
    /**
     * Completion tokens
     */
    completionTokens: number;
    
    /**
     * Total tokens
     */
    totalTokens: number;
  };
}
```

## Script Execution Types

```typescript
/**
 * Script execution result
 */
interface ScriptResult {
  /**
   * Standard output
   */
  stdout: string;
  
  /**
   * Standard error
   */
  stderr: string;
  
  /**
   * Exit code
   */
  exitCode: number;
}
```

## Error Types

```typescript
/**
 * Resource exhaustion error
 */
interface ResourceExhaustionError {
  /**
   * Error type
   */
  type: 'RESOURCE_EXHAUSTION';
  
  /**
   * Resource that was exhausted
   */
  resource: 'turns' | 'context';
  
  /**
   * Error message
   */
  message: string;
  
  /**
   * Resource metrics at time of exhaustion
   */
  metrics: ResourceMetrics[keyof ResourceMetrics];
}

/**
 * Tool execution error
 */
interface ToolExecutionError {
  /**
   * Error type
   */
  type: 'TOOL_EXECUTION_ERROR';
  
  /**
   * Tool that caused the error
   */
  tool: string;
  
  /**
   * Error message
   */
  message: string;
  
  /**
   * Error details
   */
  details: any;
}
```

These types define the data structures used throughout the Handler component implementation.
