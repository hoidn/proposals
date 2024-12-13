// first three sections on high level requirements moved to taskspec_requirements.md
## 4. Internal Architecture

### 4.1 Key Components

### Task Library Manager
1. Template Storage
```typescript
interface TemplateStorage {
  standardTemplates: Map<string, TaskTemplate>;  // Regular task templates
  reparseTemplates: Map<string, TaskTemplate>;   // Decomposition/alternative templates
  memoryTemplates: Map<string, TaskTemplate>;    // Memory operation templates
}
```

2. Operations
- Load templates from disk directories
- Parse XML to TaskTemplate structures
- Validate required fields (task_prompt, system_prompt)
- Separate specialized templates (reparse, memory)

3. Validation Rules
- Basic XML structure checking
- Required field presence
- No semantic validation
- Warning generation for missing optional fields

### Handler Manager
1. Handler Creation
```typescript
interface HandlerManager {
  createHandler(config: HandlerConfig): Handler;
  configureHandler(handler: Handler, template: TaskTemplate): void;
  executePrompt(handler: Handler, inputs: Record<string, string>): TaskResult;
}
```

2. Configuration
- Sets resource limits (turns, context size)
- Applies system prompt
- Configures error callbacks

3. Lifecycle Management
- One Handler per task execution
- Clean termination after task completion
- No state preservation between tasks

### Task Matcher
1. Matching Logic
```typescript
interface TaskMatcher {
  matchHumanInput(input: string, env: Environment): TaskMatch[];
  matchAstNode(node: ASTNode): TaskMatch[];
  scoreTemplate(template: TaskTemplate, context: string): number;
}
```

2. Scoring Implementation
- Numeric scores only
- Template-specific scoring prompts
- Return top candidates (≤5)

### Task Executor
1. Execution Flow
```typescript
interface TaskExecutor {
  executeTask(template: TaskTemplate, inputs: Record<string, string>): TaskResult;
  executeReparseTask(node: ASTNode, error: ErrorType): TaskResult;
  executeMemoryTask(query: string, context: Environment): TaskResult;
}
```

2. Task Processing
- Template preparation
- Handler creation and configuration
- Output collection
- Error handling

### 4.2 Design Decisions

### 1. Component Separation
1. Handler Encapsulation
- Rationale: Isolate LLM interaction complexity
- Benefit: Clean resource management
- Impact: Simplified error handling

2. Template Management
- Rationale: Separate template storage from matching
- Benefit: Clear separation of concerns
- Impact: Easier template maintenance

3. Execution Flow
- Rationale: Single responsibility per component
- Benefit: Clear error boundaries
- Impact: Simplified testing

### 2. Resource Handling
1. Per-Task Handlers
- Rationale: Clean resource tracking
- Benefit: Isolated failure domains
- Impact: Predictable resource usage

2. Direct Memory Access
- Rationale: Simplified context management
- Benefit: Clear data flow
- Impact: Reduced interface complexity

### 3. Error Management
1. Standard Error Types
- Rationale: Consistent error handling
- Benefit: Clear error propagation
- Impact: Simplified recovery paths

2. No State Maintenance
- Rationale: Clean component boundaries
- Benefit: Simplified recovery
- Impact: Predictable behavior

### 4. Performance Considerations
1. Template Loading
- Load templates at startup
- Cache parsed structures
- Validate on load

2. Handler Management
- Create per execution
- No connection pooling
- Clean termination

3. Memory Access
- Direct access pattern
- No caching layer

## 5. Testing Requirements

### 5.1 Unit Testing

### Template Management Tests
1. Loading Tests
- Verify template loading from XML files
- Validate specialized template separation
- Test handling of malformed XML
- Verify warning generation for optional fields

2. Validation Tests
```typescript
describe("Template Validation", () => {
  test("required fields present", () => {
    // task_prompt and system_prompt required
  });
  
  test("optional fields handling", () => {
    // inputs can be empty/missing
  });
  
  test("specialized template identification", () => {
    // reparse and memory templates properly categorized
  });
});
```

### Handler Management Tests
1. Creation Tests
```typescript
describe("Handler Creation", () => {
  test("proper initialization", () => {
    // resource limits set
    // system prompt configured
  });
  
  test("resource tracking", () => {
    // turn counter initialization
    // context window tracking
  });
});
```

2. Resource Management Tests
- Turn limit enforcement
- Context window limit enforcement
- Resource exhaustion error generation
- Clean termination

### Task Matching Tests
1. Human Input Matching
```typescript
describe("Human Input Matching", () => {
  test("environment consideration", () => {
    // verifies use of provided files
  });
  
  test("candidate limiting", () => {
    // max 5 candidates returned
  });
  
  test("score ordering", () => {
    // descending score order
  });
});
```

2. AST Node Matching
- Node-level context handling
- Template scoring implementation
- Candidate selection and ordering

### Task Execution Tests
1. Standard Tasks
```typescript
describe("Task Execution", () => {
  test("task result format", () => {
    // output and notes present
    // error handling
  });
  
  test("resource usage", () => {
    // within configured limits
  });
});
```

2. Specialized Tasks
- Reparse task execution
- Memory task execution
- Error propagation

### 5.2 Integration Testing

### Memory System Integration
1. Access Patterns
```typescript
describe("Memory System Integration", () => {
  test("memory system access", () => {
    // verify memory system instance received correctly 
    // verify no environment bindings accessed
  });
  
  test("memory operations", () => {
    // no state modification
    // no direct environment access
  });
});
```

2. Context Management
- Environment structure handling
- Context propagation
- Error conditions

### Error Handling Integration
1. Error Propagation
```typescript
describe("Error Handling", () => {
  test("resource exhaustion", () => {
    // proper error type
    // handler cleanup
  });
  
  test("invalid output", () => {
    // error details
    // partial results
  });
});
```

2. Recovery Flows
- Error type generation
- Error detail preservation
- Handler cleanup

### Resource Management Integration
1. Handler Resource Usage
```typescript
describe("Resource Management", () => {
  test("turn tracking", () => {
    // across multiple operations
  });
  
  test("context limits", () => {
    // across task execution
  });
});
```

2. System Resource Coordination
- Multiple handler management
- Resource limit enforcement
- Cleanup verification

### End-to-End Flows
1. Task Processing
```typescript
describe("Task Processing", () => {
  test("complete task flow", () => {
    // template matching
    // execution
    // result handling
  });
  
  test("error conditions", () => {
    // various failure modes
    // recovery paths
  });
});
```

2. System Integration
- Cross-component interaction
- Error handling
- Resource management

## 6. Open Questions & Risks

### Design Questions
- Task matching quality evaluation approach 
- Template management strategy

### Integration Risks
- Error propagation completeness
