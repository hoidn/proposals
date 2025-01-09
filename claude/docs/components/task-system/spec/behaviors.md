# Task System Behaviors

## Template Management

- Store and retrieve task templates in XML format
- Match human input to candidate task templates
- Match AST nodes to candidate task templates
- Support specialized template types for reparsing and memory operations
- Basic XML structure validation with warning generation
- Support manual XML tasks with optional reparsing flag
- Maintain task template persistence in disk-based XML format

## Handler Management

### Core Responsibilities
- Create and manage LLM sessions through encapsulated Handlers
- Initialize Handlers with immutable configuration:
  - System prompts
  - Resource constraints
  - Turn limits
  - Context window limits
- Delegate prompt execution to Handlers
- Surface Handler errors through the standard error type hierarchy
- Ensure proper context propagation through Handler lifecycle

### Configuration Constraints
- Handler configuration immutable after initialization
- Configuration parameters:
  * max_turns (with default)
  * max_context_window_fraction (with default)
  * default_model (optional)
  * system_prompt (defaults to empty string)

### Interactive Sessions
- Handler monitors LLM responses for input requests
- No special task type or mode required
- Agent controls when input is needed
- Input Flow:
  ```
  LLM Output -> Handler Detects Request -> onRequestInput Called -> 
  User Input Received -> Continue Conversation
  ```
- Same resource tracking as normal conversation
- Input interactions count against turn limits
- Context window includes all interaction history

### XML Processing
- Basic structural validation only
- Warning generation for validation issues
- Lenient output parsing with fallback
- Graceful handling of partially valid XML
- Support for manual XML task flag

## Task Execution

### Standard Task Execution
- Process tasks using appropriate templates
- Return both output and notes sections in TaskResult structure
- Surface errors for task failure or resource exhaustion
- Support specialized execution paths for reparsing and memory tasks
- Implement lenient XML output parsing with fallback to single string
- Generate warnings for malformed XML without blocking execution
- Include 'data usage' section in task notes as specified by system prompt

### Task Template Matching

#### Human Input Matching
- Input: Natural language text + initial environment
- Process:
  - Uses matching specialized task from library
  - Considers provided files in environment
  - No access to previous executions/history
- Output: 
  - Up to 5 highest-scoring templates
  - Each match includes numeric score and template
  - Templates ordered by descending score

#### AST Node Matching
- Input: Single AST node
- Process:
  - Uses node-specific matching task
  - Only considers node-level context
  - No traversal of parent/child nodes
- Output:
  - Up to 5 highest-scoring templates
  - Each match includes numeric score and template
  - Templates ordered by descending score

### Specialized Task Types

#### Reparse Tasks
- Triggered by:
  - Resource exhaustion errors
  - Invalid output errors
  - Progress failure errors
- Uses specialized templates from separate directory
- Returns new task structure or alternative approach

#### Memory Tasks
- Direct memory system access
- Uses associative matching templates
- Returns relevant context selections

## Memory System Integration

### File Operations
- Uses Claude's file capabilities for actual I/O
- Tracks modified files during task execution
- Maintains simple file path index
- No direct file state management

### Context Management
- Context accessed via async getContext/updateContext
- File metadata accessed via GlobalIndex
- Existing context preserved during task execution
- Structure/parsing handled by associative memory tasks

### State Management
- No complex file metadata tracking
- Minimal state maintenance between tasks
- Clear task execution boundaries
- Simple file modification tracking

## Error Handling

### Error Detection and Response

#### Resource Exhaustion
- Handler detects limit violations
- Immediate task termination
- Surfaces through standard error type
- Resource accounting completion
- Clean Handler termination
- No retry attempts

#### Invalid Output
- Structural validation failure
- Format validation errors
- No semantic validation
- Preserves partial outputs when useful
- Returns both output and notes sections
- May trigger reparse task

#### Progress Failure
- Handler detects stalled execution
- Task-specific progress indicators
- No internal progress tracking
- May trigger alternative approach
- State preserved in error response
- No automatic retry

#### XML Validation
- Immediate failure on invalid structure
- No warning collection
- Clear error messages
- Location information when available
- May trigger reparse if not disabled

### Error Response

#### Error Surfacing
- Uses standard error type system (see types.md)
- Includes relevant task notes
- Preserves partial outputs when useful
- Includes resource metrics where applicable
- Clear error messages and locations

#### Handler Cleanup
- Clean termination of LLM session
- Resource accounting completion
- No state preservation
- Context window cleanup
- Turn counter finalization

#### Recovery Delegation
- No retry attempts
- No state maintenance
- Delegates to evaluator
- Provides complete error context
- Includes notes for recovery guidance
