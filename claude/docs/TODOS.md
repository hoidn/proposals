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
   - [ ] Document best practices
   - [ ] Define efficient subtask patterns (sequential, reduce, map)
   - [ ] Extend `inherit_context` to map/reduce
   - [ ] Provide partial-result guidance (e.g. whether we preserve partial results on context generation failure)
   - [ ] Consolidate environment usage so that tasks can clearly see:
       1. The memory system instance
       2. Accumulated data from the parent or prior step
       3. Any associatively retrieved files/data
   - [ ] Add context reuse mechanisms
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
   - [ ] Several-shot examples for reparsing

2. Agent Features
   Priority: Medium
   Dependencies: Interface Consolidation
   - [ ] Agent history storage
   - [ ] REPL implementation
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
We added inherit_context only to the <task type="sequential"> element. Whether or not other operators (map, reduce) should support the same attribute (and how it interacts with parallel or iterative steps) remains to be addressed.

3. Clarification of How Context Generation Tasks Are Triggered
Although references to a “context generation task” or “associative matching” were updated, the exact mechanism—i.e. how an XML specification decides to invoke associative matching, or how that is described in the DSL—still needs more explicit design.

4. Error Taxonomy for Context Issues
We have flagged that a “context generation failure” could be a Task Failure or might need its own subcategory. Determining whether this should remain a generic “task failure” or become a separate error type is pending further design discussion.
