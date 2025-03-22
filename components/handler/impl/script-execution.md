# Script Execution Implementation [Implementation:ScriptExecution:1.0]

## Purpose

This document provides implementation details for script execution as defined in the Director-Evaluator pattern [Pattern:DirectorEvaluator:1.1].

## Related Documents

- [Pattern:DirectorEvaluator:1.1](../../../system/architecture/patterns/director-evaluator.md)
- [Handler Types](../spec/types.md)
- [Handler Behaviors](../spec/behaviors.md)

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

## Director-Evaluator Integration

When used within a Director-Evaluator loop, script execution follows this flow:

1. The Director produces an initial output
2. The script receives the Director's output as input
3. Script execution captures stdout, stderr, and exit code
4. These outputs are passed to the Evaluator
5. The Evaluator considers both the original output and script results

```typescript
// In Director-Evaluator Loop implementation
async function executeDirectorEvaluatorLoop(task: DirectorEvaluatorLoopTask): Promise<TaskResult> {
  // Execute director
  const directorResult = await executeTask(task.director);
  
  // Execute script if configured
  let scriptResult = null;
  if (task.scriptExecution) {
    scriptResult = await handler.executeScript(
      task.scriptExecution.command,
      directorResult.content,
      task.scriptExecution.timeout || 300
    );
  }
  
  // Prepare evaluator inputs
  const evaluatorInputs = {
    solution: directorResult.content,
    scriptOutput: scriptResult ? scriptResult.stdout : null,
    scriptError: scriptResult ? scriptResult.stderr : null,
    exitCode: scriptResult ? scriptResult.exitCode : null
  };
  
  // Execute evaluator with inputs
  const evaluationResult = await executeTask(task.evaluator, evaluatorInputs);
  
  // Process results and continue or terminate loop
  // ...
}
```

For complete integration details, see [Implementation:StaticDirectorEvaluator:1.0] and [Implementation:DynamicDirectorEvaluator:1.0] in the Task System documentation.
