# Task System Implementation Examples

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
        <inherit_context>false</inherit_context>
        <accumulate_data>true</accumulate_data>
        <accumulation_format>notes_only</accumulation_format>
    </context_management>
    <steps>
        <task>
            <description>Load dataset</description>
            <inputs>
                <input name="data_file">
                    <task>
                        <description>Read input CSV file</description>
                    </task>
                </input>
            </inputs>
        </task>
        <task>
            <description>Filter invalid rows</description>
        </task>
    </steps>
</task>

<!-- Example: Static Director-Evaluator with Script Execution -->
<task type="sequential">
    <description>Static Director-Evaluator Pipeline</description>
    <context_management>
        <inherit_context>none</inherit_context>
        <accumulate_data>true</accumulate_data>
        <accumulation_format>notes_only</accumulation_format>
    </context_management>
    <steps>
        <task>
            <description>Generate Initial Output</description>
        </task>
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
