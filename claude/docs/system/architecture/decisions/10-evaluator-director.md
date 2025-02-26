# Architecture Decision Record: Evaluator-to-Director Feedback Flow

## Status
Proposed

## Context
The Director-Evaluator pattern is a foundational component of our architecture that allows tasks to generate output, have it evaluated, and receive feedback for further refinement. Current documentation describes both static and dynamic variants but lacks clear specification for the feedback flow between components, especially regarding data passing and iteration control.

## Decision
We will implement a unified Director-Evaluator pattern with direct result passing between components, minimizing environment usage and providing flexible iteration control through a dedicated task type.

## Specification

### 1. Unified Task Type

We will introduce a dedicated task type for the Director-Evaluator pattern:

```xml
<task type="director_evaluator_loop">
  <description>{{task_description}}</description>
  <max_iterations>5</max_iterations>
  <director>
    <!-- Director task definition -->
    <description>Generate solution for {{original_prompt}}</description>
    <inputs>
      <input name="original_prompt" from="user_query"/>
      <input name="feedback" from="evaluation_feedback"/>
      <input name="iteration" from="current_iteration"/>
    </inputs>
  </director>
  <evaluator>
    <!-- Evaluator task definition -->
    <description>Evaluate solution against {{original_prompt}}</description>
    <inputs>
      <input name="director_output" from="director_result"/>
      <input name="original_prompt" from="user_query"/>
    </inputs>
  </evaluator>
  <script_execution>
    <!-- Optional script execution -->
    <command>{{script_path}}</command>
    <timeout>300</timeout>
    <inputs>
      <input name="script_input" from="director_result"/>
    </inputs>
  </script_execution>
  <termination_condition>
    <!-- Optional early termination -->
    <condition>evaluation.success === true</condition>
  </termination_condition>
</task>
```

### 2. Feedback Data Structure

All evaluator-to-director feedback will use this JSON structure:

```typescript
interface EvaluationResult {
    success: boolean;        // Whether the evaluation passed
    feedback: string;        // Human-readable feedback message
    details?: {              // Optional structured details
        metrics?: Record<string, number>; // Optional evaluation metrics
        violations?: string[];            // Specific validation failures
        suggestions?: string[];           // Suggested improvements
        [key: string]: any;               // Extension point for additional data
    };
    scriptOutput?: {         // Present when script execution is involved
        stdout: string;      // Standard output from script
        stderr: string;      // Standard error output from script
        exitCode: number;    // Exit code from script
    };
}
```

### 3. Execution Flow

The TaskSystem will manage the iteration flow directly:

```typescript
async function executeDirectorEvaluatorLoop(task, inputs, context) {
  const maxIterations = task.maxIterations || 5;
  const results = [];
  
  let directorOutput = null;
  let evaluationResult: EvaluationResult = { success: false, feedback: "" };
  
  for (let iteration = 0; iteration < maxIterations; iteration++) {
    // Execute director with current state
    directorOutput = await executeTask(
      task.director,
      {
        ...inputs,
        current_iteration: iteration,
        evaluation_feedback: evaluationResult.feedback,
        previous_results: results.length > 0 ? results : undefined
      },
      context
    );
    
    // Store the director's result
    results.push({ iteration, output: directorOutput, evaluation: null });
    
    // Check if we should run a script
    if (task.script_execution) {
      const scriptResult = await executeScript(task.script_execution, directorOutput);
      
      // Add script result to be passed to evaluator
      scriptOutput = {
        stdout: scriptResult.stdout,
        stderr: scriptResult.stderr,
        exitCode: scriptResult.exitCode
      };
    }
    
    // Execute evaluator
    evaluationResult = await executeTask(
      task.evaluator,
      {
        ...inputs,
        director_result: directorOutput,
        script_output: scriptOutput
      },
      context
    );
    
    // Store the evaluation
    results[results.length - 1].evaluation = evaluationResult;
    
    // Check termination condition
    if (evaluationResult.success || 
        (task.termination_condition && evaluateCondition(task.termination_condition, evaluationResult))) {
      break;
    }
  }
  
  // Return the final result and history
  return {
    final_output: directorOutput,
    final_evaluation: evaluationResult,
    success: evaluationResult.success,
    iterations_completed: results.length,
    iteration_history: results
  };
}
```

### 4. Error Handling

Two types of feedback remain as before:

1. **Negative Evaluations**: Normal flow where evaluator indicates improvement needed (`success: false`)

2. **Evaluator Errors**: Exceptional flow where evaluator itself fails, following standard error taxonomy

### 5. Iteration Control

Iteration control is explicit and configurable:

1. **Maximum Iterations**: Set via `<max_iterations>` element
2. **Early Termination**: Via `<termination_condition>` element 
3. **Success-Based Termination**: Automatically stops when `evaluationResult.success === true`
4. **Iteration History**: Maintained and returned as part of the final result

### 6. Parameter Passing

Data is passed directly between tasks rather than through environment variables:

1. **Input Parameters**: Explicitly declared in each component's `<inputs>` section
2. **Result Passing**: The TaskSystem handles passing results between director and evaluator
3. **Iteration State**: Managed by the loop executor, not stored in environment
4. **Context**: Used only for lexical variables, not for inter-task communication

## Alternatives Considered

1. **Environment-Based State**: Rejected in favor of direct passing to keep the environment focused on lexical variables rather than general state

2. **Separate Static/Dynamic Variants**: Rejected in favor of a unified representation that supports both use cases

3. **Ad-hoc Iteration Control**: Rejected in favor of explicit iteration control with maximum limits and termination conditions

## Consequences

### Positive
- Unified representation for both static and dynamic patterns
- Clear, direct data flow between components
- Proper separation of concerns (TaskSystem manages iteration)
- Explicit iteration control and history tracking
- Environment used properly for lexical scope only

### Negative
- More complex TaskSystem implementation
- New task type required
- Migration effort for existing implementations

## Implementation Guidelines

1. Add the new `director_evaluator_loop` task type to the XML schema

2. Implement the loop execution logic in the TaskSystem

3. Update the Evaluator and Director components to:
   - Use the standardized EvaluationResult structure
   - Accept direct inputs rather than environment access

4. Add validation for the termination condition expression

## Example

### Director-Evaluator Loop Task

```xml
<task type="director_evaluator_loop">
  <description>Develop a sorting algorithm based on user requirements</description>
  <max_iterations>3</max_iterations>
  <director>
    <description>Create or refine sorting algorithm based on feedback</description>
    <inputs>
      <input name="requirements" from="user_query"/>
      <input name="feedback" from="evaluation_feedback"/>
      <input name="iteration" from="current_iteration"/>
    </inputs>
  </director>
  <script_execution>
    <command>python -m test_sorting_algorithm.py</command>
    <timeout>30</timeout>
    <inputs>
      <input name="script_input" from="director_result"/>
    </inputs>
  </script_execution>
  <evaluator>
    <description>Evaluate sorting algorithm implementation</description>
    <inputs>
      <input name="algorithm" from="director_result"/>
      <input name="requirements" from="user_query"/>
      <input name="test_results" from="script_output"/>
    </inputs>
  </evaluator>
  <termination_condition>
    <condition>evaluation.success === true || (evaluation.scriptOutput?.exitCode === 0 && iteration >= 2)</condition>
  </termination_condition>
</task>
```

### Director Output (First Iteration)

```typescript
return {
  content: "def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr",
  notes: {
    explanation: "Implemented a simple bubble sort algorithm as requested"
  }
};
```

### Evaluator Output (First Iteration)

```typescript
return {
  success: false,
  feedback: "The bubble sort implementation is correct but inefficient for large datasets. Consider adding an early exit optimization when no swaps occur in a pass.",
  details: {
    violations: ["Missing early exit optimization"],
    scriptOutput: {
      stdout: "All test cases passed but performance tests show O(n²) time in all cases",
      stderr: "",
      exitCode: 0
    }
  }
};
```
