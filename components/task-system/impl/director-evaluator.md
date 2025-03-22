# Director-Evaluator Loop Implementation [Implementation:StaticDirectorEvaluator:1.0]

This document provides implementation details for the static variant (director_evaluator_loop) of the Director-Evaluator pattern defined in [Pattern:DirectorEvaluator:1.1].

## Static Director-Evaluator Loop Implementation

```typescript
class TaskSystem {
  async executeDirectorEvaluatorLoop(task: DirectorEvaluatorLoopTask, inputs: any): Promise<TaskResult> {
    // Initialize loop state
    let currentIteration = 0;
    let directorResult: TaskResult | null = null;
    let evaluationResult: EvaluationResult | null = null;
    let scriptResult: ScriptResult | null = null;
    let success = false;
    
    // Get max iterations
    const maxIterations = task.maxIterations || 3;
    
    // Create context manager based on task settings
    const contextManager = this.createContextManager(task.contextManagement);
    
    while (currentIteration < maxIterations && !success) {
      // Prepare director inputs
      const directorInputs = {
        ...inputs,
        iteration: currentIteration,
        feedback: evaluationResult?.notes?.feedback,
        previous_result: directorResult?.content
      };
      
      // Execute director
      directorResult = await this.executeTask(task.director, directorInputs);
      
      // Execute script if specified
      if (task.scriptExecution) {
        scriptResult = await this.executeScript(
          task.scriptExecution.command,
          directorResult.content,
          task.scriptExecution.timeout
        );
      }
      
      // Prepare evaluator inputs
      const evaluatorInputs = {
        solution: directorResult.content,
        original_prompt: inputs.original_prompt || inputs.problem,
        script_output: scriptResult?.stdout,
        script_errors: scriptResult?.stderr,
        exit_code: scriptResult?.exitCode
      };
      
      // Execute evaluator
      evaluationResult = await this.executeTask(task.evaluator, evaluatorInputs) as EvaluationResult;
      
      // Check for success
      success = evaluationResult.notes.success;
      
      // Check termination condition if specified
      if (task.terminationCondition) {
        const shouldTerminate = this.evaluateTerminationCondition(
          task.terminationCondition.condition,
          {
            evaluation: evaluationResult.notes,
            iteration: currentIteration,
            director_result: directorResult
          }
        );
        
        if (shouldTerminate) {
          break;
        }
      }
      
      // Accumulate results in context if configured
      if (task.contextManagement.accumulateData) {
        contextManager.accumulateResult(
          currentIteration, 
          directorResult, 
          evaluationResult
        );
      }
      
      currentIteration++;
    }
    
    // Prepare final result
    return {
      content: directorResult?.content || "",
      status: success ? "COMPLETE" : "FAILED",
      notes: {
        iterations: currentIteration,
        success,
        final_evaluation: evaluationResult?.notes,
        script_result: scriptResult
      }
    };
  }
  
  private createContextManager(config: ContextManagement): any {
    // Create context manager based on configuration
    // ...
  }
  
  private evaluateTerminationCondition(condition: string, context: any): boolean {
    // Evaluate termination condition
    // ...
  }
  
  private async executeScript(command: string, input: string, timeout?: number): Promise<ScriptResult> {
    // Execute script via Handler
    // ...
  }
}
```

For details on script execution, see [Implementation:ScriptExecution:1.0].
