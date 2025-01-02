# Task System Interfaces

For complete type definitions and implementation details, see:
- Core types: [Type:TaskSystem:1.0] in spec/types.md
- Internal interfaces: spec/interfaces.md
- XML schema: [Contract:Tasks:TemplateSchema:1.0] in protocols.md

## Core Types
```typescript
// Task Results
interface TaskResult { 
  content: string;
  notes: {
    dataUsage: string;
  };
}

// Task Types
type TaskType = "atomic" | "sequential" | "map" | "reduce";
type AtomicTaskSubtype = "standard" | "subtask";

// Task Templates
interface TaskTemplate {
  readonly taskPrompt: string;     // Maps to <instructions> in schema
  readonly systemPrompt: string;   // Maps to <system> in schema
  readonly model: string;          // Maps to <model> in schema
  readonly inputs?: Record<string, string>;
  readonly isManualXML?: boolean;     // Maps to <manual_xml> in schema
  readonly disableReparsing?: boolean; // Maps to <disable_reparsing> in schema
  readonly atomicSubtype?: AtomicTaskSubtype;  // Only for atomic tasks
}

// Primary Interface
interface TaskSystem {
  executeTask(
    task: string,
    context: MemorySystem,
    taskType?: TaskType
  ): Promise<TaskResult>;

  validateTemplate(template: TaskTemplate): boolean;
  
  findMatchingTasks(
    input: string,
    context: MemorySystem
  ): Promise<Array<{
    template: TaskTemplate;
    score: number;
    taskType: TaskType;
  }>>;
}

// Memory System Interface
interface MemorySystem {
  // Short term memory for task context
  shortTermMemory: {
    content: string;  // Unstructured text content
    files: {
      paths: string[];  // Available file paths
      modified: Set<string>;  // Which files modified on disk
    };
  };
  
  // Long term memory for potential persistence
  longTermMemory: {
    content: string;  // Unstructured text content 
    files: {
      paths: string[];  // Paths of stored files
    };
  };
}
```
