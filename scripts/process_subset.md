<role>Software architect</role>
## Context

## High-Level Objective

Update the subset of files listed in edit_paths.json according to the given description and Q&A clarifications. 

## Mid-Level Objective

- Explain why each file needs modification
- Note dependencies and potential impacts
- Evaluate whether the change, as described, is ambiguous. Review the q and a to see whether the ambiguity is addressed.
- Draft the necessary architectural changes
- Make the documentation changes corresponding to the architectural changes

### Beginning Context

- Files listed in edit_paths.json
- Description of TODO / changes to make: '<description>'
- Questions and answers: '<questions>'

### Ending Context

- Modified versions of the files based on the description and Q&A

<output_format>
1. First, summarize understanding:
   - Key points from the Q&A discussion
   - Implications for the implementation
   - How this affects the requested changes

2. Then draft the architectural changes necessary to implement the changes described by the feature / TODO description

Don't make speculative changes.
</output_format>
