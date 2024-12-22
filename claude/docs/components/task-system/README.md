# Task System Component

## Purpose
The Task System manages LLM task execution through structured templates and handlers, providing:
- Task template matching and management
- LLM session management via encapsulated Handlers
- XML task generation and validation with graceful degradation
- Management of specialized tasks (reparsing and associative memory)

## Core Components

### Handler
Manages individual LLM sessions:
- Turn counting and resource limits enforcement
- Context window management
- Direct LLM interaction
- Interactive session support
- Resource usage tracking

### Template Manager
Handles task definitions:
- Template validation
- Task matching
- XML processing

## Key Constraints

### Architectural
- Synchronous operation only
- No persistent state maintenance
- XML-based task definitions
- Read-only memory system access

### Operational
- One Handler per task execution
- Immutable Handler configuration
- Template immutability during execution
- No direct resource usage tracking (delegated to Handlers)
- No progress/retry state (managed by Evaluator)

## System Integration

### Dependencies
- Memory System: Context access and management
- Compiler: Task parsing services
- Evaluator: Error recovery support
- XML Processing: Template and output handling

### Responsibilities
Provides:
- Task execution and template management
- LLM session encapsulation
- XML processing and validation services
- Error detection and propagation

## Contracts

### Initialization
- Memory system access configured
- Resource limits defined
- Template directory available

### Runtime
- One Handler per task
- Resource limits enforced
- Templates immutable during execution

### Termination
- Handlers cleaned up
- Resources released
- No state preserved
