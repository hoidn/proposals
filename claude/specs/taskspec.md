# Task System Enhancements Specification
> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

- Enhance the task execution system by implementing a `TaskLibrary` component for task definitions, enabling function calling through a new `FunctionCall` AST node, integrating a nested `Environment` model for lexical scoping, extending the XML schema to support optional `ref` and `subtype` attributes, and introducing a `cond` primitive for conditional execution based on JSON outputs.

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
            type: TaskType;                   // e.g., "atomic" or "composite"
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

        ADD type TaskType = "atomic" | "sequential" | "reduce" | "script" | "composite";

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