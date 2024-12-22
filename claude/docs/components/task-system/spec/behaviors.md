# Task System Behaviors

## Handler Behavior

### Interactive Sessions

The Handler supports interactive sessions where an LLM agent can request user input during task execution:

1. Input Detection
   - Handler monitors LLM responses for input requests
   - No special task type or mode required
   - Agent controls when input is needed

2. Input Flow
   ```
   LLM Output -> Handler Detects Request -> onRequestInput Called -> 
   User Input Received -> Continue Conversation
   ```

3. Resource Management
   - Same resource tracking as normal conversation
   - Input interactions count against turn limits
   - Context window includes all interaction history

4. Error Cases
   - Resource exhaustion during input cycle
   - Invalid/malformed input requests
   - Input timeout/cancellation

All interactive behavior is encapsulated within the Handler, requiring no changes to task templates or the broader task system.
