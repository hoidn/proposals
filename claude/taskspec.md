// https://claude.ai/chat/6f2dfd5b-7490-46e9-a6d2-43e1875132a2

# TODO we should give the user the option to manually 
# construct an xml composite (or atomic) task structure and 
# have that parsed, instead of using a simple natural language 
# prompt
# TODO we might want to consider prompt chaining, at least 
# for sequential operations 

# TODO let's have the task output be a list of xml-demarcated strings,
# instead of just a single unstructured string

# TODO the handler configuration should be passed to the constructor / 
# instantiating function, not to a separate config method

# TODO initial context should include both a literal concatenation 
# of files *and* a file collection component

# Task System Technical Specification

## 1. Purpose and Responsibilities

The Task System is a core component responsible for:
- XML task generation and validation, including fallback behavior and warning generation
- Task template matching and management
- LLM session management via encapsulated Handlers
- Management of specialized tasks (reparsing and associative memory)
- XML output parsing with graceful degradation

## 2. Core Functionality

### 2.1 Task Template Management

- Store and retrieve task templates in XML format
- Match human input to candidate task templates
- Match AST nodes to candidate task templates
- Support specialized template types for reparsing and memory operations
- Basic XML structure validation with warning generation
- Support manual XML tasks with optional reparsing flag
- Maintain task template persistence in disk-based XML format

### 2.2 Handler Management

- Create and manage LLM sessions through encapsulated Handlers
- Initialize Handlers with immutable configuration:
  - System prompts
  - Resource constraints
  - Turn limits
  - Context window limits
- Delegate prompt execution to Handlers
- Surface Handler errors through the standard error type hierarchy
- Ensure proper context propagation through Handler lifecycle

### 2.3 Task Execution

- Process tasks using appropriate templates
- Return both output and notes sections in TaskResult structure
- Surface errors for task failure or resource exhaustion
- Support specialized execution paths for reparsing and memory tasks
- Implement lenient XML output parsing with fallback to single string
- Generate warnings for malformed XML without blocking execution
- Include 'data usage' section in task notes as specified by system prompt

## 3. Position in System Architecture

The Task System:
- Integrates directly with Memory System for read-only context access
- Provides task parsing and validation services to Compiler
- Supports Evaluator's error recovery through reparsing templates
- Manages LLM interactions through encapsulated Handlers
- Does not maintain state about task progress or retries (Evaluator responsibility)
- Does not track resource usage directly (Handler responsibility)
- Provides XML parsing services with fallback behavior

## 4. Primary Constraints and Limitations

### 4.1 Resource Management

- Does not predict resource usage
- Does not optimize task decomposition
- Relies on Handlers for resource tracking and enforcement
- Resource limits only influence reparsing/decomposition tasks
- No responsibility for context window management

### 4.2 Task Templates

- Stored as XML files in designated directories
- Support both LLM-generated and manual XML structures
- Basic XML validation with warning generation
- XML output parsing with graceful degradation to single string
- Support for disabling reparsing on manual XML tasks

### 4.3 Task Matching

- Limited to top N candidates (aim for 5 or fewer)
- Scoring is numeric only
- Context limited to node level for AST matching
- Initial environment limited to human-provided files
- Scoring logic contained within matching prompts

### 4.4 Memory System Integration

- Direct access to memory system interfaces
- Uses Memory System interfaces:
  ```typescript
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

### 4.5 Configuration Constraints

- Handler configuration immutable after initialization
- Required configuration parameters:
  - max_turns (with default)
  - max_context_window_fraction (with default)
  - system_prompt (defaults to empty string)
- No runtime configuration changes supported

### 4.6 XML Processing

- Basic structural validation only
- Warning generation for validation issues
- Lenient output parsing with fallback to single string
- Graceful handling of partially valid XML
- No validation beyond basic XML structure
- Support for manual XML task flag to disable reparsing

## 5. Future Considerations

System design should accommodate:
- Prompt chaining capabilities
- Backreferences and indexing
- Enhanced task template management
- Additional specialized task types
- Template library expansion

## 6. Dependencies

- Memory System for context access
- Evaluator for error handling and recovery
- Handler for LLM session management
- File system for template storage

# Task System Interface Definition

## 2.1 Public Interface

### Core Types

```typescript
// Task Results
interface TaskResult {
  outputs: Array<{
    name?: string;
    content: string;
    parsedFromXML: boolean;
  }>;
  notes: {
    dataUsage: string; // Free-form data usage info from LLM
    xmlParsingWarnings?: Array<Warning>;
    [key: string]: any;
  };
}

// Handler Events
type HandlerEvent = 
  | { type: 'ERROR'; error: TaskError }
  | { type: 'WARNING'; warning: Warning }

// Task Templates
interface TaskTemplate {
  readonly taskPrompt: string;
  readonly systemPrompt: string;
  readonly isManualXML?: boolean;
  readonly disableReparsing?: boolean;
  inputs?: Record<string, string>;
}

// Configuration
interface TaskConfig {
  readonly maxTurns: number;
  readonly maxContextWindowFraction: number;
  readonly systemPrompt?: string;
}

// Warning System
interface Warning {
  type: 'XML_VALIDATION';
  message: string;
}

type WarningCallback = (warning: Warning) => void;

// Memory System
interface StorageFile {
  content: string;
  metadata: StorageMetadata;
}

interface WorkingFile {
  content: string;
  metadata: WorkingMetadata;
  sourceLocation: string;
}

interface StorageMetadata {
  path: string;
  summary?: string;
  lastModified: Date;
  type?: string;
}

interface WorkingMetadata {
  path: string;
  summary?: string;
  loadedAt: Date;
  status: 'active' | 'stale';
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

// Task Types
type TaskType = 'standard' | 'reparse' | 'associative_memory';

// Error Types
interface TaskError {
  type: 'RESOURCE_EXHAUSTION' | 'INVALID_OUTPUT' | 'NO_PROGRESS';
  details: {
    resource?: 'turns' | 'context' | 'output';
    message: string;
    context?: any;
  };
}

// AST Node Type
interface ASTNode {
  type: string;
  content: string;
  children?: ASTNode[];
  metadata?: Record<string, any>;
}
```

### Primary Interface

```typescript
interface TaskSystemConstructor {
  new (config: TaskConfig): TaskSystem;
}

interface TaskSystem {
  // Task Execution
  executeTask(
    task: string,
    context: MemorySystem,
    taskType?: TaskType
  ): TaskResult;

  // Template Management
  validateTemplate(
    template: TaskTemplate,
    allowManualXML?: boolean
  ): {
    valid: boolean;
    warnings: Warning[];
  };
  
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

  // Event Handling
  onError(callback: (error: TaskError) => void): void;
  onWarning(callback: WarningCallback): void;
}
```

## 2.2 Integration Points

### With Compiler
```typescript
interface CompilerIntegration {
  validateTaskStructure(
    xml: string,
    allowManualXML?: boolean
  ): {
    valid: boolean;
    warnings: Warning[];
  };
}
```

### With Memory System

The system uses the MemorySystem interface directly without additional wrapping, as defined in the Core Types section.

## Data Flow Patterns

1. Task Execution Flow:
   ```
   Input -> Task Matching -> Handler Creation -> Execution -> Result
                                            \-> Errors   -> Error Callback
                                            \-> Warnings -> Warning Callback
   ```

2. Template Management Flow:
   ```
   Load -> Validate -> Store
   ```

3. Error Flow:
   ```
   Error Detection -> Error Callback -> Continue/Abort based on Error Type
   ```

4. Warning Flow:
   ```
   Warning Detection -> Warning Callback -> Continue Execution
   ```

## Example Usage

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
if (!result.outputs.some(output => output.parsedFromXML)) {
  console.warn("XML parsing failed, using fallback string output");
}

// Validate manual XML template
const template: TaskTemplate = {
  taskPrompt: "Process data using specific format",
  systemPrompt: "Follow strict XML format",
  isManualXML: true,
  disableReparsing: true
};

const validation = taskSystem.validateTemplate(template, true);

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

## 3. Behavioral Requirements

### 3.1 Core Operations

### Task Template Matching

1. Human Input Matching
- Input: Natural language text + initial environment
- Process:
  - Uses matching specialized task from library
  - Considers provided files in environment
  - No access to previous executions/history
- Output: 
  - Up to 5 highest-scoring templates
  - Each match includes numeric score and template
  - Templates ordered by descending score

2. AST Node Matching
- Input: Single AST node
- Process:
  - Uses node-specific matching task
  - Only considers node-level context
  - No traversal of parent/child nodes
- Output:
  - Up to 5 highest-scoring templates
  - Each match includes numeric score and template
  - Templates ordered by descending score

### Task Execution

1. Standard Task Execution
- Preparation:
  - Create new Handler instance
  - Configure resource limits
  - Set system prompt
- Execution:
  - Handler manages LLM interaction
  - Enforces resource constraints
  - Captures output and notes
- Result:
  - Returns TaskResult structure
  - Includes any error information
  - Free-form notes with data usage

2. Specialized Task Execution

A. Reparse Tasks
- Triggered by:
  - Resource exhaustion errors
  - Invalid output errors
  - Progress failure errors
- Uses specialized templates from separate directory
- Returns new task structure or alternative approach

B. Memory Tasks
- Direct memory system access
- Uses associative matching templates
- Returns relevant context selections

### 3.2 Error Handling

### Error Detection
1. Resource Exhaustion
- Handler detects limit violations
- Immediate task termination
- Surfaces through standard error type

2. Invalid Output
- Structural validation failure
- Format validation errors
- No semantic validation

3. Failure to Make Progress
- Handler detects stalled execution
- Task-specific progress indicators
- No internal progress tracking

### Error Response
1. Error Surfacing
- Uses standard error type system
- Includes relevant task notes
- Preserves partial outputs when useful

2. Handler Cleanup
- Clean termination of LLM session
- Resource accounting completion
- No state preservation

3. No Recovery Logic
- No retry attempts
- No state maintenance
- Delegates to evaluator

### 3.3 Resource Management

### Turn Counter Management
1. Handler Configuration
- Set maximum turns per task
- Per-Handler tracking
- No cross-Handler pooling

2. Enforcement
- Handler tracks turn usage
- Raises resource exhaustion error on limit
- No turn prediction/optimization

### Context Window Management
1. Size Limits
- Set maximum context tokens
- Per-Handler enforcement
- No content optimization

2. Monitoring
- Handler tracks token usage
- Raises resource exhaustion error on limit
- No pre-execution estimation

### Memory Usage
1. Access Patterns
- Direct access to Memory System
- Standard memory structure

2. Constraints
- No state maintenance
- No caching
- No cross-task persistence

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
describe("Memory Integration", () => {
  test("environment access", () => {
    // file access
    // context access
  });
  
  test("read-only operations", () => {
    // no state modification
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
- Handler resource limit optimization
- Template management strategy

### Integration Risks
- Memory System coordination
- Error propagation completeness
- Resource management effectiveness
