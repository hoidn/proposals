# Resource Warning Pattern [Pattern:ResourceWarning:1.0]

## Warning Types

### Resource Thresholds
As documented in task-system/impl/resource-management.md:
- Warning at 80% of resource limit
- Error at limit reached

### Handler Requirements
When a warning threshold is reached:
- Track in resource metrics
- Continue task execution
- Maintain resource monitoring

## Integration Points

### With Error System [Pattern:Error:1.0]
- Surface resource exhaustion
- Provide resource metrics
- Enable error handling

### With Task System [Component:TaskSystem:1.0]
- Continue resource tracking
- Maintain monitoring
- Handle exhaustion errors