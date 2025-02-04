1. Error Taxonomy and Handling
Issues Identified
Invalid Error Type: The “INVALID_OUTPUT” error is referenced in errorspec.md but conflicts with the goal of having only two error categories (Resource Exhaustion and Task Failure).
Error Propagation Examples: Several documents (e.g., errorspec.md and parts of the evaluator design) include examples that mention INVALID_OUTPUT or imply nuanced error handling not supported by the simplified control flow.
Revision Actions
Remove or Deprecate INVALID_OUTPUT:
errorspec.md: Update the “Error Categories” section so that only Resource Exhaustion and Task Failure are defined. Remove any formal definition or example of INVALID_OUTPUT.
Cross-References: Search and update any other file (e.g., in the evaluator, task system types, or decision records) that references INVALID_OUTPUT so that “invalid output” is instead treated as a form of TASK_FAILURE.
Update Error Handling Principles:
Clarify in errorspec.md that errors signal failure conditions without carrying execution state or partial results.
Update examples to show that error metadata (if any) is attached only to TASK_FAILURE and RESOURCE_EXHAUSTION.
Deliverables
Revised errorspec.md with the simplified error taxonomy.
Updated examples in any evaluation or recovery documentation to reflect the new model.
2. Atomic Task Subtyping
Issues Identified
Subtyping Conflict: The atomic_task_subtypes.md document proposes director/evaluator subtypes for atomic tasks, but the XML schema in protocols.md does not support a subtype attribute.
MVP Simplicity: The discussion recommends that if subtyping is not necessary for the MVP, then the complexity should be removed.
Revision Actions
Decision Point:
If the current MVP does not require specialized behavior between director and evaluator atomic tasks, then remove subtyping entirely.
Otherwise, update protocols.md (and related XML schema files) to add support for a “subtype” attribute.
Implementation for MVP:
Atomic Task Subtyping Removal: Remove the subtype definitions and any associated registration or custom handling from atomic_task_subtypes.md.
Types Update: In task system type definitions (e.g., in components/task-system/spec/types.md), remove or deprecate the AtomicTaskSubtype type.
Documentation Update:
Remove all references to director/evaluator subtyping in the documentation (e.g., in sample XML, decision records, and cross-component interfaces).
Deliverables
A revised atomic_task_subtypes.md that either clearly states subtyping is not supported in MVP or has been removed.
Updated protocols.md and types.md reflecting the decision.
3. Context Inheritance and Accumulation
Issues Identified
Ambiguity for Reduce Operators: The documentation on <inherit_context> is unclear for operators like reduce.
Partial Results Policy: Contradictory statements about whether partial results are preserved have led to confusion.
Revision Actions
Sequential Operator and Reduce Operator:
operators.md: Revise the description of <inherit_context> to explain the three modes (“full”, “none”, “subset”) and explicitly state that for reduce tasks the inheritance behavior is simplified (i.e. no special error mapping or partial output accumulation).
For MVP, note that only the sequential operator supports full context accumulation (if needed) and that reduce tasks will use a basic inheritance model.
Partial Results Policy:
errorspec.md & related docs: Remove all references to preserving partial results on failure. State clearly that on any task failure, intermediate data is discarded.
Evaluator and Environment Documents:
Clarify that when both inheritance and accumulation are enabled in a sequential task, the Evaluator tracks inherited context separately from any accumulated “notes” but that no merging is performed for MVP.
Deliverables
Updated operators.md with a clear, simplified explanation of context inheritance and accumulation.
Revised sections in the Evaluator and Memory System documentation to reflect that partial results are not preserved.
A note in the documentation that advanced (e.g., dual-context or merging) behaviors are deferred to future iterations.
4. Script Execution Handling
Issues Identified
Script Error Handling Gap: Currently, script errors (non-zero exit codes) are not distinguished; the proposed solution is to remove special script error handling and rely on stdout/stderr.
Integration of Script Output: It is underspecified how the outputs (stdout, stderr) are fed into the evaluator.
Revision Actions
Protocols.md and XML Schema:
Update the XML examples for tasks of type “script” to remove any elements related to error handling (like a dedicated error type for script execution).
Instead, specify that script tasks capture stdout and stderr in a designated notes field.
Evaluator Documentation:
Clearly state that the evaluator treats script execution errors as generic TASK_FAILURE conditions and that non-zero exit codes do not trigger a special error branch.
Deliverables
Revised script task XML examples in protocols.md.
Updates to any evaluator or error-handling documents describing how script outputs are passed to the evaluator.
5. Memory/Handler Responsibility Clarification
Issues Identified
Overlap in Responsibilities: The Memory System returns file paths (FileMatch[]) while file I/O is the domain of Handler tools, yet the coordination is not documented.
Revision Actions
Memory System Documentation (e.g., in components/memory/api/interfaces.md and system/contracts/interfaces.md):
Add a clarifying note that the Memory System is responsible solely for providing file metadata (file paths and associated strings) and that any file reading or writing is delegated to the Handler’s tool interfaces.
Handler Documentation:
Briefly describe that Handler tools (as documented in components/task-system/impl/resource-management.md and related files) are responsible for actual file I/O.
Deferred Clarification:
Add a “future work” note stating that the coordination mechanism between Memory System and Handler will be further refined in later versions.
Deliverables
Updated Memory System and Handler sections in the contracts and API documentation.
A note in the “Underspecified Aspects” section (or in a new FAQ) explaining that this division is intentionally left for future clarification.
6. Decomposition Protocol (Task Splitting)
Issues Identified
Undefined Decomposition: While decomposition is mentioned as a response to resource exhaustion, the process is not defined.
Revision Actions
Protocols.md and Task System Documentation:
Remove detailed decomposition process steps for MVP and mark the section as “Deferred for future iteration.”
Include a short note that “decomposition” is recognized as a desirable feature but is out of scope for the initial release.
Deliverables
A revised section in protocols.md that clearly states decomposition protocol details are deferred.
An update in the decision records (e.g., ADR documents) noting that decomposition will be specified in a future version.
7. Associative Matching Input Schema
Issues Identified
Overly Structured Input: Some discussions referenced a complex XML structure for associative matching, but the recommendation is to simplify by operating on strings.
Revision Actions
Memory System and Protocol Documentation:
Update the description of the input to getRelevantContextFor() (found in components/memory/api/interfaces.md) to state that the input can be a simple plain text string.
Remove any mandatory XML structure requirements from the documentation.
Deliverables
Updated Memory System interface documentation and protocols.md reflecting that associative matching input is unstructured text.
8. Director-Evaluator Handoff
Issues Identified
Handoff Mechanism: The current documents suggest that the evaluator should return an EvaluationResult with a simple success flag and feedback.
Revision Actions
Director-Evaluator Pattern Documentation (e.g., simplify_evaluator_feedback.md and director-evaluator.md):
Revise the flow description so that after a Director task produces a CONTINUATION result, the Evaluator spawns a subtask that returns an object of the form:
javascript
Copy
EvaluationResult(success: boolean, feedback: string | null)
Update sample XML for the static variant to reflect that the director’s output is passed to the evaluator via a designated field (e.g., <output_slot> or <input_source>).
Deliverables
Revised Director-Evaluator documentation files with updated XML examples.
A clear description of the expected EvaluationResult structure.
9. Composite Task Resource Aggregation and Global Index Updates
Issues Identified
Resource Aggregation: It is unclear whether resource tracking is done per composite task or per subtask.
Global Index Updates: Frequency and trigger conditions remain unspecified.
Revision Actions
Contracts and Protocols Documentation:
Add a brief note (or a “Deferred” marker) stating that for MVP, resource usage (turns/tokens) is tracked on a per-subtask basis.
In the global index section (e.g., in system/contracts/resources.md), state that update triggers for the global index remain unspecified and will be defined in a future iteration.
Deliverables
Minor text updates in the resource management contracts and protocols files clarifying that these issues are out-of-scope for the MVP.
10. Cross-Reference Updates and Documentation Structure
Issues Identified
Outdated and Inconsistent Cross-References: Many documents refer to different versions or legacy approaches (e.g., Memory:2.0 vs. Memory:3.0, partial results, etc.).
Revision Actions
Documentation Map (docstructure.md):
Update the directory layout and navigation map to reflect the new sections (e.g., updated error handling, context management, director-evaluator, and protocol documents).
Version Alignment:
Verify that all cross-references (in ADRs, contracts, interfaces, and types) are updated to the correct, current version numbers.
Remove Obsolete Sections:
Eliminate TODOs and references that have been resolved (e.g., references to partial result retention) and update the “Inconsistencies” document with a summary of decisions made.
Deliverables
Revised docstructure.md and docs-guide.md.
A cross-reference audit document (even if brief) to ensure consistency across the architecture documentation.
Timeline / Phasing
Phase 1 – Immediate MVP Revisions (2–3 Weeks):

Update error taxonomy (Section 1), remove INVALID_OUTPUT, and update related examples.
Revise context inheritance/accumulation and script execution handling.
Clarify Memory vs. Handler responsibilities (with “deferred” notes).
Update the Director-Evaluator handoff documentation.
Phase 2 – Interface and Cross-Reference Consolidation (2–3 Weeks Following Phase 1):

Decide on atomic task subtyping (remove if unnecessary) and update protocols/types.
Update cross-references, version numbers, and docstructure.md.
Remove or mark as deferred the decomposition protocol details and global index update triggers.
Phase 3 – Future Enhancements (Post-MVP, Future Iterations):

Refine decomposition protocols, advanced context merging (if needed), and any extended resource tracking.
Revisit any “deferred” sections with implementation feedback and update ADRs accordingly.
Final Notes
Review Process: Schedule an internal review with architects and component leads to verify that the changes align with the current implementation and future goals.
Backward Compatibility: Clearly mark any breaking changes (e.g., removal of atomic task subtyping, changes in error taxonomy) so that developers can plan for migration.
Documentation Consistency: Use this revision plan as a checklist to update all affected documents and ensure that all cross-references and examples are coherent.
By following this revision plan, the architecture documentation will reflect a streamlined error model, a simplified task and context handling approach for MVP, and clear indications of which advanced features are deferred for later iterations.
