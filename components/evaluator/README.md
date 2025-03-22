# Evaluator Component [Component:Evaluator:1.0]

## Overview

The Evaluator assesses task results and provides feedback for improvement. It works closely with the Director pattern to enable iterative refinement.

## Core Responsibilities

1. **Result Evaluation**
   - Assess task outputs against requirements
   - Identify errors and improvement opportunities
   - Generate structured feedback

2. **Feedback Generation**
   - Provide actionable feedback
   - Prioritize critical issues
   - Suggest specific improvements

3. **Integration with Director**
   - Support iterative refinement process
   - Provide evaluation metrics
   - Guide subsequent iterations

## Key Interfaces

- **evaluate**: Evaluate a task result
- **generateFeedback**: Generate structured feedback
- **assessQuality**: Assess the quality of a result

For detailed specifications, see:
- [Pattern:DirectorEvaluator:1.0] in `/system/architecture/patterns/director-evaluator.md`

For a comprehensive map of all system documentation, see [Documentation Guide](/system/docs-guide.md).
