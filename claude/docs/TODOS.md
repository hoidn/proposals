# System TODOs and Status

# Feature / arch TODOs (still pending final implementation)
1. The context / environment should explicitly combine:
   (1) a MemorySystem instance,
   (2) data accumulated from the current sequential operation (if relevant),
   (3) and working memory from associative matching. 

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

2. Version Number Alignment
   - Verify all cross-references use correct versions
   - Update any outdated references to [Interface:Memory:2.0 or 3.0]
   - Ensure consistent version numbering across documentation

   - Confirm final chosen memory interface version is used everywhere

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
- [ ] Update Task System specs to [Interface:Memory:2.0 or 3.0]
- [ ] Update API documentation
- [ ] Update component READMEs
- [ ] Document subtask usage (map, reduce, sequential) with context
- [ ] Provide best practices for partial output vs. re-parse
- [ ] Align final references to single Memory interface version
- [ ] Add context management practices
- [ ] Document subtask patterns

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
