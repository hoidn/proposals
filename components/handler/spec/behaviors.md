# Handler Behaviors [Behavior:Handler:1.0]

## Core Behaviors

### LLM Interaction

1. **Provider Abstraction**
   - Handler abstracts provider-specific details
   - Each provider requires a specific adapter
   - Common payload structure transformed as needed

2. **Conversation Management**
   - One Handler per task execution
   - Complete conversation history maintained
   - Messages tracked with roles and timestamps
   - Clear session lifecycle (init → execute → cleanup)

### Resource Management

1. **Turn Counting**
   - Turns incremented for all LLM responses
   - User messages do not increment turn count
   - Tool responses do not increment turn count
   - Turn limits enforced at Handler level

2. **Context Window Management**
   - Token counting uses heuristic estimation
   - Context includes all conversation history and inputs
   - Warnings generated at 80% of limit
   - Hard limit enforced with appropriate errors

3. **Resource Reporting**
   - Current metrics accessible via getResourceMetrics()
   - Metrics included in error responses
   - Clean termination on resource exhaustion

### Tool Execution

1. **Direct Tools**
   - Executed synchronously by Handler
   - Results returned directly to LLM
   - No continuation mechanism

2. **Subtask Tools**
   - Return CONTINUATION status
   - Include subtask_request in notes
   - Structured according to [Pattern:SubtaskSpawning:1.0]

3. **User Input Tools**
   - Standard tool for requesting user input
   - Uses callback pattern for integration
   - Results added to conversation history

### Error Handling

1. **Resource Exhaustion**
   - Clean termination with metrics
   - Clear error structure with resource type
   - No automatic retry attempts

2. **Tool Execution Errors**
   - Wrapped in standard error structure
   - Propagated to caller
   - Include context when available

For implementation guidance, see `/components/handler/impl/`.
# Handler Behaviors

## Purpose

This document describes the runtime behaviors of the Handler component, including interactive sessions, resource management, and tool execution.

## Related Documents

- [Pattern:ResourceManagement:1.0](../../../system/architecture/patterns/resource-management.md)
- [Pattern:ToolInterface:1.0](../../../system/architecture/patterns/tool-interface.md)
- [Contract:LLMInteraction:1.0](../../../system/contracts/protocols.md)

## Key Behavior Highlights

1. **Session Management:**
   - One Handler per task execution with immutable configuration
   - Complete conversation tracking with message history
   - Clean session termination on completion or error
   - No cross-session state sharing

2. **Resource Tracking:**
   - Turn counting with strict limits
   - Context window size monitoring
   - Token usage tracking
   - Warning thresholds at 80%
   - Immediate termination on limit violation

3. **Tool Execution:**
   - Direct tool execution for synchronous operations
   - User input request handling
   - Tool response integration for subtask results
   - Error handling and propagation

4. **LLM Interaction:**
   - Provider-agnostic payload construction
   - Standardized message format
   - Tool registration and configuration
   - Response processing and parsing

## Interactive Sessions

The Handler implements a standardized tool-based approach for user input requests:

- The system registers a `requestUserInput` tool during Handler initialization
- Input Flow:
  ```
  LLM -> Calls requestUserInput tool -> Handler detects tool call ->
  onRequestInput called with prompt -> User input returned ->
  Handler adds user message to session -> Conversation continues
  ```
- Sessions track all conversation turns and message history
- User messages are added to the session but don't increment turn counters
- Assistant messages increment turn counters and are tracked for resource limits
- Context window includes full conversation history managed by HandlerSession
- HandlerPayload includes all context, messages, and available tools

## Protocol Flow

The Handler-LLM interaction follows a standardized protocol:

1. The Task System creates a Handler instance with configuration
2. The Handler creates a HandlerSession to manage conversation state
3. The Evaluator ensures all placeholders are substituted
4. The Handler constructs a HandlerPayload via session.constructPayload()
5. Provider-specific adapters transform the payload to appropriate formats
6. LLM response is processed via handler.processLLMResponse()
7. Tool calls (including user input requests) are handled
8. Session state is updated with new messages
9. Resource usage is tracked and limits enforced

## Resource Management Behavior

### Turn Counting
- Incremented only for assistant messages
- Not affected by user messages or tool responses
- Checked before each LLM call
- Hard limit enforced with immediate termination
- Warning at 80% threshold

### Context Window Management
- Token-based calculation for all content
- Includes system prompt, messages, and context
- Size limit based on model and configuration
- Warning at 80% threshold
- Hard limit with immediate termination

### Resource Cleanup
- Clean session termination on completion
- Resource accounting finalization
- Message history clearing
- State invalidation
- Final metrics logging

## Tool Execution Behavior

### Direct Tools
- Synchronous execution via Handler
- Immediate result return
- Error handling with standardized format
- Resource tracking during execution
- No continuation mechanism

### User Input Request
- Special tool for interactive sessions
- Callback-based implementation
- Session state preservation
- Message history integration
- No turn counting for user messages

### Subtask Tool Integration
- CONTINUATION status for subtask requests
- Tool response integration for results
- Session preservation during subtask execution
- Clean data flow between parent and child tasks

## Script Execution Behavior

- Command validation for security
- Input/output handling
- Timeout enforcement
- Error capture and formatting
- Exit code processing
- Result integration with task output

## Error Handling

### Resource Exhaustion
- Immediate task termination
- Clean resource release
- Complete metrics reporting
- No automatic retry
- Clear error message with resource type

### Tool Execution Errors
- Standardized error format
- Tool name inclusion
- Error details preservation
- Clean error propagation
- No automatic recovery

### LLM Provider Errors
- Provider-specific error handling
- Standardized error transformation
- Session state preservation
- Resource accounting completion
- Clear error categorization
