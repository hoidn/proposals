# Director-Evaluator Pattern [Pattern:DirectorEvaluator:1.0]
 
# Overview

The Director-Evaluator pattern is a specialized variant of the unified task-subtask execution pattern. In this pattern a parent task (the **Director**) initiates the overall process by generating an initial solution or output. A **Bash Script Callback** is then executed to evaluate or adjust the environment, and finally a child task (the **Evaluator**) is spawned to refine the solution based on the callback's results.
 
# Pattern Description

This pattern follows a three-phase flow:

1. **Parent Task (Director):**
   - Generates an initial output based on the user's instructions.
   - Uses a `<context_management>` block with `inherit_context` set to `none` (i.e. no inherited context) since it starts a new execution chain.

2. **Bash Script Callback:**
   - Invoked as an intermediate subtask.
   - Runs a designated bash script (via a shell command) to evaluate the director's output.
   - May perform validation, logging, or environment adjustments.

3. **Child Task (Evaluator):**
   - Spawns after the bash script callback completes.
   - Uses a `<context_management>` block with `inherit_context` set to `subset` (to inherit only relevant context) and `accumulate_data` enabled (with an appropriate `accumulation_format`).
   - Refines or continues the execution based on the evaluated results.

# Example Workflow

Below is an example XML task definition that demonstrates the director-evaluator pattern:

```xml
<task type="sequential">
  <description>Director-Evaluator Pattern Example</description>
  <context_management>
    <inherit_context>none</inherit_context>
    <accumulate_data>false</accumulate_data>
  </context_management>
  <steps>
    <!-- Director Task: Generate initial output -->
    <task>
      <description>Generate Initial Solution</description>
      <!-- Implementation of the director's task -->
    </task>
    <!-- Bash Script Callback: Evaluate output and update context -->
    <task>
      <description>Bash Script Callback</description>
      <inputs>
        <input name="callback_script">
          <task>
            <description>Execute evaluation script via bash</description>
            <!-- This task runs a bash script to evaluate the initial output -->
          </task>
        </input>
      </inputs>
    </task>
    <!-- Evaluator Task: Refine solution based on callback output -->
    <task>
      <description>Refine Solution</description>
      <context_management>
        <inherit_context>subset</inherit_context>
        <accumulate_data>true</accumulate_data>
        <accumulation_format>notes_only</accumulation_format>
      </context_management>
      <!-- Implementation of the evaluator's task -->
    </task>
  </steps>
</task>
```

# Integration with the Unified Architecture

The Director-Evaluator pattern leverages the standard task-subtask framework. The intermediate bash script callback is specified as a subtask and does not require any new execution mechanism. Instead, it provides a hook where external evaluation (such as running a shell command) can update or validate the context before a subsequent child task (the Evaluator) continues processing.

**Key Characteristics:**

 - **Unified Model:** The pattern adheres to the unified context management and task execution model. All tasks, including those used for callbacks, use the same XML structure and TS types.

 - **Bash Script Callback:** The intermediary bash script is invoked as a subtask. Its output can be logged, used to adjust the environment, or to validate the parent task's results.

 - **Context Management:** The Evaluator subtask receives updated context via standard `<context_management>` settings (e.g. `inherit_context` set to `subset` and `accumulate_data` enabled).

# Conclusion

The Director-Evaluator pattern demonstrates how external evaluation (using, for example, a bash script) can be seamlessly integrated into the task execution flow. By treating the evaluation step as a subtask, the pattern maintains consistency with the unified architecture while enabling additional processing between the initial (director) task and subsequent (evaluator) task.

---

**Note:** The provided `director.py` is a conceptual example of this pattern. Under the updated architecture, the director-evaluator pattern is implemented using the standard task-subtask mechanism with an added bash callback step.
