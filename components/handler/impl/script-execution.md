# Script Execution Implementation [Implementation:ScriptExecution:1.0]

This document provides implementation details for script execution as defined in the Director-Evaluator pattern [Pattern:DirectorEvaluator:1.1].

## Script Execution Handler

```typescript
class Handler implements IHandler {
  async executeScript(
    command: string, 
    input: string, 
    timeout: number = 300
  ): Promise<ScriptResult> {
    // Validate command for security
    this.validateCommand(command);
    
    // Prepare environment
    const env = { ...process.env };
    
    // Prepare options
    const options = {
      timeout: timeout * 1000, // Convert to milliseconds
      input,
      env,
      maxBuffer: 10 * 1024 * 1024, // 10MB buffer
    };
    
    try {
      // Execute command
      const { stdout, stderr } = await exec(command, options);
      
      return {
        stdout,
        stderr,
        exitCode: 0
      };
    } catch (error) {
      // Command failed but we still return the result
      return {
        stdout: error.stdout || '',
        stderr: error.stderr || error.message,
        exitCode: error.code || 1
      };
    }
  }
  
  private validateCommand(command: string): void {
    // Security validation of command
    // Implement appropriate security checks
    // ...
    
    // If validation fails, throw error
    // throw new Error(`Invalid command: ${command}`);
  }
}
```

## TaskSystem Integration

```typescript
class TaskSystem {
  async executeScriptTask(task: ScriptTask, inputs: any): Promise<TaskResult> {
    // Get handler
    const handler = this.getHandlerForTask(task);
    
    // Extract command and input
    const command = this.resolveTemplate(task.command, inputs);
    const input = inputs[task.inputField] || '';
    
    // Execute script
    const scriptResult = await handler.executeScript(
      command, 
      input,
      task.timeout
    );
    
    // Return result
    return {
      content: scriptResult.stdout,
      status: "COMPLETE",
      notes: {
        stdout: scriptResult.stdout,
        stderr: scriptResult.stderr,
        exitCode: scriptResult.exitCode,
        command
      }
    };
  }
  
  private resolveTemplate(template: string, values: any): string {
    // Resolve template variables in command
    // ...
  }
}
```

For integration with the Director-Evaluator pattern, see [Implementation:StaticDirectorEvaluator:1.0] and [Implementation:DynamicDirectorEvaluator:1.0].
