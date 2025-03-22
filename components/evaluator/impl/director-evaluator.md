# Director-Evaluator Implementation [Implementation:DynamicDirectorEvaluator:1.0]

This document provides implementation details for the dynamic variant of the Director-Evaluator pattern defined in [Pattern:DirectorEvaluator:1.1].

## Dynamic Director-Evaluator Implementation

```typescript
class Evaluator {
  async handleDirectorContinuation(result: TaskResult, task: Task): Promise<TaskResult> {
    if (result.status !== 'CONTINUATION' || !result.notes?.evaluation_request) {
      return result;
    }
    
    const evaluationRequest = result.notes.evaluation_request;
    
    // Find appropriate evaluator template
    const evaluatorTemplate = await this.findEvaluatorTemplate(
      evaluationRequest.type,
      evaluationRequest.criteria
    );
    
    // Prepare evaluator inputs
    const evaluatorInputs = {
      target_content: result.content,
      criteria: evaluationRequest.criteria
    };
    
    // If there's a script to execute, do that first
    if (evaluationRequest.target && evaluationRequest.type === 'bash_script') {
      const scriptResult = await this.executeScript(
        evaluationRequest.target,
        result.content
      );
      
      // Add script results to evaluator inputs
      evaluatorInputs.stdout = scriptResult.stdout;
      evaluatorInputs.stderr = scriptResult.stderr;
      evaluatorInputs.exit_code = scriptResult.exitCode;
    }
    
    // Execute evaluator
    const evaluationResult = await this.executeTask(
      evaluatorTemplate,
      evaluatorInputs
    );
    
    // Resume director with evaluation feedback
    return this.resumeDirector(task, {
      original_output: result.content,
      evaluation: evaluationResult
    });
  }
  
  private async findEvaluatorTemplate(type: string, criteria: string[]): Promise<Task> {
    // Find evaluator template based on type and criteria
    // ...
  }
  
  private async executeScript(scriptPath: string, input: string): Promise<ScriptResult> {
    // Execute script using Handler or script execution service
    // ...
  }
  
  private async resumeDirector(task: Task, inputs: any): Promise<TaskResult> {
    // Resume director with evaluation feedback
    // ...
  }
}
```

For information on the static variant implementation, see [Implementation:StaticDirectorEvaluator:1.0].
