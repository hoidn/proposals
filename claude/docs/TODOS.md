# Critical Path TODOs - Corrected Status

## Interface Consolidation ⚠️ BLOCKING

### Completed (✓)
1. Memory System interface version defined [Interface:Memory:2.0]
2. File content type handling standardized (Handler tools)
3. Unified storage approach defined in ADR
   - Memory System: metadata and context
   - Handler tools: file access
   - Clear separation of concerns

### Still Needed (❌)
1. Update Task System Implementation
   - Update components/task-system/spec/interfaces.md to use [Interface:Memory:2.0 or 3.0] consistently
   - Remove or reconcile old/deprecated memory structure definitions
   - Update dependent interfaces to unify environment usage
   - Ensure references to "Memory:2.0" vs "Memory:3.0" are consistent across docs


## Resource and File Management ⚠️ BLOCKING

### Completed (✓)
1. File tracking ownership decided
   - Memory System owns metadata index
   - Handler tools own file access
   - Clear delegation pattern defined

2. Resource tracking responsibilities documented
   - Handler owns resource limits
   - Memory System handles metadata only
   - Clear separation established

3. File access patterns defined
   - Handler tools for file operations
   - Memory System for metadata
   - Clean separation documented

### Still Needed (❌)
1. Interface Updates
   - Update Task System interfaces to reflect current patterns
   - Remove or replace any deprecated memory system fields
   - Add missing Handler tool interfaces if needed (e.g., `writeFile` if required)
   - Ensure consistency across doc references
   - Confirm we only store file metadata in Memory System (and use Handler for actual I/O)
   - Re-check that partial references to "getContext()" align with new approach

## Next Steps
1. Focus on updating Task System interfaces
2. Complete version number verification
3. Update any remaining documentation to reflect current architecture

## Notes
- Most architectural decisions are complete and documented
- Main work needed is implementation alignment
- Focus should be on updating Task System to match current architecture

## Feature Implementation

### Completed Features (✓)
1. Memory Component Separation
   - Full component definition
   - Clear interfaces
   - Integration documentation (✓)

2. Task Type System
   - Basic types defined
   - Subtask support
   - Map operator implementation

### In-Progress Features (🔄 / Partially Implemented)
1. Context Management
   Priority: High
   Dependencies: Interface Consolidation
   - [x] Document best practices (ADR 004)
   - [x] Define efficient subtask patterns (sequential)
   - [ ] Extend `inherit_context` to map/reduce
   - [x] Provide partial-result guidance (via accumulation_format)
   - [x] Consolidate environment usage:
       1. The memory system instance
       2. Accumulated data from sequential steps
       3. Associatively retrieved data
   - [x] Add context reuse mechanisms (via context_management)
   - [ ] Update error taxonomy for context failures

2. Architecture Documentation
   Priority: Medium
   Dependencies: None
   - [ ] Standardize patterns across components
   - [ ] Add cross-component documentation
   - [ ] Improve self-similarity in structure

### Unimplemented Features (❌)
1. Task Execution Enhancements
   Priority: High
   Dependencies: Context Management
   - [ ] "Rebuild-memory" or "clear-memory" flag in templates
   - [ ] Task continuation protocol
   - [ ] Summary output handling in evaluator

2. Agent Features
   Priority: Medium
   Dependencies: Interface Consolidation
   - [ ] Agent history storage
   - [ ] REPL implementation - the handler / task system needs to give the llm a 'question answering' tool. 
   - [ ] Multi-LLM support

## Documentation Updates

### Interface and Implementation Documentation
Priority: High
Dependencies: Interface Consolidation
- [ ] Update Task System specs to [Interface:Memory:2.0]
- [ ] Update API documentation
- [ ] Update component READMEs
- [ ] Document subtask usage (map, reduce, sequential) with context
- [ ] Provide best practices for partial output vs. re-parse
- [ ] Add context management practices
- [ ] Document subtask patterns
- [ ] Update documentation to include the new "disable context" option for atomic tasks
- [ ] Document that task results' `notes` field may include an optional success score for future adaptive matching

### Implementation Documentation
Priority: Medium
Dependencies: Feature implementations
- [ ] File handling patterns
- [ ] Resource tracking
- [ ] Integration examples
- [ ] Validation guidelines
- [ ] Evaluator behavior

### Contract Documentation
Priority: High
Dependencies: Interface Consolidation
- [ ] Update [Contract:Integration:TaskMemory:2.0]
- [ ] Align all version numbers
- [ ] Update cross-references
- [ ] Add new feature contracts

## Review & Testing
Priority: Medium
Dependencies: Individual feature completion
- [ ] Interface compatibility verification
- [ ] Version number audit
- [ ] Cross-reference validation
- [ ] Implementation completeness check

## Notes
- All interface changes must maintain backward compatibility
- Documentation should be updated alongside implementation
- Version numbers must be kept consistent
- Breaking changes require major version increments
- Dependencies should be clearly marked

### Other Issues Still Requiring Design Feedback
1. Handling Partial Results on Context-Generation Failure
The patch mentions “context generation fails,” but does not fully define whether partial results or intermediate step data should be preserved or retried. Deciding on partial result preservation or an automatic re-parse is an open design item.

2. Extending inherit_context to Other Operators  
   We added inherit_context only to the <task type="sequential"> element. Whether or not other operators (like reduce or any derived "map" pattern) should support the same attribute (and how it interacts with parallel or iterative steps) remains to be addressed.

3. Clarification of How Context Generation Tasks Are Triggered
Although references to a “context generation task” or “associative matching” were updated, the exact mechanism—i.e. how the evaluator decides to invoke associative matching, or how that is described in the DSL—still needs more explicit design.

4. Error Taxonomy for Context Issues
We have flagged that a “context generation failure” could be a Task Failure or might need its own subcategory. Determining whether this should remain a generic “task failure” or become a separate error type is pending further design discussion.


### other other todos 
- allow the agent to store and recall memory files (special subdir, markdown format, inc timestamps, can be instantiated / loaded / managed by memory system)
- do we need separate context inheritance handling for the reduction and accumulation operations in reduce?
- allow simple chaining - should be supportable through nesting but it might make more sense to make it a sequential pattern so that we can use the sequential context management features
- the agent / llm interface (which will be accessed by the handler) should support a basic set of tools in a fairly model-agnostic way. for example, for anthropic models interactions that use 'file edit' or 'shell' tools will use the underlying anthropic-specific computer use mechanisms. at the beginning of a session, the handler should be able to select one or more abstract tool types without knowing about these details
- function definition / call primitives / syntax / task types. A function is a named procedure that can be either compound or atomic. Will need to define some language syntax and maybe a repl in which things can be defined and run interactively. Could be a lisp dialect. New surface syntax on top of the existing task structure should be good enough. Maybe there's an existing python impl of a lisp parser that i can reuse. alternatively, could stick with xml for now and deal with language syntax / parsing later. 
- write some user stories. example 0: o1 to generate impl plan; sonnet to incrementally take and incorporate feedback; o1 to revise the updated plan; sequential sonnet (preceded by cheap model to break the steps into an explicit list) or zero shot o1 to generate diffs for all of the files. example 1: the inconsistency resolution workflow that i wrote down a while ago. example 2: something about generating documentation / building an index (e.g. mermaid diagram). 
- at some point (maybe not part of mvp), we'll want the agent to be able to request files to be added or removed to its context. this might not be necessary for anthropic models (computer use gives them direct access), but maybe we want that for other models. (on the other hand, limiting oai models to 'pure function' roles might be an ok approach too).
- might want to revisit how task outputs are parsed / not parsed. if we want the evaluator to support bindings and backreferences then we might want to support named return values. this would bridge the llm blob-level output with evaluator / DSL-level variable bindings, which could then be passed as arguments to downstream tasks. This means also changing the template format so that it includes an (optional) output spec. 
- use LLM to optimize template format?
- review adr 005, there should be 4 context-generation combinations for sequential taskss but I think we're only handling 3
- use the messages api for the llm interaction: https://docs.anthropic.com/en/api/messages
- figure out how subtasks spawned by the task system will work. If we don't include it in mvp then the evaluator might need to be more flexible. for example, a task's 'notes' section might include instructions to spawn another task that runs tests against its generated code. The evaluator would then have to dynamically generate a child node, using the 'notes' text as input to the task-matching procedure, and then run it. If the subtask fails then the parent task should also fail / be retried (Using failure information as feedback). This would require (1) making the task matching procedure more flexible and (2) changing the evaluator's control flow, but it would be simpler to do than full reparsing. Maybe not part of mvp but something like this is prob necessary for real agentic behavior. 
- replace the 'partial output' concept with a return status, which could include something like 'continuation' for tasks that want to spawn a subtask. the control flow would be decided by the combination of return status and error info.
- llm output-to-evaluator level bindings / variables can be used to pass discrete values like file paths between tasks, which would be useful to implement something like the director-evaluator pattern
- Add the Lispy stuff to docs if they're not already there
- add `aider` code blocks to the prompts
- think about how to use aider as a coding / file editing backend and for passing information between tasks (via files). It might make sense to go through files bc a lot of the time task outputs will be run or referred to later. There could be a subset of templates that 'know' how to format aider inputs (essentially using tool calls).
- need to clarify the difference between tool calls and subtasks (the
essential difference should be that tool calls are either deterministic
or have to pass through a rigid api, whereas subtasks are llm to llm
interactions. Having the llm call aider kind of blends the two. I think
it'd be better as a subtask, bc in any case some subtasks will require
conforming to an outupt signature.
- anthropic computer use could be replaced by evaluator subtasks, but it'd involve more boilerplate with subprocess.run and all that at 
the DSL interpreter level and it might be annoying to have to handle a special case. though i guess the output xml could have a universal
optional 'execute this script' field that always gets run if it's present
- maybe it doesn't make sense to have both 'continuation' and tool use
- think about how feedback will go from subtask to parent (tool use response?)
- there should be an option, for sequential task, for the associative matching to just extract a subset of the parent context
- let's have the director evaluator pattern be a special case of a task-subtask
- 'genetic' behavior, such as multiplle tries and selecting the best one

misc issues:
this is wrong:
---
// Memory System returns unranked matches
const matches = await memorySystem.getRelevantContextFor(input);

// Task System performs ranking and selection
const scoredTemplates = matches.map(match => ({
    template: findTemplateForMatch(match),
    score: computeScore(match, input)
}));

const bestTemplate = scoredTemplates.sort((a, b) => b.score - a.score)[0];
---
the system should return a single 'best' match so there is no need for keeping track of or comparing scores.

Loose ends:
- need to specify how bash commands will be called in between the director and evaluation steps of the director-evaluator pattern.
- output of the evaluation bash script needs to go to evaluator
- let llm design more speculatively. then feedback in the form of correctinng arch decisions i don't like.
- have reasoning model address list of underspecified parts, let it take initiative on decisions and then feed back on that
- try the goat workflow
- distill the director-evaluator .py into an arch component. check how it manages context over multiple  turns
- might want to remove the stuff about anthropic computer use, since we're taking a more model agnostic approach instead
- clarify when director-evaluator involves running bash and when not, and how to handle the not case

- How does the evaluator output go back to the director? (when the director is running in continuation mode)
- need 'define' or 'let'
- passing through questions
- model temperature (and model selection in general -- how are we going to handle this?)
- how would we approach multiple tries -> selection of the best candidate result? I'm thinking something like a many-to-one version of the director-evaluator pattern. Essentially: many tries in parallel (with sandboxing so that the instances don't interfere with one another) --> evaluation and selection of the 'best' outcome.
- Bring the evaluator impl in line with Lispy's approach, such that it will be easier to later incorporate it for the DSL front end

- there should be a standard way for prompts to return lists and for the list to be extracted / bound to a variable by the evaluator, bc, this will be a very common pattern.
- in director-evaluator, all evaluator outputs should be saved (even though only the most recent one is pased to the director)
- review associative matching state, make it higher priority
- the dsl should have a 'python' operation
- try the IDL method again
- add a read-only files field to the spec prompt format
- revisit map
- switch to json outputs 
- think about something like conversation -> json -> map spec prompts. basically representing the patterns that i'm already using, in the DSL
- think about using evaluators in more ways than just director-evaluator (such as for selecting the best of N)
- is evaluator feedback redundant with 'notes' feedback?
- make sure that there's a way for tasks to send recommendations to the associative matching jobs (both ctx and template) for child tasks (prob using the 'notes' section)
- for mvp, context matching should work at the file granularity. 
- maybe extract that old convo where i got a good spec prompt out of claude
- review 'subset' context pattern
- think through the relationship between code impl and writing the tests, and then handing off the path of test file to evaluator or tool call
- use pydantic and structured output
- functions can be composite expressions. the docs need to be clear that template - function isn't 1:1
- maybe promote Evaluator to an operator type bc it might be used for control flow (right now, there's too much blending / confusion between the concepts of task and operator)
- specify that sequential operations should return lists of json (or json consisting of a list of dicts or something)
- think about how to set up benchmarking and how the self-referenntial aspect of allowing the system to modify itself will look at the DSL expression level
- think about how 'shell' nodes will fit into the picture. this has been partially addressed with the director-evaluator pattern, but need to be less ad hoc about it
- add component-wise xml tags to documentation / impl files to make later self-improvement easier

<brainstorming prompt>
- need to impl function calling in the DSL.
- what data structure should we use to represent the task library in-memory? should that be part of the Evaluator Environment, or should it be separate? How should tasks be organized by type in the environment (e.g. should assoc matching tasks be separate from the rest?). Is it redundant to have both a subtype hierarchy for different atomic task types AND an in-memory hierarchy? (I don't think so, but the mapping between these two things will have to be worked out)
- how will tasks be loaded from file? will they be in-lined in the AST or references? former might be simpler for minimum implemenrtation, but eventually both tasks and composite procedures should be abstracted as first-class functions
- do we want to add 'cond' as a primitive? in that case (and maybe also for other reasons) we need a bridge between task outputs and python types. Look into imposing json formatting for task outputs.
</brainstorming prompt>

Misc:
- RL on GPT 2?
- is there a way to mix numbers with discrete tokens? Maybe attention over each of the bits in floating point representation?
- can llms be trained at half precision?
- how does llm compute requirement scale in the size of the token dictionary?
- what's the biggest trainable model?


more open questions:
Partial-Results Policy for Failing Operators

Ambiguity: Should a failing operator discard all intermediate results (treating the operator as an “all‑or‑nothing” unit) or preserve partial outputs (for example, in a dedicated “partialResults” field) so that higher‑level tasks can decide how to handle incomplete work?
Impact: This decision affects recovery strategies, error reporting, and the design of multi‑step (e.g. sequential) tasks.
Context-Generation Failure Error Taxonomy

Ambiguity: There is a question about whether the tools used for file operations should provide only read‑access (with file content managed externally) or if write and delete operations should be included from the start.
Impact: The answer determines the complexity of the Handler’s interface and the overall approach to file and metadata management.
Memory System Interface Versioning and Boundaries

Ambiguity: Some parts of the documentation refer to “Memory System 2.0” while others mention “Memory System 3.0.” Also, it isn’t entirely clear how to separate file metadata (which the Memory System manages) from actual file content operations (delegated to Handler tools).
Impact: Inconsistent version references or unclear boundaries could lead to integration problems between the Task System, Memory System, and Handler components.
Director‑Evaluator Pattern Details

Ambiguity: Although the pattern is described in both dynamic and static variants, questions remain about how exactly the Evaluator should spawn subtasks, how output (especially when a task returns a “CONTINUATION” status) is passed back to the Director, and under what conditions a bash script should be invoked versus relying solely on LLM re‑parsing.
Impact: These details affect the control flow, context passing (especially regarding last_evaluator_output), and error recovery in multi‑step tasks.
Subtask Spawning Mechanism

Ambiguity: The method for dynamically generating subtasks (outside of the Director‑Evaluator pattern) isn’t fully defined. For example, if a task’s notes indicate that additional processing is needed, it is not entirely clear how the Evaluator should create and bind a new subtask dynamically.
Impact: This influences the design of the DSL, the AST, and the overall control flow during complex task execution.
Mapping Between XML and AST Structures

Ambiguity: The XML schema for task templates is well defined, yet the correspondence between XML elements/attributes (such as <inherit_context>, <accumulate_data>, etc.) and the resulting AST or environment structure isn’t fully formalized.
Impact: This ambiguity may lead to mismatches between how tasks are specified and how they’re executed or decomposed by the Evaluator.
DSL Function Definition and Subtask/Tool Distinction

Ambiguity: There is discussion about supporting function definition/call primitives (e.g., for a Lisp‑like DSL) and also about distinguishing between subtasks (LLM-to‑LLM interactions) and tool calls (e.g. for file editing or shell execution). The boundary between these two types of operations is not clearly drawn.
Impact: The answer affects both the syntax of the DSL and the runtime behavior of task execution, especially if different recovery or binding mechanisms are needed for each.
Handling of Accumulated Data and Output Formatting


