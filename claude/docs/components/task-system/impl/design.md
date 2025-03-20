# Implementation Design

## Terminology and References

 - **Handler** and **Evaluator** definitions are standardized in [spec/types.md](../spec/types.md).
 - XML schema definitions are available in [system/contracts/protocols.md](../system/contracts/protocols.md).
 - For detailed resource tracking implementation (including turn counter and context window monitoring), see [resource-management.md](./resource-management.md).
 - For XML processing details (parsing, validation, and fallback behavior), refer to [xml-processing.md](./xml-processing.md).

## Handler Implementation
### Session Management Strategy
- One Handler per task execution
- Create new Handler instance per executeTask call
- Configure with immutable resource limits
- Set system prompt during initialization
- Clean session termination on completion
  
### Resource Tracking Implementation
- Turn counter per Handler
- Context window size monitoring
- Token usage tracking
- Resource limit enforcement
- No cross-Handler resource sharing

### Error Propagation Design
- Standard error type system
- Immediate propagation on detection
- Clean resource release
- No retry attempt handling
- Complete error context preservation

### Interactive Session Support
- Input detection capabilities
- Agent-controlled input requests
- Resource tracking during interaction
- Input timeout handling
- Cancellation support

## Template Management
### Storage Implementation
- XML file-based storage
- Disk-based persistence
- Directory organization by type
- Template versioning support
- Schema validation enforcement
  
### Validation Implementation
- Basic XML structure validation
- Schema conformance checking
- Warning generation for issues
- Template field validation
- Model availability checking
  
### Matching Algorithm Design
- Scoring based on prompt results
- Top-N candidate selection
- Separate matching for human input vs AST
- Score normalization
- Clear ordering requirements
  
### XML Processing Details
- Lenient parsing with fallback
- Warning collection
- Graceful degradation
- Partial parsing support
- Clear error locations

## Context Management Implementation

### Hybrid Configuration Approach

The Task System implements a hybrid configuration approach with operator-specific defaults and explicit overrides:

```typescript
// Default context management settings by operator type
const DEFAULT_CONTEXT_SETTINGS = {
  atomic: {
    inheritContext: 'full',
    accumulateData: false,
    accumulationFormat: 'notes_only',
    freshContext: 'disabled'
  },
  sequential: {
    inheritContext: 'full',
    accumulateData: true,
    accumulationFormat: 'notes_only',
    freshContext: 'disabled'
  },
  reduce: {
    inheritContext: 'none',
    accumulateData: true,
    accumulationFormat: 'notes_only',
    freshContext: 'enabled'
  },
  script: {
    inheritContext: 'full',
    accumulateData: false,
    accumulationFormat: 'notes_only',
    freshContext: 'disabled'
  },
  director_evaluator_loop: {
    inheritContext: 'none',
    accumulateData: true,
    accumulationFormat: 'notes_only',
    freshContext: 'enabled'
  }
};

// Template processing with merged settings
function processTemplate(template) {
  const operatorType = template.type;
  const defaults = DEFAULT_CONTEXT_SETTINGS[operatorType];
  
  // If context_management is present, merge with defaults
  if (template.contextManagement) {
    const mergedSettings = {
      ...defaults,
      ...template.contextManagement
    };
    
    // Validate mutual exclusivity constraint
    if ((mergedSettings.inheritContext === 'full' || mergedSettings.inheritContext === 'subset') 
        && mergedSettings.freshContext === 'enabled') {
      throw new Error('Invalid context management configuration: fresh_context="enabled" cannot be combined with inherit_context="full" or inherit_context="subset"');
    }
    
    return mergedSettings;
  }
  
  // Otherwise use defaults
  return defaults;
}

// Context Constraint Validation
function validateContextSettings(settings) {
  // Check for mutual exclusivity violation
  if ((settings.inheritContext === 'full' || settings.inheritContext === 'subset') 
      && settings.freshContext === 'enabled') {
    return {
      valid: false,
      error: 'Context constraint violation: fresh_context="enabled" cannot be combined with inherit_context="full" or inherit_context="subset"'
    };
  }
  
  // Check for empty context warning
  if (settings.inheritContext === 'none' && !settings.accumulateData && settings.freshContext === 'disabled') {
    return {
      valid: true,
      warning: 'Warning: Task will execute with minimal context (no inheritance, no accumulation, no fresh context)'
    };
  }
  
  return { valid: true };
}
```

During task execution, the final merged configuration is passed to the Evaluator, which applies the settings accordingly.

## Task/Template Matching

The Task System uses a heuristic, associative matching process for atomic tasks. In this approach:

- **Heuristic Matching:** User-defined associative matching tasks compare a task's free-form description against available atomic task templates. There is no fixed metric; each matching task computes a similarity score based on fixed input/output conventions.
- **Disable Context Option:** An optional "disable context" flag can be set in the task's `ContextGenerationInput` to omit inherited context entirely. This ensures that only the explicit task description and any previous outputs inform the matching process.
- **Highest-Scoring Candidate:** The system evaluates all candidates and selects the template with the highest score. Composite tasks are built by sequencing multiple atomic task templates rather than by direct template matching.

For further details on context handling and related design decisions, see [ADR 002 - Context Management](../../system/architecture/decisions/002-context-management.md), [ADR 005 - Context Handling](../../system/architecture/decisions/005-context-handling.md), and [ADR 14 - Operator Context Configuration](../../system/architecture/decisions/14-operator-ctx-config.md).

#### Matching Call Chain

```mermaid
flowchart TD
    A[User provides task description]
    B[Construct ContextGenerationInput]
    C{Disable Context?}
    C -- Yes --> D[Omit inheritedContext]
    C -- No --> E[Include parent context]
    D & E --> F[Call MemorySystem.getRelevantContextFor]
    F --> G[Receive AssociativeMatchResult]
    G --> H[Compute similarity scores for each candidate]
    H --> I[Select highest-scoring atomic task template]
    I --> J[Return template for execution]
```

## Resource Management

The Task System enforces resource limits via a per‑Handler turn counter and context window monitoring. For the complete low‑level implementation (including code examples and configuration details), please refer to [resource-management.md](./resource-management.md).
  
### Context Window Management
- Token counting approach
- Size limit enforcement
- No optimization strategy
- Window usage monitoring
- Clear limit boundaries
  
### Limit Enforcement Strategy
- Immediate termination on violation
- Resource exhaustion error generation
- Clean session cleanup
- Resource usage reporting
- Clear violation metrics
  
### Error Detection Mechanisms
- Resource limit monitoring, progress tracking, output and XML structure validation, and input validation.

### Environment Management

#### Parameter Passing
The system implements direct parameter passing between tasks rather than using environment variables. This approach:

1. Maintains clear data flow between components
2. Improves debug visibility by making dependencies explicit
3. Supports the `director_evaluator_loop` task type
4. Enhances testability by reducing hidden state

For Director-Evaluator loops, parameters are passed explicitly:
```typescript
async function executeDirectorEvaluatorLoop(task, inputs) {
  // Execute director with current inputs
  const directorOutput = await executeTask(
    task.director,
    {
      ...inputs,
      feedback: previousEvaluation?.feedback,
      current_iteration: currentIteration
    }
  );
  
  // Execute evaluator with director's result
  const evaluationResult = await executeTask(
    task.evaluator,
    {
      solution: directorOutput.content,
      original_prompt: inputs.original_prompt
    }
  );
  
  // Resume loop with new parameters
  return continueExecution(task, {
    ...inputs,
    director_result: directorOutput,
    evaluation_result: evaluationResult
  });
}
```

## Subtask Spawning Implementation

The Task System implements a standardized subtask spawning mechanism that enables dynamic task creation and composition.

### Request Structure

```typescript
interface SubtaskRequest {
  // Required fields
  type: TaskType;                      // Type of subtask to spawn
  description: string;                 // Description of the subtask
  inputs: Record<string, any>;         // Input parameters for the subtask
  
  // Optional fields
  template_hints?: string[];           // Hints for template selection
  context_management?: {               // Override default context settings
    inherit_context?: 'full' | 'none' | 'subset';
    accumulate_data?: boolean;
    accumulation_format?: 'notes_only' | 'full_output';
    fresh_context?: 'enabled' | 'disabled';
  };
  max_depth?: number;                  // Override default max nesting depth
  subtype?: string;                    // Optional subtype for atomic tasks
}
```

### Execution Flow

The subtask spawning process follows four main steps:

1. **Validation**
   - Validates the SubtaskRequest structure
   - Checks nesting depth against maximum allowed
   - Performs cycle detection to prevent recursive spawning
   - Validates input parameters

2. **Template Matching**
   - Uses the description and template_hints for associative matching
   - Selects the highest-scoring template that matches the request
   - Falls back to default templates if no specific match is found

3. **Subtask Creation**
   - Creates a new execution environment with direct parameter passing
   - Applies context management settings (defaults or overrides)
   - Prepares resource tracking linked to the parent task

4. **Execution and Result Handling**
   - Executes the subtask with appropriate resource limits
   - Passes the complete TaskResult back to the parent task
   - Handles errors with standardized error structures
   - Ensures proper cleanup of resources

### Depth Control Implementation

To prevent infinite recursion and resource exhaustion, the system implements depth control:

```typescript
async function executeTaskWithDepthControl(
  request: SubtaskRequest, 
  parentContext: ExecutionContext,
  currentDepth: number = 0
): Promise<TaskResult> {
  // Check maximum nesting depth
  const maxDepth = request.max_depth ?? DEFAULT_MAX_NESTING_DEPTH;
  if (currentDepth >= maxDepth) {
    throw new Error({
      type: 'TASK_FAILURE',
      reason: 'execution_halted',
      message: `Maximum nesting depth (${maxDepth}) exceeded`
    });
  }
  
  // Perform cycle detection
  if (detectCycle(request, parentContext.executionPath)) {
    throw new Error({
      type: 'TASK_FAILURE',
      reason: 'execution_halted',
      message: 'Cycle detected in subtask spawning'
    });
  }
  
  // Execute subtask with incremented depth
  try {
    return await executeTask(request, {
      ...parentContext,
      nestingDepth: currentDepth + 1,
      executionPath: [...parentContext.executionPath, getTaskSignature(request)]
    });
  } catch (error) {
    // Wrap error in standardized subtask failure structure
    throw {
      type: 'TASK_FAILURE',
      reason: 'subtask_failure',
      message: `Subtask "${request.description}" failed`,
      details: {
        subtaskRequest: request,
        subtaskError: error,
        nestingDepth: currentDepth + 1,
        partialOutput: error.details?.partialOutput
      }
    };
  }
}
```

### Context Management Integration

Subtasks use a hybrid configuration approach with default settings that can be overridden:

```typescript
// Default context management settings for subtasks
const DEFAULT_SUBTASK_CONTEXT_SETTINGS = {
  inherit_context: 'subset',
  accumulate_data: false,
  accumulation_format: 'notes_only',
  fresh_context: 'enabled'
};

function getContextSettings(request: SubtaskRequest): ContextSettings {
  // If context_management is provided in the request, merge with defaults
  if (request.context_management) {
    return {
      ...DEFAULT_SUBTASK_CONTEXT_SETTINGS,
      ...request.context_management
    };
  }
  
  // Otherwise use defaults
  return DEFAULT_SUBTASK_CONTEXT_SETTINGS;
}
```

### Parent-Child Communication

When a parent task spawns a subtask, the communication follows this pattern:

1. Parent task returns a CONTINUATION status with subtask_request in notes
2. Task System validates the request and spawns the subtask
3. Subtask executes with its own resource tracking
4. Subtask result is passed back to the parent task when it resumes
5. Parent task continues execution with the subtask result available as a parameter

This approach ensures clear data flow and explicit dependencies between parent and child tasks.

For historical context and decision rationale behind this implementation approach, see [ADR 11: Subtask Spawning Mechanism].

### Script Execution Implementation
The system now supports executing external scripts as part of a static director-evaluator workflow. When a script_execution element is specified:

1. The script receives the Director's output as direct input
2. Script execution captures stdout, stderr, and exit code
3. These outputs are passed as direct parameters to the Evaluator
4. No environment variables are used in this data flow

This design ensures that the director's output flows seamlessly through the script execution step before final evaluation, using explicit parameter passing throughout.

## Integration Points
### Memory System Interaction

#### Clear Responsibility Boundaries
- **Memory System** (read-only metadata):
  - Maintains metadata index (file paths and descriptions)
  - Provides associative matching based on metadata
  - Never performs file I/O operations
  - Does not store or parse file contents
  - Follows read-only context model (no updateContext capability)

- **Handler** (all file operations):
  - Reads/writes files when needed
  - For Anthropic models: Configures computer use tools (optional)
  - For other models: Uses appropriate file access mechanisms
  - Handles all file system interaction
  
### Compiler Integration
- Task parsing services
- XML validation
- Schema conformance
- Error surfacing
- Validation feedback
  
### Evaluator Support
- Error surfacing
- Reparse template support
- No retry management
- State preservation
- Recovery guidance
  
### LLM Session Management
- Handler encapsulation
- Resource tracking
- Model selection support
- Clean termination
- Session isolation
