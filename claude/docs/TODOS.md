# Documentation Inconsistency TODOs

## Memory System Interface Reconciliation

1. Task System vs Memory System Interface Mismatch
   - [ ] Determine correct file content type (string vs Buffer)
   - [ ] Decide on metadata handling approach
   - [ ] Resolve temporary/working storage responsibility
   - [ ] Update either memory or task system interface to match

2. Integration Contracts
   - [ ] Complete [Contract:Integration:TaskMemory:1.0] in system/contracts/interfaces.md
   - [ ] Define clear integration boundaries between Task and Memory systems
   - [ ] Document how Task System accesses Memory System storage

3. Storage Types
   - [ ] Standardize storage interfaces (currently conflicts between components/memory/api/interfaces.md and components/task-system/spec/interfaces.md)
   - [ ] Define metadata types (currently TODOs in task system interface)
   - [ ] Document storage lifecycle and persistence guarantees

## Questions to Resolve
1. Does Memory System handle temporary storage or only persistent storage?
2. How does file content type choice (string vs Buffer) affect system integration?
3. What metadata is actually required for file storage?

## Required Document Updates
1. components/memory/api/interfaces.md
2. components/task-system/spec/interfaces.md
3. system/contracts/interfaces.md