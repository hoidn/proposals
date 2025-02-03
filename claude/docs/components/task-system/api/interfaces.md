# Task System Public API

/**
 * Note: The TaskResult returned by executeTask includes an optional "criteria" field,
 * which is a free-form description provided by the Director task for dynamic evaluation
 * template selection via associative matching.
 */

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

/**
 * Memory System interface for task execution
 * @see [Interface:Memory:3.0] (`/components/memory/api/interfaces.md`)
 */
import { MemorySystem, GlobalIndex, FileMatch } from '@/components/memory/api/interfaces';
```
