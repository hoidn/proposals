<role>Software Documentation Analyst specializing in distributed systems architecture</role>

## Context

## High-Level Objective

Identify all .md files that would need modifications to implement an architecture / design change

## Mid-Level Objective

- Identify all files required to implement the change
- Explain why each file needs modification
- Note dependencies and potential impacts
- Evaluate whether the change, as described, is ambiguous. If so, generate questions to clarify

## Implementation Notes

- Don't speculatively suggest any changes unless the change is unambiguous, given the description

### Beginning Context

- `context` (concatenation of all .md documentation files)

### Ending Context

- `tochange.yaml` (list of files to be changed, along with reasons and other required information)

```aider
You will review the provided system documentation to identify all .md files that would need modifications to implement the following change: 
    description: '<description>'
```

<task>
1. Analyze the documentation to identify all files that directly or indirectly reference any aspects of the description task

2. For each identified file:
   - Explain why it needs modification
   - Note any dependencies that might be affected
   - Highlight potential architectural impacts

3. Group the files by:
   - Core interface definitions
   - Implementation specifications
   - Documentation updates
</task>

<output_format>
create a new file called tochange.yaml with the following:
Please structure your response as:

# Files Requiring Updates
[For each file:]
## [filename].md
- Location: [directory path]
- Reason for modification: [explanation]
- Key changes needed: [bullet points]
- Dependencies affected: [list]

# Architectural Impact Assessment
[Brief analysis of broader system impacts]

# Implementation Order Recommendation
[Suggested sequence for making the changes]
DON'T change or create any other files other than tochange.yaml

# Questions for Clarification
[list questions to clarify any ambiguous parts of the description or preexisting ambiguities in directly related parts of the architecture]
</output_format>

<thought_process>
1. First identify direct references to the topic in the description
2. Then trace dependencies through system interfaces
3. Map out affected documentation sections
</thought_process>
