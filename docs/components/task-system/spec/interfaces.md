# Task System Interfaces

## Core Interfaces

### TaskSystem 

Primary interface for task execution and management.

```typescript
interface TaskSystem {
  // Task Execution
  executeTask(
    task: string,
    context: MemorySystem,
    taskType?: TaskType
  ): TaskResult;

  // Template Management
  validateTemplate(template: TaskTemplate): boolean;
  
  // Task Matching
  findMatchingTasks(
    input: string,
    context: MemorySystem
  ): Array<{
    template: TaskTemplate;
    score: number;
    taskType: TaskType;
  }>;

  findMatchingTasksForNode(
    node: ASTNode,
    context: MemorySystem
  ): Array<{
    template: TaskTemplate;
    score: number;
    taskType: TaskType;
  }>;
}
```

### Handler

Manages individual LLM conversation sessions.

```typescript
interface Handler {
  /**
   * Execute a prompt with the LLM
   * @param systemPrompt - System-level context and instructions
   * @param taskPrompt - Task-specific input
   * @returns Promise resolving to LLM response
   */
  executePrompt(
    systemPrompt: string,
    taskPrompt: string
  ): Promise<string>;

  /**
   * Callback for handling agent input requests
   * @param agentRequest - The agent's request for user input
   * @returns Promise resolving to user's input
   */
  onRequestInput: (agentRequest: string) => Promise<string>;
}
```

#### Contract
- Created and managed by TaskSystem
- One Handler per task execution
- Maintains conversation context
- Tracks resource usage (turns, context window)
- Detects when agent requests user input
- Handles synchronous conversation flow

#### Resource Management
- Turns and context window tracked per session
- Resource limits enforced across all interactions
- Input requests count as turns

#### Error Handling
- Resource exhaustion errors possible during any interaction
- Input requests may be rejected if limits exceeded
- Failed input requests terminate session
