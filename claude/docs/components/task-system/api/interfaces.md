# Task System Interfaces

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

// Memory System Interfaces
interface StorageFile {
  content: string;
  metadata: StorageMetadata;
}

interface WorkingFile {
  content: string;
  metadata: WorkingMetadata;
  sourceLocation: string;
}

interface MemorySystem {
  longTermStorage: {
    files: Map<string, StorageFile>;
    text: string;
  };
  shortTermMemory: {
    files: Map<string, WorkingFile>;
    dataContext: string;
  };
}
```