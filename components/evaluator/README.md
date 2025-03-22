# Evaluator Component

The Evaluator is responsible for AST processing, template variable substitution, and execution control. It serves as the core execution engine for the system, walking the AST and managing the execution flow.

Key responsibilities include:

1. Processing AST nodes according to their type
2. Managing lexical environments and variable scoping
3. Delegating LLM execution to the Handler
4. Handling error recovery and reparse requests
5. Tracking resource usage during execution

## Responsibilities and Role

The Evaluator sits at the heart of the execution model, serving as the bridge between the abstract task representation (AST) and the actual execution environment. It:

- Walks the AST recursively, dispatching based on node type
- Maintains lexical environments for variable scoping
- Performs all template variable substitution before Handler invocation
- Applies different substitution rules for function vs. standard templates
- Manages context according to the three-dimensional model
- Handles subtask spawning and continuation requests
- Implements error detection, recovery, and propagation
- Coordinates with the Handler for LLM execution and resource tracking

## Documentation Structure

The Evaluator documentation is organized into several key areas:

### API Documentation
- [Interfaces](./api/interfaces.md) - Public interfaces for integration with other components

### Implementation Details
- [Design](./impl/design.md) - Core design and execution model
- [Context Management](./impl/context-management.md) - Context management implementation
- [Director-Evaluator](./impl/director-evaluator.md) - Director-Evaluator pattern implementation
- [Subtask Spawning](./impl/subtask-spawning.md) - Subtask spawning implementation

### Specification
- [Behaviors](./spec/behaviors.md) - Runtime behaviors
- [Interfaces](./spec/interfaces.md) - Internal interfaces
- [Types](./spec/types.md) - Type definitions
- [Requirements](./spec/requirements.md) - Functional and non-functional requirements
- [Q&A](./spec/qa.md) - Common questions and clarifications

For integration with other components, see:
- [Task System](../task-system/README.md) - Task structure and management
- [Handler](../handler/README.md) - LLM execution and resource tracking
- [Memory System](../memory/README.md) - Context management and associative matching
