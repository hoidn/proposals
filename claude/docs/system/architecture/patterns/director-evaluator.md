# Director‑Evaluator Pattern [Pattern:DirectorEvaluator:1.1]

**Canonical Reference:** This document is the authoritative description of the Director‑Evaluator Pattern. All extended descriptions in planning or misc files should refer here.

## Overview

The Director-Evaluator pattern is a specialized variant of the unified task‐subtask execution model. In this pattern, a parent task (the **Director**) produces an initial output that may require further evaluation. Instead of relying on a statically defined callback step, the evaluation subtask is spawned dynamically when the Director's output returns with a `CONTINUATION` status and an `evaluation_request` object in its `notes`.

**Note:** The `evaluation_request` object must include:
 - `type`: a string indicating the evaluation type,
 - `criteria`: a free-form string providing descriptive criteria used for dynamic evaluation template selection via associative matching,
 - `target`: a string representing the target (for example, the bash script command to run or the evaluation focus).

## Pattern Description

This pattern follows a three-phase flow:

1. **Parent Task (Director):**
   - Generates an initial output based on the user's instructions.
   - May return a result with `status: 'CONTINUATION'` and a populated `evaluation_request` in its `notes`.
   - Uses a `<context_management>` block with `inherit_context` set to `none` to start a new execution chain.

2. **Evaluation Trigger via Continuation:**
   - Rather than a fixed callback subtask, the evaluation step is triggered dynamically when the Director task returns a `CONTINUATION` status.
   - The embedded `evaluation_request` specifies both:
       - The **bash script** (or external callback mechanism) to execute, and
       - The **target** string that describes the aspects of the output requiring evaluation.
   - The Evaluator uses this information—with associative matching—to select an appropriate evaluation task template.
   - Only the latest evaluator output is retained; after the Evaluator completes its feedback step, the environment contains solely last_evaluator_output while all other temporary data is cleared. This significantly simplifies the feedback loop.

3. **Child Task (Evaluator):**
   - Is dynamically spawned by the Evaluator when it detects a `CONTINUATION` status along with an `evaluation_request` in the Director's output.
   - Uses a `<context_management>` block with `inherit_context` set to `subset` and `accumulate_data` enabled to incorporate only the relevant context.
   - Executes the evaluation subtask—which may include invoking the specified bash script via the Handler or Evaluator—and feeds its results back to the parent task so that the Director may continue its sequence.

### Environment Variable Management
Environment variables are managed so that last_evaluator_output is the only persistent variable across continuations. Any new evaluation clears other data, thereby reducing context window usage.

### Example Workflow

Below is a conceptual example (in pseudocode) illustrating the updated director-evaluator flow. In this scenario, the Director task returns a result with `status: 'CONTINUATION'` and an embedded `evaluation_request`:

```typescript
// Example TaskResult returned by the Director task
const taskResult: TaskResult = {
    content: "Initial solution output...",
    status: 'CONTINUATION',
    notes: {
        evaluation_request: {
            type: "bash_script",
            criteria: ["validate", "log"],
            target: "run_analysis.sh"
        }
    }
};
```

Upon receiving this result, the Evaluator:
1. Uses the `evaluation_request` details (including the target string) to perform associative matching and select an appropriate evaluation task template.
2. Dynamically spawns an evaluation subtask (the Child Task) with a `<context_management>` block set to inherit a subset of context.
3. If necessary, invokes the specified bash script callback via the Handler or its own mechanism.
4. Feeds the evaluation results back to the Director, allowing the overall task to continue.

## Integration with the Unified Architecture

The updated Director-Evaluator pattern fully embraces the dynamic subtask concept. Rather than a statically defined bash callback subtask, the evaluation step is triggered by the Director task's output. The Evaluator examines the task result for a `CONTINUATION` status and an embedded `evaluation_request`, then:
 - Uses associative matching (with help from the Memory System if needed) to select an evaluation template.
 - Dynamically spawns the evaluation subtask.
 - Invokes any specified bash script callback via the Handler or its own callback mechanism (since tasks remain reserved for LLM sessions).

**Key Characteristics:**

 - **Unified Model:** The pattern adheres to the unified context management and task execution model. All tasks, including those used for callbacks, use the same XML structure and TS types.

 - **Bash Script Callback:** The intermediary bash script is invoked as a subtask. Its output can be logged, used to adjust the environment, or to validate the parent task's results.

 - **Context Management:** The Evaluator subtask receives updated context via standard `<context_management>` settings (e.g. `inherit_context` set to `subset` and `accumulate_data` enabled).

## Conclusion

The updated Director-Evaluator pattern exemplifies the dynamic task–subtask paradigm. By returning a CONTINUATION status along with an embedded evaluation_request, a Director task signals that additional evaluation is required. The Evaluator then dynamically spawns an evaluation subtask—invoking a bash script callback via the Handler (or its own mechanism) if specified—to process and refine the output before feeding the results back to the parent task. This approach ensures flexibility and a seamless integration of external evaluation within the unified execution architecture.

## Static Director-Evaluator Variant

In addition to the dynamic pattern described above, a static variant is available for scenarios where the entire execution sequence is predetermined. In the static variant:
 - The Director Task generates the initial output.
 - A Target Script Execution task immediately runs an external command (e.g. a bash script) using the director's output.
 - The Evaluator Task then processes the output from the script.

### XML Template Example
```xml
<task type="sequential">
    <description>Static Director-Evaluator Pipeline</description>
    <context_management>
        <inherit_context>none</inherit_context>
        <accumulate_data>true</accumulate_data>
        <accumulation_format>notes_only</accumulation_format>
    </context_management>
    <steps>
        <!-- Director Task -->
        <task>
            <description>Generate Initial Output</description>
        </task>
        <!-- Target Script Execution -->
        <task type="script">
            <description>Run Target Script</description>
            <inputs>
                <input name="director_output">
                    <task>
                        <description>Pass director output to script</description>
                    </task>
                </input>
            </inputs>
        </task>
        <!-- Evaluator Task -->
        <task>
            <description>Evaluate Script Output</description>
            <inputs>
                <input name="script_output">
                    <task>
                        <description>Process output from target script</description>
                    </task>
                </input>
            </inputs>
        </task>
    </steps>
</task>
```
