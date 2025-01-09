# Task System Interfaces

For complete type definitions see [Type:TaskSystem:1.0] in spec/types.md.
For implementation details see spec/interfaces.md.
For XML schema see [Contract:Tasks:TemplateSchema:1.0] in protocols.md.

```typescript
/**
 * Task Template Interface [Type:TaskSystem:TaskTemplate:1.0]
 * See [Contract:Tasks:TemplateSchema:1.0] for XML schema mapping
 */
interface TaskTemplate {
    readonly taskPrompt: string;     // Maps to <instructions> in schema
    readonly systemPrompt: string;   // Maps to <system> in schema
    readonly model: string;          // Maps to <model> in schema
    readonly inputs?: Record<string, string>;
    readonly isManualXML?: boolean;      // Maps to <manual_xml> in schema
    readonly disableReparsing?: boolean; // Maps to <disable_reparsing> in schema
}

/**
 * Primary task execution interface
 * Uses [Type:TaskSystem:TaskType:1.0] and [Type:TaskSystem:TaskError:1.0]
 */
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

/** Memory System Interface [Interface:Memory:3.0] */
interface MemorySystem {
    getContext(): Promise<string>;
    getGlobalIndex(): Promise<GlobalIndex>;
    updateGlobalIndex(index: GlobalIndex): Promise<void>;
}
```
