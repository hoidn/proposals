from dataclasses import dataclass
from typing import Any, Optional, Tuple
from enum import Enum

from .error_types import ExecutionError
from .environment import Environment

# TODO <dynamic reparsing> if LLM execution fails (typically bc of resource exhaustion or verification failure)
# we need to recover by reparsing the AST node into one or more rewritten subtrees 
# (i.e. either a new atomic expression or a decomposed, compound expression). See the 
# Scheme description to get the general idea. also see <errors>
# </dynamic reparsing>

class Evaluator:
    def __init__(self, compiler):
        self.compiler = compiler
        self.max_reparse_attempts = 3

    def eval(self, node: ASTNode, env: Environment, reparse_depth: int = 0) -> Any:
        """Evaluate a node with error recovery via reparsing
        
        Args:
            node: The AST node to evaluate
            env: Current execution environment
            reparse_depth: Current depth of reparsing attempts
            
        Returns:
            Result of evaluation
            
        Raises:
            ExecutionError: If evaluation fails after max attempts
        """
        try:
            if self.is_atomic(node.operator):
                return self.execute_llm(node.operator, env)
            elif node.operator.type == "reparse":
                return self.handle_reparse(node, env, reparse_depth)
            else:
                # Handle compound expressions
                evaluated_args = [self.eval(arg, env) for arg in node.args]
                return self.apply(node.operator, evaluated_args, env)
                
        except ExecutionError as error:
            if reparse_depth >= self.max_reparse_attempts:
                raise ExecutionError.max_reparse_exceeded(
                    task=node.operator.task,
                    attempts=reparse_depth
                )
            
            # Generate new AST through reparsing
            new_node = self.compiler.reparse(
                failed_task=node.operator.task,
                error=error,
                env=env
            )
            
            # Evaluate the reparsed node
            return self.eval(new_node, env, reparse_depth + 1)

    # TODO this might be unnecessary. we can handle reparsing as a regular
    # atomic task
    def handle_reparse(self, node: ASTNode, env: Environment, depth: int) -> Any:
        """Handle evaluation of reparse operators
        
        These represent explicit requests to transform a failed task.
        The transformation itself is handled by the compiler.
        
        Args:
            node: Node containing reparse operator
            env: Current environment
            depth: Current reparse depth
            
        Returns:
            Result of evaluating the reparsed task
        """
        if depth >= self.max_reparse_attempts:
            raise ExecutionError.max_reparse_exceeded(
                task=node.operator.params["original_task"],
                attempts=depth
            )
        
        # Execute the reparse prompt to get new task structure
        xml = self.execute_llm(node.operator, env)
        
        # Parse into new AST
        new_node = self.compiler.parser.task_to_ast(
            self.compiler.parser.parse_task(xml)
        )
        
        # Evaluate the new node
        return self.eval(new_node, env, depth + 1)

    def is_atomic(self, operator: Any) -> bool:
        """Check if operator represents direct LLM execution"""
        return operator.type == "atomic"
    
    def execute_llm(self, operator: Any, env: Environment) -> Any:
        """Execute task with LLM"""
        return self.llm_execute(operator.task, env)
    
    def apply(self, operator: Any, args: List[Any], env: Environment) -> Any:
        """Apply compound operator to evaluated arguments"""
        new_env = env.extend(operator.params, args)
        return self.eval(operator.body, new_env)

