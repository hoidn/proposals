from dataclasses import dataclass
from typing import Dict, Optional, Protocol
from enum import Enum

from .error_types import ExecutionError, ErrorType
from .task_system import TaskSystem

class OperatorType(Enum):
    """Types of operations that can be performed"""
    ATOMIC = "atomic"
    REPARSE = "reparse"
    MAP = "map"
    REDUCE = "reduce"
    SEQUENCE = "sequence"

@dataclass
class Operator:
    """Represents an operation to be performed"""
    type: str  # Maps to OperatorType values
    task: str  # Task description
    params: Optional[Dict] = None  # Additional parameters if needed

def create_reparse_operator(
    failed_task: str,
    error: ExecutionError,
    task_system: TaskSystem
) -> Operator:
    """Creates an operator for reparsing failed tasks
    
    Args:
        failed_task: The task description that failed
        error: Details about the failure
        task_system: System for managing tasks and prompts
        
    Returns:
        Operator configured for reparsing the failed task
    """
    # Get the LLM prompt for reparsing, with information
    # from the failed task substituted in
    prompt = task_system.get_reparse_prompt(failed_task,
                                   error)

    # Create operator with error details in params
    return Operator(
        type=OperatorType.REPARSE.value,
        task=prompt,
        params={
            "original_task": failed_task,
            "error_type": error.type.value,
            "error_details": error.details
        }
    )

class Compiler:
    """Handles AST generation and transformation"""
    
    def __init__(self, task_system: TaskSystem):
        self.task_system = task_system
        self.parser = XMLTaskParser()

    def parse(self, xml) -> ASTNode:
        """Convert XML task structure to AST
        
        Two cases:
        - Atomic: direct LLM execution (no args)
        - Compound: task with subtasks
        """
        operator = self.parse_operator(xml.operator)
        
        # Case 1: Atomic task
        if self.is_atomic(xml):
            return ASTNode(operator=operator, args=[])
            
        # Case 2: Compound task
        return ASTNode(
            operator=operator,
            args=[self.parse(arg) for arg in xml.args]
        )

    # TODO the xml needs to be validated to have the right op_data 
    # and also the right xml structure, given the operator type
    def parse_operator(self, xml_operator) -> Operator:
        """Convert XML operator element to Operator object"""
        # XML operator contains JSON text with type and task
        op_data = json.loads(xml_operator.text)
        return Operator(
            type=op_data["type"],
            task=op_data["task"],
            params=op_data.get("params")
        )

    def bootstrap(self, query: str) -> ASTNode:
        """Compiles natural language to AST"""
        xml = self.llm_translate(query)
        return self.parse(xml)

    def reparse(self, 
                failed_task: str,
                error: ExecutionError,
                env: Environment) -> ASTNode:
        """Transform failed AST node into new AST
        
        Args:
            failed_task: Description of task that failed
            error: Details about the failure
            env: Current execution environment
        
        Returns:
            New AST subtree to try executing
        """
        # Create reparse operator
        operator = create_reparse_operator(
            failed_task=failed_task,
            error=error,
            task_system=self.task_system
        )
        
        # Generate new task structure via LLM
        # TODO this should be done by calling the evaluator 
        # on operator. The result of that operation will be 
        # a reparsed expression in xml format. IMPORTANT: Note that 
        # reparse should actually be an atomic operation. This means 
        # the OperatorType / Operator spec needs to be changed. There 
        # might be no need for special handling of reparse nodes on the 
        # evaluator side as long as the xml generated by the task 
        # system has the right information. Since the task system needs 
        # special handling of reparse tasks anyways, we're not losing
        # any generality by hard coding the parameters at the task level 
        # instead of passing them around as inputs in the Evaluator 
        # the reparse node weren't special 
        xml = # TODO
        
        # Parse into intermediate structure
        task_structure = self.parser.parse_task(xml)
        
        # Convert to AST and return
        return self.parser.task_to_ast(task_structure)

    def llm_translate(self, prompt: str) -> Element:
        """Translate natural language to XML via LLM
        
        TODO: Implement LLM interaction:
        - Format prompt with XML expectations
        - Handle LLM response parsing
        - Validate XML structure
        """
        pass

# TODO: Define Protocol class for reparse operations to formalize interface
# This would allow different reparse strategies while maintaining consistent interface

# TODO: Add validation at component boundaries
# - Input validation for natural language queries
# - XML structure validation
# - AST structure validation

# TODO: Future enhancement - move XML format specification to TaskSystem
# This will allow TaskSystem to control the structure of task decomposition

# TODO: Consider adding a CompilerOptions class for configuration
# This would make the compiler more configurable without complicating the core interface
