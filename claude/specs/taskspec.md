# Simplified Director-Evaluator Flow Specification
> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

- Implement a simplified Director-Evaluator flow that only retains the latest evaluator output, reducing context window usage and simplifying error recovery.

## Mid-Level Objective

- Update the XML schema in `protocols.md` to support the new context management protocol and environment variable definitions.
- Modify the type definitions in `types.md` to include the `EvaluationResult` interface and update environment handling.
- Update the Evaluator component documentation to reflect the new single output handling and environment management.
- Revise the implementation design to incorporate output slot management and environment preparation.
- Update the Director-Evaluator pattern documentation with the simplified flow and new XML examples.

## Implementation Notes

- The evaluator will output an `EvaluationResult` object with `success` and `feedback` fields.
- Introduce a single environment variable `last_evaluator_output` to store the latest evaluator output.
- Upon continuation, all other environment variables are cleared except for `last_evaluator_output`.
- Update the `<context_management>` defaults to `<inherit_context>none</inherit_context>` and `<accumulate_data>false</accumulate_data>`.
- Add `<output_slot>` and `<input_source>` elements to the XML schema `<task>` definition.
- Ensure backward compatibility with existing templates and systems.
- Follow existing coding standards and ensure all changes are well-documented.

## Context

### Beginning Context

- `./system/contracts/protocols.md`
- `./components/task-system/spec/types.md`
- `./components/evaluator/README.md`
- `./components/task-system/impl/design.md`
- `./system/architecture/patterns/director-evaluator.md`

### Ending Context

- `./system/contracts/protocols.md` (updated)
- `./components/task-system/spec/types.md` (updated)
- `./components/evaluator/README.md` (updated)
- `./components/task-system/impl/design.md` (updated)
- `./system/architecture/patterns/director-evaluator.md` (updated)

## Low-Level Tasks
> Ordered from start to finish

1. **Update the XML Schema in `protocols.md`**

```aider
UPDATE ./system/contracts/protocols.md:

- ADD the `EvaluationResult` type definition to the XML Schema Definition section:

  ```xml
  <xs:complexType name="EvaluationResult">
    <xs:sequence>
      <xs:element name="success" type="xs:boolean"/>
      <xs:element name="feedback" type="xs:string" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  ```

- ADD `<output_slot>` and `<input_source>` elements to the `<task>` element definition:

  ```xml
  <xs:element name="task">
    <xs:complexType>
      <xs:sequence>
        <!-- Existing elements -->
        <xs:element name="output_slot" type="xs:string" minOccurs="0"/>
        <xs:element name="input_source" type="xs:string" minOccurs="0"/>
        <!-- Other elements -->
      </xs:sequence>
      <!-- Attributes -->
    </xs:complexType>
  </xs:element>
  ```

- UPDATE the `<context_management>` defaults in the Context Management Protocol section:

  ```xml
  <context_management>
      <inherit_context>none</inherit_context>
      <accumulate_data>false</accumulate_data>
  </context_management>
  ```

- ADD script execution error handling specifics under the "Script Execution Support" section, specifying how non-zero exit codes are handled and how stdout and stderr are captured.

```

2. **Modify Types in `types.md`**

```aider
UPDATE ./components/task-system/spec/types.md:

- ADD the `EvaluationResult` interface:

  ```typescript
  export interface EvaluationResult {
      success: boolean;
      feedback?: string;
  }
  ```

- UPDATE the `DirectorEnv` interface:

  ```typescript
  export interface DirectorEnv extends Environment {
      last_evaluator_output: string | null;
      // Other variables are cleared on continuation
  }
  ```

- ADD the `prepareContinuationEnv` function type:

  ```typescript
  function prepareContinuationEnv(currentEnv: Environment): Environment {
      return new Environment({
          last_evaluator_output: currentEnv.get('last_evaluator_output')
      });
  }
  ```

- ADD the `storeEvaluatorResult` function type:

  ```typescript
  function storeEvaluatorResult(result: TaskResult, env: Environment): void {
      env.set('last_evaluator_output', result.content);
      env.clearExcept(['last_evaluator_output']);
  }
  ```

```

3. **Update Evaluator Documentation in `README.md`**

```aider
UPDATE ./components/evaluator/README.md:

- DOCUMENT the handling of the single output variable `last_evaluator_output` in the "Context and Environment Handling" section.
- UPDATE the "Context Management" section to reflect that `<inherit_context>` is `none` and `<accumulate_data>` is `false` in the new protocol.
- ADD details about script execution and feedback flow, including how the evaluator captures the script's `stdout`, `stderr`, and `exitCode`, and stores them in `last_evaluator_output` as an `EvaluationResult`.
- UPDATE environment handling documentation to explain that upon continuation, all environment variables are cleared except for `last_evaluator_output`.

```

4. **Adjust Implementation Design in `design.md`**

```aider
UPDATE ./components/task-system/impl/design.md:

- ADD a subsection under "Environment Management" detailing the design for output slot management using `last_evaluator_output`.
- DOCUMENT the environment preparation process using the `prepareContinuationEnv` function to retain only `last_evaluator_output`.
- UPDATE context clearing rules to specify that all variables except `last_evaluator_output` are cleared upon continuation.
- ADD script execution handling details under "Script Execution Implementation", explaining how the evaluator executes the script task, captures the outputs, and stores the result in the environment.

```

5. **Revise Director-Evaluator Pattern Documentation in `director-evaluator.md`**

```aider
UPDATE ./system/architecture/patterns/director-evaluator.md:

- UPDATE the flow description to reflect that only the latest evaluator output is retained, simplifying the feedback loop.
- DOCUMENT environment variable management, specifying that `last_evaluator_output` stores the evaluator's output and that other variables are cleared on continuation.
- ADD a section under "Static Director-Evaluator Variant" to include the simplified flow and explain the script execution pattern.
- UPDATE XML examples to use the new context management defaults and to include `<output_slot>` and `<input_source>` elements:

  ```xml
  <task type="director">
      <output_slot>last_evaluator_output</output_slot>
  </task>

  <task type="evaluator">
      <input_source>last_evaluator_output</input_source>
  </task>
  ```

```