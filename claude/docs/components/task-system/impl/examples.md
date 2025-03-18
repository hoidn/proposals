# Task System Implementation Examples

> **Note:** For a detailed description of the Director‑Evaluator pattern, refer to [system/architecture/patterns/director-evaluator.md](../system/architecture/patterns/director-evaluator.md).

## Basic Task Execution
```typescript
// Initialize TaskSystem
const taskSystem = new TaskSystem({
  maxTurns: 10,
  maxContextWindowFraction: 0.8,
  systemPrompt: "Default system prompt"
});

// Register handlers
taskSystem.onError((error) => {
  console.error('Task error:', error);
});

taskSystem.onWarning((warning) => {
  console.warn('XML validation warning:', warning.message);
});

// Execute task
const result = await taskSystem.executeTask(
  "analyze data",
  memorySystem
);

// Check XML parsing status
if (!result.outputs.some(output => output.wasXMLParsed)) {
  console.warn("XML parsing failed, using fallback string output");
}
```

## Template Management
```typescript
const template: TaskTemplate = {
  taskPrompt: `<task>
    <task_instructions>Process data using specific format</description>
    <inputs>
      <input name="raw_data">
        <task_instructions>Load and validate input data</description>
        <expected_output>
          Validated data in standard format:
          - Field validations complete
          - Type conversions applied
          - Missing values handled
        </expected_output>
      </input>
    </inputs>
    <expected_output>
      Processed data meeting format requirements:
      - Correct structure
      - Valid field types
      - Complete required fields
    </expected_output>
  </task>`,
  systemPrompt: "Follow strict XML format",
  isManualXML: true,
  disableReparsing: true
};

// Validate template
const validation = taskSystem.validateTemplate(template);

if (!validation.valid) {
  console.warn('Template validation warnings:', validation.warnings);
}

// Find matching tasks
const matches = await taskSystem.findMatchingTasks(
  "analyze peak patterns",
  memorySystem
);

console.log('Found matching tasks:', 
  matches.map(m => ({
    score: m.score,
    type: m.taskType,
    template: m.template.taskPrompt
  }))
);
```

## Resource Management
```typescript
// Configure with resource limits
const taskSystem = new TaskSystem({
  maxTurns: 5,
  maxContextWindowFraction: 0.5,
  systemPrompt: "Resource-constrained execution"
});

try {
  const result = await taskSystem.executeTask(
    "process large dataset",
    memorySystem
  );
} catch (error) {
  if (error.type === 'RESOURCE_EXHAUSTION') {
    console.log('Resource limit exceeded:', error.resource);
    console.log('Usage metrics:', error.metrics);
  }
}
```

## Template Definition and Function Calling

### Basic Template Definition
```xml
<template name="validate_input" params="data,rules">
  <task type="atomic">
    <description>Validate {{data}} against {{rules}}</description>
    <context_management>
      <inherit_context>none</inherit_context>
      <fresh_context>disabled</fresh_context>
    </context_management>
  </task>
</template>
```

### Function Call with Variable Arguments
```xml
<call template="validate_input">
  <arg>user_input</arg>
  <arg>validation_schema</arg>
</call>
```

### Template with Return Type
```xml
<template name="extract_metrics" params="log_data" returns="object">
  <task type="atomic">
    <description>Extract performance metrics from {{log_data}}</description>
    <output_format type="json" schema="object" />
  </task>
</template>
```

### Complex Function Composition
```xml
<task type="sequential">
  <steps>
    <task>
      <description>Load input data</description>
    </task>
    <call template="validate_input">
      <arg>loaded_data</arg>
      <arg>{"required": ["name", "email"], "format": {"email": "email"}}</arg>
    </call>
    <call template="process_validated_data">
      <arg>validation_result</arg>
      <arg>processing_options</arg>
    </call>
  </steps>
</task>
```

### TypeScript Example
```typescript
// Register template
await taskSystem.registerTemplate({
  name: "analyze_data",
  parameters: ["dataset", "config"],
  body: {
    type: "atomic",
    description: "Analyze {{dataset}} using {{config}}",
    // Additional properties...
  },
  returns: "object"
});

// Execute function call
const result = await taskSystem.executeCall({
  templateName: "analyze_data",
  arguments: [
    "sensor_readings.csv",
    {method: "statistical", outliers: "remove"}
  ]
}, environment);

console.log("Analysis result:", result.content);
```

## Global Index Example
```typescript
// Minimal memory object focusing on file metadata
const memory = {
  getGlobalIndex() {
    return new Map([
      ['data.txt', 'metadata'],
      ['config.json', 'metadata'],
      ['history.log', 'metadata']
    ]);
  },
  updateGlobalIndex(index) {}
};

// Now we can pass this memory object to the taskSystem
const result = await taskSystem.executeTask("analyze recent changes", memory);
```

## Specialized Task Types

### Reparse Task Example
```typescript
const reparseTemplate: TaskTemplate = {
  taskPrompt: `<task type="reparse">
    <description>Decompose large task into smaller units</description>
    <failed_task>
      <error type="RESOURCE_EXHAUSTION">
        <resource>context</resource>
        <message>Context window limit exceeded</message>
      </error>
      <original_prompt>Process entire codebase</original_prompt>
    </failed_task>
  </task>`,
  systemPrompt: "Decomposition specialist",
  model: "claude-3-sonnet",
  isManualXML: true
};

try {
  const result = await taskSystem.executeTask(
    reparseTemplate.taskPrompt,
    memorySystem,
    "reparse"
  );
} catch (error) {
  console.error('Reparse failed:', error);
}
```

### Memory Task Example
```typescript
const memoryTemplate: TaskTemplate = {
  taskPrompt: `<task type="associative_memory">
    <description>Find relevant context for implementation</description>
    <query>error handling patterns</query>
    <constraints>
      <max_results>3</max_results>
      <relevance_threshold>0.8</relevance_threshold>
    </constraints>
  </task>`,
  systemPrompt: "Context retrieval specialist",
  model: "claude-3-sonnet"
};

const memoryResult = await taskSystem.executeTask(
  memoryTemplate.taskPrompt,
  memorySystem,
  "associative_memory"
);

console.log('Retrieved context:', memoryResult.content);
```

---

<!-- Example: Sequential Task with Data Accumulation -->
<task type="sequential">
    <description>Process and analyze data</description>
    <context_management>
        <inherit_context>none</inherit_context>
        <accumulate_data>true</accumulate_data>
        <accumulation_format>notes_only</accumulation_format>
        <fresh_context>enabled</fresh_context>
    </context_management>
    <steps>
        <task>
            <description>Load dataset</description>
            <inputs>
                <input name="data_file" from="csv_file_path"/>
            </inputs>
        </task>
        <task>
            <description>Filter invalid rows</description>
        </task>
    </steps>
</task>

<!-- Example: Static Director-Evaluator Loop with Script Execution -->
<task type="director_evaluator_loop">
  <description>Process and evaluate code</description>
  <max_iterations>3</max_iterations>
  <context_management>
    <inherit_context>none</inherit_context>
    <accumulate_data>true</accumulate_data>
    <accumulation_format>notes_only</accumulation_format>
    <fresh_context>enabled</fresh_context>
  </context_management>
  <director>
    <description>Generate Python code to solve problem: {{problem_statement}}</description>
    <inputs>
      <input name="problem_statement" from="user_query"/>
      <input name="feedback" from="evaluation_feedback"/>
      <input name="iteration" from="current_iteration"/>
    </inputs>
  </director>
  <script_execution>
    <command>python3 -c "{{script_input}}"</command>
    <timeout>5</timeout>
    <inputs>
      <input name="script_input" from="director_result"/>
    </inputs>
  </script_execution>
  <evaluator>
    <description>Evaluate code quality and execution results</description>
    <inputs>
      <input name="code" from="director_result"/>
      <input name="execution_output" from="script_output"/>
      <input name="execution_errors" from="script_errors"/>
      <input name="exit_code" from="script_exit_code"/>
    </inputs>
  </evaluator>
  <termination_condition>
    <condition>evaluation.success === true || iteration >= 3</condition>
  </termination_condition>
</task>
