# Tool Execution Implementation

This document provides implementation details for the Tool Interface Pattern defined in [Pattern:ToolInterface:1.0].

## Direct Tool Implementation [Implementation:DirectTools:1.0]

```typescript
class Handler implements IHandler {
  private directTools: Map<string, Function> = new Map();
  
  registerDirectTool(name: string, handler: Function): void {
    if (this.directTools.has(name)) {
      throw new Error(`Tool '${name}' is already registered`);
    }
    this.directTools.set(name, handler);
  }
  
  async executeDirectTool(name: string, params: any): Promise<any> {
    const handler = this.directTools.get(name);
    if (!handler) {
      throw new Error(`Tool '${name}' is not registered`);
    }
    
    try {
      return await handler(params);
    } catch (error) {
      throw {
        type: 'TOOL_EXECUTION_ERROR',
        tool: name,
        message: error.message,
        details: error
      };
    }
  }
}
```

## User Input Tool Implementation [Implementation:UserInputTools:1.0]

```typescript
// Standard tool definition
const USER_INPUT_TOOL: ToolDefinition = {
  name: "requestUserInput",
  description: "Request input from the user when additional information is needed",
  parameters: {
    type: "object",
    properties: {
      prompt: {
        type: "string",
        description: "The question or prompt to show to the user"
      }
    },
    required: ["prompt"]
  }
};

// Handler implementation
class Handler implements IHandler {
  private onRequestInput?: (prompt: string) => Promise<string>;
  
  constructor(config: HandlerConfig) {
    // Register standard tools
    this.registerDirectTool(USER_INPUT_TOOL.name, this.handleUserInputRequest.bind(this));
  }
  
  setRequestInputCallback(callback: (prompt: string) => Promise<string>): void {
    this.onRequestInput = callback;
  }
  
  private async handleUserInputRequest(params: {prompt: string}): Promise<{userInput: string}> {
    if (!this.onRequestInput) {
      throw new Error("No input request handler registered");
    }
    
    const userInput = await this.onRequestInput(params.prompt);
    this.session.addUserMessage(userInput);
    
    return { userInput };
  }
}
```

For information on subtask tools, see [Implementation:SubtaskTools:1.0].
# Tool Execution Implementation [Implementation:DirectTools:1.0]

## Purpose

This document provides implementation details for the Tool Interface Pattern defined in [Pattern:ToolInterface:1.0].

## Related Documents

- [Pattern:ToolInterface:1.0](../../../system/architecture/patterns/tool-interface.md)
- [Handler Types](../spec/types.md)
- [Handler Behaviors](../spec/behaviors.md)

## Direct Tool Implementation

```typescript
class Handler implements IHandler {
  private directTools: Map<string, Function> = new Map();
  
  registerDirectTool(name: string, handler: Function): void {
    if (this.directTools.has(name)) {
      throw new Error(`Tool '${name}' is already registered`);
    }
    this.directTools.set(name, handler);
  }
  
  async executeDirectTool(name: string, params: any): Promise<any> {
    const handler = this.directTools.get(name);
    if (!handler) {
      throw new Error(`Tool '${name}' is not registered`);
    }
    
    try {
      return await handler(params);
    } catch (error) {
      throw {
        type: 'TOOL_EXECUTION_ERROR',
        tool: name,
        message: error.message,
        details: error
      };
    }
  }
}
```

## User Input Tool Implementation [Implementation:UserInputTools:1.0]

```typescript
// Standard tool definition
const USER_INPUT_TOOL: ToolDefinition = {
  name: "requestUserInput",
  description: "Request input from the user when additional information is needed",
  parameters: {
    type: "object",
    properties: {
      prompt: {
        type: "string",
        description: "The question or prompt to show to the user"
      }
    },
    required: ["prompt"]
  }
};

// Handler implementation
class Handler implements IHandler {
  private onRequestInput?: (prompt: string) => Promise<string>;
  
  constructor(config: HandlerConfig) {
    // Register standard tools
    this.registerDirectTool(USER_INPUT_TOOL.name, this.handleUserInputRequest.bind(this));
  }
  
  setRequestInputCallback(callback: (prompt: string) => Promise<string>): void {
    this.onRequestInput = callback;
  }
  
  private async handleUserInputRequest(params: {prompt: string}): Promise<{userInput: string}> {
    if (!this.onRequestInput) {
      throw new Error("No input request handler registered");
    }
    
    const userInput = await this.onRequestInput(params.prompt);
    this.session.addUserMessage(userInput);
    
    return { userInput };
  }
}
```

## Subtask Tool Integration

The Handler integrates with the subtask spawning mechanism through the CONTINUATION status:

```typescript
class Handler implements IHandler {
  // Other methods...
  
  registerSubtaskTool(name: string, templateHints: string[]): void {
    this.registerDirectTool(name, async (params: any) => {
      // Return a CONTINUATION status with subtask_request
      return {
        status: "CONTINUATION",
        notes: {
          subtask_request: {
            type: "atomic",
            description: `Execute ${name} subtask`,
            inputs: params,
            template_hints: templateHints
          }
        }
      };
    });
  }
  
  addToolResponse(toolName: string, response: string): void {
    // Add the tool response to the session
    this.session.addToolResponse(toolName, response);
  }
}
```

For information on subtask tools implementation in the Task System, see [Implementation:SubtaskTools:1.0] in the Task System documentation.
