# Sequential and Reduce Operator Specification

## Purpose
Define the structure and semantics of Sequential and Reduce operators for task composition and execution, specifying XML schemas and execution behaviors.

## Memory Structure
```typescript
shortTermMemory: {
    files: Map<string, WorkingFile>;
    dataContext: string;
}
```

## Sequential Operator

### Purpose
Execute a series of tasks with explicit dependencies. Maintains execution order while allowing parallel execution of independent inputs.

### Structure
```xml
<task type="sequential">
    <description>Overall sequence description</description>
    <inherit_context>true</inherit_context>
    <steps>
        <!-- Task without dependencies -->
        <task>
            <description>Process raw data</description>
            <inputs>
                <input name="raw_file">
                    <task>
                        <description>Load data file</description>
                    </task>
                </input>
            </inputs>
        </task>
        
        <!-- Task with multiple parallel inputs -->
        <task>
            <description>Combine processed results</description>
            <inputs>
                <input name="processed_data">
                    <!-- Reference to previous task -->
                    <task>
                        <description>Transform data format</description>
                    </task>
                </input>
                <input name="configuration">
                    <task>
                        <description>Load config settings</description>
                    </task>
                </input>
            </inputs>
        </task>
    </steps>
</task>
```

### Execution Semantics
- Tasks execute in specified order
- For tasks with multiple inputs:
  - All input tasks execute in parallel
  - Parent task executes after all inputs complete
- Execution fails if:
  - Required task structure is missing/invalid
  - Any task execution fails (with failure context indicating which task)

## Reduce Operator

### Purpose
Process a list of named inputs through repeated application of inner task and reduction operations.

### Structure
```xml
<task type="reduce">
    <description>Reduction operation description</description>
    <initial_value>
        <!-- Initial accumulator value -->
    </initial_value>
    <inputs>
        <input name="dataset1">Value 1</input>
        <input name="dataset2">Value 2</input>
        <input name="dataset3">Value 3</input>
    </inputs>
    <inner_task>
        <description>Processing for each input</description>
        <inputs>
            <input name="current_data">
                <!-- Current input being processed -->
            </input>
            <input name="metadata">
                <!-- Additional input needed for processing -->
                <task>
                    <description>Load metadata for processing</description>
                </task>
            </input>
        </inputs>
    </inner_task>
    <reduction_task>
        <description>Combine current result with accumulator</description>
        <inputs>
            <input name="current_result">
                <!-- Result from inner_task -->
            </input>
            <input name="accumulator">
                <!-- Current accumulated value -->
            </input>
            <input name="original_input">
                <!-- Original input being processed -->
            </input>
        </inputs>
    </reduction_task>
</task>
```

### Execution Semantics
- For each named input:
  1. Execute inner_task with:
     - Current input
     - Any additional specified inputs
  2. Execute reduction_task with:
     - Current inner_task result
     - Current accumulator value
     - Original input
  3. Result becomes new accumulator value
- Maintains strict ordering of input processing
- Context changes managed by memory system
- Execution fails if:
  - Required task structure is missing/invalid 
  - Any inner_task execution fails (with failure context indicating which input)
  - Any reduction_task execution fails (with failure context indicating current state)

## Integration Points

### With Memory System
- System maintains execution context via shortTermMemory
- Files and data context available to all tasks
- Context changes managed by memory system, not tasks

### With Task System
- Responsible for generating valid XML
- Manages task decomposition on failure
- Handles task library matching

## Dependencies
- Error types defined in errorspec.md
- Memory system must handle context
- Task system must support XML generation

## Constraints
- Tasks cannot modify context directly
- XML structure must encode all input dependencies
- All inputs must have unique names within their scope
- Inner tasks can specify multiple inputs
