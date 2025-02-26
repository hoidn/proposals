# Architecture Decision Record: Subtask Spawning Mechanism

## Status
Proposed

## Context
The system needs a standardized mechanism for tasks to dynamically spawn subtasks during execution. This capability is essential for:

1. Breaking down complex tasks adaptively
2. Handling cases where dependencies are discovered during execution
3. Supporting verification through dynamically generated test tasks
4. Enabling workflow-like task sequences that aren't known in advance

## Decision
We will implement a standardized subtask spawning mechanism based on structured continuation requests. This approach formalizes how tasks can request subtask creation and receive results, building on our established patterns.

## Specification

### 1. Task Result with Subtask Request

Tasks request subtask spawning by returning a result with:

```typescript
interface TaskResult {
    content: string;
    status: "CONTINUATION";
    notes: {
        subtask_request: SubtaskRequest;
        [key: string]: any;
    };
}

interface SubtaskRequest {
    type: string;           // Type of subtask (e.g., "verification", "elaboration")
    description: string;    // Human-readable description of the subtask
    inputs: {               // Inputs to provide to the subtask
        [key: string]: any;
    };
    template_hints?: string[]; // Optional hints for template matching
    return_expectations?: string; // Optional description of expected output format
}
```

### 2. Status Types

We will extend the ReturnStatus enum to include:

```typescript
type ReturnStatus = 
  | "COMPLETE"     // Task completed successfully
  | "CONTINUATION" // Task requesting subtask
  | "WAITING"      // Task waiting for external input
  | "FAILED";      // Task failed to complete
```

The task system will track continuation state internally rather than introducing a new "RESUMED" status.

### 3. Subtask Creation and Execution Flow

When a task returns with CONTINUATION status and a subtask_request:

1. The TaskSystem extracts the subtask_request
2. It selects an appropriate template using associative matching
3. It creates inputs for the subtask, incorporating parent task context
4. It executes the subtask with appropriate context management
5. After subtask completion, it resumes the parent task with subtask results as direct inputs

```typescript
// Flow within TaskSystem
async function executeTask(task, inputs) {
    // Normal task execution path...
    const result = await executeTaskWithLLM(task, inputs);
    
    if (result.status === "CONTINUATION" && result.notes?.subtask_request) {
        const subtaskRequest = result.notes.subtask_request;
        
        // Find template for subtask
        const subtaskTemplate = await findMatchingTemplate(
            subtaskRequest.type,
            subtaskRequest.description,
            subtaskRequest.template_hints
        );
        
        // Execute subtask with appropriate inputs
        const subtaskInputs = {
            ...subtaskRequest.inputs,
            parent_task_description: task.description,
            parent_task_result: result.content
        };
        
        const subtaskResult = await executeTask(subtaskTemplate, subtaskInputs);
        
        // Resume original task with subtask results
        const resumeInputs = {
            ...inputs,
            subtask_result: subtaskResult
        };
        
        // Recursively call executeTask with updated inputs
        return executeTask(task, resumeInputs);
    }
    
    return result;
}
```

### 4. Context Management for Subtasks

Subtasks follow the standardized context management from our Context Management Standardization ADR with specific defaults:

```xml
<task>
    <context_management>
        <inherit_context>full</inherit_context>
        <fresh_context>disabled</fresh_context>
    </context_management>
</task>
```

#### Relationship Between Context Settings

`inherit_context` and `fresh_context` settings are compatible and complementary:

- **inherit_context**: Controls what context is received from the parent task
  - `full`: All parent context is inherited
  - `none`: No parent context is inherited
  - `subset`: Only relevant parts of parent context are inherited

- **fresh_context**: Controls whether additional context is retrieved
  - `enabled`: Additional relevant context is retrieved through associative matching
  - `disabled`: No additional context is retrieved beyond what's inherited

#### Default Settings for Subtasks

By default, subtasks have:
- **Full parent context inheritance**: Ensuring continuity and access to all relevant information from the parent task
- **Fresh context disabled**: Preventing unnecessary context retrieval for efficiency, as the parent context is usually sufficient

These defaults can be explicitly overridden in a subtask template if needed.

### 5. Subtask Result Structure

Subtask results follow the standard TaskResult structure:

```typescript
interface TaskResult {
    content: string;        // Main subtask output
    status: ReturnStatus;   // COMPLETE, CONTINUATION, FAILED, etc.
    notes: {                // Additional metadata
        [key: string]: any;
    };
}
```

### 6. Error Handling

Error handling follows these rules:

1. If a subtask fails, its error is captured and passed to the parent when it resumes
2. Parent task receives the error information as part of its inputs
3. Parent can handle errors by checking the subtask_result.status
4. Chain of errors maintains the error taxonomy from our Error Taxonomy ADR

## Implementation Guidelines

1. Enhance the TaskSystem to:
   - Process CONTINUATION status with subtask_request
   - Find appropriate templates for subtasks
   - Pass results back to parent tasks when resuming

2. Update template matching to consider:
   - The subtask type
   - Template hints
   - Return expectations

3. Implement input/output mapping to:
   - Transform parent task context into subtask inputs
   - Process subtask results into parent inputs when resuming

4. Add task state tracking to:
   - Maintain parent task state during subtask execution
   - Support multiple sequential subtasks
   - Prevent unbounded task chains (with depth limits)

## Example: Code Implementation with Testing

### Parent Task XML Definition
```xml
<task type="atomic">
  <description>Implement a sorting algorithm based on requirements</description>
  <inputs>
    <input name="requirements" from="user_query"/>
  </inputs>
  <!-- Context management settings use defaults -->
</task>
```

### LLM-Generated Result (Requesting Test Generation)
```json
{
  "content": "def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr",
  "status": "CONTINUATION",
  "notes": {
    "subtask_request": {
      "type": "test_generation",
      "description": "Create tests for the bubble sort implementation",
      "inputs": {
        "code": "def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr",
        "requirements": "Create a sorting algorithm that sorts an array in ascending order"
      },
      "template_hints": ["test", "python"]
    }
  }
}
```

### Test Generation Subtask XML (Found by Template Matching)
```xml
<task type="atomic">
  <description>Generate tests for {{code_type}}</description>
  <inputs>
    <input name="code" from="code"/>
    <input name="requirements" from="requirements"/>
    <input name="code_type" from="code_type"/>
  </inputs>
  <context_management>
    <inherit_context>full</inherit_context>
    <fresh_context>disabled</fresh_context>
  </context_management>
</task>
```

### LLM-Generated Subtask Result (Tests)
```json
{
  "content": "import unittest\n\nclass TestBubbleSort(unittest.TestCase):\n    def test_empty_array(self):\n        self.assertEqual(bubble_sort([]), [])\n        \n    def test_sorted_array(self):\n        self.assertEqual(bubble_sort([1, 2, 3, 4, 5]), [1, 2, 3, 4, 5])\n        \n    def test_reverse_array(self):\n        self.assertEqual(bubble_sort([5, 4, 3, 2, 1]), [1, 2, 3, 4, 5])\n        \n    def test_mixed_array(self):\n        self.assertEqual(bubble_sort([3, 1, 4, 1, 5, 9, 2, 6]), [1, 1, 2, 3, 4, 5, 6, 9])\n\nif __name__ == '__main__':\n    unittest.main()",
  "status": "COMPLETE",
  "notes": {
    "test_coverage": "Basic functionality, edge cases, and sorted/reverse inputs",
    "frameworks_used": ["unittest"]
  }
}
```

### Parent Task Resumption (LLM receives subtask result and original task)
When the parent task resumes, the LLM receives:
1. The original requirements
2. Its previous code implementation
3. The test generation results

```json
{
  "content": "# Implementation\ndef bubble_sort(arr):\n    if not arr:\n        return []\n    n = len(arr)\n    for i in range(n):\n        # Optimization: track if any swaps occurred\n        swapped = False\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n                swapped = True\n        # If no swaps occurred in this pass, array is sorted\n        if not swapped:\n            break\n    return arr\n\n# Tests\nimport unittest\n\nclass TestBubbleSort(unittest.TestCase):\n    def test_empty_array(self):\n        self.assertEqual(bubble_sort([]), [])\n        \n    def test_sorted_array(self):\n        self.assertEqual(bubble_sort([1, 2, 3, 4, 5]), [1, 2, 3, 4, 5])\n        \n    def test_reverse_array(self):\n        self.assertEqual(bubble_sort([5, 4, 3, 2, 1]), [1, 2, 3, 4, 5])\n        \n    def test_mixed_array(self):\n        self.assertEqual(bubble_sort([3, 1, 4, 1, 5, 9, 2, 6]), [1, 1, 2, 3, 4, 5, 6, 9])\n\nif __name__ == '__main__':\n    unittest.main()",
  "status": "COMPLETE",
  "notes": {
    "improvements": [
      "Added empty array check",
      "Added optimization for early termination when sorted",
      "Tests verify correct functionality for all cases"
    ]
  }
}
```

## Relationship to Director-Evaluator Loop

The Subtask Spawning mechanism and the Director-Evaluator Loop are **distinct but complementary** features in our architecture:

### Director-Evaluator Loop
- A **specialized task type** (`director_evaluator_loop`) with dedicated execution logic
- Explicitly designed for **iterative refinement workflows**
- Has **built-in iteration management** and configurable termination conditions
- Represents a **higher-level pattern** with predefined components
- Optimized for feedback loops with multiple iterations

### Subtask Spawning Mechanism
- A **general-purpose mechanism** for dynamic task composition
- Enables **ad-hoc subtask creation** during task execution
- Supports **one-off subtask requests** without predefined iterations
- Provides a **lower-level primitive** with more flexibility
- Suitable for tasks that need to spawn occasional subtasks

### When to Use Each

- **Use Director-Evaluator Loop when:**
  - You need an iterative refinement process
  - The pattern involves generating content and evaluating it
  - Multiple iterations may be required
  - You want built-in iteration management

- **Use Subtask Spawning when:**
  - A task needs to dynamically spawn a subtask based on its progress
  - Subtasks are created ad-hoc rather than following a fixed pattern
  - You need flexible, one-off subtask creation
  - The task flow isn't primarily iterative

While a task using the Subtask Spawning mechanism could implement its own Director-Evaluator pattern, the dedicated `director_evaluator_loop` task type provides a more structured, optimized implementation for that specific pattern.

## Context Combinations Reference Table

| inherit_context | fresh_context | Result |
|-----------------|---------------|--------|
| full | enabled | Subtask has full parent context + additional relevant context |
| full | disabled | Subtask has only parent context, no new context (DEFAULT) |
| none | enabled | Subtask has only fresh context, no parent context |
| none | disabled | Subtask has minimal context (only inputs) |
| subset | enabled | Subtask has relevant parent context + additional context |
| subset | disabled | Subtask has only relevant parent context |

## Alternatives Considered

1. **Environment Variable Approach**
   - Storing subtask results in environment variables
   - Rejected to maintain consistency with our decision to minimize environment usage for data transfer

2. **Callback-Based Approach**
   - Using callback functions specified in the subtask request
   - Rejected due to added complexity and potential security concerns

3. **AST-Based Dynamic Creation**
   - Creating AST nodes directly for subtasks
   - Rejected as too complex and less flexible than template matching

## Questions for Consideration

1. **Depth Limits**: What maximum depth of subtask chaining should we support?

2. **Template Selection**: Should we provide multiple template matching strategies for subtasks?

3. **Result Format Standardization**: Should we standardize specific format types for subtask results?

## Consequences

### Positive
- Standardized mechanism for dynamic task composition
- Clear data flow between parent and subtasks
- Support for complex workflows with ad-hoc subtasks
- Consistency with our context management approach
- Efficient context handling with sensible defaults
- Complements the dedicated Director-Evaluator Loop

### Negative
- More complex TaskSystem implementation
- Potential for deep task chains that are hard to debug
- Additional template matching overhead
- Requires careful state management for parent tasks
