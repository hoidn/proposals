// https://claude.ai/chat/6f2dfd5b-7490-46e9-a6d2-43e1875132a2

# Task System Technical Specification

## 1. Component Overview

### Purpose and Responsibilities
The Task System is a core component responsible for:
1. XML task generation and validation
2. Task template matching and management
3. LLM session management via encapsulated Handlers
4. Management of specialized tasks (reparsing and associative memory)

### Core Functionality
1. Task Template Management
   - Store and retrieve task templates in XML format
   - Match human input to candidate task templates
   - Match AST nodes to candidate task templates
   - Support specialized template types for reparsing and memory operations

2. Handler Management  
   - Create and manage LLM sessions through encapsulated Handlers
   - Initialize Handlers with system prompts and resource constraints
   - Delegate prompt execution to Handlers
   - Surface Handler errors through the standard error type system

3. Task Execution
   - Process tasks using appropriate templates
   - Return both output and notes sections in TaskResult structure
   - Surface errors for task failure or resource exhaustion
   - Support specialized execution paths for reparsing and memory tasks

### Position in System Architecture
The Task System:
- Integrates directly with Memory System for context access
- Provides task parsing and validation services to Compiler
- Supports Evaluator's error recovery through reparsing templates
- Manages LLM interactions through encapsulated Handlers
- Does not maintain state about task progress or retries (Evaluator responsibility)
- Does not track resource usage directly (Handler responsibility)

### Primary Constraints and Limitations
1. Resource Management
   - Does not predict resource usage
   - Does not optimize task decomposition
   - Relies on Handlers for resource tracking and enforcement
   - Resource limits only influence reparsing/decomposition tasks

2. Task Templates
   - Stored as XML files in designated directories
   - No categories/groupings required beyond specialized tasks
   - No searching/filtering capabilities required
   - Basic XML validation only

3. Task Matching
   - Limited to top N candidates (aim for 5 or fewer)
   - Scoring is numeric only
   - Context limited to node level for AST matching
   - Initial environment limited to human-provided files

## 2. Interface Definition

### 2.1 Public Interface

### Core Types
```typescript
// Type for task structure based on operator.md
type TaskStructure = {
  type: TaskType;  // Sequential, Reduce, or Atomic
  description: string;
  subtasks?: TaskStructure[];
  parameters?: Record<string, string>;
}

// Task execution result
type TaskResult = {
  output: string;     // Task output content
  notes: string;      // Free-form notes including data usage
  error?: ErrorType;  // Optional error information
}

// Template definition
type TaskTemplate = {
  task_prompt: string;    // Main task prompt
  system_prompt: string;  // System context/instructions
  inputs?: {             // Optional input definitions
    name: string;
    placeholder?: string;
  }[];
}

// Scored template match
type TaskMatch = {
  score: number;        // Numeric score
  template: TaskTemplate;
}

// Handler configuration
type HandlerConfig = {
  max_turns: number;          // Turn limit
  max_context_tokens: number; // Context window size
  system_prompt: string;      // Base system prompt
}
```

### Public Methods

1. Template Matching
```typescript
// Match human input to task templates
matchHumanInput(
  input: string,
  environment: Environment
): TaskMatch[]

// Match AST node to task templates
matchAstNode(
  node: ASTNode
): TaskMatch[]
```

2. Task Execution
```typescript
// Execute task using template
executeTask(
  template: TaskTemplate,
  inputs: Record<string, string>,
  config: HandlerConfig
): TaskResult

// Execute specialized reparse task
executeReparseTask(
  failedNode: ASTNode,
  error: ErrorType,
  config: HandlerConfig
): TaskResult

// Execute memory task
executeMemoryTask(
  query: string,
  context: Environment,
  config: HandlerConfig
): TaskResult
```

3. Template Management
```typescript
// Load templates from disk
loadTemplates(
  directory: string
): void

// Validate template structure
validateTemplate(
  template: TaskTemplate
): boolean
```

### 2.2 Integration Points

### Memory System Integration
- Direct access to `Environment` structure:
```typescript
interface Environment {
  files: Map<string, WorkingFile>;
  dataContext: string;
}
```
- Read-only access pattern
- No state maintenance

### Compiler Integration
- Provides task parsing validation
- Returns structured errors for invalid XML
- Supplies templates for task generation
- No compilation state maintenance

### Evaluator Integration
- Surfaces errors through standard error types
- Returns consistent TaskResult format
- No progress/retry tracking
- Clean separation of execution state

### Handler Integration
- Internal to Task System
- Created per task execution
- Configured with:
  - Resource limits (turns, context size)
  - System prompts
  - Error handling callbacks
- Handles all LLM interactions
- Reports resource usage and errors

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
- Read-only operations
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
- Read-only operations

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
