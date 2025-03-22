# Handler Q&A

## Purpose

This document addresses common questions about the Handler component, its responsibilities, and its integration with other components.

## Related Documents

- [Handler README](../README.md)
- [Handler Behaviors](./behaviors.md)
- [Handler Types](./types.md)

## General Questions

### Q: What is the Handler component responsible for?

**A:** The Handler component is responsible for:
- Managing LLM interactions (sending prompts, processing responses)
- Tracking resource usage (turns, context window)
- Executing tools (file operations, user input requests, scripts)
- Managing conversation state through sessions
- Enforcing resource limits
- Providing a unified interface for different LLM providers

### Q: How does the Handler differ from the Evaluator?

**A:** The Handler and Evaluator have distinct responsibilities:

**Handler:**
- Manages direct LLM interactions
- Tracks resource usage
- Executes tools and scripts
- Performs file I/O operations
- Works with fully resolved content (no template variables)

**Evaluator:**
- Interprets and executes AST nodes
- Manages execution flow
- Resolves template variables
- Handles reparse requests
- Delegates LLM interactions to Handler

The key distinction is that the Evaluator handles "what to execute" while the Handler handles "how to execute it" with the LLM.

## Resource Management

### Q: How does the Handler enforce resource limits?

**A:** The Handler enforces resource limits through:
1. **Turn Counter**: Tracks conversation turns and enforces a maximum limit
2. **Context Manager**: Monitors token usage against context window limits
3. **Timeout Handling**: Enforces execution timeouts for scripts
4. **Warning Thresholds**: Emits warnings at 80% of limits
5. **Hard Termination**: Immediately terminates execution when limits are reached

### Q: What happens when a resource limit is exceeded?

**A:** When a resource limit is exceeded:
1. The Handler throws a `ResourceExhaustionError` with details about the limit
2. The session is cleaned up (resources released, state cleared)
3. Complete metrics are included in the error
4. The Task System receives the error and can implement recovery strategies
5. No automatic retry is attempted by the Handler

### Q: How are resource limits configured?

**A:** Resource limits are configured through the `HandlerConfig` object:
- `maxTurns`: Maximum number of conversation turns
- `maxContextWindowFraction`: Fraction of model's context window to use (e.g., 0.8)
- `defaultModel`: Model identifier that determines base context window size
- Timeouts for script execution are specified per script

## Session Management

### Q: What is a HandlerSession?

**A:** A HandlerSession represents a single conversation with an LLM and manages:
- Message history (user, assistant, and tool messages)
- Turn counting
- Context window tracking
- Tool registration and execution
- Payload construction
- Resource cleanup

Each task execution gets its own HandlerSession, ensuring isolation and clean resource tracking.

### Q: How are messages tracked in a session?

**A:** Messages are tracked in a session through:
- An ordered array of message objects
- Each message has a role (user, assistant, system, tool)
- Messages include content and timestamps
- Tool messages include the tool name
- User messages don't increment turn counter
- Assistant messages increment turn counter
- All messages count toward context window usage

### Q: How is conversation state preserved?

**A:** Conversation state is preserved through:
- Complete message history in the session
- Tool registration state
- Resource usage metrics
- System prompt
- Context from Memory System

This state is included in each LLM payload to maintain conversation coherence.

## Tool Execution

### Q: How does the Handler support tools?

**A:** The Handler supports tools through:
1. **Tool Registration**: Tools are registered with name, description, and parameter schema
2. **Tool Execution**: The Handler detects and executes tool calls from LLM responses
3. **Tool Response**: Results are added to the conversation history
4. **Direct Tools**: Synchronous operations executed directly by the Handler
5. **Subtask Tools**: Complex operations implemented via CONTINUATION mechanism

### Q: How does the Handler handle user input requests?

**A:** The Handler handles user input requests through:
1. A standard `requestUserInput` tool registered during initialization
2. When the LLM calls this tool, the Handler invokes the `onRequestInput` callback
3. The callback prompts the user and returns their input
4. The user's input is added to the session as a user message
5. The conversation continues with the user's input available to the LLM

### Q: How does script execution work?

**A:** Script execution works through:
1. The Handler's `executeScript` method that takes command, input, and timeout
2. Command validation for security
3. Execution with input piped to the script
4. Capture of stdout, stderr, and exit code
5. Return of a standardized `ScriptResult` object
6. Integration with Director-Evaluator pattern for evaluation

## Integration with Other Components

### Q: How does the Handler integrate with the Task System?

**A:** The Handler integrates with the Task System through:
1. The Task System creates Handler instances with configuration
2. The Task System delegates task execution to the Handler
3. The Handler returns results to the Task System
4. The Task System handles resource errors from the Handler
5. The Task System coordinates subtask execution based on CONTINUATION status

### Q: How does the Handler integrate with the Memory System?

**A:** The Handler integrates with the Memory System through:
1. The Memory System provides context for LLM interactions
2. The Handler includes this context in LLM payloads
3. The Handler performs file operations based on file paths from Memory System
4. The Handler does NOT modify or update the Memory System
5. Clear separation of responsibilities: Memory System provides metadata, Handler handles content

### Q: How does the Handler support different LLM providers?

**A:** The Handler supports different LLM providers through:
1. Provider adapters that implement the `ProviderAdapter` interface
2. Standardized `HandlerPayload` structure for all providers
3. Provider-specific transformations for tools and parameters
4. Consistent error handling across providers
5. Model-specific token counting and context window limits

This abstraction allows the system to work with different LLM providers while maintaining consistent behavior.
