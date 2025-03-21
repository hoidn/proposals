# System Interface Contracts

## 1. Component Integration Contracts

### 1.1 Compiler Integration [Contract:Integration:CompilerTask:1.0]
Defined in [Component:Compiler:1.0]
[TBD: Complete contract specification]

### 1.2 Evaluator Integration [Contract:Integration:EvaluatorTask:1.0]
See [Component:Evaluator:1.0] for complete interface.
[TBD: Complete contract specification]

### 1.3 Task System Integration
See [Component:TaskSystem:1.0] in components/task-system/README.md

#### Interfaces
- Task Execution: [Interface:TaskSystem:1.0] 
- Template Management: [Interface:TaskSystem:Templates:1.0]
- XML Processing: [Contract:Tasks:TemplateSchema:1.0]

#### Component Responsibilities
- Evaluator: Responsible for all template variable substitution (resolving {{variable_name}} placeholders)
- Handler: Works with fully resolved content only, no template substitution

#### Resource Contracts
See [Contract:Resources:1.0]

### 1.4 Memory System Integration [Contract:Integration:TaskMemory:3.0]
See [Component:Memory:3.0]

#### Interfaces
  - Metadata Management: [Interface:Memory:3.0]
    - Task System uses metadata for associative matching; see Appendix A for validation criteria.
  - Index Management: [Interface:Memory:3.0]
    - Global index serves as the bootstrap for matching; updates occur in bulk.

#### Responsibilities
Memory System:
 - Maintains global file metadata index
 - Provides bulk index updates
 - Supplies metadata for associative matching (refer to Appendix A for constraints)
 - NEVER performs file I/O operations (reading, writing, deletion)
 - Does NOT store or process file contents
 - Follows read-only context model (no updateContext capability)

Task System:
 - Uses context for task execution
 - Receives file references via associative matching
 - Delegates file access to Handler tools
 - Must not attempt to update context directly (removed in 3.0)

Handler:
 - Performs ALL file I/O operations
 - For Anthropic models: Configures computer use tools (optional)
 - For other models: Uses appropriate file access mechanisms
 - Manages all direct interaction with file system

#### Integration Points
 - Context flow from associative matching to task execution
 - File metadata index is used exclusively for matching; file access is handled by Handler tools

#### Interfaces
  - Metadata Management: [Interface:Memory:3.0]
    - Task System uses metadata for associative matching; see Appendix A for validation criteria.
  - Index Management: [Interface:Memory:3.0]
    - Global index serves as the bootstrap for matching; updates occur in bulk.

### 1.5 Delegation Boundaries

#### Handler Responsibilities
- Present unified tool interface to the LLM
- Execute direct tools synchronously
- Transform subtask tool calls into CONTINUATION requests
- Manage tool-specific resources
- Configure model-specific tools (e.g., Anthropic computer use)
- Direct execution without continuation mechanism
- Track resource usage for tool operations

#### Memory System Responsibilities
- Provide context for subtask execution
- Support context inheritance for LLM-to-LLM interaction
- Not involved in tool call execution
- Maintain metadata for associative matching

#### Task System Responsibilities
- Coordinate tool implementations (direct and subtask)
- Process CONTINUATION requests from subtask tools
- Manage execution flow between direct and subtask operations
- Handle template selection for subtask tools

#### Responsibilities
Memory System:
 - Maintains global file metadata index
 - Provides bulk index updates
 - Supplies metadata for associative matching (refer to Appendix A for constraints)
 - NEVER performs file I/O operations (reading, writing, deletion)
 - Does NOT store or process file contents
 - Follows read-only context model (no updateContext capability)

Task System:
 - Uses context for task execution
 - Receives file references via associative matching
 - Delegates file access to Handler tools
 - Must not attempt to update context directly (removed in 3.0)

Handler:
 - Performs ALL file I/O operations
 - For Anthropic models: Configures computer use tools (optional)
 - For other models: Uses appropriate file access mechanisms
 - Manages all direct interaction with file system

#### Integration Points
 - Context flow from associative matching to task execution
 - File metadata index is used exclusively for matching; file access is handled by Handler tools

## 2. Cross-Component Requirements

### 2.1 State Management
See [Pattern:Error:1.0] for error state handling.

Context Management:
- Task context maintained by Memory System
- Context operations provide immediate consistency
- No persistence guarantees for context data
- Context scope limited to current task execution

### 2.2 Error Propagation
Error handling defined in [Pattern:Error:1.0]

### 2.3 Resource Tracking
Resource contracts defined in [Contract:Resources:1.0]

Memory-Specific Resource Considerations:
- Context size limits defined by Handler
- Global index accessed in full only
- No partial index updates or queries
- File content handling delegated to Handler tools

## 3. Contract Validation 

### 3.1 Validation Requirements
- Context Management
  - Context updates must be atomic
  - Context retrieval must be consistent
  - No data persistence required
- Index Management
  - Index updates must be atomic
  - Index must persist across sessions
  - All file paths must be absolute
  - All metadata must be strings

### 3.2 Success Criteria
Context Management:
- Context updates visible to immediate subsequent reads
- No context data persists between sessions
- Context size within Handler limits

Index Management:
- Index survives system restarts
- Bulk updates atomic and consistent
- All paths resolvable by Handler tools

### 3.3 Verification Methods
- Unit tests for context operations
- Integration tests for index persistence
- Validation of file paths with Handler tools
- Context size limit compliance checks
