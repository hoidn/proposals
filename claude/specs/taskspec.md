# Task System Enhancements Specification
> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

- Enhance the task execution system by implementing a `TaskLibrary` component for task definitions, enabling function calling through a new `FunctionCall` AST node, integrating a nested `Environment` model for lexical scoping, extending the XML schema to support optional `ref` and `subtype` attributes, and introducing a `cond` primitive for conditional execution based on JSON outputs. Follow the goals of the <high-level plan>

<high-level plan>
# Integration Overview
  ## 2.1 Existing Components and Interfaces
  
  ### XML Task Definitions & AST
  Tasks are defined in XML with attributes such as type and (newly) optional ref and subtype. The Compiler translates these into an Abstract Syntax Tree (AST).
  
  ### Evaluator
  The Evaluator executes the AST nodes, managing context and resource usage. It will now create and propagate a nested Environment (see Section 3.1) that carries both variable bindings and a reference to the global TaskLibrary.
  
  ### Handler & Memory System
  Existing components (Handler, Memory, etc.) continue to manage resource tracking, file metadata, and context window management. The new design does not change these responsibilities.
  
  ### Error Handling
  Errors (such as TASK_FAILURE and RESOURCE_EXHAUSTION) continue to be signaled using the same error types as before.
  
  ## 2.2 New or Updated Interfaces
  
  ### TaskLibrary Component
  A new in–memory registry that stores task definitions (both atomic and composite) organized by type and subtype. It is integrated into the global environment so that every nested environment can access the library.
  
  ### FunctionCall AST Node
  A new AST node type that represents function (task) calls. It looks up task definitions in the TaskLibrary (via the environment chain) and creates a new child environment with parameter bindings for execution.
  
  ### Nested Environment (Env) Model
  Inspired by Norvig's Lispy, every Environment object now supports an "outer" pointer and a find(var) method to perform lexical lookups. The global environment includes the TaskLibrary (and built–in variables) and is inherited by every child environment.
  
  ### Conditional Primitive (cond)
  A new DSL primitive that enforces that task outputs are in JSON format and enables conditional execution based on structured output.
  
  ## 3. Proposed Architecture Modifications
  
  ### 3.1 Nested Environment Model Integration
  
  #### A. Environment Class Definition
  Introduce a Lispy–style Environment class to manage variable bindings and context with lexical scoping:
  
  ```python
  class Env(dict):
      """
      An environment mapping variable names to values, with an optional outer environment.
      Mimics Norvig's Lispy environment for lexical scoping.
      """
      def __init__(self, parms=(), args=(), outer=None):
          super().__init__(zip(parms, args))
          self.outer = outer  # Reference to parent environment
  
      def find(self, var):
          "Find the innermost environment in which 'var' appears."
          if var in self:
              return self
          elif self.outer is not None:
              return self.outer.find(var)
          else:
              raise NameError(f"Variable '{var}' not found.")
  ```
  
  #### Integration Notes
  - The Evaluator creates a global environment (global_env) that includes standard built–in variables and, importantly, a reference to the TaskLibrary (e.g., global_env["taskLibrary"] = taskLibrary).
  - When a task is executed (or a function is called), the Evaluator creates a new child environment using Env(…, outer=parent_env), so that the TaskLibrary (and any other globals) remain accessible via the environment chain.
  
  #### B. Environment Interface in XML–Driven Execution
  The existing <inherit_context> XML attribute now directly maps to how a new environment is created:
  - inherit_context="full": Create a child environment with its outer pointer set to the parent.
  - inherit_context="none": Create an environment whose outer pointer is set to the global environment (or None).
  - inherit_context="subset": Optionally, create an environment with a filtered copy of parent bindings (details to be refined later).
  
  ### 3.2 TaskLibrary Component
  
  #### Purpose
  Maintain a global registry of task definitions so that tasks (whether defined inline or registered via a reference) can be looked up and reused. This decouples task metadata from runtime execution.
  
  #### Data Structure & Interface
  ```python
  class TaskDefinition:
      def __init__(self, name, type, subtype, metadata, ast_node):
          self.name = name            # Unique task identifier
          self.type = type            # e.g., "atomic" 
          self.subtype = subtype      # e.g., "director", "evaluator", etc.
          self.metadata = metadata    # Parameter schemas, return specs, etc.
          self.ast_node = ast_node    # Parsed AST for the task
  
  class TaskLibrary:
      def __init__(self):
          # Organize tasks by type; each type maps to a dict of subtypes to tasks.
          self.tasks = {
              'atomic': {},
              'composite': {},
              # Other task categories as needed.
          }
      
      def register_task(self, task_def: TaskDefinition):
          """Registers a new task definition. Raises an error if duplicate."""
          type_dict = self.tasks.setdefault(task_def.type, {})
          subtype_dict = type_dict.setdefault(task_def.subtype, {})
          if task_def.name in subtype_dict:
              raise ValueError(f"Task {task_def.name} is already registered.")
          subtype_dict[task_def.name] = task_def
  
      def get_task(self, name: str) -> TaskDefinition:
          """Looks up a task by name across all types and subtypes."""
          for type_group in self.tasks.values():
              for subtype_group in type_group.values():
                  if name in subtype_group:
                      return subtype_group[name]
          raise KeyError(f"Task {name} not found.")
  ```
  
  #### Integration Notes
  - The global environment (see Section 3.1) stores the TaskLibrary (e.g., under the key "taskLibrary").
  - When a FunctionCall is executed, it uses env.find("taskLibrary") to retrieve the registry regardless of the current nested environment.
  
  ### 3.3 FunctionCall AST Node for DSL Function Calling
  
  #### Purpose
  Enable tasks to be called like functions. Both atomic tasks and composite tasks are callable using a uniform interface that creates a new execution context.
  
  #### Implementation
  ```python
  class FunctionCall(ASTNode):
      def __init__(self, func_name, args):
          self.func_name = func_name  # The name of the task/function to be invoked.
          self.args = args            # A list of AST nodes representing arguments.
  
      def eval(self, env: Env):
          # Retrieve the TaskLibrary from the environment chain.
          task_library = env.find("taskLibrary")["taskLibrary"]
          task_def = task_library.get_task(self.func_name)
          
          # Create a child environment that inherits from the current one.
          # This child environment is used for executing the task.
          func_env = Env(outer=env)
          
          # Bind parameters to arguments, assuming task_def.metadata defines a list of parameter names.
          parameters = task_def.metadata.get("parameters", [])
          for param, arg_node in zip(parameters, self.args):
              func_env[param] = arg_node.eval(env)
          
          # Evaluate the task's AST node using the new environment.
          result = task_def.ast_node.eval(func_env)
          return result
  ```
  
  #### Key Points
  - The FunctionCall node looks up the task definition from the TaskLibrary.
  - It creates a new child environment (via the nested Env model) that automatically inherits global objects (like the TaskLibrary).
  - Parameter binding occurs by evaluating each argument in the caller's environment.
  - The task's AST is then executed in this fresh environment, ensuring proper lexical scoping.
  
  ### 3.4 XML Schema Extensions
  While the external XML syntax remains backward compatible, the following optional attributes are added for future–proofing and reference resolution:
  
  ```diff
  <xs:element name="task">
    <xs:complexType>
      <xs:attribute name="type" use="required">
        <xs:simpleType>
          <xs:restriction base="xs:string">
            <xs:enumeration value="atomic"/>
            <xs:enumeration value="sequential"/>
            <xs:enumeration value="reduce"/>
  +         <xs:enumeration value="script"/>
          </xs:restriction>
        </xs:simpleType>
      </xs:attribute>
  +   <xs:attribute name="ref" type="xs:string" use="optional"/>
  +   <xs:attribute name="subtype" type="xs:string" use="optional"/>
    </xs:complexType>
  </xs:element>
  ```
  
  #### Notes
  - The optional ref attribute enables a task node to reference a pre–registered task in the TaskLibrary.
  - The optional subtype attribute refines the task type (e.g., distinguishing director vs. evaluator in atomic tasks).
  
  ### 3.5 Conditional Primitive (cond) with JSON Output Enforcement
  
  #### Purpose
  Allow tasks to conditionally execute based on the structure of their outputs. In this design, tasks that are candidates for conditional execution must produce JSON–formatted output.
  
  #### Evaluator Helper Function Example
  ```python
  import json
  
  def eval_cond(condition_expr, env: Env):
      """
      Evaluates a condition against the last task output stored in env.last_output.
      Raises TASK_FAILURE if the output is not valid JSON.
      """
      try:
          output = json.loads(env.get("last_output", "{}"))
      except json.JSONDecodeError:
          raise Exception("TASK_FAILURE: Task output must be valid JSON for conditionals.")
      
      # Use Python's eval (with a safe namespace) to evaluate the condition.
      if eval(condition_expr, {"output": output}):
          return True
      else:
          return False
  ```
  
  #### DSL XML Example
  ```xml
  <cond>
      <case test="output.valid == true">
          <task type="atomic" subtype="success_handler">
              <description>Handle success</description>
          </task>
      </case>
      <case test="output.errors > 0">
          <task type="atomic" subtype="error_handler">
              <description>Handle error</description>
          </task>
      </case>
  </cond>
  ```
  
  #### Integration Notes
  - The evaluator uses the eval_cond helper to check conditions before selecting which task branch to execute.
  - This primitive bridges the DSL's control flow constructs with the need for structured (JSON) task output.
  
  ## 4. Phased Implementation Roadmap
  
  ### Phase 1: Minimal Implementation (MVP)
  
  #### Inline Task Support
  - Continue to support in–lined XML task definitions; tasks are directly embedded in the AST.
  
  #### Basic Function Calling
  - Implement the FunctionCall node as described above. Use a temporary TaskLibrary built during compilation.
  
  #### Nested Environment Model
  - Replace the flat environment model with the nested Env class. Initialize the global environment with built–in variables and the TaskLibrary.
  
  #### Conditional Primitive
  - Add support for the cond primitive that requires task outputs to be JSON–formatted.
  
  #### XML Compatibility
  - No external changes are required; XML remains unchanged apart from optional attributes that future phases can use.
  
  ### Phase 2: Hybrid Model
  
  #### Task Registration
  - Introduce a persistent TaskLibrary component that registers tasks from XML files (using the ref attribute).
  
  #### Reference Resolution
  - Update the Compiler so that when a task node has a ref attribute, the Evaluator retrieves the task definition from the TaskLibrary.
  
  #### Environment Propagation
  - Verify that every new environment created during function calls properly inherits the global TaskLibrary and built–in variables.
  
  ### Phase 3: Mature First–Class Functions
  
  #### Full Function Abstraction
  - Support parameterized, first–class task functions including potential closure–like behavior.
  
  #### Extended DSL Syntax
  - Introduce syntax (possibly a Lisp–like dialect or extended XML) for function definitions and calls.
  
  #### Evaluator Refactoring
  - Integrate the new function–calling mechanism throughout the system, including support for dynamic sub–task spawning and chaining.
  
  #### Enhanced Conditional & Output Validation
  - Refine the conditional primitive to support richer JSON–based decision making and output validation.
  
  ## 5. Testing and Verification
  
  ### Environment Lookup
  Verify that a child environment (e.g., created during a FunctionCall) can successfully use env.find('taskLibrary') to access the global TaskLibrary.
  
  ### FunctionCall Evaluation
  Test that a FunctionCall node correctly looks up the task definition, creates a new environment with parameter bindings, and returns the expected result.
  
  ### Conditional Execution
  Execute tasks with a cond block and verify that non–JSON outputs trigger a TASK_FAILURE error and that valid JSON outputs correctly guide execution.
  
  ### XML Schema and Reference Resolution
  Validate that tasks defined with the optional ref and subtype attributes are correctly resolved during evaluation without altering existing XML–based workflows.
  
  ## 6. Advantages and Justification
  
  ### Unified Environment Resolution
  The nested environment model simplifies variable and global object lookups by allowing child tasks to transparently access the TaskLibrary and built–ins.
  
  ### Decoupling of Task Metadata
  With a dedicated TaskLibrary, task definitions are managed independently of runtime execution. This decoupling supports reuse, modularity, and a phased migration from inline tasks.
  
  ### Seamless DSL Function Calling
  The new FunctionCall node allows tasks to be treated uniformly as callable procedures. Parameter binding and return–value handling are consistent with the new environment model.
  
  ### Backward Compatibility
  External XML syntax remains unchanged (except for optional extensions), ensuring that existing workflows and error–handling semantics continue to function.
  
  ### Extensibility
  The phased roadmap allows the system to start with a minimal, stable MVP and then evolve toward more complex features (such as closures, extended DSL syntax, and dynamic sub–task spawning) without disrupting the core execution model.
  to the model instead of a global variable. 
</high-level plan>

## Mid-Level Objective

- Implement a `TaskLibrary` to register and retrieve task definitions, both atomic and composite.
- Update AST types to include a `FunctionCall` node that enables function-like task invocation.
- Integrate a nested `Environment` model into the Evaluator to support lexical scoping and variable bindings.
- Extend the XML schema to include optional `ref` and `subtype` attributes for tasks.
- Implement the `cond` primitive to enable conditional execution based on structured JSON outputs.
- Update resource management patterns to accommodate script execution tasks and sequential history tracking.
- Ensure backward compatibility with existing XML syntax and task execution flows.

## Implementation Notes

- Use type hints throughout all new and updated code.
- Maintain backward compatibility with existing XML task definitions.
- The `Environment` model should support nested environments with lexical scoping via an `outer` reference and a `find(var)` method.
- The `Evaluator` should create and manage environments appropriately when executing tasks, including function calls.
- The `TaskLibrary` should be accessible globally via the environment chain.
- Update all relevant interfaces and types to reflect the new components and features.
- Ensure that resource limits and context management adhere to the updated resource management patterns.
- Provide thorough documentation and inline comments for all new code and updates.

## Context

### Beginning Context

- `./components/task-system/spec/types.md`
- `./components/task-system/spec/interfaces.md`
- `./components/evaluator/README.md`
- `./system/contracts/protocols.md`
- `./system/architecture/patterns/resource-management.md`
- `./components/memory/api/interfaces.md`



### Ending Context

- Updated versions of all the files listed in the Beginning Context, incorporating the new components and features.

## Low-Level Tasks
> Ordered from start to finish

1. **Update Task Types to Include TaskDefinition and TaskLibrary**

    ```aider
    UPDATE ./components/task-system/spec/types.md:
        ADD interface TaskDefinition {
            name: string;                     // Unique task identifier
            isatomic: bool;
            type: TaskType;                   // e.g., "atomic" or "sequence"
            subtype?: string;                 // Optional subtype, e.g., "director", "evaluator"
            metadata?: Record<string, any>;    // Parameter schemas, return specs, etc.
            astNode: ASTNode;                 // Parsed AST for the task
        }

        ADD class TaskLibrary {
            tasks: Map<string, TaskDefinition>;

            constructor() {
                this.tasks = new Map();
            }

            registerTask(taskDef: TaskDefinition): void {
                if (this.tasks.has(taskDef.name)) {
                    throw new Error(`Task ${taskDef.name} is already registered.`);
                }
                this.tasks.set(taskDef.name, taskDef);
            }

            getTask(name: string): TaskDefinition {
                const taskDef = this.tasks.get(name);
                if (!taskDef) {
                    throw new Error(`Task ${name} not found in TaskLibrary.`);
                }
                return taskDef;
            }
        }

        ADD type TaskType = "atomic" | "sequential" | "reduce" | "script" ;

        ADD interface FunctionCall extends ASTNode {
            funcName: string;
            args: ASTNode[];
        }

        ADD interface Environment {
            bindings: Record<string, any>;
            outer?: Environment;
            find(varName: string): any;
        }

        UPDATE ContextManagement interface:
            inheritContext: 'full' | 'none' | 'subset';
    ```

2. **Update TaskSystem Interfaces to Include TaskLibrary Methods**

    ```aider
    UPDATE ./components/task-system/spec/interfaces.md:
        ADD interface TaskSystem {
            // Existing methods...
            registerTask(taskDef: TaskDefinition): void;
            executeFunctionCall(funcCall: FunctionCall, env: Environment): Promise<any>;
        }

        ADD interface Environment {
            bindings: Record<string, any>;
            outer?: Environment;
            find(varName: string): any;
        }

        UPDATE Handler interface:
            ADD executeScriptTask(scriptTask: ScriptTask, env: Environment): Promise<ScriptTaskResult>;
    ```

3. **Integrate Nested Environment Model into Evaluator**

    ```aider
    UPDATE ./components/evaluator/README.md:
        ADD section "3.1 Nested Environment Model Integration":
            - Describe the `Environment` class supporting nested scopes with an `outer` reference and `find(var)` method.
            - Explain how the `Evaluator` creates a global environment (`globalEnv`) that includes the `TaskLibrary` and built-in variables.
            - Detail how a new child environment is created when executing a task or function call, inheriting from the parent environment.
            - Include code examples demonstrating environment creation and variable lookup.

        ADD section "3.3 FunctionCall AST Node for DSL Function Calling":
            - Explain the purpose and implementation of the `FunctionCall` node.
            - Show how the `Evaluator` handles `FunctionCall` nodes by looking up the task in the `TaskLibrary`, creating a new environment, binding parameters, and evaluating the task's AST node.
            - Provide code examples for `FunctionCall` evaluation.

        ADD updates to "Context and Environment Handling":
            - Discuss how the nested `Environment` model affects context propagation and variable scoping during task execution.
    ```

4. **Extend XML Schema to Support Optional Attributes and Conditional Execution**

    ```aider
    UPDATE ./system/contracts/protocols.md:
        EXTEND XML Schema Definition:
            ADD optional `ref` attribute to `<task>` element:
                <xs:attribute name="ref" type="xs:string" use="optional"/>

            ADD optional `subtype` attribute to `<task>` element:
                <xs:attribute name="subtype" type="xs:string" use="optional"/>

            ADD new `<cond>` element definition to support conditional execution:
                <xs:element name="cond">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="case" maxOccurs="unbounded">
                                <xs:complexType>
                                    <xs:attribute name="test" type="xs:string" use="required"/>
                                    <xs:sequence>
                                        <xs:element name="task" minOccurs="1" maxOccurs="1">
                                            <!-- Task definition inside case -->
                                        </xs:element>
                                    </xs:sequence>
                                </xs:complexType>
                            </xs:element>
                        </xs:sequence>
                    </xs:complexType>
                </xs:element>

        UPDATE Field Definitions:
            - Describe the optional `ref` attribute used to reference pre-registered tasks in the `TaskLibrary`.
            - Explain the optional `subtype` attribute for refining task types.

        ADD Example usage of `<cond>` element in XML templates, demonstrating conditional execution based on JSON-formatted task outputs.

        UPDATE Interface Mapping:
            - Map the new XML elements and attributes to the corresponding interfaces and types in the Task System.
    ```

5. **Update Resource Management Patterns for Script Execution and Sequential History**

    ```aider
    UPDATE ./system/architecture/patterns/resource-management.md:
        ADD section "Script Execution Resource Management":
            - Describe how script tasks are handled regarding resource usage.
            - Explain that the `Handler` executes script tasks and captures `stdout`, `stderr`, and `exitCode`.
            - Detail how non-zero `exitCode` values are treated as `TASK_FAILURE` errors.

        UPDATE "Sequential Task Resources":
            - Explain how the `Evaluator` maintains a `SequentialHistory` for sequential tasks.
            - Clarify that the `SequentialHistory` is not tracked against the `Handler`'s context window limits.
            - Describe how accumulated outputs are stored and when they are discarded to free memory.
            - Include code examples or interfaces for `SequentialHistory` if applicable.

        UPDATE "Context Management":
            - Discuss how the nested `Environment` model affects resource isolation and context preservation.
            - Emphasize the importance of proper environment chaining to prevent context leakage.
    ```

6. **Update Memory System Interface for New Environment Model**

    ```aider
    UPDATE ./components/memory/api/interfaces.md:
        REMOVE method:
            - delete updateContext(context: Environment): Promise<void>;

        ADD structured input format for getRelevantContextFor():
            UPDATE interface ContextGenerationInput {
                previousOutputs?: string;   // Accumulated outputs from previous steps
                inheritedContext?: string;  // Context inherited from parent tasks
                taskText: string;           // The primary task description or request
            }

        UPDATE getRelevantContextFor() method signature:
            declare function getRelevantContextFor(input: ContextGenerationInput): Promise<AssociativeMatchResult>;

        UPDATE GlobalIndex interface:
            - Ensure that the GlobalIndex reflects the latest needs of the `TaskLibrary` and environment model.
            - Clarify any changes needed to support the nested environment model and task associative matching.
    ```
