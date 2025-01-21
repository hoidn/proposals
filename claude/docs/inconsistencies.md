1. Inconsistencies with Clear Resolutions

A. Conflicting Memory Interface Versions (2.0 vs. 3.0)

Issue: Some documents and code snippets refer to [Interface:Memory:2.0] with getContext(), while others refer to [Interface:Memory:3.0] that omits getContext() (and also removes updateContext).
Resolution:
Pick 3.0 (or whichever you officially adopt) as the sole interface.
Remove references to getContext() or any fields like shortTermMemory that appear only in the old version.
Replace all mentions of [Interface:Memory:2.0] in task-system/spec/interfaces.md, operators.md, ADRs, and the system docs with the final [Interface:Memory:3.0].
Verify code snippets to ensure they only show methods that truly exist in 3.0 (e.g., getGlobalIndex, updateGlobalIndex).
B. Leftover Mentions of “Short-Term Memory” Structure

Issue: misc/operators.md (and a few other spots) define shortTermMemory: { files: Map<string, WorkingFile>; dataContext: string }, but the [Interface:Memory:3.0] design no longer has a concept of short-term memory or getContext().
Resolution:
Remove or rewrite any references to a “shortTermMemory” object.
Emphasize that the new MemorySystem is only for global file metadata and does not store direct short-term context.
Any needed working data should be passed around via the proposed Environment or “context frames” (not by the MemorySystem).
C. Inconsistent Partial-Results Guidance

Issue: The “Phase 2” plan and operator docs talk about saving partial results or partial context if a sub-task fails, yet errorspec.md says no partial results are preserved in errors.
Resolution:
Decide if partial results belong in the final TaskResult (e.g., TaskResult.notes.partialResults) or if they must be discarded upon failure.
Align the error spec to allow partial data if you do in fact want partial outcomes. For example, clarify that partial results may be preserved in TaskResult but are not injected into the Error object itself.
Update both errorspec.md and the references in “Phase 2: Expanded Context Management” accordingly.
D. References to context generation failure but No Matching Error Type

Issue: Documentation proposes a special “CONTEXT_GENERATION_FAILURE” or “context generation failure,” but errorspec.md only defines Resource Exhaustion and Task Failure generically.
Resolution:
Either add a dedicated error subtype (e.g., type: 'CONTEXT_GENERATION_FAILURE';) in errorspec.md
Or treat it as a subset of existing TASK_FAILURE and remove references suggesting a separate error name.
Whichever path you choose, update the main error taxonomy for clarity.
E. Inconsistent Handler “Tools” Methods

Issue: Some places mention readFile, others mention a possible writeFile or deleteFile, but it is unclear whether the final design includes them.
Resolution:
Confirm if the architecture must remain read-only for the LLM or if writing/deletion is truly needed.
If read/write is needed, define those methods in Handler.tools. If you are read-only, remove all mention of writeFile or deleteFile.
Cross-check references in Task System docs to reflect the final read/write posture.
<br/>
2. Inconsistencies Requiring Subjective Choices

Below are areas where the documents highlight open design questions or competing approaches. Each needs a decision to remove ambiguity.

Partial-Results Policy for Failing Operators

Options:
A: Discard partial outputs on sub-task failure, treat the entire operator as a single unit of success/failure.
B: Keep partial outcomes (in TaskResult.notes.partialResults, etc.) and let higher-level tasks decide how to handle them.
Recommendation: If your use cases frequently require partial data (e.g., some parallel tasks succeed while others fail), choose (B) and store partial results. If the system rarely benefits from partial data, keep (A) for simplicity.
Context-Generation Failure as Its Own Error

Options:
A: New error type (CONTEXT_GENERATION_FAILURE) in errorspec.md, distinctly recognized so that tasks can handle it differently than normal “task failures.”
B: Keep a single TASK_FAILURE category and rely on message or reason to identify context errors.
Recommendation: If you plan to handle context failures with specialized fallback or re-tries, choose (A). If context issues are not special in your system’s eyes, keep (B) to avoid error-type proliferation.
Inherited Context for Map and Reduce

Question: “Should <inherit_context> be available on all operators (map, reduce, sequential) so sub-tasks can share or skip context?”
Options:
A: Provide <inherit_context> consistently on all multi-step operators.
B: Keep inheritance on sequential only, and treat map/reduce differently.
Recommendation: If the system’s mental model is that all nested tasks might optionally share the environment, use (A). If parallel tasks or reduce tasks inherently require a “fresh” environment, then (B) is simpler.
Handler Tools API (Read-Only vs. Read/Write)

Question: “Do tasks need to modify or delete files, or is read-only enough?”
Options:
A: Provide readFile, writeFile, deleteFile from the start.
B: Provide only readFile, and mention a future extension for writes.
Recommendation: Decide based on real usage. If you have no short-term need for writes, option (B) keeps it simpler, adding write methods later if necessary.
<br/>
Summary
Immediate Action: Pick one Memory interface (likely 3.0) and remove all leftover references to getContext() or other 2.0-era constructs.
Then fix references to partial results, error taxonomy, and Handler tools to ensure your docs match the final approach.
Finally resolve each “Subjective Choice” (partial results, specialized error type, etc.) so that your architecture docs remain consistent and unambiguous.
