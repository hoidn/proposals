# Task System Requirements Q&A

## Component Boundaries & Responsibilities

Q: Does the Task System own XML generation/validation?  
A: Yes, owned by the task system.

Q: Is the Task System responsible for maintaining a library of task templates or just matching tasks to templates?  
A: Mainly matching. The library is disk persistent, but there should eventually be capability to add new templates.

Q: What is the division of responsibilities between Task System and Evaluator for recovery strategies?  
A: The task system surfaces errors, which the evaluator uses as signal to reparse the failed AST node. Reparsing can also mean simply retrying.

Q: Is the Task System responsible for tracking progress/retries?  
A: No, belongs to evaluator.

## Integration & Interfaces

Q: How does the Task System interact with the Memory System?  
A: Direct access.

Q: What outputs must the Task System provide for error recovery scenarios?  
A: It should at minimum return the 'notes' section from the failed task.

Q: How should task templates/patterns be stored and accessed?  
A: In XML format on disk.

## Resource Management

Q: Is the Task System responsible for predicting resource usage before execution?  
A: No.

Q: Should the Task System track its own resource usage or rely on the Evaluator?  
A: Resource usage is tracked mainly by the Handler, which manages individual LLM sessions. Most important things to track are context window usage and number of turns.

Q: Does the Task System need to optimize task decomposition based on resource constraints?  
A: This is a responsibility of the decomposition task/prompt.

Q: How should resource limits influence task template selection?  
A: The decomposition/reparsing task should be aware of the context window usage level but that's about it.

## Task Matching

Q: Are there different types of task matching?  
A: Yes, two distinct scenarios:
1. Human input → scored list of candidate task/AST structures (XML)
2. Existing atomic AST node → scored list of matching candidate task/AST structures (XML)

Q: Should the scoring be numeric or include metadata?  
A: Numeric.

Q: Should there be a minimum score threshold?  
A: Aim for 5 or fewer candidates.

Q: How should multiple matches be handled?  
A: Return top N.

## Task Definitions

Q: How should inputs be handled in task definitions?  
A: All inputs will be text. Empty fields can be left empty or provided with a placeholder. No input validation required.

Q: How should task definitions be organized?  
A: As XML files in a subdirectory.

Q: Should there be categories/groupings?  
A: Not necessarily, as long as we can keep track of specialized entries (reparsing and associative memory).

Q: Do we need to support searching/filtering of tasks?  
A: No, we just need to be able to collate them.

## Error Handling

Q: Should there be a standardized format for the 'notes' section?  
A: No, let it be free form.

Q: What information should a task failure return?  
A: Both output and notes should be returned in case of failure. For validation (not resource exhaustion) failure we might want to see the output.

## Handler Interaction

Q: How should TaskSystem interact with LLM sessions?  
A: Create/manage LLM sessions directly.

Q: Who is responsible for sending prompts to the LLM?  
A: The Handler.

Q: How should resource limits be communicated/enforced?  
A: They are passed to the handler and enforced by it.

Q: Who tracks session state?  
A: The Handler tracks session state (turns used, context window, etc).

## Specialized Tasks

Q: How should specialized tasks be handled?  
A: They will bypass the normal task matching procedure.

Q: Should specialized tasks be stored separately?  
A: Yes, in a separate directory.

Q: Are there different types of REPARSE tasks?  
A: Yes, two types: one for resource exhaustion (decomposition) and one for invalid output/failure to make progress (alternative approaches).

## Task Definitions

Q: How should inputs be handled in task definitions?  
A: All inputs will be text. Empty fields can be left empty or provided with a placeholder. No input validation required. Input names should appear as XML names/attributes in the prompt.

Q: What elements are required in task definitions?  
A: Only task_prompt and system_prompt are required. Should generate warnings for missing inputs but not validation errors.

Q: How should task definitions be organized?  
A: As XML files in a subdirectory.

Q: Should there be categories/groupings?  
A: Not necessarily, as long as we can keep track of specialized entries (reparsing and associative memory).

Q: Do we need to support searching/filtering of tasks?  
A: No, we just need to be able to collate them.

## Error Handling & Task Results

Q: Should there be a standardized format for the 'notes' section?  
A: No, let it be free form.

Q: What information should a task failure return?  
A: Both output and notes should be returned in case of failure (in TaskResult structure). For validation (not resource exhaustion) failure we might want to see the output.

Q: What should the notes section contain?  
A: Must contain a 'data usage' section, but this is NOT specified by the task system. It will be part of the system prompt or library entry for a given concrete task INSTANCE.

## Handler Interaction

Q: How should TaskSystem interact with LLM sessions?  
A: Create/manage LLM sessions directly.

Q: How many Handlers should be created?  
A: One Handler per task execution.

Q: Who is responsible for sending prompts to the LLM?  
A: The Handler.

Q: How should resource limits be communicated/enforced?  
A: They are passed to the handler and enforced by it.

Q: Who tracks session state?  
A: The Handler tracks session state (turns used, context window, etc).

Q: How should Handler failures be handled?  
A: Handler failures will surface through the existing error types system.

Handler Management:


Q: Should Handler creation/management logic be encapsulated or exposed?
What specific initialization info needs to be passed to Handlers?
Should Task System maintain state about active Handlers?

A: a. encapsulated. b. things like turn limits, max context window size, system prompt. c. no


Task Matching:


Q: For human input → candidates scenario, what context beyond input text?
For AST node → candidates, full AST context or just node?
Should scoring be consistent between scenarios?
A: an initial environment, which will consist of human-provided files. b. context is a node-level concept. c. the scoring prompt / task library element will be different, but the output format should be the same.


Task Definition:


Q: Relationship between task_prompt and system_prompt?
Any validation beyond basic XML structure?

A: a. there's no constraints on either. b. no

