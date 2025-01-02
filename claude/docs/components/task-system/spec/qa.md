# Task System Requirements Q&A

[Previous sections unchanged...]

## Handler Management & Interaction

Q: How should TaskSystem interact with LLM sessions?  
A: Create/manage LLM sessions directly.

Q: Who is responsible for sending prompts to the LLM?  
A: The Handler.

Q: How many Handlers should be created?  
A: One Handler per task execution.

Q: How should resource limits be communicated/enforced?  
A: They are passed to the handler and enforced by it.

Q: Who tracks session state?  
A: The Handler tracks session state (turns used, context window, etc).

Q: How should Handler failures be handled?  
A: Handler failures will surface through the existing error types system.

Q: Should Handler creation/management logic be encapsulated or exposed?
What specific initialization info needs to be passed to Handlers?
Should Task System maintain state about active Handlers?

A: a. encapsulated. b. things like turn limits, max context window size, system prompt. c. no

[Remaining sections unchanged...]