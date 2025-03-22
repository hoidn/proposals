# Subtask Tool Implementation [Implementation:SubtaskTools:1.0]

This document provides implementation details for subtask tools as defined in [Pattern:ToolInterface:1.0] and [Pattern:SubtaskSpawning:1.0].

## Subtask Tool Registration

```typescript
class TaskSystem {
  private subtaskTools: Map<string, string[]> = new Map();
  
  registerSubtaskTool(name: string, templateHints: string[]): void {
    if (this.subtaskTools.has(name)) {
      throw new Error(`Subtask tool '${name}' is already registered`);
    }
    this.subtaskTools.set(name, templateHints);
  }
}
```

## Subtask Tool Execution

```typescript
class Handler implements IHandler {
  private subtaskTools: Map<string, string[]> = new Map();
  
  registerSubtaskTool(name: string, templateHints: string[]): void {
    this.subtaskTools.set(name, templateHints);
  }
  
  async processToolCall(toolCall: ToolCall): Promise<TaskResult> {
    const { name, input } = toolCall;
    
    // Check if this is a subtask tool
    if (this.subtaskTools.has(name)) {
      // Return a continuation with subtask request
      return {
        content: `Executing subtask tool: ${name}`,
        status: "CONTINUATION",
        notes: {
          subtask_request: {
            type: "atomic",
            description: `Execute ${name} with provided inputs`,
            inputs: input,
            template_hints: this.subtaskTools.get(name),
            subtype: "subtask"
          }
        }
      };
    }
    
    // Otherwise, it's a direct tool
    // ...
  }
}
```

## TaskSystem Continuation Processing

```typescript
class TaskSystem {
  async executeTask(task: Task, memorySystem: MemorySystem): Promise<TaskResult> {
    const handler = this.getHandlerForTask(task);
    
    // Execute initial prompt
    const result = await handler.executePrompt(task.systemPrompt, task.taskPrompt);
    
    // Check for continuation with subtask request
    if (result.status === "CONTINUATION" && result.notes?.subtask_request) {
      const subtaskRequest = result.notes.subtask_request;
      
      // Find matching template
      const template = await this.findMatchingTemplate(
        subtaskRequest.description,
        subtaskRequest.template_hints
      );
      
      // Execute subtask
      const subtaskResult = await this.executeSubtask(template, subtaskRequest.inputs);
      
      // Add subtask result as tool response
      const toolName = this.getToolNameFromRequest(subtaskRequest);
      handler.addToolResponse(toolName, subtaskResult.content);
      
      // Continue parent task execution
      return handler.executePrompt(
        task.systemPrompt,
        "Continue based on the tool results."
      );
    }
    
    return result;
  }
}
```

For more information on the continuation protocol, see [Pattern:SubtaskSpawning:1.0].
