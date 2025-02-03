# Task System Requirements

## System Constraints

### Resource Management
- Does not predict resource usage
- Does not optimize task decomposition
- No responsibility for context window management
- Relies on Handlers for resource tracking
- Model selection delegated to Handler
- No cross-Handler resource pooling
- Per-session resource isolation
- Clean resource release on completion

### Task Templates and Script Execution Support
- XML templates must conform to [Contract:Tasks:TemplateSchema:1.0] and now support script execution tasks within sequential workflows.
- Support both LLM-generated and manual XML structures.
- Basic XML validation with warning generation and graceful degradation.
- Support for disabling reparsing on manual XML tasks.
- Template persistence in disk-based XML format with clear versioning.
- Script Task Requirements:
   - The XML schema must allow specification of command details for script execution.
   - Define clear input/output contracts to pass data from the director task to the script and from the script to the evaluator.

### Task Matching
- Limited to top N candidates (aim for 5 or fewer)
- Scoring is numeric only
- Context limited to node level for AST matching
- Initial environment limited to human-provided files
- Scoring logic contained within matching prompts
- No cross-session matching history
- Independent scoring for human vs AST matching
- Clear score ordering requirements

### Memory Integration
- Direct access to memory system interfaces
- Read-only context access
- No state maintenance between tasks
- Clear separation from Evaluator state
- Standard memory structure requirements
- No caching or persistence
- Explicit context boundaries

### Handler Management
- One Handler per task execution
- Clean Handler lifecycle management
- Immutable Handler configuration
- Resource tracking requirements
- Clear turn counting rules
- Context window management
- No Handler state persistence
- Independent Handler execution
