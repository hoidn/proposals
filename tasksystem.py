class XMLTaskParser:
    """Parses XML task descriptions into structured form"""
    
    def parse_task(self, xml: Element) -> TaskStructure:
        """Parse XML into TaskStructure
        
        Handles both atomic tasks and decompositions.
        
        Args:
            xml: XML element representing task
            
        Returns:
            Parsed task structure
        """
        task_type = TaskType(xml.get('type', 'atomic'))
        description = xml.find('description').text
        
        # Handle parameters if present
        params = {}
        params_elem = xml.find('parameters')
        if params_elem is not None:
            for param in params_elem:
                params[param.get('name')] = param.text
                
        # Handle subtasks for non-atomic tasks
        subtasks = []
        if task_type != TaskType.ATOMIC:
            for subtask in xml.findall('subtask'):
                subtasks.append(self.parse_task(subtask))
        
        return TaskStructure(
            type=task_type,
            description=description,
            subtasks=subtasks if subtasks else None,
            parameters=params if params else None
        )

    def task_to_ast(self, task: TaskStructure) -> ASTNode:
        """Convert parsed task structure to AST
        
        Maps task types to appropriate AST structures:
        - ATOMIC -> single node
        - MAP -> parallel execution structure
        - REDUCE -> result combination structure
        - SEQUENCE -> sequential execution structure
        
        Args:
            task: Parsed task structure
            
        Returns:
            Corresponding AST node
        """
        operator = Operator(
            type=task.type.value,
            task=task.description,
            params=task.parameters
        )
        
        if task.type == TaskType.ATOMIC:
            return ASTNode(operator=operator, args=[])
            
        # For non-atomic tasks, recursively convert subtasks
        return ASTNode(
            operator=operator,
            args=[self.task_to_ast(subtask) for subtask in task.subtasks]
        )

