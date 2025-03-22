# System Overview

## Architecture

This system implements a modular architecture for AI-assisted task execution with the following key components:

- **Task System**: Manages task execution, delegation, and resource tracking
- **Handler**: Provides LLM provider integration and resource enforcement
- **Memory**: Manages context and persistent storage
- **Evaluator**: Evaluates task results and provides feedback
- **Compiler**: Handles AST generation and transformation

## References & Documentation Map

For a comprehensive documentation map with navigation paths and references, see [Documentation Guide](/system/docs-guide.md).

## Component Responsibilities

Each component has well-defined responsibilities and interfaces documented in their respective README files:

- [Task System](/components/task-system/README.md)
- [Handler](/components/handler/README.md)
- [Memory](/components/memory/README.md)
- [Evaluator](/components/evaluator/README.md)
- [Compiler](/components/compiler/README.md)
