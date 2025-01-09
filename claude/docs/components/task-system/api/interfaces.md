# Task System Public API

## References

- Core Types: See [Type:TaskSystem:1.0] (`/components/task-system/spec/types.md`)
- Implementation: See `/components/task-system/spec/interfaces.md`
- XML Schema: See [Contract:Tasks:TemplateSchema:1.0] (`/system/contracts/protocols.md`)

```typescript
/**
 * Public API Surface
 * All types imported from [Type:TaskSystem:1.0]:
 * - TaskTemplate
 * - TaskResult 
 * - TaskType

/** 
 * For the full Handler interface definition, see [Interface:Handler:1.0] in spec/interfaces.md
 */

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

/** @see [Interface:Memory:3.0] (`/components/memory/api/interfaces.md`) */
interface MemorySystem {
    getContext(): Promise<string>;
    getGlobalIndex(): Promise<GlobalIndex>;
    updateGlobalIndex(index: GlobalIndex): Promise<void>;
}
```
