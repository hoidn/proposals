# Architecture Decision Record: Evaluator-to-Director Feedback Flow

## Status
Proposed

## Context
The Director-Evaluator pattern is a foundational component of our architecture that allows tasks to generate output, have it evaluated (potentially through external tools or scripts), and receive feedback for further refinement. Currently, the documentation describes both static and dynamic variants of this pattern, but lacks clear specification for how feedback flows between components, how errors are handled, and how the environment is maintained across multiple iterations.

## Decision
We will standardize the Evaluator-to-Director feedback flow using a structured JSON format stored in the `last_evaluator_output` environment variable, with unified handling for both static and dynamic pattern variants.

## Specification

### 1. Feedback Data Structure

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

### 2. Environment Management

The environment will maintain continuity across director-evaluator cycles:

```typescript
// After evaluator completes:
function storeEvaluatorOutput(evaluationResult: EvaluationResult, env: Environment): void {
    // Serialize result to JSON
    env.set('last_evaluator_output', JSON.stringify(evaluationResult));
    
    // Clear all other variables from the environment except last_evaluator_output
    env.clearExcept(['last_evaluator_output']);
}

// When director accesses evaluator output:
function getLastEvaluation(env: Environment): EvaluationResult | null {
    const rawOutput = env.get('last_evaluator_output');
    if (!rawOutput) return null;
    
    try {
        return JSON.parse(rawOutput) as EvaluationResult;
    } catch (error) {
        throw createTaskFailure(
            'context_parsing_failure', 
            'Failed to parse evaluator output JSON',
            { rawOutput: rawOutput.substring(0, 100) + '...' }
        );
    }
}
```

### 3. Error Handling

We distinguish between two types of feedback:

1. **Negative Evaluations** (normal flow):
   - Evaluator runs successfully but reports director's output as problematic
   - Uses `success: false` with explanatory feedback
   - Director receives this as normal feedback, not as an error

2. **Evaluator Errors** (exceptional flow):
   - Evaluator itself fails to run or process output
   - Follows standard error taxonomy with `reason` field
   - Bubbles up to calling context rather than returning to director

### 4. Director Template Parameters

The director template should include these parameters to maintain state across iterations:

```xml
<task type="atomic" subtype="director">
    <description>Generate solution for {{original_prompt}}</description>
    <inputs>
        <input name="original_prompt" from="user_query"/>
        <input name="iteration" from="current_iteration"/>
        <input name="max_iterations" from="max_attempts"/>
        <input name="last_evaluation" from="last_evaluator_output"/>
        <input name="previous_output" from="last_director_output"/>
    </inputs>
    <output_slot>last_director_output</output_slot>
</task>
```

### 5. Unified XML Representation

We will unify the static and dynamic pattern variants with a single, flexible XML representation:

```xml
<!-- Static variant with predetermined execution flow -->
<task type="sequential">
    <description>{{task_description}}</description>
    <context_management>
        <inherit_context>none</inherit_context>
        <accumulate_data>true</accumulate_data>
        <accumulation_format>notes_only</accumulation_format>
        <fresh_context>enabled</fresh_context>
    </context_management>
    <steps>
        <task type="atomic" subtype="director">
            <description>Generate solution for {{original_prompt}}</description>
            <inputs>
                <input name="original_prompt" from="user_query"/>
                <input name="iteration" from="current_iteration"/>
                <input name="last_evaluation" from="last_evaluator_output"/>
            </inputs>
            <output_slot>last_director_output</output_slot>
        </task>
        
        <!-- Optional script execution step -->
        <task type="script">
            <description>Execute verification script</description>
            <inputs>
                <input name="script_input" from="last_director_output"/>
            </inputs>
            <script>
                <command>{{script_path}}</command>
                <timeout>300</timeout>
            </script>
            <output_slot>script_result</output_slot>
        </task>
        
        <task type="atomic" subtype="evaluator">
            <description>Evaluate output</description>
            <inputs>
                <input name="director_output" from="last_director_output"/>
                <input name="script_result" from="script_result"/>
                <input name="original_prompt" from="user_query"/>
            </inputs>
            <output_slot>last_evaluator_output</output_slot>
        </task>
    </steps>
</task>

<!-- Dynamic variant - director decides when to request evaluation -->
<task type="atomic" subtype="director">
    <description>Generate solution for {{original_prompt}}</description>
    <inputs>
        <input name="original_prompt" from="user_query"/>
        <input name="iteration" from="current_iteration"/>
        <input name="last_evaluation" from="last_evaluator_output"/>
    </inputs>
    <continuation_policy>request_evaluation</continuation_policy>
    <output_slot>last_director_output</output_slot>
</task>
```

### 6. Continuation Flow

The dynamic variant uses the following flow:

1. Director executes and returns a result with:
   ```json
   {
       "content": "Generated solution...",
       "status": "CONTINUATION",
       "notes": {
           "evaluation_request": {
               "type": "validation",
               "criteria": "Verify formatting and completeness",
               "target": "solution.py"
           }
       }
   }
   ```

2. The evaluator is dynamically spawned with appropriate inputs

3. The evaluator produces an EvaluationResult that's stored in last_evaluator_output

4. Control returns to the director with the evaluation feedback

### 7. Iteration Configuration

The number of iterations should be configurable and eventually exposed in the DSL. The director should have access to:

- Current iteration count
- Maximum allowed iterations
- Previous iterations' outputs and evaluations

## Alternatives Considered

1. **Plain Text Feedback**: Rejected in favor of structured JSON for type safety and extensibility

2. **Separate Static and Dynamic Implementations**: Rejected to reduce duplication and complexity

3. **Context Inheritance for State**: Rejected in favor of explicit template parameters for transparency and predictability

## Consequences

### Positive
- Clear, structured feedback flow between components
- Unified handling for both static and dynamic variants
- Support for multiple iteration cycles
- Clean environment management
- Explicit error handling

### Negative
- More verbose XML templates
- Requires JSON parsing/serialization
- Potential failure points in JSON handling

## Implementation Guidelines

1. Update the Evaluator to:
   - Use the EvaluationResult structure
   - Properly serialize to JSON
   - Clear environment variables except last_evaluator_output

2. Update the Director to:
   - Expect and parse JSON structure from last_evaluator_output
   - Handle potential parsing failures
   - Include original prompt context for the evaluator

3. Add validation for the CONTINUATION/evaluation_request pattern

## Example

### Director Requesting Evaluation

```typescript
return {
    content: "function calculateTotal(items) {\n  return items.reduce((sum, item) => sum + item.price, 0);\n}",
    status: "CONTINUATION",
    notes: {
        evaluation_request: {
            type: "code_validation",
            criteria: "Check for correctness, style, and edge cases",
            target: "calculateTotal.js"
        }
    }
};
```

### Evaluator Response

```typescript
const evaluationResult: EvaluationResult = {
    success: false,
    feedback: "Function doesn't handle empty arrays correctly and will return NaN if item.price is missing.",
    details: {
        violations: [
            "No empty array check",
            "Missing null/undefined handling for item.price"
        ],
        suggestions: [
            "Add a check for empty array at the beginning",
            "Use optional chaining: item?.price || 0"
        ]
    }
};
```
