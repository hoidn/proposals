How well is associative matching (both of task strings / templates and of context) specced out in this documentation?

---

<file path="./misc/errorspec.md" project="">
# Error Type Hierarchy and Handling Design

## Purpose
Define the core error types that enable control flow and task adaptation in the intelligent task execution system.

## Error Categories

### 1. Resource Exhaustion
- **Purpose**: Signal when system resource limits are exceeded
- **Characteristics**:
  - Parameterized resource type and limits (e.g., turns, context window)
  - Clear threshold for triggering
  - No partial results preserved
- **Control Flow Impact**: 
  - Signals that task requires more resources than available

### 2. Task Failure
- **Purpose**: Signal that a task cannot be completed as attempted
- **Characteristics**:
  - Generic failure mechanism
  - No internal categorization
  - No partial results preserved
- **Control Flow Impact**:
  - Task terminates
  - Control returns to parent task/evaluator

## Error Handling Principles

### 1. Separation of Concerns
- Errors purely signal failure conditions
- No recovery logic in error objects
- No state/progress tracking
- No partial results

### 2. Control Flow
- Resource Exhaustion → Task too large
- Task Failure → Termination
- No retry logic in components

### 3. Context Independence  
- Errors do not carry execution state.
- No partial results in errors.
- Clean separation from context management.

### Missing Argument Handling
When a task attempts to resolve an input, the evaluator first performs template substitution on any placeholders in the form {{variable_name}} within the task definition—using values from its current lexical environment. Additionally, if an <input> element specifies a from attribute, the evaluator binds that input using the value associated with that environment variable. If a required binding is missing, the evaluator returns a standard TASK_FAILURE error with a message such as "Missing required input: variable_name."

## Integration Points

All components in the unified task-execution system use the same generic error signaling.
In particular:
 - The Task System (and its unified execution component) detects resource exhaustion and signals a generic TASK_FAILURE with attached metadata.
 - The Memory System continues to provide context without carrying error state.

## Design Decisions & Rationale

1. Minimal Error Categories
   - Only essential control flow signals
   - Clear mapping to system behaviors
   - Simplified error handling

2. Stateless Error Design
   - Separates control flow from state
   - Clean component boundaries
   - Simplified recovery

3. No Complex Recovery
   - Decomposition as consequence not strategy
   - Simplified control flow
   - Clear system behavior

## Context Operation Failures

In scenarios where a task step calls MemorySystem.getRelevantContextFor() (or otherwise attempts context assembly), any failure is reported as a standard TASK_FAILURE.
Partial results are not preserved; on any failure, intermediate data is discarded.

In short, "context operation failures" are reported solely as TASK_FAILURE, and no partial sub-task outputs are retained.

## Dependencies
- Task system must detect resource limits

## Script Execution Errors
Script execution errors (e.g. non-zero exit codes) are captured and passed along to the evaluator for downstream decision-making rather than causing an immediate task failure.
- Evaluator must handle control flow
- Memory system must maintain context
</file>
<file path="./misc/operators.md" project="">
# Sequential and Reduce Operator Specification

## Purpose
Define the structure and semantics of Sequential and Reduce operators for task composition and execution, specifying XML schemas and execution behaviors.

## Memory Structure
typescript
shortTermMemory: {
    files: Map<string, WorkingFile>;
    dataContext: string;
}


## Sequential Operator

### Purpose
Execute a series of tasks with explicit dependencies. Maintains execution order while allowing parallel execution of independent inputs.

### Structure
xml
<task type="sequential">
    <description>Analyze {{dataset_name}} using provided configuration</description>
    <context_management>
        <inherit_context>none</inherit_context>
        <accumulate_data>true</accumulate_data>
        <accumulation_format>notes_only</accumulation_format>
    </context_management>
    <steps>
        <task>
            <description>Load initial data</description>
            <inputs>
                <input name="data" from="raw_data"/>
            </inputs>
        </task>
        <task>
            <description>Apply configuration from {{config_profile}}</description>
            <inputs>
                <input name="config" from="default_config"/>
            </inputs>
        </task>
    </steps>
</task>


### Context Management Modes

In the updated model, the <inherit_context> element is now an enumeration with allowed values:
 - **full** – the full parent context is passed unchanged,
 - **none** – no parent context is inherited,
 - **subset** – only a subset (as determined by task-specific rules) is inherited.

The accumulation of step outputs remains controlled by the boolean <accumulate_data> element, and <accumulation_format> is restricted to either notes_only or full_output. **Note:** For the MVP, no partial results are preserved—if any subtask fails, intermediate outputs are discarded.

For example, the above XML snippet indicates that no parent context is inherited while step outputs are accumulated in "notes-only" mode.

### Execution Semantics
- Tasks execute in specified order
- For tasks with multiple inputs:
  - All input tasks execute in parallel
  - Parent task executes after all inputs complete
- Execution fails if:
  - Required task structure is missing/invalid
  - Any task execution fails (with failure context indicating which task)

## Reduce Operator

### Purpose
Process a list of named inputs through repeated application of inner task and reduction operations.

### Structure
xml
<task type="reduce">
    <description>Reduction operation description</description>
    <initial_value>
        <!-- Initial accumulator value -->
    </initial_value>
    <inputs>
        <input name="dataset1">Value 1</input>
        <input name="dataset2">Value 2</input>
        <input name="dataset3">Value 3</input>
    </inputs>
    <inner_task>
        <description>Processing for each input</description>
        <inputs>
            <input name="current_data">
                <!-- Current input being processed -->
            </input>
            <input name="metadata">
                <!-- Additional input needed for processing -->
                <task>
                    <description>Load metadata for processing</description>
                </task>
            </input>
        </inputs>
    </inner_task>
    <reduction_task>
        <description>Combine current result with accumulator</description>
        <inputs>
            <input name="current_result">
                <!-- Result from inner_task -->
            </input>
            <input name="accumulator">
                <!-- Current accumulated value -->
            </input>
            <input name="original_input">
                <!-- Original input being processed -->
            </input>
        </inputs>
    </reduction_task>
</task>


### Execution Semantics
- For each named input:
  1. Execute inner_task with:
     - Current input
     - Any additional specified inputs
     - When both inheritance and accumulation are enabled in a reduce operator, a basic inheritance model is used without merging accumulated outputs. Advanced dual-context tracking is deferred to future iterations.
  2. Execute reduction_task with:
     - Current inner_task result
     - Current accumulator value
     - Original input
  3. Result becomes new accumulator value
- Maintains strict ordering of input processing
- Context changes managed by memory system
- Execution fails if:
  - Required task structure is missing/invalid 
  - Any inner_task execution fails (with failure context indicating which input)
  - Any reduction_task execution fails (with failure context indicating current state)

## Integration Points

### With Memory System
- System maintains execution context via shortTermMemory
- Files and data context available to all tasks
- Context changes managed by memory system, not tasks

### With Task System
- Responsible for generating valid XML
- Manages task decomposition on failure
- Handles task library matching

## Dependencies
- Error types defined in errorspec.md
- Memory system must handle context
- Task system must support XML generation

## Constraints
- Tasks cannot modify context directly
- XML structure must encode all input dependencies
- All inputs must have unique names within their scope
- Inner tasks can specify multiple inputs
</file>
<file path="./misc/textonly.tex.md" project="">
\documentclass{article}

\usepackage[numbers]{natbib}  % For citation management - numbers style matches current format
\usepackage{subcaption}  % Add this to preamble if not already present
\usepackage{fancyvrb}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{listings}
\usepackage[ruled,vlined]{algorithm2e}
\usepackage{xcolor}
% Add to preamble:
\usepackage{listings}
\usepackage{xcolor}

% Define colors for syntax highlighting
\definecolor{codebackground}{rgb}{0.98,0.98,0.98}
\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{codegreen}{rgb}{0.25,0.5,0.37}
\definecolor{codekeyw}{rgb}{0.23,0.49,0.73}

% Full definition of Scheme language for listings
\lstdefinelanguage{Scheme}{
    morekeywords={define, lambda, if, cond, else, let, and, or, map, 
                  begin, quote, car, cdr, cons, list, null, set!, 
                  apply, eval, display, newline},
    sensitive=true,
    morecomment=[l]{;},
    morestring=[b]",
    basicstyle=\ttfamily\footnotesize,
    keywordstyle=\color{codekeyw}\bfseries,
    commentstyle=\color{codegray},
    stringstyle=\color{codepurple},
    showstringspaces=false
}

% Set up code listing style
\lstset{
    % Reduced font size and adjusted line spread
    basicstyle=\linespread{1.1}\ttfamily\footnotesize,
    backgroundcolor=\color{codebackground},
    commentstyle=\color{codegray},
    keywordstyle=\color{codekeyw}\bfseries,
    stringstyle=\color{codepurple},
    numberstyle=\tiny\color{codegray},
    breakatwhitespace=false,
    breaklines=true,
    captionpos=b,
    keepspaces=true,
    numbers=left,
    numbersep=8pt,  % Reduced number separation
    showspaces=false,
    showstringspaces=false,
    showtabs=false,
    tabsize=2,
    frame=leftline,
    framesep=6pt,  % Reduced frame separation
    framexleftmargin=10pt,
    framextopmargin=4pt,
    framexbottommargin=4pt,
    % Adjusted margins to use more horizontal space
    xleftmargin=15pt,
    xrightmargin=2pt,  % Reduced right margin
    aboveskip=16pt,
    belowskip=16pt,
    emphstyle={\color{codekeyw}},
    morekeywords={env, args, node},
    % Better line breaking settings
    breaklines=true,
    breakatwhitespace=true,
    prebreak=\raisebox{0ex}[0ex][0ex]{\ensuremath{\hookleftarrow}},
    columns=flexible  % Better spacing for code
}

% Language-specific adjustments
\lstdefinestyle{pythonstyle}{
    language=Python,
    morekeywords={self, return, yield, raise, break, continue, pass, assert},
    commentstyle=\color{codegray},
    stringstyle=\color{codepurple},
}

\lstdefinestyle{xmlstyle}{
    language=XML,
    morekeywords={xmlns,xml,version}
}

\lstdefinestyle{schemestyle}{
    language=Scheme
}
\title{Intelligent Automation for Scientific Workflows}
%\author{Oliver Hoidn} % Replace with actual author name
\date{}

\usepackage[hidelinks]{hyperref}
\begin{document}
\maketitle


The main insight is treating natural language interaction with an LLM as a form of code execution. Suppose that we first ask the LLM to translate natural language instructions into programs written in a DSL (domain specific language). The structure of such a DSL program will represent the decomposition of a complex prompt into multiple tasks. The interpretation of the same program involves distribution of each component task to an LLM instance and the linking together of instances through a calling convention and shared memory system.

More concretely:

\begin{algorithm}[H]
\SetAlgoLined
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
Natural Language Query\;
$\downarrow$ [LLM Translation]\;
XML Task Structure (equivalent to S-expression)\;
$\downarrow$ [Parser]\;
Abstract Syntax Tree\;
$\downarrow$ [tree traversal]\;
LLM execution\;
\caption{System Overview}
\end{algorithm}

In this schema, natural language queries are first translated into composite expressions made up of smaller units (atomic tasks) with the purpose to make the execution tractable while preserving semantics of the original query. A satisfying feature of the setup is that it will be self-hosting in the sense that the LLM evaluates DSL procedures generated by the LLM.

An equivalent perspective is that the framework will dynamically compile the user's prompt into a directed acyclic graph (DAG). Each node of the DAG is dispatched to a separate LLM session, and data travels down and up the nodes of the graph in the form of environment frames and return values, respectively. 

The architecture consists of three main components:

\newpage
\subsection{Execution Model}
Two mutually recursive procedures, eval and apply, work with each other to evaluate DSL expressions:


\begin{lstlisting}[language=Scheme, caption = Scheme sketch of the evaluation procedure]
; Evaluates a task in the given environment; returns direct result or decomposed tasks
(define (eval-task task env)
  (cond 
    ; For atomic tasks, try direct application; if it fails, decompose
    ((atomic? task)
     ; amb tries the first option; if it fails, backtracks to the second
     (amb (apply-proc task '() env)                 ; Direct application
          (eval-task (decompose task) env)))        ; Or decomposition
    
    ; For compound tasks: evaluate arguments, apply procedure
    (else 
     (let ((proc (task-proc task))
           (args (map (lambda (arg) (eval-task arg env))
                     (task-args task))))
       (apply-proc proc args env)))))

; Applies a procedure to evaluated arguments in given environment
(define (apply-proc proc args env)
  (cond
    ; For primitives, try direct execution; if it fails, decompose and retry
    ((primitive? proc)
     ; amb tries the first option; if it fails, backtracks to the second
     (amb (execute-llm proc args env)               ; Direct execution
          (eval-task (decompose proc args) env)))   ; Or decomposition
    
    ; For compound procedures: create new environment, evaluate body
    (else
     (let ((new-env (extend-environment proc args env)))
       (eval-task (procedure-body proc) new-env)))))
\end{lstlisting}

When task execution ends with an error (e.g. context window overrun, output validation failure), the executor can retry by generating and evaluating an alternate procedure -- for example, a decomposition of the task into multiple subtasks.

The creation of the execution data context 'env' is mediated by the memory subsystem.

\subsection{Associative memory system}
The memory system explicitly separates storage and working contexts through a hierarchical design:
\begin{itemize}
    \item Long-term memory for data and procedures
    \item Working memory for active computations
    \item Context frames that capture execution environments (including working memory)
\end{itemize}

Working memory is instantiated from long-term storage using an associative retrieval mechanism that is itself an (atomic) LLM procedure whose purpose is to match an atomic task to a contextually relevant subset of the data in long-term memory.

\subsection{Task Expression Framework}
The expression system supports nested procedures and basic functional patterns:

\begin{lstlisting}[caption=Task Expression Types]
AtomicTask     -> Direct LLM execution
NestedTask     -> Compositional evaluation  
MapExpression  -> Parallel processing
ReduceExpression -> Result combination
\end{lstlisting}

These expressions, which can be extended, provide formal semantics for the DSL.


\section{PL concepts and concrete examples}
\subsection{Compilation}

Staged compilation traditionally refers to breaking down compilation into distinct phases, where each stage transforms the program into a new representation closer to the target execution form:

\begin{verbatim}
Source code → Parse tree → AST → Intermediate code → Machine code
\end{verbatim}

%Our system adapts this concept for LLM task execution. Instead of fixed transformations between predefined languages, we use the LLM itself to generate intermediate representations. 




Our system uses the LLM to parse natural language into structured expressions:

\emph{TODO this is incomplete. There should be a cycle connecting 'Task executable' back to 
'AST', to represent dynamic / incremental reparsing. See also: the other TODOSs, <dynamic reparsing>}
\begin{verbatim}
Source code (English) → Parse tree (XML) → AST (Python) → Task data + executable (XML) 
\end{verbatim}

In Python the first three steps (\verb|Source code (English) → Parse tree (XML) → AST (Python)|) are orchestrated by the class Compiler. The remaining portion is generated by the interaction between Compile and the evaluation loop (see Evaluator, next section):

\begin{lstlisting}[language=Python]
from dataclasses import dataclass
from typing import List, Any

@dataclass
class ASTNode:
    operator: Any
    args: List['ASTNode']

@dataclass
class Operator:
    """Represents an operation to be performed"""
    type: str  # "atomic" or "compound" 
    task: str  # The actual task description
    params: Optional[Dict] = None  # Additional parameters if needed

from dataclasses import dataclass
from typing import List, Any, Optional, Dict
from enum import Enum
from xml.etree.ElementTree import Element

from .error_types import ExecutionError, ErrorType, ResourceType
from .environment import Environment
from .task_system import TaskSystem, TaskType, XMLTaskParser, TaskStructure

@dataclass
class ASTNode:
    """Represents a node in the Abstract Syntax Tree"""
    operator: Any
    args: List['ASTNode']

@dataclass
class Operator:
    """Represents an operation to be performed"""
    type: str  # Maps to TaskType values
    task: str  # Task description
    params: Optional[Dict[str, Any]] = None

from dataclasses import dataclass
from typing import Protocol, Dict, Optional
from enum import Enum
from xml.etree.ElementTree import Element

from .error_types import ResourceType, ExecutionError

class TaskSystem(Protocol):
    """Interface for task management and prompt generation"""
    
    def get_decomposition_prompt(self, task: str, resource: ResourceType) -> str:
        """Generate prompt for decomposing a task that exceeded resources
        
        Args:
            task: The task description that failed
            resource: Which resource was exhausted
            
        Returns:
            Prompt for LLM to generate decomposed task structure
        """
        ...
        
    def get_alternative_prompt(self, task: str, failure_reason: str) -> str:
        """Generate prompt for alternative approach after task failure
        
        Args:
            task: The task description that failed
            failure_reason: Why the task failed
            
        Returns:
            Prompt for LLM to generate alternative approach
        """
        ...

class TaskType(Enum):
    """Types of tasks in decomposition"""
    ATOMIC = "atomic"         # Direct LLM execution
    MAP = "map"              # Parallel subtasks
    REDUCE = "reduce"        # Combine results
    SEQUENCE = "sequence"    # Sequential steps

@dataclass
class TaskStructure:
    """Parsed representation of a task from XML"""
    type: TaskType
    description: str
    subtasks: list['TaskStructure'] = None
    parameters: Optional[Dict[str, str]] = None



\end{lstlisting}

Example task structure in XML:
\begin{lstlisting}[language=XML]
<task>
  <description>analyze peak patterns across detectors</description>
  <inputs>
    <input name="detector1_data">
      <task>
        <description>load and preprocess detector 1 data</description>
        <expected_output>
          Preprocessed detector 1 data in standard format:
          - Intensity values
          - Peak positions
          - Background levels
        </expected_output>
      </task>
    </input>
    <input name="detector2_data">
      <task>
        <description>load and preprocess detector 2 data</description>
        <expected_output>
          Preprocessed detector 2 data in standard format:
          - Intensity values
          - Peak positions
          - Background levels
        </expected_output>
      </task>
    </input>
  </inputs>
  <expected_output>
    Comparative peak analysis:
    - Peak correlations between detectors
    - Intensity pattern matching
    - Anomaly detection
  </expected_output>
</task>
    <!--
# TODO the above xml is just an example, but we need to clearly define a mapping between the 
# structure of xml generated by the llm (when it does <reparsing>) and AST subtrees. (We could 
# potentially simplify this by constraining the llm <reparsing> process so that it can only generate 
# one ASTNode at a time. In the case of composite nodes, this would mean generating xml for an outer 
# task (e.g. a reduction function) and inner task(s) (e.g. the individual tasks whose outputs the 
# reduction is operating on)
    -->
\end{lstlisting}

In summary:
\begin{enumerate}
    \item The XML stage lets the LLM express task composition and input / output conventions in a structured way
    \item XML provides the interface between LLM and the evaluator
    \item Every AST node follows a uniform structure representing operations and their arguments
    \item Composite task behavior emerges from AST semantics and atomic task behavior
    \item Atomic task behavior emerge from natural-language operator definitions, which are \emph{not} exposed at this level
    \item Environments handle local variable bindings and global working memory for LLM operations (see next section)
    \item New atomic task patterns can be added without changing the evaluator or execution system
\end{enumerate}



\subsection{Environment}

An environment represents the complete context needed to evaluate expressions. In traditional programming languages, this mostly means lexical scope---the set of variables accessible from inside a given stack frame. %Our system extends this concept to include working memory for LLM tasks.


Our environments support traditional variable scoping while also managing the short-term memory component of the LLM execution context. The basic aspects are:

\begin{lstlisting}[language=Python]
class Environment:
    def __init__(self):
        """Environment holds bindings and LLM working context"""
        self.bindings = {}    # Current variable bindings
        self.context = {}     # LLM working memory
    
    def extend(self, names, values):
        """Create new environment with additional bindings"""
        new_env = Environment()
        new_env.bindings = dict(zip(names, values))
        # The full implementation will update the context using associative
        # matching via the long term - short term memory system instead of 
        # just cloning it
        new_env.context = self.context.copy()  
        return new_env
    
    def lookup(self, name):
        """Look up value in current bindings"""
        return self.bindings.get(name)
\end{lstlisting}

This is sufficient for us to:
\begin{enumerate}
    \item Track context through nested evaluations
    \item Pass relevant state between task executions
    \item Allow the evaluator to pass around execution contexts and create new ones using the associative memory procedure
\end{enumerate}

\subsection{Metacircular Evaluator}

A metacircular evaluator is an interpreter implemented using similar fundamental operations to the ones it aims to interpret. In our context, we implement a domain-specific language (DSL) evaluator using LLM operations as one basic component of the evaluation machinery, and this evaluator in turn coordinates and executes higher-level LLM tasks.

The architecture has two key aspects. First, the environment must be a first-class data structure that can be explicitly introspected by both the evaluator and the LLM. The environment captures not just variable bindings (as in a conventional programming language implementation) but the complete context needed for task interpretation and decomposition. (In contrast, in a traditional language implementation, the execution environment is entangled with the parsing and code generation process in a rather opaque way.)

The second aspect is the self-hosting property mentioned above. The LLM provides the evaluator with primitive capabilities for generating structured output from natural language (as XML task descriptions), and for executing atomic tasks. The evaluator combines these primitive operations to implement higher-level functionality: managing execution environments, parsing and dispatching structured task descriptions, and collecting execution outputs. 

Here's the core evaluator pseudo-implemented in Python:

\begin{lstlisting}[language=Python]
from dataclasses import dataclass
from typing import List, Any, Optional
from enum import Enum

# Shared type definitions
class OperatorType(Enum):
    ATOMIC = "atomic"    # Direct LLM execution
    MAP = "map"         # Process multiple inputs
    REDUCE = "reduce"   # Combine results
    SEQUENCE = "sequence" # Execute in order

# TODO only ATOMIC operators should have (or populate) the task attribute,
# because the other operator types aren't directly llm-executable. 
# Note an asymmetry between llm parsing and llm execution: when parsing, 
# the llm is locally aware of the AST structure, but when executing the 
# llm only sees one atomic node at a time. <reparsing>
@dataclass
class Operator:
    type: OperatorType
    task: str           # Task description/prompt
    params: Dict = None # Optional parameters

%<errors>
%type ExecutionError = 
%  | { type: 'resourceExhaustion'; resource: 'turns' | 'context' | 'output' }
%  | { type: 'taskFailure'; reason: string }
%  | { type: 'incompleteTask' };
%</errors>

% see evaluator.py
\end{lstlisting}

Note that the dynamic reparsing is spread out as an interaction between Evaluator and Compiler, but it is conceptually equivalent to this simple expression from the Scheme version: 

\begin{lstlisting}[language=Scheme, caption = nondeterministic evaluation using the amb (ambiguous) operator]
...
    ; For atomic tasks, try direct application; if it fails, decompose
    ((atomic? task)
     ; amb tries the first option; if it fails, backtracks to the second
     (amb (apply-proc task '() env)                 ; Direct application
          (eval-task (decompose task) env)))        ; Or decomposition
...
\end{lstlisting}


\subsection{End-to-End Example}

Let's examine how the system handles a user request that benefits from natural language understanding:

Review our XRD analysis and check if we chose a good background region.'

The LLM first translates this into nested tasks:

\begin{lstlisting}[language=XML]
<task>
  <description>analyze background region quality</description>
  <inputs>
    <input name="region_stats">
      <task>
        <description>extract statistics from experiment logs</description>
        <parameters>
          Extract and analyze:
          - Background region coordinates
          - Statistical test p-values 
          - Distribution uniformity metrics
        </parameters>
        <expected_output>
          Structured statistics including:
          - ROI coordinates
          - P-value series
          - Distribution metrics
        </expected_output>
      </task>
    </input>
  </inputs>
  <expected_output>
    Quality assessment including:
    - Statistical validity evaluation
    - Potential signal contamination check
    - Recommendations for improvement if needed
  </expected_output>
</task>
\end{lstlisting}

The compiler builds an AST:

\begin{lstlisting}[language=Python]
node = ASTNode(
    operator=Operator(
        type="atomic",
        task="analyze_region_quality"
    ),
    args=[
        ASTNode(
            operator=Operator(
                type="atomic",
                task="extract_stats",
                params={"instruction": "Find background..."}
            ),
            args=[]
        )
    ]
)
\end{lstlisting}

The evaluator processes this with environment handling:

\begin{lstlisting}[language=Python]
# Initialize environment with both logs and documentation
env = Environment(context={
    "log_contents": """
    2024-04-06 10:15:32 INFO: Starting analysis of run 123
    2024-04-06 10:15:33 DEBUG: Background ROI set to [80,95,5,45]  
    2024-04-06 10:15:34 DEBUG: Method: local linear
    2024-04-06 10:15:35 WARNING: High fit residuals
    2024-04-06 10:15:36 DEBUG: P-values: [0.394, 0.412, 0.378]
    ...""",
    
    "analysis_docs": """
    Background Region Quality Assessment Guide:
    - P-values should follow uniform distribution (mean approximately 0.5)
    - KS test should show p > 0.05
    - Region should be at least 20 pixels from any peak
    - Common failure modes:
      * Signal contamination causes p-value clustering
      * Edge effects near beam stop distort background
    ..."""
})

# Evaluate full expression
result, final_env = evaluator.eval(node, env)

# The evaluation proceeds:
# 1. Inner extract_stats task receives filtered environment:
#    env.context = {
#        "log_contents": "..." # Only the log data needed for extraction
#    }
#    -> Returns structured data like:
#       {"roi": [80,95,5,45], 
#        "pvalues": [0.394, 0.412, 0.378]}

# 2. Outer analyze_region_quality task receives full context:
#    env.context = {
#        "analysis_docs": "...", # Documentation for analysis guidance
#        "extraction_results": {"roi": [80,95,5,45], ...}
#    }
#    -> Uses docs to guide analysis:
#       "Background region shows signs of signal contamination.
#        P-value clustering (mean=0.394) matches known failure mode
#        described in analysis guide."
\end{lstlisting}

In this example, each task gets minimal context needed for its operation and the outer tasks can access both the log-parsing results (as direct input) and reference documentation (as context / short-term memory).

\end{document}

</file>
<file path="./plans/atomic_task_subtypes.md" project="">
1. Type Hierarchy Recommendation

mermaid
Copy
graph TD
    Task[Base Task Type]
    Task --> Atomic
    Task --> Sequential
    Task --> Reduce
    Atomic --> Director
    Atomic --> Evaluator
    classDef atomic fill:#cff,stroke:#099;
    class Director,Evaluator atomic
2. XML Implementation Strategy

xml
Copy
<!-- As atomic subtypes -->
<task type="atomic" subtype="director">
    <continuation_policy>latest-only</continuation_policy>
    <output_slot>last_eval_input</output_slot>
</task>

<task type="atomic" subtype="evaluator">
    <input_source>last_eval_input</input_source>
    <validation_rules>strict</validation_rules>
</task>

<!-- Example using template substitution for input binding -->
<task type="atomic">
    <description>Process {{input_data}} with parameters from {{config}}</description>
    <inputs>
        <input name="data" from="input_data"/>
        <input name="settings" from="config"/>
    </inputs>
</task>
Run HTML
3. Advantages of Atomic Subtyping

Aspect	Benefit
Execution Flow	Inherits standard atomic task lifecycle (init → execute → cleanup)
Error Handling	Uses existing atomic error recovery patterns
Resource Tracking	Leverages atomic task's turn counting & context management
Template Matching	Works with current associative matching system
4. Context Management Additions

typescript
Copy
interface AtomicTaskEnv {
    // Shared atomic properties
    turnsUsed: number;
    contextWindowUsage: number;
    
    // Director-Evaluator specific
    lastEvaluation?: {
        output: string;
        timestamp: Date;
        success: boolean;
    };
}
5. Implementation Requirements

a. Subtype Registration

typescript
Copy
// In task-system initialization
registerAtomicSubtype('director', {
    continuationHandler: handleDirectorContinuation,
    maxTurns: 10 // Special limit for directors
});

registerAtomicSubtype('evaluator', {
    outputValidation: strictJSONValidator,
    autoClearContext: true
});
b. Execution Flow Modifications

Copy
[Director Task]
1. Execute as normal atomic task
2. On CONTINUATION:
   a. Store output in lastEvaluation slot
   b. Clear other context variables
   c. Pass control to Evaluator subtype

[Evaluator Task]
1. Receive lastEvaluation data as input
2. Execute validation/processing
3. Return results to parent environment
4. Auto-clear lastEvaluation slot
6. XML Schema Changes (operators.md update)

diff
Copy
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
+   <xs:attribute name="subtype">
+     <xs:simpleType>
+       <xs:restriction base="xs:string">
+         <xs:enumeration value="director"/>
+         <xs:enumeration value="evaluator"/>
+       </xs:restriction>
+     </xs:simpleType>
+   </xs:attribute>
  </xs:complexType>
</xs:element>
7. Transition Plan

Phase 1: Add subtype support to atomic tasks

Phase 2: Migrate existing director/evaluator templates

Phase 3: Deprecate top-level director/evaluator types

Phase 4: Update documentation (errorspec.md, operators.md)

Key Benefits:

Maintains atomic task execution semantics

Enables custom director/evaluator logic through subtype hooks

Reduces type system complexity

Allows shared resource tracking infrastructure

Preserves XML schema backward compatibility

This approach balances specialization needs with architectural consistency, while maintaining the simplified context model from previous planning.
</file>
<file path="./plans/general_improvements.md" project="">
# Architecture Analysis and Recommendations

## Key Inconsistencies and Gaps

### 1. Context Management Ambiguity

#### Current Issues
- Unclear distinction between how inherit_context and accumulate_data interact in reduce operations
- Inconsistent handling of dual-context tracking across different operators
- Ambiguous mapping between XML schema and AST structure for context attributes

#### Recommendations
1. Standardize context inheritance model:
   - Define clear rules for when context is inherited vs. accumulated
   - Document interaction between inheritance and accumulation
   - Specify behavior for each operator type

2. Formalize context flow:
   
Parent Context -> Child Task
     │
     ├─ inherit_context: none  -> Fresh context only
     ├─ inherit_context: full  -> Complete parent context
     └─ inherit_context: subset -> Filtered via associative matching


### 2. Resource Management Gaps

#### Current Issues
- Unclear ownership of resource tracking between Handler and Memory System
- Inconsistent handling of partial results during resource exhaustion
- Ambiguous cleanup responsibilities

#### Recommendations
1. Define strict resource boundaries:
   - Handler: Turn counting, context window, execution resources
   - Memory System: File metadata only
   - Task System: Template and execution coordination

2. Standardize cleanup protocol:
   
Task Completion/Failure
     ├─ Handler: Clean session state
     ├─ Memory System: Clear transient context
     └─ Task System: Release template resources


### 3. Error Handling Inconsistencies

#### Current Issues
- Mixed approaches to context generation failures
- Unclear recovery strategies for different error types
- Inconsistent error propagation across components

#### Recommendations
1. Standardize error taxonomy:
   
Error Types
     ├─ RESOURCE_EXHAUSTION
     │   ├─ turns
     │   ├─ context
     │   └─ output
     ├─ TASK_FAILURE
     │   ├─ execution
     │   ├─ validation
     │   └─ progress
     └─ CONTEXT_FAILURE (new)
         ├─ generation
         └─ inheritance


2. Define clear recovery paths for each error type

### 4. Script Execution Integration

#### Current Issues
- Ambiguous handling of script execution in Director-Evaluator pattern
- Unclear error propagation from script execution
- Missing standardization of script execution environment

#### Recommendations
1. Formalize script execution model:
   
xml
   <task type="script">
     <description>Execute target script</description>
     <inputs>
       <input name="script_input" from="director_output"/>
     </inputs>
     <execution>
       <command>{{script_path}}</command>
       <timeout>300</timeout>
       <environment inherit="none"/>
     </execution>
   </task>


2. Standardize script execution results:
   - Capture stdout, stderr, exit code
   - Define error handling strategy
   - Specify environment inheritance rules

### 5. Memory System Interface Ambiguity

#### Current Issues
- Inconsistent version references (2.0 vs 3.0)
- Unclear boundaries between file operations and metadata management
- Mixed approaches to context retrieval

#### Recommendations
1. Standardize Memory System interface:
   
typescript
   interface MemorySystem {
     // Core operations
     getGlobalIndex(): Promise<GlobalIndex>;
     updateGlobalIndex(index: GlobalIndex): Promise<void>;
     
     // Context operations
     getRelevantContextFor(input: ContextGenerationInput): Promise<AssociativeMatchResult>;
     
     // No file operations - delegated to Handler tools
   }


2. Clear separation of responsibilities:
   - Memory System: Metadata and context management
   - Handler Tools: File operations
   - Task System: Execution coordination

## Implementation Priorities

### Phase 1: Core Architecture Alignment
1. Standardize Memory System interface (version 3.0)
2. Implement clear context management rules
3. Define strict resource boundaries
4. Update error taxonomy

### Phase 2: Feature Implementation
1. Enhanced context inheritance
2. Script execution integration
3. Error recovery paths
4. Resource cleanup protocols

### Phase 3: Documentation Updates
1. Update cross-references to Memory System 3.0
2. Document context inheritance rules
3. Define script execution guidelines
4. Standardize error handling documentation

## Recommendations for Open Questions

1. **Context Generation Failures**
   - Treat as distinct error type (CONTEXT_FAILURE)
   - Preserve partial results for potential recovery
   - Allow task-specific handling via template

2. **Operator Inheritance**
   - Extend inherit_context to all operators
   - Define operator-specific inheritance rules
   - Document interaction with accumulation

3. **Subtask Spawning**
   - Implement through CONTINUATION status
   - Use notes section for spawn parameters
   - Define clear parent-child relationship

## Additional Considerations

### 1. Environment Model
typescript
interface Environment {
    bindings: Map<string, any>;
    context: Map<string, any>;
    taskLibrary: TaskLibrary;
    
    extend(bindings: Map<string, any>): Environment;
    find(name: string): any;
    cleanup(): void;
}


### 2. Task Library Organization
typescript
interface TaskLibrary {
    // Core task types
    atomic: Map<string, TaskDefinition>;
    sequential: Map<string, TaskDefinition>;
    reduce: Map<string, TaskDefinition>;
    
    // Special types
    associativeMatch: Map<string, TaskDefinition>;
    scriptExecution: Map<string, TaskDefinition>;
    
    // Operations
    register(task: TaskDefinition): void;
    find(type: string, criteria: string): TaskDefinition[];
    get(id: string): TaskDefinition;
}


### 3. Context Management Rules
typescript
interface ContextManagement {
    inheritContext: 'none' | 'full' | 'subset';
    accumulateData: boolean;
    accumulationFormat: 'notes_only' | 'full_output';
    
    // New fields
    clearOnContinuation: boolean;
    preserveOnError: boolean;
}


## Next Steps

1. **Immediate Actions**
   - Finalize Memory System 3.0 interface
   - Update all cross-references
   - Implement standardized context management
   - Define error taxonomy

2. **Short-term Goals**
   - Implement script execution integration
   - Update documentation
   - Add error recovery paths
   - Standardize cleanup protocols

3. **Long-term Considerations**
   - Agent features
   - Multi-LLM support
   - Enhanced error recovery
   - Performance optimization
</file>
<file path="./inconsistencies.md" project="">
# Inconsistencies Requiring Subjective Choices

Below are areas where the documents highlight open design questions or competing approaches. Each needs a decision to remove ambiguity.

## Partial-Results Policy for Failing Operators

Options:
- A: Discard partial outputs on sub‐task failure, treating the entire operator as a single unit of success/failure.
- B: Preserve partial outcomes (e.g. in TaskResult.notes.partialResults) so higher‐level tasks can decide how to handle them.

Recommendation: If your use cases frequently require partial data (e.g., some parallel tasks succeed while others fail), choose (B) and store partial results. If the system rarely benefits from partial data, keep (A) for simplicity.

## Context-Generation Failure as Its Own Error

Options:
- A: New error type (CONTEXT_GENERATION_FAILURE) in errorspec.md, distinctly recognized so that tasks can handle it differently than normal "task failures."
- B: Keep a single TASK_FAILURE category and rely on message or reason to identify context errors.

Recommendation: If you plan to handle context failures with specialized fallback or re-tries, choose (A). If context issues are not special in your system's eyes, keep (B) to avoid error-type proliferation.

## Inherited Context for Map and Reduce

Question: "Should <inherit_context> be available on all operators (map, reduce, sequential) so sub-tasks can share or skip context?"

Options:
- A: Provide <inherit_context> consistently on all multi-step operators.
- B: Keep inheritance on sequential only, and treat map/reduce differently.

Recommendation: If the system's mental model is that all nested tasks might optionally share the environment, use (A). If parallel tasks or reduce tasks inherently require a "fresh" environment, then (B) is simpler.

## Handler Tools API (Read-Only vs. Read/Write)

Question: "Do tasks need to modify or delete files, or is read-only enough?"

Options:
- A: Provide readFile, writeFile, deleteFile from the start.
- B: Provide only readFile, and mention a future extension for writes.

Recommendation: Decide based on real usage. If you have no short-term need for writes, option (B) keeps it simpler, adding write methods later if necessary.

## Summary

To maintain consistency going forward:
1. Pick one approach for partial results behavior
2. Choose error taxonomy for context generation failures
3. Decide on context inheritance scope
4. Finalize Handler tools API requirements
5. Document these decisions clearly to prevent future ambiguity
</file>
<file path="./docstructure.md" project="">
# Documentation Structure

## Directory Layout
docs/
├── system/                         # System-level documentation
│   ├── README.md                   # System overview & development sequence
│   ├── docs-guide.md               # Documentation standards, map & navigation
│   ├── architecture/               # Core architecture
│   │   ├── overview.md            # High-level design
│   │   ├── decisions/             # Architecture Decision Records (ADRs)
│   │   └── patterns/              # Core patterns & principles
│   ├── protocols/                  # System-wide protocols
│   │   └── resources.md            # Protocol-level resource definitions
│   └── contracts/                  # System-wide contracts
│       ├── interfaces.md          # External interfaces
│       └── resources.md           # Resource management
│
└── components/                     # Component documentation
    └── [component]/               # Per component (can be nested)
        ├── README.md              # Component overview
        ├── api/                   # Public API documentation
        │   └── interfaces.md      # Public interface definitions
        ├── spec/                  # Formal specifications
        │   ├── requirements.md    # Component requirements
        │   ├── interfaces.md      # Internal interface definitions
        │   ├── types.md          # Type definitions
        │   └── behaviors.md       # Expected behaviors
        └── impl/                  # Implementation details
            ├── design.md         # Design decisions
            ├── protocols.md      # Protocol implementations
            └── examples.md       # Implementation examples


## Common Types
[Rest of common types section remains unchanged]

## Cross-Reference Updates
Ensure that all components referencing the Director-Evaluator pattern mention both the dynamic and static variants. In particular, update references to [Pattern:DirectorEvaluator:1.1] to include the static variant with script execution support.

## Document Standards

### System Level Documents

#### README.md
[README.md template remains unchanged]

#### docs-guide.md
markdown
# Documentation Guide

## Documentation Map
Required:
- Core system specifications
- Component contracts & integration
- Core patterns & protocols
- Key data structures
- Documentation status
- Cross-reference guide

## Standards
Required:
- Writing style guidelines
- Document templates
- Cross-reference syntax
- Version control practices

## Documentation Principles
Required:
1. Single Responsibility
   - Each document covers one concern
   - Clear boundaries between concerns
   - Explicit dependencies
2. Template Consistency
   - All new task templates must use the unified template substitution mechanism.
   - Evaluator's lexically scoped variables are referenced using the `{{variable_name}}` syntax.
   - Input bindings can be explicitly declared using the optional `from` attribute on `<input>` elements.

2. Contract Completeness
   - All requirements stated
   - All guarantees explicit
   - All resources documented

3. Resource Clarity
   - Ownership explicit
   - Lifecycle documented
   - Cleanup requirements specified

## Writing Style
Required:
1. Active voice
2. One sentence per line
3. Explicit section numbering
4. Consistent terminology

## Documentation Map
Required:
- Core system specifications
- Component contracts & integration
- Core patterns & protocols
- Key data structures
- Documentation status

## Version Management
Required:
1. Version Format: MAJOR.MINOR.PATCH
2. Update Rules:
   - MAJOR: Breaking changes
   - MINOR: New features, backward compatible
   - PATCH: Bug fixes, backward compatible

## Navigation
Required:
1. Documentation Map Usage
   - Primary navigation aid
   - Definitive specification locations
   - Cross-reference resolution
   - Documentation status tracking

2. Map Maintenance
   - Regular updates with changes
   - Validation of references
   - Status accuracy verification
   - Gap identification

Note: The Documentation Map in this guide serves as the primary navigation aid
for finding specifications and understanding document relationships.

## Templates
[See individual document templates in this guide]


[Rest of document remains unchanged]
</file>
<file path="./system/contracts/resources.md" project="">
# Resource Management Contracts [Contract:Resources:1.0]

## 1. Resource Types

### 1.1 Turn Counter
Implemented in [Component:Handler:1.0]. Tracking is defined in [Interface:Handler:ResourceMonitoring:1.0] and limits are enforced via [Pattern:Error:1.0]. For additional details, please refer to Appendix A.

### 1.2 Context Window
See [Interface:Handler:ContextManagement:1.0]. Detailed constraints and usage guidelines are provided in Appendix A.

### 1.3 Memory Resources
See [Component:MemorySystem:1.0]. Further specifications are outlined in Appendix A.

## 2. Resource Management Protocols

For tracking, allocation, and release requirements, please refer to Appendix A.

### 3. Contract Validation
Resource, operational, and implementation constraints are governed by the guidelines set forth in Appendix A.

## Appendix A: Contract Validation Guidelines

The following guidelines apply across all resource management and integration contracts:

1. **Required Fields:** All mandatory fields (e.g. turn limits, context window sizes) must be present and conform to type specifications.
2. **Uniqueness:** Input names and resource identifiers must be unique within their respective scopes.
3. **Format Validation:** Boolean fields must be exactly "true" or "false", and string fields must adhere to defined LLM identifier formats.
4. **Resource Limits:** Warning thresholds should be triggered at 80% usage, with hard limits enforced at 100%.
5. **Context Management:** Context data must be extended (not merged) to ensure immutability; new information is added via extension.

For further details and future updates, consult the development roadmap.
</file>
<file path="./system/contracts/interfaces.md" project="">
# System Interface Contracts

## 1. Component Integration Contracts

### 1.1 Compiler Integration [Contract:Integration:CompilerTask:1.0]
Defined in [Component:Compiler:1.0]
[TBD: Complete contract specification]

### 1.2 Evaluator Integration [Contract:Integration:EvaluatorTask:1.0]
See [Component:Evaluator:1.0] for complete interface.
[TBD: Complete contract specification]

### 1.3 Task System Integration
See [Component:TaskSystem:1.0] in components/task-system/README.md

#### Interfaces
- Task Execution: [Interface:TaskSystem:1.0] 
- Template Management: [Interface:TaskSystem:Templates:1.0]
- XML Processing: [Contract:Tasks:TemplateSchema:1.0]

#### Resource Contracts
See [Contract:Resources:1.0]

### 1.4 Memory System Integration [Contract:Integration:TaskMemory:3.0]
See [Component:MemorySystem:3.0]

#### Interfaces
  - Metadata Management: [Interface:Memory:3.0]
    - Task System uses metadata for associative matching; see Appendix A for validation criteria.
  - Index Management: [Interface:Memory:3.0]
    - Global index serves as the bootstrap for matching; updates occur in bulk.

#### Responsibilities
Memory System:
 - Maintains global file metadata index
 - Provides bulk index updates
 - Supplies metadata for associative matching (refer to Appendix A for constraints)

Task System:
 - Uses context for task execution
 - Receives file references via associative matching
 - Delegates file access to Handler tools

#### Integration Points
 - Context flow from associative matching to task execution
 - File metadata index is used exclusively for matching; file access is handled by Handler tools

## 2. Cross-Component Requirements

### 2.1 State Management
See [Pattern:Error:1.0] for error state handling.

Context Management:
- Task context maintained by Memory System
- Context operations provide immediate consistency
- No persistence guarantees for context data
- Context scope limited to current task execution

### 2.2 Error Propagation
Error handling defined in [Pattern:Error:1.0]

### 2.3 Resource Tracking
Resource contracts defined in [Contract:Resources:1.0]

Memory-Specific Resource Considerations:
- Context size limits defined by Handler
- Global index accessed in full only
- No partial index updates or queries
- File content handling delegated to Handler tools

## 3. Contract Validation 

### 3.1 Validation Requirements
- Context Management
  - Context updates must be atomic
  - Context retrieval must be consistent
  - No data persistence required
- Index Management
  - Index updates must be atomic
  - Index must persist across sessions
  - All file paths must be absolute
  - All metadata must be strings

### 3.2 Success Criteria
Context Management:
- Context updates visible to immediate subsequent reads
- No context data persists between sessions
- Context size within Handler limits

Index Management:
- Index survives system restarts
- Bulk updates atomic and consistent
- All paths resolvable by Handler tools

### 3.3 Verification Methods
- Unit tests for context operations
- Integration tests for index persistence
- Validation of file paths with Handler tools
- Context size limit compliance checks
</file>
<file path="./system/contracts/protocols.md" project="">
# System Protocols

## Task Template Schema [Contract:Tasks:TemplateSchema:1.0]

**Note:** This document is the authoritative specification for the XML schema used in task template definitions. All field definitions, allowed enumerations (such as for <inherit_context> and <accumulation_format>), and validation rules are defined here. For complete validation guidelines, please see Appendix A in [Contract:Resources:1.0].

The task template schema defines the structure for XML task template files and maps to the TaskTemplate interface.

### XML Schema Definition

xml
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:complexType name="EvaluationResult">
    <xs:sequence>
      <xs:element name="success" type="xs:boolean"/>
      <xs:element name="feedback" type="xs:string" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>

  <xs:element name="task">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="description" type="xs:string"/>
        <xs:element name="output_slot" type="xs:string" minOccurs="0"/>
        <xs:element name="input_source" type="xs:string" minOccurs="0"/>
        <xs:element name="context_management">
          <xs:complexType>
            <xs:sequence>
              <xs:element name="inherit_context">
                <xs:simpleType>
                  <xs:restriction base="xs:string">
                    <xs:enumeration value="full"/>
                    <xs:enumeration value="none"/>
                    <xs:enumeration value="subset"/>
                  </xs:restriction>
                </xs:simpleType>
              </xs:element>
              <xs:element name="accumulate_data" type="xs:boolean" default="false"/>
              <xs:element name="accumulation_format" minOccurs="0">
                <xs:simpleType>
                  <xs:restriction base="xs:string">
                    <xs:enumeration value="full_output"/>
                    <xs:enumeration value="notes_only"/>
                  </xs:restriction>
                </xs:simpleType>
              </xs:element>
            </xs:sequence>
          </xs:complexType>
        </xs:element>
        <xs:element name="steps">
          <xs:complexType>
            <xs:sequence>
              <xs:element name="task" maxOccurs="unbounded">
                <xs:complexType>
                  <xs:sequence>
                    <xs:element name="description" type="xs:string"/>
                    <xs:element name="inputs" minOccurs="0">
                      <xs:complexType>
                        <xs:sequence>
                          <xs:element name="input" maxOccurs="unbounded">
                            <xs:complexType>
                              <xs:sequence>
                                <xs:element name="task">
                                  <xs:complexType>
                                    <xs:sequence>
                                      <xs:element name="description" type="xs:string"/>
                                    </xs:sequence>
                                  </xs:complexType>
                                </xs:element>
                              </xs:sequence>
                              <xs:attribute name="name" type="xs:string" use="required"/>
                            </xs:complexType>
                          </xs:element>
                        </xs:sequence>
                      </xs:complexType>
                    </xs:element>
                  </xs:sequence>
                </xs:complexType>
              </xs:element>
            </xs:sequence>
          </xs:complexType>
        </xs:element>
        <xs:element name="inputs" minOccurs="0">             <!-- Maps to inputs -->
          <xs:complexType>
            <xs:sequence>
              <xs:element name="input" maxOccurs="unbounded">
                <xs:complexType>
                  <xs:simpleContent>
                    <xs:extension base="xs:string">
                      <xs:attribute name="name" type="xs:string" use="required"/>
                      <xs:attribute name="from" type="xs:string" use="optional"/>
                    </xs:extension>
                  </xs:simpleContent>
                </xs:complexType>
              </xs:element>
            </xs:sequence>
          </xs:complexType>
        </xs:element>
        <xs:element name="manual_xml" type="xs:boolean" minOccurs="0" default="false"/>      <!-- Maps to isManualXML -->
        <xs:element name="disable_reparsing" type="xs:boolean" minOccurs="0" default="false"/> <!-- Maps to disableReparsing -->
      </xs:sequence>
      <xs:attribute name="ref" type="xs:string" use="optional"/>
      <xs:attribute name="subtype" type="xs:string" use="optional"/>
    </xs:complexType>
  </xs:element>
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
</xs:schema>


### Script Execution Support

The XML task template schema now supports defining tasks for script execution within sequential tasks. These tasks enable:
 - Command Specification: Defining external commands (e.g. bash scripts) to be executed.
 - Input/Output Contracts: Passing the director's output as input to the script task, and capturing the script's output for subsequent evaluation.
Script execution errors (e.g. non-zero exit codes) are treated as generic TASK_FAILURE conditions. The evaluator captures the script's stdout and stderr in a designated notes field for downstream decision-making.

Example:
xml
<task type="sequential">
  <description>Static Director-Evaluator Pipeline</description>
  <context_management>
    <inherit_context>none</inherit_context>
    <accumulate_data>true</accumulate_data>
    <accumulation_format>notes_only</accumulation_format>
  </context_management>
  <steps>
    <task>
      <description>Generate Initial Output</description>
    </task>
    <task type="script">
      <description>Run Target Script</description>
      <inputs>
        <input name="director_output">
          <task>
            <description>Pass director output to script</description>
          </task>
        </input>
      </inputs>
      <!-- The script task captures stdout and stderr in the notes field.
           Non-zero exit codes are treated as TASK_FAILURE. -->
    </task>
    <task>
      <description>Evaluate Script Output</description>
      <inputs>
        <input name="script_output">
          <task>
            <description>Process output from target script</description>
          </task>
        </input>
      </inputs>
    </task>
  </steps>
</task>


This extension to the schema ensures a clear definition of script execution tasks within a sequential workflow.

### Field Definitions

- The optional ref attribute is used to reference a pre-registered task in the TaskLibrary.
- The optional subtype attribute refines the task type (for example, indicating "director", "evaluator", etc.)

Example:
xml
<cond>
  <case test="output.valid == true">
    <task type="atomic" subtype="success_handler">
      <description>Handle success</description>
    </task>
  </case>
  <case test="output.errors > 0">
    <task type="atomic" subtype="error_handler">
      <description>Handle errors</description>
    </task>
  </case>
</cond>

All required and optional fields (including instructions, system, model, and inputs) are defined by this schema. For full details and allowed values, please see Appendix A in [Contract:Resources:1.0].

### Example Template

xml
<task>
  <instructions>Analyze the given code for readability issues.</instructions>
  <system>You are a code quality expert focused on readability.</system>
  <model>claude-3-sonnet</model>
  <!-- The criteria element provides a free-form description used for dynamic evaluation template selection via associative matching -->
  <criteria>validate, log</criteria>
  <inputs>
    <input name="code">The code to analyze</input>
  </inputs>
  <manual_xml>false</manual_xml>
  <disable_reparsing>false</disable_reparsing>
</task>


### Validation Rules

1. All required fields must be present
2. Input names must be unique
3. Boolean fields must be "true" or "false"
4. Model must be a valid LLM identifier

### Interface Mapping

This schema is used by the TaskSystem component. For implementation details and interface definitions, see:
- TaskTemplate interface in spec/types.md [Type:TaskSystem:TaskTemplate:1.0]
- Template validation in TaskSystem.validateTemplate() 
- Template parsing in TaskSystem constructor

Note: The new XML attributes (ref and subtype) and the <cond> element map to the corresponding types (i.e., TaskDefinition and FunctionCall) used in the Task System.

### Map Pattern Implementation
Refer to the XML schema for correct usage. For a complete example, please see the Task System documentation.
</file>
<file path="./system/README.md" project="">
# Intelligent Task Execution System

## Overview

This system will coordinate LLM-based task decomposition and structured execution. It treats natural language interaction as a form of code execution, using a DSL (domain-specific language) to represent task decomposition and manage execution flow.

### Key Components

mermaid
graph TD
    subgraph "Input Processing"
        NL[Natural Language Query] --> Compiler
        DSL[DSL Expression] --> Parser
        Parser --> AST_DSL[DSL AST]
        Compiler --> AST_NL[Task AST]
    end

    subgraph "Execution Environment"
        AST_DSL --> Evaluator
        AST_NL --> Evaluator
        Evaluator -->|Execute| LLM
        Evaluator -->|Recover| Compiler
        Evaluator -->|Query| Memory
    end
    
    subgraph "Memory System"
        LongTerm[Long Term Store]
        Working[Working Memory]
        LongTerm -->|Associative Match| Working
    end

    subgraph "Runtime Environment"
        TaskLib[Task Library]
        Env[Environment Frame]
        TaskLib --> Evaluator
        Env --> Evaluator
    end


## Core Architecture

### 1. DSL Interpretation
The system a DSL frontent for expressing task composition and control flow (this feature will be added last):

scheme
; Example DSL expression
(define (process-data data-source)
  (sequential
    (task "load-data" data-source)
    (reduce
      (lambda (chunk acc)
        (task "analyze-chunk" chunk acc))
      initial-value
      chunks)))


Key aspects of DSL interpretation:
- First-class functions and task definitions
- Environment-based lexical scoping

The DSL interpreter follows a classic eval/apply model:
typescript
interface Interpreter {
    eval(expr: Expression, env: Environment): Promise<any>;
    apply(proc: Procedure, args: any[], env: Environment): Promise<any>;
}


### 2. Task System
- Manages template matching and execution
- Handles XML task definitions with graceful degradation
- Enforces resource limits through Handlers
- Provides error detection and propagation

### 3. Evaluator
- Controls AST processing and execution
- Manages failure recovery through task decomposition
- Tracks resource usage with Handlers
- Handles reparse/decomposition requests
- Maintains context across task boundaries

### 4. Memory System
- Maintains global file metadata index
- Provides associative matching for context retrieval
- Delegates file operations to Handler tools
- Manages task execution context

### 5. Task Expression Framework
Supports multiple operator types:
- **Sequential**: Ordered execution with context inheritance
- **Reduce**: Result aggregation with accumulation
- **Map**: Parallel task processing
- **Atomic**: Direct LLM execution

## Key Patterns

### 1. Director-Evaluator Pattern
xml
<task type="sequential">
    <description>Static Director-Evaluator Pipeline</description>
    <context_management>
        <inherit_context>none</inherit_context>
        <accumulate_data>true</accumulate_data>
        <accumulation_format>notes_only</accumulation_format>
    </context_management>
    <steps>
        <task>
            <description>Generate Initial Output</description>
        </task>
        <task type="script">
            <description>Run Target Script</description>
        </task>
        <task>
            <description>Evaluate Script Output</description>
        </task>
    </steps>
</task>


### 2. Context Management
- Explicit control through context_management blocks
- Three inheritance modes: full, none, subset
- Support for data accumulation across steps
- Clean separation between inheritance and accumulation

### 3. Resource Management
- Handler-based resource isolation
- Per-task resource tracking
- Clear ownership boundaries
- Explicit cleanup procedures

### 4. Error Handling
Two primary error types:
- **Resource Exhaustion**: Signals when system limits are exceeded
- **Task Failure**: Indicates unrecoverable execution failures

## Integration Patterns

### 1. Environment Model
typescript
interface Environment {
    // Lexical scope for variable bindings
    bindings: Map<string, any>
    
    // Working memory for task execution
    context: Map<string, any>
    
    // Parent environment reference
    outer: Environment | null
    
    // Create child environment with new bindings
    extend(bindings: Map<string, any>): Environment
}


### 2. Memory Integration
typescript
interface MemorySystem {
    // Find relevant context for current task
    getRelevantContextFor(input: ContextQuery): Promise<Context>
    
    // Access global metadata index
    getGlobalIndex(): Promise<GlobalIndex>
}


### 3. Script Execution
- Support for external command execution
- Capture of stdout, stderr, and exit codes
- Integration with evaluation workflows
- Clean error propagation

## Resource Constraints

### 1. Execution Limits
- Fixed context window size
- Limited turn counts
- Synchronous operation only
- One Handler per task execution

### 2. Memory System
- Read-only file metadata access
- No direct file content storage
- Context updates through extension only
- Clear cleanup protocols

## Development Guidelines

### 1. Task Templates
- Must conform to XML schema
- Support both LLM-generated and manual XML
- Include clear input/output contracts
- Specify context management requirements

### 2. Error Recovery
- Implement proper resource cleanup
- Surface errors with complete context
- Support task decomposition
- Maintain execution history

### 3. Context Management
- Use explicit context inheritance
- Implement clean data accumulation
- Follow resource cleanup protocols
- Maintain context boundaries

## Usage Example

typescript
// Initialize system components
const taskSystem = new TaskSystem({
    maxTurns: 10,
    maxContextWindowFraction: 0.8,
    systemPrompt: "System-level context"
});

const memorySystem = new MemorySystem();

// Execute a task
const result = await taskSystem.executeTask(
    "Process and analyze experimental data",
    memorySystem
);

// Check results and handle any errors
if (result.status === "FAILED") {
    console.error("Task failed:", result.error);
    // Implement recovery logic
}


## Future Directions

### 1. Planned Enhancements
- Advanced context optimization
- Parallel execution support
- Enhanced error recovery
- Dynamic resource management

### 2. Potential Extensions
- Multi-LLM support
- Persistent context storage
- Interactive sessions
- Enhanced debugging tools

## References

1. **Core Documentation**
   - Architecture Decisions (ADRs)
   - Pattern Specifications
   - Component Interfaces

2. **Component Documentation**
   - Task System
   - Evaluator
   - Memory System
   - Handler Interface

For detailed implementation specifications and patterns, refer to the component-level documentation.
</file>
<file path="./system/architecture/overview.md" project="">
# Architecture Overview

## Problem Statement and Goals

This document provides a high‑level overview of the system architecture. Detailed technical discussions have been moved into canonical files in the sub‑folders:

- **Patterns:** Core patterns such as Director‑Evaluator, Error Handling, and Resource Management (see files under system/architecture/patterns/).
– **Decisions (ADRs):** Architecture Decision Records on topics such as context management and memory system design (see system/architecture/decisions/).
– **Q&A and Open Questions:** Clarifications and unresolved issues (see system/architecture/qa/ and system/architecture/questions.md).

## Document Map

**This folder contains:**
 - overview.md: This high‑level summary and navigation index.
 - patterns/: Detailed technical descriptions of core patterns.
 - decisions/: Architecture Decision Records (ADRs) with rationale and scope.
 - qa/: Frequently asked questions and clarifications.
 - questions.md: A list of open and unresolved architecture questions.

For full technical details on any topic, please refer to the canonical file listed above.

### System Goals
1. Primary Goals
- Provide reliable task automation through structured decomposition and execution
- Ensure consistent task processing despite resource constraints
- Enable robust error recovery without human intervention
- Maintain system coherence across task boundaries

2. Quality Goals
- Predictable resource usage through explicit tracking and limits
- Consistent behavior through standardized protocols and interfaces
- Extensible task handling via template-based architecture
- Maintainable system through clear component boundaries

3. Operational Goals
- Handle varying task complexities through dynamic decomposition
- Support diverse task types through flexible template system
- Preserve critical context across task boundaries
- Manage resources efficiently within defined constraints

### System Constraints

#### Resource Constraints
- Fixed context window size
- Limited turn counts
- Synchronous operation only
- File access via Handler tools only

#### Operational Constraints  
- One Handler per task execution
- Immutable Handler configuration
- No persistent state maintenance
- Template immutability during execution

## Core Patterns

The Director-Evaluator Pattern supports both dynamic and static variants. The static variant pre-compiles the execution sequence—including script execution tasks—for predictable control flow (see [Pattern:DirectorEvaluator:1.1](system/architecture/patterns/director-evaluator.md)).

The system now follows a unified context management model. In addition, task input values are dynamically substituted using the {{...}} syntax, allowing the Evaluator to inject lexically scoped variables into task descriptions and input declarations. This explicit binding mechanism (augmented by the optional from attribute) improves clarity and flexibility in task execution.

Context is managed via a single <context_management> block that distinguishes between:
 - **Inheritance:** (using the new inherit_context enumeration)
 - **Accumulation:** (using the boolean accumulate_data and the accumulation_format setting)

### Error Handling [Pattern:Error:1.0]
Defines how errors propagate and recover across component boundaries.

See [Interface:ErrorHandling:1.0] in system/contracts/interfaces.md for complete specification.

### Resource Management [Pattern:Resource:2.0]
Defines resource usage tracking and lifecycle across components.

#### Core Principles
- Handler-based resource isolation
- Per-task resource tracking
- Context window management
- Memory system integration
- No cross-Handler resource sharing
- Read-only memory access

#### Component Responsibilities

##### Handler
- Owns turn counting per task execution
- Manages context window size
- Tracks token usage
- Enforces resource limits
- Ensures session termination

##### Task System
- Creates Handler instances
- Configures immutable resource limits
- Delegates resource tracking to Handler
- Manages template persistence

##### Memory System
- Maintains task context data
- Provides context management interface
- Maintains global file metadata index
- No file content storage

#### Resource Types and Protocols
- Turn Counter: Per-Handler atomic tracking with strict limits
- Context Window: Token-based size monitoring and enforcement
- Memory Resources: Short-term task context with clear boundaries
- Resource Release: Coordinated cleanup and state invalidation
- Error Handling: Resource exhaustion detection and preservation

See [Contract:Resources:2.0] in system/contracts/resources.md for complete specification.

### Task Execution [Pattern:TaskExecution:2.0]
Defines how tasks are structured, executed, and managed.

Key concepts:
- Template-based definition
- Handler-managed execution
- Resource-aware processing
- XML-based protocols

See [Contract:Tasks:2.0] in system/contracts/protocols.md for complete specification.

## Component Architecture

The system consists of four core components working together to process, execute, and manage tasks:

### Compiler [Component:Compiler:1.0]
Task parsing and transformation component.
- Translates natural language to XML/AST
- Validates against XML schema
- Handles task transformation
- Manages template validation

See [Contract:Integration:CompilerTask:1.0] for integration specification.

### Evaluator [Component:Evaluator:1.0]
Execution control component.
- Controls AST processing and execution
- Manages failure recovery
- Tracks resource usage
- Handles reparse requests

See [Contract:Integration:EvaluatorTask:1.0] for integration specification.

### Task System [Component:TaskSystem:1.0]
Task execution and management component.
- Coordinates task execution via Handlers
- Manages task templates and matching
- Interfaces with Memory System
- Processes XML input/output

See components/task-system/README.md for complete specification.

### Memory System [Component:Memory:3.0]
Metadata management component.
- Maintains global file metadata index
- Provides metadata for associative matching without ranking or prioritization
- Supplies metadata for file-based lookup and partial matching
- Does not store file content or task context
- Does not allocate or manage resources - only provides matching services

See [Contract:Integration:TaskMemory:2.0] for integration specification.

## Component Integration

### Core Integration Patterns
Components interact through defined contracts:

#### Compiler ↔ Task System
- Task parsing coordination
- Schema validation
- Template utilization

#### Evaluator ↔ Compiler
- AST execution feedback
- Reparse requests
- Resource usage updates

#### Task System ↔ Evaluator
- Execution coordination
- Resource allocation
- State management

#### Task System ↔ Memory System
- Context management
- Metadata index access
- Associative matching support

See system/contracts/interfaces.md for complete contract specifications.

### Resource Ownership
- Handlers own task resources
- Memory system owns context storage
- Task system coordinates allocation
- Clean resource release required

See system/contracts/resources.md for complete ownership model.

### System-Wide Protocols
- XML-based task definitions and protocols
- Standard error propagation
- Resource usage tracking
- Context management

---

### Sequential Task Management [Pattern:SequentialTask:2.0]

The system maintains **explicit task history** for sequential operations. This design clarifies how multiple steps in a single task can share context in a controlled, trackable way, and how partial or final outputs are captured.

1. **Output Tracking**
   - The Evaluator maintains a list of all previous task outputs, keyed by step index or ID.
   - The lifecycle for this history is well-defined; it is preserved until the sequence finishes.
   - Storage must remain resource-aware to avoid memory limit issues. If output is large, the evaluator can store a summarized version or notes-only.

2. **Context Management**
   - Context inheritance is separated from data accumulation.
   - Three distinct modes of operation are recognized:
     1. **Direct parent context inheritance**: The sub-task uses the same context as its parent, unchanged.
     2. **History-aware associative matching**: The sub-task can optionally reference all previous step outputs as additional matching data.
     3. **Standard associative matching**: The sub-task only uses the normal memory system and the known parent context, ignoring any step-by-step accumulations.

3. **Partial Failures**
   - If a step fails, all previous step outputs remain available in the final (error) output.
   - The final error output includes which step number or ID caused the failure.

4. **Resource Handling**
   - Maximum stored-history size is enforced by the system to prevent out-of-memory or context window exhaustion.
   - The evaluator must handle large output storage carefully, possibly discarding or summarizing to keep track usage in check.
   - Clear cleanup protocols ensure that once the sequence completes (successfully or in error), the stored step outputs are removed.

In summary, **SequentialTask** pattern addresses multi-step tasks with optional or partial data inheritance across steps, ensuring that both resource usage and error behavior remain consistent and predictable.

See system/contracts/protocols.md for protocol specifications.
</file>
<file path="./system/architecture/patterns/context-frames.md" project="">
# Context Frame Pattern [Pattern:ContextFrame:1.0]

## Related Documents
- Memory System ADR in [ADR:Memory:1.0]
- Memory component in [Component:Memory:1.0]
- Resource Management Pattern in [Pattern:ResourceManagement:1.0]

## Context Frame Operations

### Frame Creation and Extension
typescript
interface ContextFrame {
    // Based on Memory System design (see [ADR:Memory:1.0])
    bindings: Map<string, any>;    // Current variable bindings
    context: Map<string, any>;     // Working memory context
    
    extend(bindings: Map<string, any>): ContextFrame;
    cleanup(): void;
}

---
**Related Decisions:** For higher‑level context management decisions, see [decisions/002-context-management.md](../decisions/002-context-management.md) and [decisions/005-context-handling.md](../decisions/005-context-handling.md).


## EnvironmentFrame Interface

To support argument passing during task evaluation, we introduce a new interface:

typescript
interface EnvironmentFrame {
    bindings: Map<string, any>;    // Arguments bound to this scope
    parent?: EnvironmentFrame;     // Parent scope for lookup chain
    context: Record<string, any>;    // Task execution context (separate from bindings)
}


This EnvironmentFrame is created at the start of each task execution (using the new createFrame method) and is chained to any existing parent frame. Its purpose is to maintain a clear separation between argument bindings and the overall task context.

### Frame Immutability
- No modification of existing frames
- New frames created through extension
- Clear task isolation boundaries
- Minimal required context principle

### Memory System Integration
- Associative memory system mediates between long-term and working memory
- Working memory instantiated from long-term storage using associative retrieval
- Context updates managed through frame extension
- Resource tracking delegated to Handler

## Implementation Examples

### Frame Creation
typescript
// Example based on [Component:Memory:1.0] implementation
class ContextFrame implements IContextFrame {
    private bindings: Map<string, any>;
    private context: Map<string, any>;
    
    extend(newBindings: Map<string, any>): ContextFrame {
        const frame = new ContextFrame();
        frame.bindings = new Map([...this.bindings, ...newBindings]);
        frame.context = this.context;  // Shared context reference
        return frame;
    }
    
    cleanup(): void {
        // Resource cleanup handled by Handler
        this.bindings.clear();
        this.context = null;
    }
}
</file>
<file path="./system/architecture/patterns/director-evaluator.md" project="">
# Director‑Evaluator Pattern [Pattern:DirectorEvaluator:1.1]

**Canonical Reference:** This document is the authoritative description of the Director‑Evaluator Pattern. All extended descriptions in planning or misc files should refer here.

## Overview

The Director-Evaluator pattern is a specialized variant of the unified task‐subtask execution model. In this pattern, a parent task (the **Director**) produces an initial output that may require further evaluation. Instead of relying on a statically defined callback step, the evaluation subtask is spawned dynamically when the Director's output returns with a `CONTINUATION` status and an `evaluation_request` object in its `notes`.

**Note:** The `evaluation_request` object must include:
 - `type`: a string indicating the evaluation type,
 - `criteria`: a free-form string providing descriptive criteria used for dynamic evaluation template selection via associative matching,
 - `target`: a string representing the target (for example, the bash script command to run or the evaluation focus).

## Pattern Description

This pattern follows a three-phase flow:

1. **Parent Task (Director):**
   - Generates an initial output based on the user's instructions.
   - May return a result with `status: 'CONTINUATION'` and a populated `evaluation_request` in its `notes`.
   - Uses a `<context_management>` block with `inherit_context` set to `none` to start a new execution chain.

2. **Evaluation Trigger via Continuation:**
   - Rather than a fixed callback subtask, the evaluation step is triggered dynamically when the Director task returns a `CONTINUATION` status.
   - The embedded `evaluation_request` specifies both:
       - The **bash script** (or external callback mechanism) to execute, and
       - The **target** string that describes the aspects of the output requiring evaluation.
   - The Evaluator uses this information—with associative matching—to select an appropriate evaluation task template.
   - Only the latest evaluator output is retained; after the Evaluator completes its feedback step, the environment contains solely last_evaluator_output while all other temporary data is cleared. This significantly simplifies the feedback loop.

3. **Child Task (Evaluator):**
   - Is dynamically spawned by the Evaluator when it detects a `CONTINUATION` status along with an `evaluation_request` in the Director's output.
   - Uses a `<context_management>` block with `inherit_context` set to `subset` and `accumulate_data` enabled to incorporate only the relevant context.
   - Executes the evaluation subtask—which may include invoking the specified bash script via the Handler or Evaluator—and feeds its results back to the parent task so that the Director may continue its sequence.

### Environment Variable Management
Environment variables are managed so that last_evaluator_output is the only persistent variable across continuations. Any new evaluation clears other data, thereby reducing context window usage.

### Example Workflow

Below is a conceptual example (in pseudocode) illustrating the updated director-evaluator flow. In this scenario, the Director task returns a result with `status: 'CONTINUATION'` and an embedded `evaluation_request`:
typescript
// Example TaskResult returned by the Director task
const taskResult: TaskResult = {
    content: "Initial solution output...",
    status: 'CONTINUATION',
    notes: {
        evaluation_request: {
            type: "bash_script",
            criteria: ["validate", "log"],
            target: "run_analysis.sh"
        }
    }
};
Upon receiving this result, the Evaluator:
1. Uses the `evaluation_request` details (including the target string) to perform associative matching and select an appropriate evaluation task template.
2. Dynamically spawns an evaluation subtask (the Child Task) with a `<context_management>` block set to inherit a subset of context.
3. If necessary, invokes the specified bash script callback via the Handler or its own mechanism.
4. Feeds the evaluation results back to the Director, allowing the overall task to continue.

## Integration with the Unified Architecture

The updated Director-Evaluator pattern fully embraces the dynamic subtask concept. Rather than a statically defined bash callback subtask, the evaluation step is triggered by the Director task's output. The Evaluator examines the task result for a `CONTINUATION` status and an embedded `evaluation_request`, then:
 - Uses associative matching (with help from the Memory System if needed) to select an evaluation template.
 - Dynamically spawns the evaluation subtask.
 - Invokes any specified bash script callback via the Handler or its own callback mechanism (since tasks remain reserved for LLM sessions).

**Key Characteristics:**

 - **Unified Model:** The pattern adheres to the unified context management and task execution model. All tasks, including those used for callbacks, use the same XML structure and TS types.

 - **Bash Script Callback:** The intermediary bash script is invoked as a subtask. Its output can be logged, used to adjust the environment, or to validate the parent task's results.

 - **Context Management:** The Evaluator subtask receives updated context via standard `<context_management>` settings (e.g. `inherit_context` set to `subset` and `accumulate_data` enabled).

## Conclusion

The updated Director-Evaluator pattern exemplifies the dynamic task–subtask paradigm. By returning a CONTINUATION status along with an embedded evaluation_request, a Director task signals that additional evaluation is required. The Evaluator then dynamically spawns an evaluation subtask—invoking a bash script callback via the Handler (or its own mechanism) if specified—to process and refine the output before feeding the results back to the parent task. This approach ensures flexibility and a seamless integration of external evaluation within the unified execution architecture.

## Static Director-Evaluator Variant

In addition to the dynamic pattern described above, a static variant is available for scenarios where the entire execution sequence is predetermined. In the static variant:
 - The Director Task generates the initial output.
 - A Target Script Execution task immediately runs an external command (e.g. a bash script) using the director's output.
 - The Evaluator Task then processes the output from the script.

### XML Template Example
xml
<task type="director">
    <output_slot>last_evaluator_output</output_slot>
</task>

<task type="evaluator">
    <input_source>last_evaluator_output</input_source>
</task>
</file>
<file path="./system/architecture/patterns/error-resources.md" project="">
# Error Condition Resource Pattern [Pattern:ErrorResource:1.0]

## Resource Handling During Errors

From task-system/spec/behaviors.md and impl/resource-management.md:

### Required Actions
On error detection:
- Stop resource usage
- Complete resource accounting
- Begin cleanup process
- Surface error with metrics

### Cleanup Requirements
From task-system/impl/resource-management.md:
- Handler cleanup
- Resource release
- Memory cleanup
- Metric collection

## Implementation
typescript
interface ErrorResourceMetrics {
    // From task-system/spec/types.md
    turns: {
        used: number;
        limit: number;
    };
    context: {
        used: number;
        limit: number;
        peakUsage: number;
    };
}
</file>
<file path="./system/architecture/patterns/errors.md" project="">
# Error Handling and Recovery Pattern [Pattern:Error:1.0]

**Intended Focus:** This document covers overall error detection, classification, and recovery strategies. For resource‑related cleanup details, see the "Resource Cleanup" subsection below. (For low‑level resource metrics, refer to [Handler Resource Tracking](../decisions/001-memory-system.md) and related docs.)

## 1. Pattern Definition

### 1.1 Purpose
Error handling pattern for the task execution system, focusing on three key concerns:
- Resource exhaustion detection and recovery
- Invalid output handling
- Progress failure management

### 1.2 Context
This pattern is used by:
- [Component:TaskSystem:1.0] for error detection
- [Component:Evaluator:1.0] for error recovery
- [Component:Handler:1.0] for resource monitoring

### 1.3 Core Elements
- Error Type System: See [Type:TaskSystem:TaskError:1.0]
- Recovery Protocols: See [Protocol:Tasks:Reparse:1.0]
- Resource Contracts: See [Contract:Resources:1.0]

## 2. Error Categories

### 2.1 Resource Exhaustion
Handled by [Protocol:Tasks:Reparse:1.0]
[TBD: Complete category specification]

### 2.2 Invalid Output Structure
Related to [Contract:Tasks:TemplateSchema:1.0]
[TBD: Complete category specification]

### 2.3 Failure to Make Progress
[TBD: Progress failure specification]

## 3. Recovery Process

### 3.1 Detection Phase
See [Interface:Handler:ResourceMonitoring:1.0]
[TBD: Detection requirements]

### 3.2 Planning Phase
See [Component:Evaluator:1.0] for recovery planning.
[TBD: Planning requirements]

### 3.3 Execution Phase
See [Protocol:Tasks:Reparse:1.0] for execution details.
[TBD: Execution requirements]

### 3.4 Validation Phase
[TBD: Validation requirements]

## 4. Pattern Examples
See components/task-system/impl/examples.md for concrete examples.
[TBD: Additional examples]

## 5. Known Limitations
[TBD: Pattern limitations]

## 6. Related Patterns
- [Pattern:ResourceManagement:1.0]
- [Pattern:TaskExecution:1.0]
</file>
<file path="./system/architecture/patterns/resource-warnings.md" project="">
<!-- This file has been consolidated into resource-management.md. Refer to the "Warning Thresholds" subsection there. -->
</file>
<file path="./system/architecture/patterns/resource-management.md" project="">
# Resource Management Pattern [Pattern:ResourceManagement:1.0]

## Purpose & Constraints
This document defines the resource management strategy for the task execution system. It covers:
 - Memory Hierarchy
 - Resource Tracking (turn counts, context window, token usage)
 - Warning Thresholds (e.g. 80% limits)
 - Cleanup Procedures

**Note:** Warning signals are purely informative; hard limits trigger termination.

## Core Components

### Memory Hierarchy
1. **Long‑term Memory:** Stores data and procedures; accessed via the Memory System (read‑only during task execution).
2. **Working Memory:** The active computation space (task‑specific context) managed through Environment objects; cleared after task completion.
3. **Context Frames:** Capture complete execution environments (bindings and working memory) using a minimal‑context extension pattern.

### Resource Tracking

The Handler is responsible for:
 - Tracking turn counts and enforcing limits.
 - Monitoring context window usage (tokens) with warning thresholds (e.g. 80%) and hard limits.
 - Reporting resource metrics for error handling.

### Resource Tracking

#### Handler Responsibility
- One Handler per task execution
- Tracks resource usage:
  * Turn counts
  * Context window size
  * Token usage
  * Peak usage statistics
- Enforces resource limits
- Manages clean termination

#### Isolation Requirements
- No cross-Handler resource pooling
- Per-session resource isolation
- Clean resource release on completion
- Independent Handler execution

### Context Management

#### Window Management
- Token-based calculation
- Explicit size monitoring
- Fraction-based limits
- No content optimization
- Warning thresholds at 80%
- Hard limits with error handling

#### Context Preservation

- The nested Environment model ensures that each child task gets its own context.
- Proper chaining of environments prevents context leakage.
- InheritedContext and any built-in objects (like TaskLibrary) persist unchanged in the chain.
- Context frames capture environments
- Minimal required context per task
- Associative memory mediation
- Clean extension mechanism

## Resource Configuration

### Default Configuration
- Base resource limits
- Warning thresholds
- Default turn counts
- Context window limits

### Per-Task Overrides
- Task-specific limits
- Custom thresholds
- Resource constraints
- Performance targets

## Script Execution Resource Management

- Script tasks (type="script") are executed by the Handler.
- The Handler captures stdout, stderr, and exitCode for script tasks.
- A non-zero exitCode is treated as a TASK_FAILURE error.

Example interface:
typescript
interface ScriptTaskResult {
    stdout: string;
    stderr: string;
    exitCode: number;
}
## Interactions

### With Memory System [Component:MemorySystem:1.0]
- Provides long-term storage
- Manages context persistence
- Handles file operations
- Maintains memory hierarchy

### With Task System [Component:TaskSystem:1.0]
- Creates/manages Handlers
- Enforces resource limits
- Manages task execution
- Handles resource errors

### With Handler [Component:Handler:1.0]
- Tracks resource usage
- Enforces limits
- Manages session lifecycle
- Reports resource metrics

## Implementation Requirements

### Resource Tracking
typescript
// Resource metrics definition moved to spec/types.md
// See [Type:ResourceMetrics:1.0] for the complete interface
### Handler Configuration
typescript
interface HandlerConfig {
    maxTurns: number;
    maxContextWindowFraction: number;
    warningThreshold: number;
    defaultModel?: string;
    systemPrompt: string;
}
## Error Handling

### Resource Exhaustion
- Immediate task termination
- Clean resource release
- Error surfacing with metrics
- No automatic retry

### Context Overflow
- Token limit enforcement
- Warning at threshold
- Clean termination
- Context metrics reported

### Progress Failure
- Resource accounting completion
- State cleanup
- Error propagation
- Recovery guidance

### Sequential Task Resources

For **sequential** tasks, the Evaluator maintains a step-by-step record of partial results and history, often called `SequentialHistory`. This history is **not** tracked against the Handler's context window limits. Instead:

- **Evaluator** owns the entire sequential history for multi-step tasks.
- **Handler** continues to track standard resource usage (turns, tokens).
- Because the sequential history is purely textual or metadata that the Evaluator stores separately, it does not consume the Handler's context window.
- If the task is configured to accumulate data (`<accumulate_data>true</accumulate_data>`), the Evaluator may pass prior step outputs into `MemorySystem.getRelevantContextFor()`.
- The Evaluator maintains a SequentialHistory for sequential (type="sequential") tasks.
- The SequentialHistory (holding step outputs and metadata) is not counted against the Handler’s context window limits.
- Accumulated outputs are retained for the entire sequential task execution loop and then discarded (or archived) once the sequence completes.

Example interface:
typescript
interface SequentialHistory {
    outputs: TaskOutput[];
    metadata: { startTime: Date; currentStep: number; resourceUsage: ResourceMetrics; };
}
interface TaskOutput {
    stepId: string;
    output: string;
    notes: string;
    timestamp: Date;
}
- This separation ensures Handler resource metrics stay consistent and the Evaluator can keep any relevant partial outputs for as long as needed.
- Once the sequential task completes (success or failure), the Evaluator discards (or archives) the sequential history to free memory.

This design ensures a clean boundary between higher-level multi-step results (owned by the Evaluator) and resource usage constraints (handled by the Handler).

## Related Patterns
- [Pattern:Error:1.0] - Error handling strategy
- [Pattern:TaskExecution:1.0] - Task execution flow
</file>
<file path="./system/architecture/qa/resource-management.md" project="">
# Resource Management Q&A

## Memory Types & Organization

Q: What types of memory need to be managed?
A: The system has a hierarchical memory design:
- Long-term memory for data and procedures
- Working memory for active computations
- Context frames that capture execution environments (including working memory)
- Variable bindings within environments

Q: How is context organized and managed?
A: Through Environment objects that combine:
- Variable bindings (local scope)
- Working memory context
- Context frames are passed and extended through task execution

Q: How is minimal required context determined?
A: Context selection is handled at the LLM + prompt level, not by the system architecture. This allows for more intelligent and flexible context selection based on task requirements.

## Resource Ownership & Isolation

Q: Who owns and tracks resources?
A: Per existing documentation:
- Handler-based resource tracking
- One Handler per task execution
- No cross-Handler resource pooling
- Per-session resource isolation

Q: How are resources allocated and released?
A: As documented:
- Clean resource release on completion
- Turn limit passed during Handler initialization
- Default resource limits from config
- Per-task limit overrides possible

Q: How are memory operation failures handled?
A: Through a simple retry mechanism:
- Failed operations should be retried once
- If retry fails, an informative error is surfaced
- No complex recovery mechanisms in MVP

## Context Window Management

Q: How is the context window managed?
A: Through explicit tracking:
- Token-based calculation
- Window size monitoring
- Fraction-based limits
- No content optimization
- Warning at 80% threshold
- Error at limit reached

Q: How does context preservation work between tasks?
A: Through the Environment system:
- Context frames capture complete execution environments
- Each task receives minimal required context
- Associative memory system mediates between long-term and working memory
- Environment.extend() creates new contexts with additional bindings
- No context merging in MVP - extension patterns only

## Resource Metrics & Limits

Q: What resource metrics are tracked?
A: Currently documented:
- Turn counts
- Context window size
- Token usage
- Peak usage statistics

Q: How are resource limits handled?
A: As specified:
- Default limits from config
- Per-task overrides possible
- Warning thresholds (80%) are purely informative
- Hard limits with error handling
- Clean termination on limit violation
</file>
<file path="./system/architecture/decisions/001-memory-system.md" project="">
# Architecture Decision Record: Memory System Design

## Context

The memory system needs to manage short-term task context and maintain a global index of file metadata, while delegating file access to direct tool usage. This ADR captures key decisions about responsibilities and interfaces.

## Related Documents
- See [Component:Memory:2.0] in components/memory/api/interfaces.md for interface specification
- See [Component:TaskSystem:1.0] in components/task-system/README.md for task execution details
- See [Interface:Handler:Tools:1.0] for file access tools

## Decisions

### Memory System Scope

1. **Component Responsibilities**
   - Maintains short-term task data context
   - Manages global file metadata index
   - Delegates file access to Handler tools
   - Does not handle file content storage or retrieval

2. **Memory Organization**
   - Working Memory includes only data context from associative matching
   - Global Index includes file paths and associated metadata strings
   - Clear separation between metadata indexing and file access

### Context Management

1. **Context Sources**
   - Short-term context comes from:
     * Associative matching results
     * Direct updates during task execution
   - Global index serves as bootstrap for associative matching
   - File content accessed via Handler tools when needed

2. **Context Control**
   - Associative matching uses global index for initial filtering
   - Actual file content accessed through Handler tools
   - Metadata strings provide search context without content storage

### Interface Design

1. **Global Index**
   - Simple map of file paths to metadata strings
   - Bulk updates only
   - No hierarchical organization
   - Serves as search bootstrap

2. **Associative Match Results**
   - Combines unstructured context with file matches
   - File matches include optional per-file metadata 
   - File paths used with Handler tools for content access

## Consequences

1. **Positive**
   - Simplified memory system responsibilities
   - Clear separation between metadata and content
   - More flexible file access via tools
   - Reduced system complexity

2. **Negative**
   - Requires tool support in Handler
   - May need optimization for large file sets
   - Potential context window pressure from file content

## Implementation Notes

1. Update Memory System interface to reflect simplified scope
2. Implement Handler file access tools
3. Ensure efficient global index updates
4. Review associative matching for new approach</file>
<file path="./system/architecture/decisions/002-context-management.md" project="">
# Context Management Architectural Decisions

## Status
Accepted

## Context
The system needs to manage task execution context efficiently while supporting composition operations. Several key decisions were needed regarding context selection, merging, and extension patterns.

## Decisions

### 1. Context Selection via LLM
- Context selection (determining minimal required context) will be handled at the LLM + prompt level
- This is NOT a system architecture concern
- Allows for more flexible and intelligent context selection
- Pushes complexity to the prompt engineering layer where it can be more easily tuned

### 2. Context Extension vs Merging
- Will use context extension patterns rather than merging
- Tasks extend from parent context rather than merging multiple contexts
- Simpler model that satisfies MVP composition requirements
- Reduces complexity in the memory system implementation

### 3. Warning Behavior
- Resource warning thresholds are purely informative
- Warnings do not affect execution flow
- Simplifies resource management behavior
- Maintains clear separation between warnings and hard limits

### 4. Memory Operation Error Handling
- Memory operations that fail should be retried
- If retry fails, surface an informative error
- Provides simple but robust error handling strategy
- Gives operations a chance to recover without complex logic

## Consequences
- Positive:
  - Simpler memory system implementation
  - Clear separation of concerns between system and LLM layers
  - Straightforward error handling model
  - Reduced complexity in context management
- Negative:
  - May need to revisit context merging for post-MVP requirements
  - More responsibility on prompt engineering for context selection
  - Limited automatic intervention on warnings

## Related
- [Component:MemorySystem:1.0]
- [Pattern:TaskExecution:1.0]
- [Contract:Resources:1.0]</file>
<file path="./system/architecture/decisions/004-sequential-context-management.md" project="">
# Architecture Decision Record: Sequential Context Management

## Status
Proposed

## Context
We need to separate context inheritance from data accumulation and provide a robust mechanism for step-by-step history tracking.

Currently, tasks either share context automatically or produce data that might or might not propagate. This leads to confusion when partial outputs are produced but we do not have a consistent mechanism to feed them into subsequent steps. Also, memory consumption can balloon if every subtask blindly appends data. 

## Decision
1. **Introduce `<context_management>`** for controlling context inheritance and accumulation in sequential tasks.  
2. **Add explicit outputtracking** in the Evaluator for each step of a sequential task.  
3. **Provide structured ways** to use task history in associative matching or subsequent steps.  
4. **Include step outputs** in error results for failed sequences.  
5. **Enforce resource limits** on total stored step data.

## Consequences
- **Cleaner separation of concerns** between inheritance and accumulation  
- **More flexible context management** through distinct modes (`inherit_context`, `accumulate_data`, etc.)  
- **Better step-by-step tracking** for partial outputs  
- **Predictable error output**: if step N fails, steps 1..N-1 remain visible  
- **Clear resource usage capping** for historical data

## Implementation Notes
1. The new `<context_management>` block in the `sequential` task schema.  
2. The Evaluator stores subtask outputs in a local structure (`SequentialHistory`).  
3. On subtask completion (whether success or error), the Evaluator updates the history.  
4. If `accumulate_data` is `true`, the next subtask can optionally see prior outputs (the system uses these to fill in an associative matching context or a merged notes field).  
5. If `accumulation_format` is `notes_only`, we store only minimal text from each step in the history. If `full_output`, we store the entire subtask result.  
6. The plan accounts for partial failures by storing partial results in the final error. 

## Alternatives Considered
- **Context merging** in each step: Rejected due to complexity and risk of indefinite growth.  
- **Forcing every step to have fresh context**: Would break certain use cases that require incremental data usage.  
- **Implicit partial output usage**: Proposed approach is more explicit, ensuring developers set `accumulate_data` if they need it.

## Related
- [Pattern:SequentialTask:2.0] in system/architecture/overview.md  
- [misc/operators.md] for structural usage  
- [system/contracts/protocols.md] for updated XSD schema  
- [components/task-system/impl/examples.md] for a usage example
</file>
<file path="./system/architecture/decisions/005-context-handling.md" project="">
# Architecture Decision Record: Context Generation Clarifications

## Status
Accepted

## Context
Recent feedback provided several important clarifications about context generation and associative matching that were either unclear or inconsistent in existing documentation.
The system needs clear policies for how context inheritance and accumulation work across different operator types. This includes sequential tasks, reduce operations, and potential future parallel tasks. We need to define both the inheritance rules and error handling approaches.

## Key Clarifications

### 1. Input Structure for Associative Matching
**Surprise:** The input to getRelevantContextFor() has a specific XML structure with three potential fields:
- Previous outputs (if applicable)
- Inherited context (if applicable)
- Task text
Each with standardized headings from system configuration.

Current documentation does not mention this structure at all.

### 2. Dual Context Components
**Surprise:** When both inheritance and accumulation are active, the system maintains two distinct context components:
- 'Regular' inherited context
- 'Accumulation' context from prior steps
These are tracked separately but can be concatenated for use.

Current documentation suggests a simpler single-context model.

### 3. Resource Allocation Clarification
**Surprise:** The concept of "resource allocation" in relation to context generation timing is irrelevant - the system only signals exhaustion without actual allocation operations.

Current documentation contains references to resource allocation that may be misleading.

### 4. Memory System Scope
**Surprise:** The Memory System does not perform any ranking or prioritization of matched files - this responsibility is explicitly not part of its scope.

Current documentation is ambiguous about this limitation.

## Decision
Update architecture documentation to reflect these clarifications, particularly:
1. The structured XML format for getRelevantContextFor() input
2. The dual-context tracking mechanism
3. Remove references to resource "allocation"
4. Clarify Memory System scope limitations

## Consequences
- Clearer component responsibilities
- More precise context management specification
- Removal of ambiguous resource management concepts
- Better defined Memory System boundaries


# more decisions
### 1. Context Support by Operator Type

- **Sequential Tasks**: Full support for both inheritance and accumulation via `context_management` block
- **Reduce Tasks**: Support context inheritance only (no accumulation)
- **Parallel Execution**: Not implemented in MVP

### 2. Context Management Configuration
- Context management settings (`inherit_context`, `accumulate_data`) are fixed at template definition time
- No dynamic modification during task execution
- Settings remain consistent within a task/sequence

### 3. Reduce Task Context Flow
- Inner task results automatically influence reduction_task context
- Reduction task has access to:
  * Inherited context (if enabled)
  * Results from inner task execution

### 4. Error Handling
- No custom error handling for context failures in MVP
- All context failures map to standard `TASK_FAILURE`
- Future versions may support advanced context handling (e.g., input data reduction)
- No operator-specific error handling mechanisms

## Consequences

### Positive
- Clear, consistent context management model
- Simpler implementation without parallel execution concerns
- Predictable behavior with fixed settings
- Standard error handling reduces complexity
- Clear development path for future enhancements

### Negative
- Less flexibility in dynamic context management
- May require template changes for different context needs
- No operator-specific error handling in MVP
- Must handle all errors through standard `TASK_FAILURE`

## Related
- [Pattern:SequentialTask:2.0]
- [Interface:Memory:3.0]
- Task System operator specifications
</file>
<file path="./system/architecture/decisions/001-memory-system-qa.md" project="">
# Memory System Architecture Q&A

## Related Documents
- Memory component specification in [Component:Memory:2.0]
- Handler interface in [Interface:Handler:ResourceMonitoring:1.0]
- Memory Task Example in components/task-system/impl/examples.md
- Context Frame Pattern in [Pattern:ContextFrame:1.0]
- Resource Management Pattern in [Pattern:ResourceManagement:1.0]

## Memory and Context Concepts

Q: What exactly constitutes working memory?
A: The Memory System only manages two types of data:
1. Short-term task data context generated by associative matching
2. Global file metadata index for bootstrapping associative matching

The Handler manages all other task-related data including chat history and prompt handling.

Q: How is "context" different from "working memory"?
A: "Context" specifically refers to data context, while working memory is broader and includes chat history, system prompts, and templates. See [Pattern:ContextFrame:1.0] for details.

Q: What exactly does associative matching return?
A: Associative matching has two specific return values:
1. An unstructured data context section
2. A list of tuples containing absolute file paths and optional index strings for those files

## Component Responsibilities 

Q: Should the memory system track context window size?
A: No, this is delegated to the Handler (see [Interface:Handler:ResourceMonitoring:1.0]). The memory system stores content but doesn't track usage limits.

Q: Is the memory system responsible for managing system prompts and templates?
A: No, the Memory System does not handle prompts or templates at all. These are managed by the Task System and Handler.

Q: Who handles chat history?
A: The Handler manages all chat history and interaction state. The Memory System does not store any chat history.

Q: Who handles file content access?
A: File content access is handled by the LLM using Handler tools, not by the Memory System. The Memory System only provides the file paths and metadata needed to identify relevant files.

## Global Index

Q: What is the format of file metadata in the global index?
A: The metadata is simply stored as strings, with file paths as keys in a map structure. There is no predefined structure for the metadata content.

Q: What operations are supported on the global index?
A: The global index only supports two operations:
1. Getting the complete index
2. Bulk updates to the index
Individual updates, filtering, and querying are intentionally not supported to maintain simplicity.

## Context Management

Q: How can tasks get their data context?
A: Two ways (see operator specifications in components/task-system/spec/operators.md):
1. Inherit from parent/predecessor task
2. Generate fresh via associative matching using the global file metadata index as bootstrap. The associative matching task returns both context and a list of potentially relevant files, which can then be accessed using Handler tools.

Q: How does associative matching work when there's too much content?
A: When the full contents of all long-term storage files don't fit in the context window (times some factor), the associative matching task uses the existing global index to bootstrap the matching process. The input to the associative matching task includes all file paths in long-term storage.

Q: Should context inheritance vs. generation be a template parameter?
A: No, it should be part of the operator XML syntax in task library entries (see [Contract:Tasks:TemplateSchema:1.0]). It's not a substitutable parameter like task inputs.

Q: Can prior task output influence context generation?
A: Yes, the notes section of prior task output can be passed to associative matching for child/successor tasks. See Memory Task Example in components/task-system/impl/examples.md.

## Interface Design

Q: How should context source be controlled in the XML?
A: Through an optional inherit_context attribute on task elements, with defaults that can vary by operator type. See operator specifications in components/task-system/spec/operators.md.

## Implementation Questions

Q: Do operator defaults need to be standardized?
A: Not immediately. Different operators can have different context inheritance defaults based on their use cases. See operator specifications.

Q: How should context be handled in map/reduce operations?
A: The inherit_context attribute can be part of inner_task and reduction_task elements, following the same pattern as other operators. See operator specifications.

## Future Considerations

Q: When would file pre-extraction be considered?
A: File pre-extraction and concatenation is explicitly deferred for later consideration. The current design relies solely on tool-based file access via the Handler. Any performance optimizations through pre-extraction would only be considered after evaluating the effectiveness of the tool-based approach.</file>
<file path="./system/architecture/decisions/003-memory-context-update.md" project="">
# Architecture Decision Record: Remove Context Update Capability

## Status
Accepted

## Context
The Memory System's updateContext capability was found to be inconsistent with its architectural goals:
- System primarily provides context FOR tasks
- No persistence guarantees documented
- Context scope limited to current task
- No clear use cases for bi-directional context flow

## Decision
Remove updateContext method and enforce read-only context model.

### Changes
1. Remove updateContext from [Interface:Memory:3.0]
2. Enforce read-only context access
3. Maintain clear task isolation
4. Simplify state management

### Version Impact
- Major version increment to 3.0
- Breaking change for interface consumers
- Required updates to dependent systems

## Consequences

### Positive
- Clearer architectural boundaries
- Simpler interface
- Better task isolation
- Reduced state complexity
- More predictable behavior

### Negative
- Breaking change for existing code
- Migration effort required
- Potential feature impact

## Implementation
1. Update interface definitions
2. Remove update capabilities
3. Update documentation
4. Add migration guide
5. Update cross-references
6. Release version 3.0
</file>
<file path="./system/architecture/decisions/006-context-types.md" project="">
<!-- This file is currently under construction.
It will cover decisions on the precise data types for context representation.
For now, refer to the context management ADRs (002 and 005).
-->
</file>
<file path="./system/architecture/questions.md" project="">
# Open Architecture Questions

This document now lists only *unresolved* questions. Many items previously listed have been answered in the ADRs or clarified in the patterns.

## Unresolved Questions

1. **Context Generation Failures:** When associative matching fails, should partial outputs be preserved for re‑try? (See ADRs 002 and 005 for related discussion.)

2. **Operator Inheritance for Reduce/Map:** Should the `inherit_context` attribute be extended to reduce and parallel operators, and if so, how should it interact with accumulation?

3. **Subtask Spawning Mechanism:** How exactly should subtasks be created dynamically (beyond the Director‑Evaluator pattern)? This remains an open design area.

For additional background, see also [decisions/005-context-handling.md](decisions/005-context-handling.md) and [questions.md](questions.md) in previous revisions.
</file>
<file path="./components/evaluator/README.md" project="">
# Evaluator Component

## Overview

The **Evaluator** is the unified task-execution component of the system. It is responsible for:

1. **Controlling AST processing and execution**  
2. **Managing failure recovery** via standard task return statuses (`COMPLETE`, `CONTINUATION`, `FAILED`)
3. **Tracking resource usage** (in coordination with Handlers)
4. **Handling reparse/decomposition requests** when tasks fail (e.g. due to resource exhaustion or invalid output)

### References in Existing Documentation

- **System-Level References**  
  - *System README (`system/README.md`)* and *Architecture Overview (`system/architecture/overview.md`)* list the Evaluator as a core component, describing it as the manager for AST execution, resource tracking, and reparse/error handling.  
  - *Contracts & Interfaces (`system/contracts/interfaces.md`)* references "[Contract:Integration:EvaluatorTask:1.0]," tying the Evaluator to tasks and describing the need for an integration interface (though that interface is not yet fully elaborated).  
  - The *"Metacircular Evaluator"* concept is mentioned in `misc/textonly.tex.md`, demonstrating an evaluator that calls LLM operations as part of `apply-proc` and `eval-task`. This underscores that the Evaluator runs tasks by leveraging LLM-based primitives (for decomposition, atomic calls, or re-checking).  

- **Error Handling**  
  - The Evaluator is mentioned repeatedly (e.g., `misc/errorspec.md`, `system/architecture/patterns/errors.md`) as the component receiving error signals from tasks or sub-operations. It manages or coordinates the "control flow" when resource exhaustion or invalid outputs appear.  
  - Errors of type `RESOURCE_EXHAUSTION` or `TASK_FAILURE` can cause the Evaluator to request "reparse" or "decomposition."  

- **Implementation Plan**  
  - *Phase 2: Expanded Context Management* mentions extending environment usage so that sub-tasks may inherit or manage context. The Evaluator is implicitly involved in ensuring tasks have the right environment or partial results.  
  - *Phase 3: Task Execution Enhancements* explicitly names the Evaluator as a place to add "summary output or additional logging" for advanced debugging. The same phase also suggests new flags like `rebuild_memory` or `clear_memory` that the Evaluator would honor when building or discarding context.  

In many existing code examples (both TypeScript-like and Scheme-like), the system calls an `eval` or `apply` function that effectively belongs to the Evaluator domain. When direct execution fails, a decomposition or reparse step is triggered, also under the Evaluator's responsibility.

## 3.1 Nested Environment Model Integration

The Environment class supports nested scopes via an "outer" reference. The Evaluator creates a global environment (globalEnv) that includes built-in variables along with an instance of TaskLibrary (e.g., globalEnv.bindings["taskLibrary"] = taskLibrary). A new child environment is created for each task or function call.
typescript
// Example Environment implementation
class Env implements Environment {
    constructor(public bindings: Record<string, any> = {}, public outer?: Environment) {}
    find(varName: string): any {
        return (varName in this.bindings)
            ? this.bindings[varName]
            : this.outer ? this.outer.find(varName) : throw new Error(Variable ${varName} not found);
    }
}
## Responsibilities and Role

1. **AST Execution Controller**  
   - Orchestrates the step-by-step or operator-by-operator execution of tasks represented as an AST.
   - Calls out to the Handler for LLM-specific interactions and resource tracking (e.g. turn counts, context window checks).
   - Interacts with the Compiler when re-parsing or decomposition is required.

2. **Failure Recovery**  
   - Detects or receives error signals when tasks fail or exceed resources.  
   - Initiates "reparse" tasks or alternative decomposition approaches if the system's policies allow.  
   - Surfaces errors back to the Task System or parent contexts (e.g., "resource exhaustion," "invalid output").  

3. **Resource Usage Coordination**  
   - Not purely "owns" resource tracking (that's part of the Handler), but integrates with it. The Evaluator is aware of usage or limit errors and decides whether to attempt decomposition or fail outright.  

4. **Context and Environment Handling**  
   - In multi-step or operator-based tasks (sequential, reduce, etc.), the Evaluator ensures the proper propagation of the environment and partial context. Every new task or function call execution uses a child environment (based on the parent environment or the global environment, depending on the XML attribute `inherit_context`), thereby ensuring that the TaskLibrary and any built-in variables remain accessible through the environment chain.
   - The Evaluator leverages the Memory System for associative context retrieval but does not manage file content directly.  
   - Note: The Evaluator now writes its output exclusively to the environment variable last_evaluator_output—this value is a serialized EvaluationResult (with fields success and optional feedback).

5. **Integration with Task System**  
   - The Task System may call the Evaluator with a structured or partially structured task. The Evaluator then "executes" it by walking its representation (e.g., an AST or an XML-based operator chain).  
   - On error or partial success, the Evaluator can signal the Task System to orchestrate higher-level recovery or store partial results.  

## 3.3 FunctionCall AST Node for DSL Function Calling

The FunctionCall node is used to invoke a task functionally by looking up its definition in the TaskLibrary. When a FunctionCall is evaluated, the Evaluator:
- Uses env.find("taskLibrary") to retrieve the registry;
- Looks up the task by its funcName;
- Creates a child environment (e.g., new Env({}, env));
- Binds the parameters from task_def.metadata to the evaluated arguments;
- And finally calls taskDef.astNode.eval(newEnv) to get the result.
typescript
// Example FunctionCall evaluation
class FunctionCallNode implements FunctionCall {
    constructor(public funcName: string, public args: ASTNode[]) {}
    async eval(env: Environment): Promise<any> {
        const taskLibrary = env.find("taskLibrary")["taskLibrary"];
        const taskDef = taskLibrary.getTask(this.funcName);
        const funcEnv = new Env({}, env);
        const parameters: string[] = taskDef.metadata?.parameters || [];
        for (let i = 0; i < parameters.length && i < this.args.length; i++) {
            funcEnv.bindings[parameters[i]] = await this.args[i].eval(env);
        }
        return await taskDef.astNode.eval(funcEnv);
    }
}
## Metacircular Approach

Documentation (especially in `misc/textonly.tex.md`) sometimes refers to the system's evaluator as a "metacircular evaluator," meaning:
> The interpreter (Evaluator) uses LLM-based operations as its basic building blocks, while the LLM also uses the DSL or AST from the evaluator for self-decomposition tasks.

In practice, this means:  
- The Evaluator calls an LLM to run "atomic" tasks or to do "decomposition."  
- The LLM might generate or refine structured XML tasks that, in turn, the Evaluator must interpret again.  
- This cycle repeats until the tasks can be successfully executed without exceeding resource or output constraints.

Because of this, the Evaluator is partially "self-hosting": it leverages the same LLM to break down tasks that can't be executed directly.  

---

## Potential Future Enhancements

The existing plan outlines several optional or future features that involve the Evaluator:

1. **Advanced Debug Logging** (Phase 3 in the Implementation Plan)  
   - Collecting or storing extensive logs in `notes.debugLogs` or similar.  
   - Exposing partial steps or re-try decisions for advanced debugging.  

2. **`rebuild_memory` or `clear_memory` Flags**  
   - When tasks specify these, the Evaluator would create or discard certain environment data at the start of a sub-task.  
   - This is relevant for tasks that explicitly want a fresh context (e.g., ignoring prior steps' context).  

3. **Multi-Step or "Continuation" Protocol**  
   - The Evaluator might support tasks that require multiple interactions or "continuation steps" without losing context.  
   - This could involve storing partial states or sub-results in the environment and continuing in a new iteration.  

4. **Agent Features** (Phase 4 in some documents)  
   - The Evaluator could handle conversation-like tasks with a "REPL" approach, or coordinate multiple LLM backends.  
   - This is out of scope for the MVP, but recognized as an extension point.

---

## Known Open Questions

1. **Partial Results**  
   - Some references (e.g., "Phase 2: Expanded Context Management") mention partial-result handling if sub-tasks fail mid-operator. It is not yet finalized how the Evaluator will pass partial data up or whether to discard it.  

2. **Context Generation Errors**  
   - The error taxonomy may or may not include a dedicated "CONTEXT_GENERATION_FAILURE." Currently, the Evaluator might treat it as a generic `TASK_FAILURE` or trigger reparse.  

3. **Inheritance on Map/Reduce**  
   - It is hinted that "inherit_context" might become relevant for parallel or reduce operators. The Evaluator's role in distributing or discarding environment data for sub-tasks is still being discussed.

---

## Summary

The Evaluator coordinates the execution of tasks—represented in AST or XML-based form—by calling LLM operations, handling resource usage signals, managing sub-task context, and recovering from errors. It serves as the system's "control loop" for deciding whether tasks can be executed directly or require alternative approaches (like decomposition).  

*For further details:*  
- **System-Level Descriptions:** See `system/architecture/overview.md`  
- **Error Patterns & Recovery:** See `system/architecture/patterns/errors.md`, `misc/errorspec.md`  
- **Metacircular Evaluator Examples:** See the "Evaluator" sketches in `misc/textonly.tex.md`  
- **Future Expansions:** Refer to Implementation Plan phases in `implementation.md` (root-level or system docs).

## Dual Context Tracking

The Evaluator maintains two distinct types of context when both inheritance and accumulation are enabled:

1. **Inherited Context**: The parent task's context that is passed down unchanged
2. **Accumulated Data**: The step-by-step outputs collected during sequential execution

Under the new protocol, tasks use <inherit_context>none</inherit_context> and <accumulate_data>false</accumulate_data> to ensure that no prior environment variables are carried over except last_evaluator_output. When contexts are needed, the Evaluator:

1. Maintains the parent's inherited context unchanged throughout execution
2. Separately tracks accumulated outputs from previous steps
3. Calls `getRelevantContextFor()` with both contexts when needed:
typescript
   const contextInput: ContextGenerationInput = {
       previousOutputs: accumulatedData,    // From sequential history
       inheritedContext: parentContext,     // From parent task
       taskText: currentTaskDescription     // Current step
   };
   const matchResult = await getRelevantContextFor(contextInput);
   
4. Uses the returned context and matches during prompt generation

## Associative Matching Invocation

When executing a sequential task step with `<inherit_context>false</inherit_context>` **but** `<accumulate_data>true</accumulate_data>`, the Evaluator:
1. Calls `MemorySystem.getRelevantContextFor()` with prior steps' partial results
2. Merges the returned `AssociativeMatchResult` into the next step's environment
3. Maintains complete separation from the Handler's resource management

### Evaluator Responsibilities for Associative Matching

* **Initiation**: The Evaluator is the *sole* caller of `MemorySystem.getRelevantContextFor()`.
* **Sequential History**: It retrieves partial outputs from `SequentialHistory` (the step-by-step data structure it maintains).
* **Context Merging**: If the step is configured for accumulation, the Evaluator incorporates the match results into the upcoming step's environment.
* **Error Handling**: Any failure to retrieve context (e.g., a memory system error) is handled through the existing `TASK_FAILURE` or resource-related error flow. No new error category is introduced.
* **No Handler Involvement**: The Handler does not participate in the retrieval or assembly of this context data, beyond tracking resource usage at a high level.

This design ensures that only the Evaluator initiates associative matching, preventing confusion about which component is responsible for cross-step data retrieval. The Memory System remains a service that simply provides matches upon request.

---

---

## Sequential Task History

When evaluating a **sequential** task (type="sequential"), the Evaluator maintains a **step-by-step output history**:

### Output Tracking
1. **History per sequence**: Each sequential task run has a dedicated list (or array) of step outputs.
2. **Preservation**: All step outputs remain available until the task completes (success or error).
3. **Failure case**: If a step fails, the partial results from prior steps are included in the final error notes.
4. **Resource awareness**: The evaluator must keep track of the size of stored outputs, possibly truncating or summarizing them to prevent memory or token overflow.

### History Structure (example)
typescript
interface SequentialHistory {
    outputs: TaskOutput[];
    metadata: {
        startTime: Date;
        currentStep: number;
        resourceUsage: ResourceMetrics;
    };
}

interface TaskOutput {
    stepId: string;       // or step index
    output: string;       // The main content from that step
    notes: string;        // Additional or partial notes
    timestamp: Date;
}
### Lifecycle Management
1. **Creation**: On the first step of a sequential task, the Evaluator initializes a new `SequentialHistory`.
2. **Updates**: After each step completes, the Evaluator appends a `TaskOutput` object to `SequentialHistory.outputs`.
3. **Clearing**: Once the entire sequence finishes (success or error), the Evaluator discards the stored step outputs to reclaim resources.
4. **Error Handling**: If a step fails, the last known `SequentialHistory` object is packaged with the error output, so that partial results can be surfaced if needed.

### Script Execution and Feedback Flow
When executing a script task, the evaluator captures stdout, stderr, and exitCode from the external command. These outputs are then formatted into an EvaluationResult and stored in last_evaluator_output. Upon continuation, all other environment variables are cleared to isolate this single piece of feedback.

### Static Pattern Execution
The Evaluator now supports a static Director-Evaluator variant. In this mode, after the Director task generates the initial output, a script execution task (of type "script") is automatically invoked. The Evaluator captures the script's output—including stdout, stderr, and exit code—and feeds it into the subsequent evaluation step, ensuring a predictable, pre-compiled control flow.

### Usage Example
When a multi-step sequence is run, each subtask is executed in turn. The Evaluator:
1. Sets up a new `SequentialHistory` with `currentStep=0`.
2. Executes the first subtask, storing its `TaskOutput` in `outputs[0]`.
3. Moves on to the second subtask, incrementing `currentStep`. If it fails, the Evaluator includes `outputs[0]` data in the final error's notes, to assist debugging or partial re-usage.
4. If steps continue successfully, the final result merges all step outputs or final subtask output as the overall `TaskResult`.

The evaluator now produces an EvaluationResult (with success and optional feedback) for each task. Only the last evaluator output is stored in the environment variable last_evaluator_output; all other variables are cleared on continuation.

Example task definitions:
xml
<task type="director">
    <output_slot>last_evaluator_output</output_slot>
</task>

<task type="evaluator">
    <input_source>last_evaluator_output</input_source>
</task>
**Important**: Because subtask outputs can be large, the system should either store them as short notes or partial references. The data accumulation approach can be toggled with `accumulateData` (in `ContextManagement`), plus an `accumulationFormat` indicating whether to store full outputs or only summary notes.
</file>
<file path="./components/memory/README.md" project="">
# Memory System Component [Version 3.0]

## Overview

The Memory System provides context management and associative matching services for task execution. It maintains a global metadata index to support context retrieval while delegating actual file operations to Handler tools. The system focuses purely on metadata management and context retrieval - it does not store file content, perform file operations, track resources, or rank matches.

## Core Interface
typescript
interface MemorySystem {
    // Retrieve global file metadata index
    getGlobalIndex(): Promise<GlobalIndex>;
    
    // Update global metadata index (bulk operation)
    updateGlobalIndex(index: GlobalIndex): Promise<void>;
    
    // Get relevant context for task execution
    getRelevantContextFor(input: ContextGenerationInput): Promise<AssociativeMatchResult>;
}
The system works with a simple but flexible type system. File metadata is stored as unstructured strings, with a global index mapping absolute file paths to their metadata. When performing associative matching, the system returns both relevant context and a list of matching files.

## Usage

The Memory System is typically used for two main purposes: managing the global metadata index and retrieving context for task execution. Here's a typical usage pattern:
typescript
// Initialize and update index
const memory = new MemorySystem();
await memory.updateGlobalIndex(new Map([
    ['data.txt', 'Experimental results from 2024-02'],
    ['config.json', 'System configuration parameters']
]));

// Request context for task execution
const result = await memory.getRelevantContextFor({
    taskText: "Analyze recent experimental results",
    inheritedContext: "Previous analysis focused on temperature variance",
    previousOutputs: "Initial data validation complete"
});
## Integration Points

The Memory System integrates with other components through clear boundaries. It provides context and metadata to the Task System and Evaluator while relying on Handler tools for any actual file operations. The system maintains a read-only approach to context management, with updates happening through bulk operations on the metadata index.

All file operations go through Handler tools rather than the Memory System itself. This separation ensures clean resource management and clear responsibility boundaries. Error handling follows a simple pattern - all failures map to standard TASK_FAILURE errors with clear messages.

## Resource Management

The system takes a conservative approach to resource management. Index updates are bulk operations that replace the entire index, avoiding complexities of partial updates or hierarchical organization. Context is never preserved between tasks, and all updates happen through clean extensions rather than merging.

## Implementation Guidelines

When implementing against the Memory System, keep these principles in mind:
typescript
// Context generation requires structured input
const input: ContextGenerationInput = {
    taskText: "Required task description",
    inheritedContext: "Optional parent context",
    previousOutputs: "Optional step outputs"
};

// Index management uses absolute paths
const index: GlobalIndex = new Map([
    ['/absolute/path/to/file', 'Metadata string']
]);
Use descriptive but concise metadata strings, maintain consistent formats, and handle all error cases explicitly. Always access file content through Handler tools rather than trying to store it in the Memory System.

## Version History

The current Version 3.0 removed the updateContext capability and enforces a read-only context model with simplified state management. This follows from architecture decisions documented in [ADR:Memory:1.0] and interface specifications in [Interface:Memory:3.0].

For detailed implementation specifications and patterns, refer to [Contract:Integration:TaskMemory:1.0] and [Pattern:ContextFrame:1.0].
</file>
<file path="./components/memory/api/interfaces.md" project="">
# Memory System Interfaces [Interface:Memory:3.0]

## Overview
The Memory System provides two core capabilities:
1. Global file metadata index maintenance for associative matching

The system does not handle file content storage or retrieval.

## Core Types

/**
 * Represents metadata associated with a file
 * Stored as an unstructured string for flexibility
 */
type FileMetadata = string;

/**
 * Global index mapping file paths to their metadata
 * - Keys are absolute file paths
 * - Values are unstructured metadata strings
 */
type GlobalIndex = Map<string, FileMetadata>;


A mapping of file paths to their associated metadata strings. **Note:** The Memory System is responsible only for providing file metadata (including file paths and unstructured metadata strings). All file I/O operations (reading, writing, deletion) are delegated to Handler tools. The index serves as a bootstrap mechanism for associative matching when full content scanning is not feasible.

Key characteristics:
- Keys are absolute file paths
- Values are unstructured metadata strings
- No hierarchical organization
- Updated in bulk operations only

### FileMatch
typescript
type FileMatch = [string, string | undefined];


Represents a relevant file match from associative matching:
- First element: Absolute file path
- Second element: Optional metadata string providing context for this specific match

### AssociativeMatchResult
typescript
interface AssociativeMatchResult {
    context: string;      // Unstructured data context
    matches: FileMatch[]; // Relevant file matches
}


The complete result of associative matching, containing:
- Unstructured context data relevant to the current task
- List of potentially relevant files with optional per-file context

## Interface Methods


### Index Management

#### getGlobalIndex()
typescript
getGlobalIndex(): Promise<GlobalIndex>

Retrieves the complete global file metadata index. The GlobalIndex should now support the needs of the TaskLibrary and nested environment model. Any changes to the GlobalIndex structure must allow associative matching in the context of nested task environments. Keys remain absolute file paths and values remain unstructured metadata but remain useful for task context extraction.

#### updateGlobalIndex(index: GlobalIndex)
typescript
updateGlobalIndex(index: GlobalIndex): Promise<void>

Performs a bulk update of the global file metadata index. Replaces the entire existing index.


/**
 * Retrieve context using associative matching.
 * 
 * The Memory System does NOT perform ranking or prioritization of matches.
 * It only provides associative matching based on the input structure.
 *
 * @param input - The ContextGenerationInput containing task context
 * @returns A promise resolving to an AssociativeMatchResult object containing:
 *   - context: Unstructured text data relevant to the query
 *   - matches: An unordered list of file paths (and optional metadata) relevant to the query
 * @throws {INVALID_INPUT} If the input structure is malformed or missing required fields
 */
declare function getRelevantContextFor(input: ContextGenerationInput): Promise<AssociativeMatchResult>;

## Integration Points
- Handler: Uses file paths from AssociativeMatchResult to read files via tools
- Associative Matching: Uses GlobalIndex as basis for context generation in tasks
</file>
<file path="./components/task-system/impl/examples.md" project="">
# Task System Implementation Examples

> **Note:** For a detailed description of the Director‑Evaluator pattern, refer to [system/architecture/patterns/director-evaluator.md](../system/architecture/patterns/director-evaluator.md).

## Basic Task Execution
typescript
// Initialize TaskSystem
const taskSystem = new TaskSystem({
  maxTurns: 10,
  maxContextWindowFraction: 0.8,
  systemPrompt: "Default system prompt"
});

// Register handlers
taskSystem.onError((error) => {
  console.error('Task error:', error);
});

taskSystem.onWarning((warning) => {
  console.warn('XML validation warning:', warning.message);
});

// Execute task
const result = await taskSystem.executeTask(
  "analyze data",
  memorySystem
);

// Check XML parsing status
if (!result.outputs.some(output => output.wasXMLParsed)) {
  console.warn("XML parsing failed, using fallback string output");
}


## Template Management
typescript
const template: TaskTemplate = {
  taskPrompt: `<task>
    <task_instructions>Process data using specific format</description>
    <inputs>
      <input name="raw_data">
        <task_instructions>Load and validate input data</description>
        <expected_output>
          Validated data in standard format:
          - Field validations complete
          - Type conversions applied
          - Missing values handled
        </expected_output>
      </input>
    </inputs>
    <expected_output>
      Processed data meeting format requirements:
      - Correct structure
      - Valid field types
      - Complete required fields
    </expected_output>
  </task>`,
  systemPrompt: "Follow strict XML format",
  isManualXML: true,
  disableReparsing: true
};

// Validate template
const validation = taskSystem.validateTemplate(template);

if (!validation.valid) {
  console.warn('Template validation warnings:', validation.warnings);
}

// Find matching tasks
const matches = await taskSystem.findMatchingTasks(
  "analyze peak patterns",
  memorySystem
);

console.log('Found matching tasks:', 
  matches.map(m => ({
    score: m.score,
    type: m.taskType,
    template: m.template.taskPrompt
  }))
);


## Resource Management
typescript
// Configure with resource limits
const taskSystem = new TaskSystem({
  maxTurns: 5,
  maxContextWindowFraction: 0.5,
  systemPrompt: "Resource-constrained execution"
});

try {
  const result = await taskSystem.executeTask(
    "process large dataset",
    memorySystem
  );
} catch (error) {
  if (error.type === 'RESOURCE_EXHAUSTION') {
    console.log('Resource limit exceeded:', error.resource);
    console.log('Usage metrics:', error.metrics);
  }
}


## Global Index Example
typescript
// Minimal memory object focusing on file metadata
const memory = {
  getGlobalIndex() {
    return new Map([
      ['data.txt', 'metadata'],
      ['config.json', 'metadata'],
      ['history.log', 'metadata']
    ]);
  },
  updateGlobalIndex(index) {}
};

// Now we can pass this memory object to the taskSystem
const result = await taskSystem.executeTask("analyze recent changes", memory);


## Specialized Task Types

### Reparse Task Example
typescript
const reparseTemplate: TaskTemplate = {
  taskPrompt: `<task type="reparse">
    <description>Decompose large task into smaller units</description>
    <failed_task>
      <error type="RESOURCE_EXHAUSTION">
        <resource>context</resource>
        <message>Context window limit exceeded</message>
      </error>
      <original_prompt>Process entire codebase</original_prompt>
    </failed_task>
  </task>`,
  systemPrompt: "Decomposition specialist",
  model: "claude-3-sonnet",
  isManualXML: true
};

try {
  const result = await taskSystem.executeTask(
    reparseTemplate.taskPrompt,
    memorySystem,
    "reparse"
  );
} catch (error) {
  console.error('Reparse failed:', error);
}


### Memory Task Example
typescript
const memoryTemplate: TaskTemplate = {
  taskPrompt: `<task type="associative_memory">
    <description>Find relevant context for implementation</description>
    <query>error handling patterns</query>
    <constraints>
      <max_results>3</max_results>
      <relevance_threshold>0.8</relevance_threshold>
    </constraints>
  </task>`,
  systemPrompt: "Context retrieval specialist",
  model: "claude-3-sonnet"
};

const memoryResult = await taskSystem.executeTask(
  memoryTemplate.taskPrompt,
  memorySystem,
  "associative_memory"
);

console.log('Retrieved context:', memoryResult.content);


---

<!-- Example: Sequential Task with Data Accumulation -->
<task type="sequential">
    <description>Process and analyze data</description>
    <context_management>
        <inherit_context>false</inherit_context>
        <accumulate_data>true</accumulate_data>
        <accumulation_format>notes_only</accumulation_format>
    </context_management>
    <steps>
        <task>
            <description>Load dataset</description>
            <inputs>
                <input name="data_file" from="csv_file_path"/>
            </inputs>
        </task>
        <task>
            <description>Filter invalid rows</description>
        </task>
    </steps>
</task>

<!-- Example: Static Director-Evaluator with Script Execution -->
<task type="sequential">
    <description>Static Director-Evaluator Pipeline</description>
    <context_management>
        <inherit_context>none</inherit_context>
        <accumulate_data>true</accumulate_data>
        <accumulation_format>notes_only</accumulation_format>
    </context_management>
    <steps>
        <task>
            <description>Generate Initial Output</description>
        </task>
        <task type="script">
            <description>Run Target Script</description>
            <inputs>
                <input name="director_output" from="last_director_output"/>
            </inputs>
        </task>
        <task>
            <description>Evaluate Script Output</description>
            <inputs>
                <input name="script_output">
                    <task>
                        <description>Process output from target script</description>
                    </task>
                </input>
            </inputs>
        </task>
    </steps>
</task>
</file>
<file path="./components/task-system/impl/xml-processing.md" project="">
# XML Processing Implementation

> **Overview and References:** This document focuses on the Task System's XML processing implementation. For the complete XML schema definition and template guidelines, please refer to [system/contracts/protocols.md](../system/contracts/protocols.md).

## Schema Validation

### Core Schema Requirements
- Based on [Contract:Tasks:TemplateSchema:1.0]
- Required elements:
  * instructions (maps to taskPrompt)
  * system (maps to systemPrompt)
  * model (maps to model)
- Optional elements:
  * inputs with named input definitions
  * manual_xml flag
  * disable_reparsing flag

### Validation Rules
- All required fields must be present
- Input names must be unique
- Boolean fields must be "true" or "false"
- Model must be a valid LLM identifier

## Template Processing

### Template Validation
- Schema conformance checking
- Required field validation
- Type checking for known fields
- Warning generation for non-critical issues

### Manual XML Tasks
- Direct structure usage without reparsing
- Schema validation still applies
- Support for disable_reparsing flag
- No automatic restructuring

## Output Processing

### XML Generation
xml
<!-- Example Output Structure -->
<task type="sequential">
    <description>Task description</description>
    <steps>
        <task>
            <description>Step description</description>
            <inputs>
                <input name="input_name">
                    <task>
                        <description>Input task</description>
                    </task>
                </input>
            </inputs>
        </task>
    </steps>
</task>


### Output Validation
- Structure validation against schema
- Required field presence checking
- Type validation for known fields
- XML well-formedness checking

### Fallback Behavior
- Return unstructured string on parse failure
- Collect and surface warnings
- Maintain original content
- Include parsing error details

## Error Handling

### Validation Errors
typescript
interface XMLError {
  type: 'XML_PARSE_ERROR' | 'VALIDATION_ERROR';
  message: string;
  location?: string;
  violations?: string[];
}


### Recovery Strategies
- Attempt partial content recovery
- Generate fallback string output
- Preserve original content
- Surface all validation issues

## Integration Points

### Template Management
- Load and validate schemas
- Process template definitions
- Handle manual XML flags
- Track template versions

### Task Execution
- Validate output structure
- Handle parsing failures
- Surface warnings appropriately
- Maintain execution context
</file>
<file path="./components/task-system/impl/resource-management.md" project="">
# Resource Management Implementation

> **Further Reading:** For an architectural overview of resource management principles, see [system/architecture/patterns/resource-management.md](../system/architecture/patterns/resource-management.md).

## Core Principles
- No resource usage prediction
- No task decomposition optimization
- Handler-based resource tracking
- Clear resource ownership boundaries

## Turn Counter Management

### Implementation Details
- Per-Handler turn tracking
- Atomic increment operations
- Strict limit enforcement
- No cross-Handler pooling

### Turn Management Rules
- Turn tracking owned by Handler instance
- Turn limit passed during Handler initialization
- Interactive sessions count against turn limits

### Usage Tracking
typescript
// Using canonical ResourceMetrics definition from spec/types.md
// See [Type:ResourceMetrics:1.0]

class TurnCounter {
  private metrics: ResourceMetrics['turns'];
  
  increment(): void {
    if (this.metrics.used >= this.metrics.limit) {
      throw new ResourceExhaustionError('turns');
    }
    this.metrics.used++;
    this.metrics.lastTurnAt = new Date();
  }
}


### Configuration
- Default turn limits from config
- Per-task limit overrides
- Warning at 80% threshold
- Error at limit reached

## Context Window Management

### Size Tracking
- Token-based calculation
- Window size monitoring
- Fraction-based limits
- No content optimization

### Implementation
typescript
// Using canonical ResourceMetrics definition from spec/types.md
// See [Type:ResourceMetrics:1.0]

class ContextManager {
  private metrics: ResourceMetrics['context'];
  
  addContent(content: string): void {
    const tokens = this.countTokens(content);
    if (this.metrics.used + tokens > this.metrics.limit) {
      throw new ResourceExhaustionError('context');
    }
    this.metrics.used += tokens;
    this.metrics.peakUsage = Math.max(this.metrics.peakUsage, this.metrics.used);
  }
}


### Monitoring
- Continuous token tracking
- Peak usage recording
- Threshold warnings
- Limit enforcement

## Resource Cleanup

### Handler Termination
- Clean session shutdown
- Resource accounting completion
- Metric collection
- No state preservation

### Memory Management
- Context cleanup
- Reference clearing
- Memory release
- State invalidation

## Integration Points

### Handler Integration
- Resource initialization
- Usage monitoring
- Limit enforcement
- Cleanup coordination

### Memory System
- Read-only access
- No state maintenance
- Direct interface usage
- Context boundaries

### Error Handling
- Resource exhaustion detection
- Clean termination
- Metric reporting
- State cleanup
</file>
<file path="./components/task-system/impl/design.md" project="">
# Implementation Design

## Terminology and References

 - **Handler** and **Evaluator** definitions are standardized in [spec/types.md](../spec/types.md).
 - XML schema definitions are available in [system/contracts/protocols.md](../system/contracts/protocols.md).
 - For detailed resource tracking implementation (including turn counter and context window monitoring), see [resource-management.md](./resource-management.md).
 - For XML processing details (parsing, validation, and fallback behavior), refer to [xml-processing.md](./xml-processing.md).

## Handler Implementation
### Session Management Strategy
- One Handler per task execution
- Create new Handler instance per executeTask call
- Configure with immutable resource limits
- Set system prompt during initialization
- Clean session termination on completion
  
### Resource Tracking Implementation
- Turn counter per Handler
- Context window size monitoring
- Token usage tracking
- Resource limit enforcement
- No cross-Handler resource sharing

### Error Propagation Design
- Standard error type system
- Immediate propagation on detection
- Clean resource release
- No retry attempt handling
- Complete error context preservation

### Interactive Session Support
- Input detection capabilities
- Agent-controlled input requests
- Resource tracking during interaction
- Input timeout handling
- Cancellation support

## Template Management
### Storage Implementation
- XML file-based storage
- Disk-based persistence
- Directory organization by type
- Template versioning support
- Schema validation enforcement
  
### Validation Implementation
- Basic XML structure validation
- Schema conformance checking
- Warning generation for issues
- Template field validation
- Model availability checking
  
### Matching Algorithm Design
- Scoring based on prompt results
- Top-N candidate selection
- Separate matching for human input vs AST
- Score normalization
- Clear ordering requirements
  
### XML Processing Details
- Lenient parsing with fallback
- Warning collection
- Graceful degradation
- Partial parsing support
- Clear error locations

## Resource Management

The Task System enforces resource limits via a per‑Handler turn counter and context window monitoring. For the complete low‑level implementation (including code examples and configuration details), please refer to [resource-management.md](./resource-management.md).
  
### Context Window Management
- Token counting approach
- Size limit enforcement
- No optimization strategy
- Window usage monitoring
- Clear limit boundaries
  
### Limit Enforcement Strategy
- Immediate termination on violation
- Resource exhaustion error generation
- Clean session cleanup
- Resource usage reporting
- Clear violation metrics
  
### Error Detection Mechanisms
- Resource limit monitoring, progress tracking, output and XML structure validation, and input validation.

### Environment Management

#### Output Slot Management
The design now leverages last_evaluator_output as the single persistent feedback variable. The function prepareContinuationEnv(currentEnv) constructs a new environment retaining only last_evaluator_output, ensuring that all other keys are cleared on continuation.

On continuation, the evaluator clears all environment variables except for last_evaluator_output. This reset is achieved via the prepareContinuationEnv helper, which copies only last_evaluator_output from the current environment.

### Script Execution Implementation
The system now supports executing external scripts as part of a static director-evaluator workflow. When a task of type "script" is encountered, the Handler:
- Detects the "script" task type.
- Executes the specified external command (e.g. a bash script).
- Captures the command's standard output, error output, and exit code.
- Passes the script's output to the subsequent evaluator task.

During script execution, the evaluator invokes the script task, captures its outputs (stdout, stderr, and exitCode), and then wraps these into an EvaluationResult. This result is stored in last_evaluator_output, which is later used by the Director upon resuming the sequence.

This design ensures that the director's output flows seamlessly through the script execution step before final evaluation.

## Integration Points
### Memory System Interaction
- Uses Anthropic's computer use tools for file operations.
- Read-only access.
- No state maintenance.
- Clear context boundaries.
- Standard memory structure.
  
### Compiler Integration
- Task parsing services
- XML validation
- Schema conformance
- Error surfacing
- Validation feedback
  
### Evaluator Support
- Error surfacing
- Reparse template support
- No retry management
- State preservation
- Recovery guidance
  
### LLM Session Management
- Handler encapsulation
- Resource tracking
- Model selection support
- Clean termination
- Session isolation
</file>
<file path="./components/task-system/spec/requirements.md" project="">
# Task System Requirements

This document outlines the high-level functional and non‑functional requirements for the Task System.

## Key Requirements Summary

1. **XML-based Task Templates:**  
   - All task templates must conform to [Contract:Tasks:TemplateSchema:1.0].  
   - Both LLM‑generated and manual XML structures are supported, with options to disable reparsing.

2. **Handler and Resource Management:**  
   - One Handler is created per task execution with immutable configuration and strict resource tracking.
   - Resource limits (turn counts, context window) are enforced by the Handler. For details, see [Pattern:ResourceManagement:1.0].

3. **Task Matching:**  
   - The system matches natural language inputs and AST nodes to candidate task templates (up to 5 candidates) using numeric scoring.

4. **Memory Integration:**  
   - The Task System uses a read‑only Memory System interface for context retrieval. See [Interface:Memory:3.0].

5. **Script Execution Support:**  
   - XML schema extensions support specifying external command details for script tasks. Clear input/output contracts must be defined.

For detailed operational behavior, see the Behaviors document. Additional system‑level details are available in the central contracts and architecture documents.

## See Also

 - [Task System Behaviors](behaviors.md)
 - [Task System Interfaces](interfaces.md)
 - System-level contracts: [Contract:Tasks:TemplateSchema:1.0] and [Pattern:ResourceManagement:1.0]
</file>
<file path="./components/task-system/spec/behaviors.md" project="">
# Task System Behaviors

This document describes the runtime behaviors of the Task System.

## Overview

The Task System is responsible for managing LLM task execution, including:
 - Template matching and management,
 - Lifecycle handling for Handlers,
 - XML processing with graceful degradation, and
 - Error detection and recovery.

## Key Behavior Highlights

1. **Template Management:**  
   - Task templates are stored and validated against the XML schema defined in [Contract:Tasks:TemplateSchema:1.0].  
   - The system matches both natural language inputs and AST nodes to candidate templates (up to 5 candidates), using numeric scoring.

2. **Handler Lifecycle:**  
   - A new Handler is created for each task execution with an immutable configuration.
   - The Handler enforces resource limits (turn counts, context window limits) as described in [Pattern:ResourceManagement:1.0].

3. **XML Processing:**  
   - Basic structural validation is performed, with warnings generated for non‑critical issues.
   - In cases of partial XML parsing failure, the original content is preserved and error details are included in the task notes.

4. **Error Handling:**  
   - Errors such as RESOURCE_EXHAUSTION and TASK_FAILURE are surfaced according to the rules defined in [Pattern:Error:1.0].
   - The Evaluator delegates error recovery (e.g., reparse tasks) and includes partial outputs when available.

## See Also

 - [Task System Requirements](requirements.md)
 - [Task System Interfaces](interfaces.md)
 - System-level error handling: [Pattern:Error:1.0]

### Interactive Sessions
- Handler monitors LLM responses for input requests
- No special task type or mode required
- Agent controls when input is needed
- Input Flow:
  
LLM Output -> Handler Detects Request -> onRequestInput Called -> 
  User Input Received -> Continue Conversation

- Same resource tracking as normal conversation
- Input interactions count against turn limits
- Context window includes all interaction history

### XML Processing
- Basic structural validation only
- Warning generation for validation issues
- Lenient output parsing with fallback
- Graceful handling of partially valid XML
- Support for manual XML task flag

## Task Execution

### Standard Task Execution
- Process tasks using appropriate templates
- Return both output and notes sections in TaskResult structure
- Surface errors for task failure or resource exhaustion
- Support specialized execution paths for reparsing and memory tasks
- Implement lenient XML output parsing with fallback to single string
- Generate warnings for malformed XML without blocking execution
- Include 'data usage' section in task notes as specified by system prompt

### Task Template Matching

#### Human Input Matching
- Input: Natural language text + initial environment
- Process:
  - Uses matching specialized task from library
  - Considers provided files in environment
  - No access to previous executions/history
- Output: 
  - Up to 5 highest-scoring templates
  - Each match includes numeric score and template
  - Templates ordered by descending score

#### AST Node Matching
- Input: Single AST node
- Process:
  - Uses node-specific matching task
  - Only considers node-level context
  - No traversal of parent/child nodes
- Output:
  - Up to 5 highest-scoring templates
  - Each match includes numeric score and template
  - Templates ordered by descending score

### Specialized Task Types

#### Reparse Tasks
- Triggered by:
  - Resource exhaustion errors
  - Invalid output errors
  - Progress failure errors
- Uses specialized templates from separate directory
- Returns new task structure or alternative approach

#### Memory Tasks
- Direct memory system access
- Uses associative matching templates
- Returns relevant context selections

## Memory System Integration

### File Operations
- Uses Anthropic's computer use tools:
  * computer_20241022
  * text_editor_20241022
  * bash_20241022
- No direct file operation interface
- Managed through Anthropic's tool use system
- See Anthropic documentation for details

### Context Management
- Context accessed via async getContext/updateContext
- File metadata accessed via GlobalIndex
- Existing context preserved during task execution
- Structure/parsing handled by associative memory tasks

### State Management
- No complex file metadata tracking
- Minimal state maintenance between tasks
- Clear task execution boundaries
- Simple file modification tracking

## File Operations
- Uses Anthropic's computer use tools:
  * computer_20241022
  * text_editor_20241022
  * bash_20241022
- No direct file operation interface
- Managed through Anthropic's tool use system
- See Anthropic documentation for details

## Context Management Delegation

The Task System delegates **all context management** to the Evaluator. In other words:
1. The Task System's role is primarily to define task structure (sequential, map, reduce, etc.) and signal the Evaluator to execute steps.
2. The Evaluator decides how and when to call MemorySystem.getRelevantContextFor().
3. The Handler remains focused on resource tracking (turns, tokens).
4. No direct context accumulation logic occurs in the Task System itself.

## Error Handling

### Error Detection and Response

#### Resource Exhaustion
- Handler detects limit violations
- Immediate task termination
- Surfaces through standard error type
- Resource accounting completion
- Clean Handler termination
- No retry attempts

#### Invalid Output
- Structural validation failure
- Format validation errors
- No semantic validation
- Preserves partial outputs when useful
- Returns both output and notes sections
- May trigger reparse task

#### Progress Failure
- Handler detects stalled execution
- Task-specific progress indicators
- No internal progress tracking
- May trigger alternative approach
- State preserved in error response
- No automatic retry

#### XML Validation
- Immediate failure on invalid structure
- No warning collection
- Clear error messages
- Location information when available
- May trigger reparse if not disabled

### Error Response

#### Error Surfacing
- Uses standard error type system (see types.md)
- Includes relevant task notes
- Preserves partial outputs when useful
- Includes resource metrics where applicable
- Clear error messages and locations

#### Handler Cleanup
- Clean termination of LLM session
- Resource accounting completion
- No state preservation
- Context window cleanup
- Turn counter finalization

#### Recovery Delegation
- No retry attempts
- Delegates to evaluator
- Provides complete error context
- Includes notes for recovery guidance
</file>
<file path="./components/task-system/spec/qa.md" project="">
# Task System FAQ

This FAQ provides concise answers to common questions about the Task System.

**Q: How many Handlers should be created per task execution?**  
A: One Handler per task execution. See [Task System Requirements](requirements.md) for details.

**Q: Who is responsible for sending prompts to the LLM?**  
A: The Handler is responsible for all LLM interactions.

**Q: How are resource limits enforced?**  
A: Resource limits are passed to the Handler at initialization and enforced during execution. For more details, see [Task System Behaviors](behaviors.md).

For additional questions, please refer to system‑level documentation or contact the Task System maintainers.
</file>
<file path="./components/task-system/spec/interfaces.md" project="">
# Task System Interfaces

// For core type definitions (e.g. TaskResult, TaskTemplate, TaskType, AtomicTaskSubtype),
// please refer to components/task-system/spec/types.md.

import { MemorySystem } from "../../memory/api/interfaces";

/**
 * TaskSystem Interface
 * 
 * Provides methods to execute tasks, validate templates, and find matching templates.
 */
export interface TaskSystem {
    executeTask(
        task: string,
        memory: MemorySystem,
        taskType?: "atomic" | "sequential" | "reduce" | "script"
    ): Promise<TaskResult>;

    validateTemplate(template: TaskTemplate): boolean;
    
    findMatchingTasks(
        input: string,
        context: MemorySystem
    ): Promise<Array<{
        template: TaskTemplate;
        score: number;
        taskType: "atomic" | "sequential" | "reduce" | "script";
    }>>;
    registerTask(taskDef: TaskDefinition): void;
    executeFunctionCall(funcCall: FunctionCall, env: Environment): Promise<any>;
export interface Environment {
    bindings: Record<string, any>;
    outer?: Environment;
    /**
     * Perform a lexical lookup for varName.
     * Returns the value if found; otherwise, throws an error.
     */
    find(varName: string): any;
    executeScriptTask(scriptTask: ScriptTask, env: Environment): Promise<ScriptTaskResult>;
}

// Handler interface details are maintained in external documentation.
 * Memory management interface focused on metadata
 */
type FileMetadata = string;

type GlobalIndex = Map<string, FileMetadata>;

type FileMatch = [string, string | undefined];

interface AssociativeMatchResult {
    context: string;      // Unstructured data context
    matches: FileMatch[]; // Relevant file matches
}

interface MemorySystem {
    // Get global file metadata index
    getGlobalIndex(): Promise<GlobalIndex>;
    
    // Update global file metadata index
    updateGlobalIndex(index: GlobalIndex): Promise<void>;
}
### Handler Interface
typescript
/**
 * Types specific to Handler interface
 */
interface HandlerConfig {
    maxTurns: number;
    maxContextWindowFraction: number;
    defaultModel?: string;
    systemPrompt: string;
}

/**
 * LLM interaction interface
 * Uses [Type:TaskSystem:ResourceMetrics:1.0], [Type:TaskSystem:ResourceLimits:1.0]
 */
interface Handler {
    /**
     * Execute a prompt with the LLM
     * @param systemPrompt - System-level context and instructions
     * @param taskPrompt - Task-specific input
     * @returns Promise resolving to LLM response
     */
    executePrompt(
        systemPrompt: string,
        taskPrompt: string
    ): Promise<string>;

    /**
     * Callback for handling agent input requests
     * @param agentRequest - The agent's request for user input
     * @returns Promise resolving to user's input
     */
    onRequestInput: (agentRequest: string) => Promise<string>;
}
</file>
<file path="./components/task-system/spec/types.md" project="">
# Task System Types

// Core task types used across the Task System.
export type TaskType = "atomic" | "sequential" | "reduce" | "script";
export type AtomicTaskSubtype = "standard" | "subtask";

// Task execution status.
export type ReturnStatus = "COMPLETE" | "CONTINUATION" | "FAILED";

// Core interfaces:

export interface TaskResult {
    content: string;
    status: ReturnStatus;
    /**
     * Optional free-form description used for dynamic evaluation template selection.
     */
    criteria?: string;
    notes: {
        dataUsage: string;
        [key: string]: any;
    };
}

/**
 * Represents a sequential task which has its own context management block
 * and multiple steps of subtasks.
 */
interface SequentialTask extends BaseTask {
    type: 'sequential';
    contextManagement: ContextManagement;
    steps: Task[];
}

/**
 * A general-purpose task result, now updated to store optional string notes
 * or structured data. This may override or augment the existing TaskResult
 * if needed, but is shown here as the revision plan states.
 */
interface RevisedTaskResult {
    content: string;
    notes: string;
}

/**
 * Defines context inheritance and accumulation policies for tasks.
 * The new model replaces a boolean inheritContext flag with an enumeration:
 *   - "full" for complete inheritance,
 *   - "none" for no inheritance, and
 *   - "subset" for selective inheritance.
 */
export interface ContextManagement {
    inheritContext: 'full' | 'none' | 'subset';
    accumulateData: boolean;
    accumulationFormat: 'full_output' | 'notes_only';
}

/**
 * Input structure for Memory System context requests
 */
interface ContextGenerationInput {
    previousOutputs?: string;   // Outputs accumulated from previous steps
    inheritedContext?: string;  // Context inherited from parent tasks
    taskText: string;          // The primary task description or request
}

interface TaskTemplate {
    readonly taskPrompt: string;      // Maps to <instructions> in schema
    readonly systemPrompt: string;    // Maps to <system> in schema
    readonly model: string;           // Maps to <model> in schema
    readonly inputs?: Record<string, string>;
    readonly isManualXML?: boolean;   // Maps to <manual_xml> in schema
    readonly disableReparsing?: boolean; // Maps to <disable_reparsing> in schema
    readonly atomicSubtype?: AtomicTaskSubtype;
}


## AST Types

export interface FunctionCall extends ASTNode {
    funcName: string;
    args: ASTNode[];
}
typescript
interface OperatorSpec {
    type: TaskType;
    subtype?: AtomicTaskSubtype;
    inputs: Record<string, string>;
    disableReparsing?: boolean;
}

interface ASTNode {
    type: string;
    content: string;
    children?: ASTNode[];
    metadata?: Record<string, any>;
    operatorType?: TaskType;
}


export interface EvaluationResult {
    success: boolean;
    feedback?: string;
}

export interface DirectorEnv extends Environment {
    last_evaluator_output: string | null;
    // Other variables are cleared on continuation
}

export interface Environment {
    bindings: Record<string, any>;
    outer?: Environment;
    /**
     * Perform a lexical lookup for varName.
     * Returns the value if found; otherwise, throws an error.
     */
    find(varName: string): any;
}

function prepareContinuationEnv(currentEnv: Environment): Environment {
    return new Environment({
        last_evaluator_output: currentEnv.get('last_evaluator_output')
    });
}

function storeEvaluatorResult(result: TaskResult, env: Environment): void {
    env.set('last_evaluator_output', result.content);
    env.clearExcept(['last_evaluator_output']);
}

## Resource Management Types

export interface TaskDefinition {
    name: string;                     // Unique task identifier
    isatomic: boolean;
    type: TaskType;                   // e.g., "atomic" or "sequential"
    subtype?: string;                 // Optional subtype, e.g., "director", "evaluator", etc.
    metadata?: Record<string, any>;   // Parameter schemas, return specs, etc.
    astNode: ASTNode;                 // Parsed AST for the task
}

export class TaskLibrary {
    private tasks: Map<string, TaskDefinition>;

    constructor() {
        this.tasks = new Map();
    }

    public registerTask(taskDef: TaskDefinition): void {
        if (this.tasks.has(taskDef.name)) {
            throw new Error(Task ${taskDef.name} is already registered.);
        }
        this.tasks.set(taskDef.name, taskDef);
    }

    public getTask(name: string): TaskDefinition {
        const taskDef = this.tasks.get(name);
        if (!taskDef) {
            throw new Error(Task ${name} not found in TaskLibrary.);
        }
        return taskDef;
    }
}
typescript
interface HandlerConfig {
    maxTurns: number;
    maxContextWindowFraction: number;
    defaultModel?: string;
    systemPrompt: string;
}

/**
 * Represents the result of executing a script task.
 */
interface ScriptTaskResult extends TaskResult {
    stdout: string;
    stderr: string;
    exitCode: number;
}

interface ResourceMetrics {
    turns: {
        used: number;
        limit: number;
        lastTurnAt: Date;
    };
    context: {
        used: number;
        limit: number;
        peakUsage: number;
    };
}

interface ResourceLimits {
    maxTurns: number;
    maxContextWindow: number;
    warningThreshold: number;
    timeout?: number;
}

/**
 * EvaluationInput interface clarifies that target_content refers to the original output from the Director task.
 * The raw outputs from the script (stdout, stderr, exit_code) are passed directly without preprocessing.
 */
interface EvaluationInput {
    target_content: string; // The original output from the Director task.
    stdout?: string;        // Raw standard output from the script.
    stderr?: string;        // Raw standard error output from the script.
    exit_code?: number;     // Script exit code (non-zero exit codes do not block evaluation but inform decision-making).
}



## Error Types
typescript
type TaskError = 
    | { 
        type: 'RESOURCE_EXHAUSTION';
        resource: 'turns' | 'context' | 'output';
        message: string;
        metrics?: { used: number; limit: number; };
    }
    | { 
        type: 'INVALID_OUTPUT';
        message: string;
        violations?: string[];
    }
    | { 
        type: 'VALIDATION_ERROR';
        message: string;
        path?: string;
        invalidModel?: boolean;
    }
    | { 
        type: 'XML_PARSE_ERROR';
        message: string;
        location?: string;
    };


## Validation Types
typescript
interface ValidationResult {
    valid: boolean;
    warnings: string[];
    errors?: string[];
    location?: string;
}

interface XMLValidation extends ValidationResult {
    xmlValid: boolean;
    schemaValid: boolean;
    parsedContent?: any;
}

interface TemplateValidation extends ValidationResult {
    templateValid: boolean;
    modelValid: boolean;
    inputsValid: boolean;
}


## Cross-References
- For XML schema definitions, see [Contract:Tasks:TemplateSchema:1.0] in protocols.md
- For interface implementations, see spec/interfaces.md
- For public API surface, see api/interfaces.md

## Notes
1. All types supporting the core task system are defined here
2. Public API types are a subset of these definitions
3. Implementation details for memory system metadata types pending definition
4. All resource limits and metrics are enforced per-Handler
</file>
<file path="./components/task-system/README.md" project="">
# Task System Component

## Overview

The Task System orchestrates LLM task execution through structured XML templates and handlers. It proovides template-based task definition, resource tracking, and an XML-based interface with the LLM.

## Core Architecture

The system manages task execution through isolated Handler instances, with one Handler per task to enforce resource limits and manage LLM interactions. 

Task definitions use an XML-based template system that supports both manual and LLM-generated structures. 

## Core Interface

typescript
interface TaskSystem {
    executeTask(
        task: string,
        context: MemorySystem,
        taskType?: TaskType
    ): Promise<TaskResult>;

    validateTemplate(template: TaskTemplate): boolean;
    
    findMatchingTasks(
        input: string,
        context: MemorySystem
    ): Promise<Array<{
        template: TaskTemplate;
        score: number;
        taskType: TaskType;
    }>>;
}


## Task Types and Execution

The system supports several task types for different execution patterns. Atomic tasks provide direct LLM execution with resource tracking and output validation. Sequential tasks enable ordered execution with context management between steps. Reduce tasks handle iterative data processing with accumulator management. Script tasks support external command execution with output capture and evaluation flow integration.

Each task type can specify its context management requirements through XML configuration:

xml
<task>
    <description>Task description</description>
    <context_management>
        <inherit_context>none|full|subset</inherit_context>
        <accumulate_data>true|false</accumulate_data>
        <accumulation_format>notes_only|full_output</accumulation_format>
    </context_management>
    <inputs>
        <input name="input_name" from="source_var"/>
    </inputs>
</task>


## Integration and Dependencies

The Task System integrates with several core components. It uses the Memory System for context access and management, Handler Tools for file and system operations, the Compiler for task parsing and transformation, and the Evaluator for error recovery and task decomposition. These integrations enable comprehensive task execution while maintaining clean component boundaries.

## Usage

Here's how the Task System would be instantiated:

typescript
const taskSystem = new TaskSystem({
    maxTurns: 10,
    maxContextWindowFraction: 0.8,
    systemPrompt: "Default system prompt"
});

// Execute a task
const result = await taskSystem.executeTask(
    "analyze data",
    memorySystem
);

// Validate a template
const validation = taskSystem.validateTemplate({
    taskPrompt: "<task>...</task>",
    systemPrompt: "System context",
    model: "claude-3-sonnet",
    isManualXML: false
});


## Error Handling

The system handles several error types during execution, including resource exhaustion (for turns, context, or output), invalid output structure, XML parsing or validation errors, and general task execution failures. Each error type includes relevant context and metrics to aid in recovery and debugging. Errors will be surfaced to the Evaluator, which will use them for control flow.

## Resource Management

Resource management follows strict constraints with fixed context window sizes and limited turn counts. The system ensures clean resource release after task execution and prevents cross-Handler resource sharing. Handler configuration controls these limits:

typescript
interface HandlerConfig {
    maxTurns: number;
    maxContextWindowFraction: number;
    defaultModel?: string;
    systemPrompt: string;
}


For detailed implementation specifications and patterns, refer to the component-level documentation and system contracts.
</file>
<file path="./components/task-system/api/interfaces.md" project="">
# Task System Public API

/**
 * Note: The TaskResult returned by executeTask includes an optional "criteria" field,
 * which is a free-form description provided by the Director task for dynamic evaluation
 * template selection via associative matching.
 */

## References

- Core Types: See [Type:TaskSystem:1.0] (/components/task-system/spec/types.md)
- Implementation: See /components/task-system/spec/interfaces.md
- XML Schema: See [Contract:Tasks:TemplateSchema:1.0] (/system/contracts/protocols.md)

typescript
/**
 * Public API Surface
 * All types imported from [Type:TaskSystem:1.0]:
 * - TaskTemplate
 * - TaskResult 
 * - TaskType

/** 
 * For the full Handler interface definition, see [Interface:Handler:1.0] in spec/interfaces.md
 */

/**
 * Primary task execution interface
 * Uses [Type:TaskSystem:TaskType:1.0] and [Type:TaskSystem:TaskError:1.0]
 */
interface TaskSystem {
    executeTask(
        task: string,
        context: MemorySystem,
        taskType?: TaskType
    ): Promise<TaskResult>;

    validateTemplate(template: TaskTemplate): boolean;
  
    findMatchingTasks(
        input: string,
        context: MemorySystem
    ): Promise<Array<{
        template: TaskTemplate;
        score: number;
        taskType: TaskType;
    }>>;
}

/**
 * Memory System interface for task execution
 * @see [Interface:Memory:3.0] (`/components/memory/api/interfaces.md`)
 */
import { MemorySystem, GlobalIndex, FileMatch } from '@/components/memory/api/interfaces';

</file>
<file path="./components/compiler/README.md" project="">
# Compiler Component

## Purpose
The compiler handles translation and transformation of tasks into executable formats.

## Requirements

### Task Understanding
- Parse task requirements and constraints from natural language
- Identify task type and complexity  
- Validate instruction completeness

### XML Schema Requirements
- Define valid operation types
- Specify input/output formats
- Support task validation

### AST Structure  
- Node type definitions
- Tree validation rules
- Traversal requirements

### Validation Rules
- Input format validation
- Schema compliance
- AST structure validation

## Integration Points
[See existing interfaces documentation]
</file>
<file path="./TODOS.md" project="">
# Critical Path TODOs - Corrected Status

## Interface Consolidation ⚠️ BLOCKING

### Completed (✓)
1. Memory System interface version defined [Interface:Memory:2.0]
2. File content type handling standardized (Handler tools)
3. Unified storage approach defined in ADR
   - Memory System: metadata and context
   - Handler tools: file access
   - Clear separation of concerns

### Still Needed (❌)
1. Update Task System Implementation
   - Update components/task-system/spec/interfaces.md to use [Interface:Memory:2.0 or 3.0] consistently
   - Remove or reconcile old/deprecated memory structure definitions
   - Update dependent interfaces to unify environment usage
   - Ensure references to "Memory:2.0" vs "Memory:3.0" are consistent across docs

2. Version Number Alignment
   - Verify all cross-references use correct versions
   - Update any outdated references to [Interface:Memory:2.0 or 3.0]
   - Ensure consistent version numbering across documentation

   - Confirm final chosen memory interface version is used everywhere

## Resource and File Management ⚠️ BLOCKING

### Completed (✓)
1. File tracking ownership decided
   - Memory System owns metadata index
   - Handler tools own file access
   - Clear delegation pattern defined

2. Resource tracking responsibilities documented
   - Handler owns resource limits
   - Memory System handles metadata only
   - Clear separation established

3. File access patterns defined
   - Handler tools for file operations
   - Memory System for metadata
   - Clean separation documented

### Still Needed (❌)
1. Interface Updates
   - Update Task System interfaces to reflect current patterns
   - Remove or replace any deprecated memory system fields
   - Add missing Handler tool interfaces if needed (e.g., writeFile if required)
   - Ensure consistency across doc references
   - Confirm we only store file metadata in Memory System (and use Handler for actual I/O)
   - Re-check that partial references to "getContext()" align with new approach

## Next Steps
1. Focus on updating Task System interfaces
2. Complete version number verification
3. Update any remaining documentation to reflect current architecture

## Notes
- Most architectural decisions are complete and documented
- Main work needed is implementation alignment
- Focus should be on updating Task System to match current architecture

## Feature Implementation

### Completed Features (✓)
1. Memory Component Separation
   - Full component definition
   - Clear interfaces
   - Integration documentation (✓)

2. Task Type System
   - Basic types defined
   - Subtask support
   - Map operator implementation

### In-Progress Features (🔄 / Partially Implemented)
1. Context Management
   Priority: High
   Dependencies: Interface Consolidation
   - [x] Document best practices (ADR 004)
   - [x] Define efficient subtask patterns (sequential)
   - [ ] Extend inherit_context to map/reduce
   - [x] Provide partial-result guidance (via accumulation_format)
   - [x] Consolidate environment usage:
       1. The memory system instance
       2. Accumulated data from sequential steps
       3. Associatively retrieved data
   - [x] Add context reuse mechanisms (via context_management)
   - [ ] Update error taxonomy for context failures

2. Architecture Documentation
   Priority: Medium
   Dependencies: None
   - [ ] Standardize patterns across components
   - [ ] Add cross-component documentation
   - [ ] Improve self-similarity in structure

### Unimplemented Features (❌)
1. Task Execution Enhancements
   Priority: High
   Dependencies: Context Management
   - [ ] "Rebuild-memory" or "clear-memory" flag in templates
   - [ ] Task continuation protocol
   - [ ] Summary output handling in evaluator

2. Agent Features
   Priority: Medium
   Dependencies: Interface Consolidation
   - [ ] Agent history storage
   - [ ] REPL implementation - the handler / task system needs to give the llm a 'question answering' tool. 
   - [ ] Multi-LLM support

## Documentation Updates

### Interface and Implementation Documentation
Priority: High
Dependencies: Interface Consolidation
- [ ] Update Task System specs to [Interface:Memory:2.0 or 3.0]
- [ ] Update API documentation
- [ ] Update component READMEs
- [ ] Document subtask usage (map, reduce, sequential) with context
- [ ] Provide best practices for partial output vs. re-parse
- [ ] Align final references to single Memory interface version
- [ ] Add context management practices
- [ ] Document subtask patterns

### Implementation Documentation
Priority: Medium
Dependencies: Feature implementations
- [ ] File handling patterns
- [ ] Resource tracking
- [ ] Integration examples
- [ ] Validation guidelines
- [ ] Evaluator behavior

### Contract Documentation
Priority: High
Dependencies: Interface Consolidation
- [ ] Update [Contract:Integration:TaskMemory:2.0]
- [ ] Align all version numbers
- [ ] Update cross-references
- [ ] Add new feature contracts

## Review & Testing
Priority: Medium
Dependencies: Individual feature completion
- [ ] Interface compatibility verification
- [ ] Version number audit
- [ ] Cross-reference validation
- [ ] Implementation completeness check

## Notes
- All interface changes must maintain backward compatibility
- Documentation should be updated alongside implementation
- Version numbers must be kept consistent
- Breaking changes require major version increments
- Dependencies should be clearly marked

### Other Issues Still Requiring Design Feedback
1. Handling Partial Results on Context-Generation Failure
The patch mentions “context generation fails,” but does not fully define whether partial results or intermediate step data should be preserved or retried. Deciding on partial result preservation or an automatic re-parse is an open design item.

2. Extending inherit_context to Other Operators  
   We added inherit_context only to the <task type="sequential"> element. Whether or not other operators (like reduce or any derived "map" pattern) should support the same attribute (and how it interacts with parallel or iterative steps) remains to be addressed.

3. Clarification of How Context Generation Tasks Are Triggered
Although references to a “context generation task” or “associative matching” were updated, the exact mechanism—i.e. how the evaluator decides to invoke associative matching, or how that is described in the DSL—still needs more explicit design.

4. Error Taxonomy for Context Issues
We have flagged that a “context generation failure” could be a Task Failure or might need its own subcategory. Determining whether this should remain a generic “task failure” or become a separate error type is pending further design discussion.


### other other todos 
- allow the agent to store and recall memory files (special subdir, markdown format, inc timestamps, can be instantiated / loaded / managed by memory system)
- do we need separate context inheritance handling for the reduction and accumulation operations in reduce?
- allow simple chaining - should be supportable through nesting but it might make more sense to make it a sequential pattern so that we can use the sequential context management features
- the agent / llm interface (which will be accessed by the handler) should support a basic set of tools in a fairly model-agnostic way. for example, for anthropic models interactions that use 'file edit' or 'shell' tools will use the underlying anthropic-specific computer use mechanisms. at the beginning of a session, the handler should be able to select one or more abstract tool types without knowing about these details
- function definition / call primitives / syntax / task types. A function is a named procedure that can be either compound or atomic. Will need to define some language syntax and maybe a repl in which things can be defined and run interactively. Could be a lisp dialect. New surface syntax on top of the existing task structure should be good enough. Maybe there's an existing python impl of a lisp parser that i can reuse. alternatively, could stick with xml for now and deal with language syntax / parsing later. 
- write some user stories. example 0: o1 to generate impl plan; sonnet to incrementally take and incorporate feedback; o1 to revise the updated plan; sequential sonnet (preceded by cheap model to break the steps into an explicit list) or zero shot o1 to generate diffs for all of the files. example 1: the inconsistency resolution workflow that i wrote down a while ago. example 2: something about generating documentation / building an index (e.g. mermaid diagram). 
- at some point (maybe not part of mvp), we'll want the agent to be able to request files to be added or removed to its context. this might not be necessary for anthropic models (computer use gives them direct access), but maybe we want that for other models. (on the other hand, limiting oai models to 'pure function' roles might be an ok approach too).
- might want to revisit how task outputs are parsed / not parsed. if we want the evaluator to support bindings and backreferences then we might want to support named return values. this would bridge the llm blob-level output with evaluator / DSL-level variable bindings, which could then be passed as arguments to downstream tasks. This means also changing the template format so that it includes an (optional) output spec. 
- use LLM to optimize template format?
- review adr 005, there should be 4 context-generation combinations for sequential taskss but I think we're only handling 3
- use the messages api for the llm interaction: https://docs.anthropic.com/en/api/messages
- figure out how subtasks spawned by the task system will work. If we don't include it in mvp then the evaluator might need to be more flexible. for example, a task's 'notes' section might include instructions to spawn another task that runs tests against its generated code. The evaluator would then have to dynamically generate a child node, using the 'notes' text as input to the task-matching procedure, and then run it. If the subtask fails then the parent task should also fail / be retried (Using failure information as feedback). This would require (1) making the task matching procedure more flexible and (2) changing the evaluator's control flow, but it would be simpler to do than full reparsing. Maybe not part of mvp but something like this is prob necessary for real agentic behavior. 
- replace the 'partial output' concept with a return status, which could include something like 'continuation' for tasks that want to spawn a subtask. the control flow would be decided by the combination of return status and error info.
- llm output-to-evaluator level bindings / variables can be used to pass discrete values like file paths between tasks, which would be useful to implement something like the director-evaluator pattern
- Add the Lispy stuff to docs if they're not already there
- add aider code blocks to the prompts
- think about how to use aider as a coding / file editing backend and for passing information between tasks (via files). It might make sense to go through files bc a lot of the time task outputs will be run or referred to later. There could be a subset of templates that 'know' how to format aider inputs (essentially using tool calls).
- need to clarify the difference between tool calls and subtasks (the
essential difference should be that tool calls are either deterministic
or have to pass through a rigid api, whereas subtasks are llm to llm
interactions. Having the llm call aider kind of blends the two. I think
it'd be better as a subtask, bc in any case some subtasks will require
conforming to an outupt signature.
- anthropic computer use could be replaced by evaluator subtasks, but it'd involve more boilerplate with subprocess.run and all that at 
the DSL interpreter level and it might be annoying to have to handle a special case. though i guess the output xml could have a universal
optional 'execute this script' field that always gets run if it's present
- maybe it doesn't make sense to have both 'continuation' and tool use
- think about how feedback will go from subtask to parent (tool use response?)
- there should be an option, for sequential task, for the associative matching to just extract a subset of the parent context
- let's have the director evaluator pattern be a special case of a task-subtask
- 'genetic' behavior, such as multiplle tries and selecting the best one


Loose ends:
- need to specify how bash commands will be called in between the director and evaluation steps of the director-evaluator pattern.
- output of the evaluation bash script needs to go to evaluator
- let llm design more speculatively. then feedback in the form of correctinng arch decisions i don't like.
- have reasoning model address list of underspecified parts, let it take initiative on decisions and then feed back on that
- try the goat workflow
- distill the director-evaluator .py into an arch component. check how it manages context over multiple  turns
- might want to remove the stuff about anthropic computer use, since we're taking a more model agnostic approach instead
- clarify when director-evaluator involves running bash and when not, and how to handle the not case

- How does the evaluator output go back to the director? (when the director is running in continuation mode)
- need 'define' or 'let'
- passing through questions
- model temperature (and model selection in general -- how are we going to handle this?)
- how would we approach multiple tries -> selection of the best candidate result? I'm thinking something like a many-to-one version of the director-evaluator pattern. Essentially: many tries in parallel (with sandboxing so that the instances don't interfere with one another) --> evaluation and selection of the 'best' outcome.
- Bring the evaluator impl in line with Lispy's approach, such that it will be easier to later incorporate it for the DSL front end

- there should be a standard way for prompts to return lists and for the list to be extracted / bound to a variable by the evaluator, bc, this will be a very common pattern.
- in director-evaluator, all evaluator outputs should be saved (even though only the most recent one is pased to the director)
- review associative matching state, make it higher priority
- the dsl should have a 'python' operation
- try the IDL method again

<brainstorming prompt>
- need to impl function calling in the DSL.
- what data structure should we use to represent the task library in-memory? should that be part of the Evaluator Environment, or should it be separate? How should tasks be organized by type in the environment (e.g. should assoc matching tasks be separate from the rest?). Is it redundant to have both a subtype hierarchy for different atomic task types AND an in-memory hierarchy? (I don't think so, but the mapping between these two things will have to be worked out)
- how will tasks be loaded from file? will they be in-lined in the AST or references? former might be simpler for minimum implemenrtation, but eventually both tasks and composite procedures should be abstracted as first-class functions
- do we want to add 'cond' as a primitive? in that case (and maybe also for other reasons) we need a bridge between task outputs and python types. Look into imposing json formatting for task outputs.
</brainstorming prompt>

Misc:
- RL on GPT 2?
- is there a way to mix numbers with discrete tokens? Maybe attention over each of the bits in floating point representation?
- can llms be trained at half precision?
- how does llm compute requirement scale in the size of the token dictionary?
- what's the biggest trainable model?

</file>
Reasoned for 8 seconds
The documentation does address associative matching for both task/template selection and context retrieval, but the level of detail isn’t uniform across both areas. Here’s a breakdown:

Associative Matching for Context:

Interfaces and Types:
The Memory System documentation defines a clear interface for context retrieval via associative matching. For example, the function
typescript
Copy
getRelevantContextFor(input: ContextGenerationInput): Promise<AssociativeMatchResult>;
expects a structured input (with fields like taskText, inheritedContext, and previousOutputs) and returns an AssociativeMatchResult that includes an unstructured context string and a list of file matches. This specification details the types and expected behavior, which makes it relatively well‑defined at the integration level.
Integration and Usage:
The documentation explains that the Evaluator calls this function—merging inherited context with accumulated outputs when needed—to generate a context that is then injected into subsequent tasks. The “Context Frame Pattern” and related ADRs provide further guidance on how context is extended, but they leave room for further refinement regarding ranking or prioritization of matches.
Associative Matching for Task/Template Selection:

High‑Level References:
The Task System documentation and parts of the “atomic_task_subtypes” discussion mention that task template matching works with the “associative matching system.” For example, the XML templates include a <criteria> element used for dynamic evaluation template selection via associative matching.
Lack of Algorithmic Detail:
While it’s clear that the system will score and match natural language task descriptions to candidate templates (with hints at numeric scoring), the underlying matching algorithm isn’t spelled out in detail. The focus is more on the fact that such a mechanism exists rather than on how it works internally.
Open Questions:
Several TODOs and open issues (notably in the “inconsistencies.md” and “TODOS.md” files) indicate that aspects such as error handling for context-generation failures and the extension of the inherit_context attribute to non‑sequential operators remain areas for further design work.
In summary:

Context Retrieval: The associative matching for context is fairly well‑spec’d at the interface level (with defined types and expected behavior), though the internal ranking and error recovery strategies are only sketched out.
Task/Template Matching: There is an acknowledgment that associative matching plays a role in selecting and binding task templates (using free-form criteria and numeric scores), but the documentation provides only a high‑level description without in‑depth algorithmic details.
Overall, while the integration points and intended behaviors are clearly documented, many of the deeper algorithmic and error‑handling details—especially for task/template matching—are left open for future refinement.






You said:
come up with a list of open questions about the task / template matching that need to be claridfied
Reasoned for 4 seconds
Below is a list of open questions about task/template matching that still need clarification:

Scoring and Ranking:

What precise metrics or algorithms should be used to score the similarity between a user’s task description and candidate templates?
Is there a threshold score that distinguishes a “good” match from an insufficient one, and how should borderline cases be handled?
Criteria Usage:

How should the free‑form <criteria> element in the XML be interpreted and weighted during matching?
Can multiple criteria be specified, and if so, how should they be combined to influence the match score?
Context Integration:

How is inherited context (from parent tasks) versus accumulated context (from previous outputs) factored into the matching process?
Should the matching algorithm dynamically adjust its weighting based on available context, or is there a fixed strategy?
Template Differentiation:

How should the system differentiate between templates intended for atomic tasks versus those designed for sequential, reduce, or script tasks?
Do different task types require separate matching strategies or scoring adjustments?
Handling Ambiguity and Incompleteness:

How should the matching process deal with ambiguous or incomplete task descriptions?
Is there a fallback mechanism (e.g., re-parsing or prompting for clarification) if no template achieves a satisfactory match?
Adaptability and Learning:

Should the matching system be adaptive—learning from past successes or user corrections—and if so, what form would that feedback loop take?
Is there a mechanism to update template scores over time based on usage or error outcomes?
Error and Failure Handling:

How should template matching react if the associative matching for context fails or returns partial data?
In cases where the best match still results in a task failure, should there be an automatic retry with alternative templates?
Interaction with Template Substitution:

How do placeholder substitutions (e.g., using {{variable_name}}) interact with the matching algorithm? Are there requirements on the template text that affect matching accuracy?
Handling Multiple Matches:

When multiple templates score similarly, should the system select the highest score automatically, or present alternatives for manual intervention or further evaluation?
Is there a need for a ranking mechanism that can return the top-N candidates for further processing?
Cross-Operator Consistency:

Should the matching logic be consistent across all operators (atomic, sequential, reduce, script), or are there operator‑specific nuances that need separate matching rules?
If inheritance and accumulation settings differ between operators, how should the matching algorithm adjust its behavior accordingly?
Template Versioning and Compatibility:

How should the matching system handle different versions of task templates if updates occur? Is there a versioning strategy that ensures backward compatibility during matching?
Clarifying these questions will help ensure that the task/template matching process is robust, transparent, and well integrated into the overall task execution system.






You said:
1. no precise metric. associative matching tasks are responsible for heuristically calculating this similarity. the associative matching task templates are data element, so they don't need to be specified past their input / output signatures
2. again, the associative matching templates are user-defined, and only need to object the input / output conventions that i mentioned
3. the associative matching task should have similar semantics in terms of context inheritance flags and so on
4. this is a misunderstanding of the system. only atomic tasks have templates. composite expressions are composed of multiple atomic tasks, sequenced or combined in different ways
5. let's not worry about that, but in general the system should be able to dynamically surface questiosn to the user
6. It will eventually be adaptive, but not for mvp. historical template scores, when they are added, will be based on success of *executed* instances of the task
7. same as an associative matching failure in any other case. there should be an automatic retry
8. placeholder substitutions are always completed *before* a task executes. associative matching tasks are no different
9. selects highest score
10. for mvp, the matching logic will be uniform
11. No versioning

---

review the above and summarize your updated understanding. ask any follow up questions, if needed
Reasoned for 4 seconds
Here's my summary of your updated understanding regarding task/template matching:

Metric Definition:

There isn’t a need for a precise, system-wide metric. Instead, each associative matching task will heuristically calculate similarity based solely on its input/output signatures.
Associative Matching Templates:

These templates are user‑defined. They only need to adhere to the established input/output conventions without further detailed specification.
Context Inheritance:

Associative matching tasks should follow similar semantics regarding context inheritance flags as other tasks.
Template Scope:

Only atomic tasks have templates. Composite expressions are built by combining multiple atomic tasks in sequence or through other combinations, so no separate template matching is needed for composites.
Handling Ambiguity:

While handling ambiguous or incomplete descriptions isn’t a priority for MVP, the system should have the capability to dynamically surface questions to the user when necessary.
Adaptivity:

Adaptive behavior isn’t included in MVP. In the future, historical template scores will be based on the success of executed task instances.
Failure Handling:

If an associative matching task fails (or returns partial data), it will trigger an automatic retry, consistent with failure handling in other parts of the system.
Placeholder Substitution:

Placeholders (e.g., {{variable_name}}) are always substituted before task execution, so associative matching tasks follow the same rule.
Multiple Matches:

When multiple candidates are available, the system selects the template with the highest score.
Uniform Matching Logic:

For the MVP, the matching logic is uniform across all cases (no special rules for different operators).
Versioning:

There is no versioning for templates.
Follow-up Questions:

For context inheritance flags in associative matching tasks, do you envision any special cases in the future, or will they exactly mirror the behavior of other atomic tasks?

Regarding the dynamic surfacing of questions to the user (point 5), do you have any preferred approach for how and when these questions should be triggered, or is that left entirely open for future design?

Finally, as adaptive behavior is deferred to future versions, is there any specific feedback mechanism you want documented now (even at a high level) for how executed instance success will eventually influence template scoring?

Let me know if any further details or clarifications are needed!






You said:
1. there should also be an option to disable the context entirely (cant' remember whether other atomic tasks have that or not)
2. from the handler perspective, these questions will be a form of tool use
3. the 'notes' section will contain an optional success score. this is what will be aggregated / kept track of.

---

review each .md arch doc and decide whether our discussion is relevant to it. then draft a plan describing, in detail, the changes to the .md arch docs that would be required to incorporate the feedback and design decisions from our discussion
**Updated Understanding:** 1. **Context Inheritance Flags for Associative Matching Tasks:** - In addition to the regular inheritance flags, there should be an option to **disable context** entirely for associative matching tasks, allowing the task to run without relying on any context at all. It's unclear if other atomic tasks have this option, but it should be available for associative matching tasks. 2. **Dynamic Surfacing of Questions to the User:** - The system should be designed to dynamically surface questions to the user when necessary. However, the specifics of **how and when** these questions should appear are left open for future implementation details. 3. **Adaptive Behavior and Scoring:** - **Adaptive scoring** will not be part of the MVP. Future implementation plans involve incorporating historical scores to adjust template matching based on the success of previously executed task instances. **Follow-up Questions:** 1. **Disabling Context Entirely:** - Should the option to disable context entirely for associative matching tasks be an attribute directly within the task’s definition? Or would this be an optional parameter for specific tasks in the future? Let me know if I’ve captured everything appropriately, and feel free to clarify any remaining details! for 9 seconds
Below is a detailed plan that reviews our architectural markdown files and describes the changes needed to incorporate the design decisions and feedback about task/template matching (and related context handling) from our discussion.

1. Identify Relevant Documents and Their Update Needs
A. System‑Level and Pattern Documents
system/architecture/overview.md

Relevance: Provides the high‑level summary of the architecture.
Changes:
Add a short section (or bullet item) that explains the matching strategy for atomic task templates.
Note that only atomic tasks have templates and that matching is done heuristically via associative matching tasks.
Mention that future adaptivity is planned via success scores stored in the “notes” field.
system/architecture/patterns/context-frames.md

Relevance: Describes how context is passed and extended between tasks.
Changes:
Update the “Context Frame Operations” section to mention that atomic tasks (and by extension, associative matching tasks) may include an option to completely disable context inheritance.
Add a note that this “disable context” flag is an available option (if not already defined for atomic tasks).
system/architecture/patterns/errors.md

Relevance: Covers error handling across the system.
Changes:
Insert a clarification that an associative matching failure (including cases where context cannot be retrieved) will trigger an automatic retry.
Note that if a matching task ultimately fails, it will produce an error that includes any partial “notes” (which will also contain a success score when available).
system/architecture/decisions/002-context-management.md

Relevance: Describes context selection, inheritance, and extension.
Changes:
Add a bullet point or subsection discussing the new design decision to allow an option to disable context entirely for atomic tasks (and by extension, associative matching tasks).
Clarify that the same inheritance semantics (full/none/subset) apply to associative matching tasks and that “none” may be used to disable context.
system/architecture/decisions/005-context-handling.md

Relevance: Focuses on context generation and clarifies context handling details.
Changes:
Update to mention that placeholders are substituted before execution and that associative matching tasks use the same conventions.
Include a note that the “notes” section of a task result will optionally carry a success score (used later for adaptive scoring).
Reiterate that automatic retry is applied when associative matching fails.
system/architecture/questions.md

Relevance: Lists unresolved open questions.
Changes:
Remove or update questions related to template matching that have now been answered by our design decisions (e.g., “should multiple templates be returned?” is now “select highest score”).
Add a note that for MVP, only a uniform matching strategy is used for atomic tasks with no versioning or operator‑specific matching rules.
B. Component‑Level Documents (Task System & Evaluator)
components/task-system/spec/types.md

Relevance: Defines core types for the task system.
Changes:
Update the definition of the “notes” field (or add commentary) to specify that it may include an optional success score that will eventually be aggregated to inform adaptive scoring.
Emphasize that only atomic tasks have templates and that composite tasks are built by sequencing multiple atomic tasks.
components/task-system/impl/design.md

Relevance: Describes the overall design of the Task System.
Changes:
Insert a subsection on “Task/Template Matching” that explains:
The matching is performed heuristically by associative matching tasks that work based solely on input/output signatures.
There is no precise metric; each matching task template is user‑defined.
The matching logic is uniform for MVP.
The system always selects the highest‑scoring candidate.
Add details about the “disable context” option available for atomic tasks, including its expected effects.
Mention that the “notes” field will include an optional success score that is eventually aggregated by the system.
Clarify that any ambiguity questions raised by the matching task will be surfaced as tool calls (handled by the Handler).
components/task-system/spec/behaviors.md

Relevance: Describes runtime behaviors.
Changes:
Add a bullet under “Template Matching” describing that:
Only atomic task templates are matched.
Associative matching is performed heuristically.
The system uses the highest score candidate.
The “notes” field in the task result may contain a success score.
Note that if context is disabled (via the flag), matching proceeds without incorporating inherited context.
components/task-system/spec/interfaces.md

Relevance: Defines public API interfaces.
Changes:
Ensure that any description of task templates for atomic tasks clarifies that composite tasks do not have their own templates.
Optionally, add a comment indicating that the matching process relies on associative matching tasks whose input/output contracts are fixed and that adaptive scoring will be reflected via the “notes” field.
components/evaluator/README.md

Relevance: Describes the Evaluator’s responsibilities.
Changes:
Update the section on context handling to mention that before a task executes, placeholder substitution is complete and that associative matching tasks follow the same pattern.
Include a brief note that the Evaluator will extract an optional success score from the “notes” field of a task result for future adaptive behavior.
C. TOD O’S and Miscellaneous Documents
TODOS.md
Relevance: Lists outstanding tasks.
Changes:
Add items to update documentation in the above files to incorporate:
The “disable context” option for atomic tasks.
A clear description of how the success score is stored in the “notes” field.
Clarification that ambiguity resolution will be handled as tool calls by the Handler.
Remove any outdated open questions about multiple matching strategies if they have been resolved by the design decisions.
2. Detailed Change Plan
Step 1. Update System‑Level Context and Matching Sections
Overview & Patterns:
In system/architecture/overview.md, add a bullet item under “Key Patterns” describing:
“Atomic Task Matching: Only atomic tasks have templates. Matching is performed heuristically using associative matching tasks that rely on fixed input/output signatures. The system always selects the highest‑scoring candidate. An optional ‘disable context’ flag is available to completely omit inherited context when desired, and task results may include an optional success score in their ‘notes’ field for future adaptivity.”

Context Frames:
In system/architecture/patterns/context-frames.md, add a paragraph under “Frame Creation and Extension”:
“Note: Atomic tasks (including associative matching tasks) can be configured with an option to disable context inheritance entirely, ensuring no parent context is passed forward when that is not desired.”

Context Management Decisions:
In decisions/002-context-management.md, under the “Context Extension vs Merging” section, insert:
“New decision: An option to disable context entirely is provided for atomic tasks (and by extension, associative matching tasks) via a dedicated flag. When disabled, no context is inherited.”

Context Handling Clarifications:
In decisions/005-context-handling.md, add a note:
“Additionally, the ‘notes’ section in task results will optionally contain a success score. This score, aggregated from successful executions, will be used in future adaptive scoring of templates.”

Questions Document:
In system/architecture/questions.md, remove or update any questions regarding operator-specific matching strategies and versioning. Add a note that for MVP:
“The matching strategy is uniform across all atomic tasks, and only the highest‑scoring template is selected. Versioning is not applied.”

Step 2. Update Task System Component Documents
Core Types:

In components/task-system/spec/types.md, update the description of the “notes” field (or add an annotation) to include:
“An optional success score may be included in the ‘notes’ field to record the outcome of template execution. This score will be aggregated over time to enable adaptive template selection in future versions.”

Emphasize that only atomic tasks have their own templates, and that composite expressions are composed of multiple atomic tasks.
Implementation Design:

In components/task-system/impl/design.md, add a new subsection titled “Task/Template Matching” that explains:
The matching process is done via associative matching tasks.
No precise metric is defined; each matching task template is user‑defined and works with its fixed I/O conventions.
The system selects the highest‑scoring template.
An option exists to disable context entirely for atomic tasks.
The “notes” section may contain an optional success score for future adaptivity.
Ambiguity questions will be surfaced as tool calls via the Handler.
Runtime Behaviors:

In components/task-system/spec/behaviors.md, under the “Task Template Matching” section, add bullet points that summarize the above points.
Interfaces Documentation:

In components/task-system/spec/interfaces.md, add clarifying comments in the API documentation to state:
“Note: Only atomic tasks have templates. The matching logic for these tasks is uniform, and composite tasks are formed by sequencing atomic tasks.”

Evaluator Overview:

In components/evaluator/README.md, add a brief paragraph that explains:
“Before task execution, placeholder substitutions are completed. Associative matching tasks (used for atomic tasks) follow the same substitution rules and may include an optional ‘disable context’ flag. The Evaluator also looks for an optional success score in the ‘notes’ field of task results, which will inform future adaptive scoring.”

Step 3. Update TOD O’S
In TODOS.md, add/update items to reflect:
“Update all architecture documentation to include the new ‘disable context’ option for atomic tasks.”
“Document that the ‘notes’ field in task results now includes an optional success score.”
“Clarify that ambiguity resolution for associative matching tasks will be handled as tool calls by the Handler.”
Remove any to‑do items regarding versioning of templates and operator‑specific matching rules (as these are now resolved).
3. Follow‑Up and Verification
After making these documentation changes:

Cross‑Reference Check: Verify that all cross‑references (e.g., between decisions, patterns, and component specs) accurately reflect the new design.
Stakeholder Review: Circulate the updated documents for feedback from the team responsible for the Task System and Evaluator.
Version Control: Commit the changes with clear commit messages indicating that they update the template matching and context handling sections based on our latest design decisions.
This plan ensures that our architectural documentation reflects:

The exclusive use of atomic task templates.
Heuristic, associative matching without a precise metric.
A uniform matching strategy that always selects the highest‑scoring candidate.
The option to disable context entirely.
That adaptive behavior (via a success score in the “notes” field) is planned for future versions.
That ambiguity resolution will be handled as tool calls by the Handler.
Do you need any further clarifications or additional details on any specific document?






You said:
trace the call chain for associative task template matching
...and supports disabling context inheritance when needed. - The inclusion of a success score in the "notes" field for future adaptive scoring. - The handling of ambiguity through tool calls in the Handler. - The consistent application of these design decisions across the task system and related components. After the documentation is updated based on our discussion, these changes should provide a clear and consistent framework for how task/template matching works, ensuring that both the design decisions and implementation details align appropriately for the MVP. for 8 seconds
Below is a step‐by‐step trace of how an associative task template matching request flows through the system. (Keep in mind that in our design only atomic tasks have templates, and that matching is performed heuristically by user‑defined associative matching tasks.)

1. User Input and Initial Request
User Action:
A user provides a natural language description (e.g., “analyze experimental data”) as the basis for a new task.

Entry Point:
The Task System’s public API is invoked via a call such as:

typescript
Copy
taskSystem.findMatchingTasks(userDescription, memorySystem);
This method is responsible for selecting the appropriate atomic task template.

2. Preparing the Matching Input
Inside findMatchingTasks:
The Task System creates a ContextGenerationInput object that bundles:

taskText: The natural language description provided by the user.
inheritedContext: (If applicable) Context inherited from the parent task—or omitted if the “disable context” option is active.
previousOutputs: Any accumulated outputs from earlier steps (if available).
Example pseudocode:

typescript
Copy
const input: ContextGenerationInput = {
    taskText: userDescription,
    inheritedContext: (contextDisabled ? undefined : currentInheritedContext),
    previousOutputs: accumulatedStepOutputs
};
3. Invoking Associative Matching via the Memory System
Call to Memory System:
With the input prepared, the Task System calls:

typescript
Copy
const matchResult = await memorySystem.getRelevantContextFor(input);
Within MemorySystem.getRelevantContextFor:

The Memory System accesses its GlobalIndex (a mapping of absolute file paths to metadata strings).
It applies its internal, heuristic (user‑defined) associative matching logic on the input.
This logic compares the input’s taskText (and, if provided, inheritedContext and previousOutputs) against the stored metadata.
It then returns an AssociativeMatchResult that includes:
An unstructured context string (which might be used later for prompt generation), and
A list of file matches (tuples of file path and optional metadata).
4. Scoring and Template Selection
Back in findMatchingTasks:
The Task System uses the returned AssociativeMatchResult to:

Evaluate candidate atomic task templates according to the matching heuristic.
(Recall: No precise metric is defined—the matching tasks themselves are responsible for computing similarity based on their fixed input/output signatures.)
Assign a numeric score to each candidate based on the quality of the match.
Candidate Selection:
Since the design specifies that the system selects the highest‑scoring candidate:

The Task System compares the scores and selects the template with the highest score.
If there are ambiguities or multiple similar candidates, the system simply returns the highest‑scoring one (with any ambiguity resolution later being handled as a tool call by the Handler).
5. Return and Subsequent Execution
Final Output:
The highest‑scoring atomic task template is returned from findMatchingTasks to the caller.

Follow‑On:
The Task System then proceeds to use this template to execute the atomic task.
(Note: Placeholder substitutions occur before execution, so the associative matching task is unaffected by variable substitution concerns.)

Failure Handling:
If the associative matching call fails (for example, if no sufficient context is retrieved), the system automatically triggers a retry according to the general error‑handling strategy.

Diagrammatic Overview
mermaid
Copy
flowchart TD
    A[User Provides Task Description]
    B[TaskSystem.findMatchingTasks(userDescription, memorySystem)]
    C[Prepare ContextGenerationInput { taskText, inheritedContext, previousOutputs }]
    D[Call MemorySystem.getRelevantContextFor(input)]
    E[MemorySystem Processes GlobalIndex and Applies Heuristic Matching]
    F[Return AssociativeMatchResult { context, fileMatches }]
    G[TaskSystem Computes Scores for Candidate Atomic Templates]
    H[Select Highest-Scoring Template]
    I[Return Selected Template to Caller]
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
Additional Considerations
Context Disabling:
An option exists for atomic tasks to disable context entirely. If that flag is active, the inheritedContext field in the input is omitted, and the matching logic uses only the raw task description (and any previous outputs, if available).

Success Score in ‘Notes’:
When a task executes, its result may include an optional success score in the “notes” field. Although adaptive behavior is not part of the MVP, this score will eventually be aggregated to inform future matching decisions.

Uniform Matching Logic for MVP:
For now, the matching logic is uniform across all atomic tasks with no versioning or operator‑specific adjustments.

This call chain—from user input to the selection of the highest‑scoring atomic task template—illustrates how the system leverages associative matching tasks (via the Memory System) to map natural language descriptions to concrete task templates.

Do you need any further details or clarifications on any step in this chain?






You said:
which documentation format would capture the specs we've been discussing best? Is the existing format already good? If not, what's wrong with it?
processes associative task template matching. The flow highlights key interaction points between the Task System, Memory System, and the evaluation of candidate templates before final selection and execution. If there are any further questions or additional clarifications you'd like to add to this trace, feel free to let me know! for 5 seconds
The current set of Markdown-based documents does a reasonable job capturing high-level architectural decisions, patterns, and component interfaces. It’s human‑readable, organized into directories (system-level, components, decisions, patterns, etc.), and already makes use of diagrams (such as mermaid flowcharts) and structured sections (e.g., ADRs). However, there are some areas where improvements could better capture the detailed specs we’ve discussed:

Consistency and Structure:

Strengths:
The hierarchical organization (system/architecture, components, contracts, etc.) makes it easy to locate related documents.
Dedicated files for architectural decisions (ADRs) and patterns help in understanding design rationale.
Areas for Improvement:
Some sections are fragmented or inconsistent in format. A more standardized template for each document type (e.g., a consistent ADR template, interface spec template, and pattern description template) would make the documentation easier to navigate and update.
Cross-references sometimes become outdated or ambiguous. A more formal system for tracking links (perhaps using a tool or stricter versioning) could help ensure consistency.
Formal Specification of Interfaces and Data Types:

Strengths:
The documents include TypeScript-like definitions and descriptions of key interfaces and types.
Areas for Improvement:
The input/output signatures for associative matching and related tasks are described mostly in prose. A more formal notation—such as JSON Schema, OpenAPI, or even a dedicated DSL—could better capture the precise details (e.g., for the ContextGenerationInput and AssociativeMatchResult).
Using a formal specification for these parts would help reduce ambiguity and ensure that all developers are on the same page regarding what each interface expects and returns.
Diagrams and Call Chains:

Strengths:
The mermaid diagrams and sequence diagrams help illustrate the call chain for associative matching.
Areas for Improvement:
While diagrams exist, they could be more systematically incorporated across all relevant sections. For example, adding call chain diagrams for each key interaction (template matching, context retrieval, error handling) would create a more comprehensive picture.
A unified “flowchart” for the matching process (from user input through memory system invocation to template selection) could be maintained as part of the core design docs.
Adaptability and Future Enhancements:

Strengths:
The docs mention planned future enhancements (like adaptive scoring via the success score in “notes”).
Areas for Improvement:
The current format does not clearly delineate what parts of the design are MVP versus what is planned for future iterations. A “roadmap” or “future work” section in the relevant documents might make it clearer which features (like adaptivity or operator‑specific matching) are deferred.
More explicit notes on how dynamic questions (surfaced as tool calls) integrate into the call chain would also be useful.
Summary
Is the existing format already good?
The existing Markdown format is generally good for high‑level documentation—it is accessible, modular, and familiar to most teams. However, for the detailed specifications we’ve been discussing, especially regarding associative matching and context handling, there are shortcomings:

The precise input/output details are often left in free‑form text rather than a formal schema.
Document consistency and cross-referencing could be improved.
Diagrams and flowcharts could be integrated more systematically.
Recommendations:

Standardize Document Templates: Develop a consistent template for ADRs, interface specifications, and pattern documents.
Adopt Formal Specification for Critical Interfaces: Complement the Markdown docs with formal definitions (e.g., using JSON Schema or OpenAPI for data types like ContextGenerationInput and AssociativeMatchResult).
Enhance Diagrams: Create unified, detailed diagrams for key processes such as associative matching, error handling, and context inheritance.
Clarify MVP vs. Future Enhancements: Clearly mark which aspects (such as adaptive scoring or operator‑specific matching) are deferred for future versions.
In conclusion, while the current Markdown format serves as a solid foundation, it would benefit from additional structure, formal specification for critical interfaces, and more integrated visual aids to fully capture the detailed specifications we’ve discussed.






You said:
for each .md file that requires changes, write an updated recommendation for changes to that doc, including both the changes from our arch discussion and any changes in structure, diagrams, etc. for that .md file as a whole
...representations (diagrams and flowcharts). These adjustments would make the documentation more robust, accessible, and easily maintainable in the long term, especially as the system evolves and more complex features like adaptive scoring are introduced. By introducing a more formalized approach to input/output specifications and standardizing templates, you can ensure clearer communication and reduce potential ambiguities in the future. for 9 seconds
Below is a file‐by‐file list of updated recommendations. For each Markdown file that requires changes, the recommendations detail both the architectural feedback we’ve discussed (e.g., how associative matching is handled for atomic tasks, the “disable context” option, the success score in the “notes” field, and uniform matching logic) and improvements to structure, diagrams, and cross‑referencing.

1. system/architecture/overview.md
Changes Recommended:

Add a “Template Matching” Section:
Include a bullet point or short subsection explaining that only atomic tasks have templates. Describe that matching is performed heuristically via associative matching tasks that work from fixed input/output signatures, always selecting the highest‑scoring candidate. Mention that an optional “disable context” flag can completely omit inherited context.
Integrate a Diagram:
Insert a mermaid flowchart (similar to the one tracing the call chain) that shows how a user’s task description is transformed via the Memory System into a selected atomic task template.
Clarify Future Adaptivity:
Briefly note that while adaptivity (via aggregation of a success score in the “notes” field) isn’t part of the MVP, it is planned for later versions.
2. system/architecture/patterns/context-frames.md
Changes Recommended:

Expand on Context Inheritance Options:
Add a dedicated subsection (or table) that describes the available context inheritance modes—“full,” “subset,” and a new “disable” option (or “none”) that allows atomic tasks to run without any inherited context.
Update Diagrams:
Enhance or add a diagram showing two parallel flows:
One for a task with standard inheritance,
And one where the “disable context” flag is set, so no parent context flows into the new context frame.
Cross‑Reference Matching:
Include a note that these context modes also govern how associative matching tasks receive context, ensuring uniform semantics.
3. system/architecture/patterns/errors.md
Changes Recommended:

Error Handling for Matching:
Add a bullet under “Recovery Process” that clarifies if an associative matching task fails (for instance, if no adequate context is retrieved), the system will automatically trigger a retry. Mention that any error produced will include partial outputs and an optional success score (if present) in the “notes” field.
Include a Diagram:
Insert a small flowchart outlining the error path for template matching—starting from the Memory System’s matching call, detection of failure, automatic retry, and eventual error propagation.
Uniform Error Strategy:
Ensure that the text reinforces that associative matching errors are handled in the same way as other TASK_FAILURE errors.
4. system/architecture/decisions/002-context-management.md
Changes Recommended:

New Decision Item – Disable Context:
Add a new bullet or subsection that specifies:
“An option to disable context entirely is provided for atomic tasks (and associative matching tasks), using a dedicated flag. When set, no inherited context is passed.”

Clarify Inheritance Semantics:
Update examples or discussion to show that the same inheritance flags (full, subset, none) apply to associative matching tasks.
Structure & Cross‑References:
Use a standardized decision format and include references (e.g., “see also Evaluator documentation”) for where these settings affect the call chain.
5. system/architecture/decisions/005-context-handling.md
Changes Recommended:

Placeholder Substitution Clarification:
Add a paragraph clarifying that placeholder substitutions (e.g., {{variable_name}}) are performed before task execution for all task types, including associative matching tasks.
Include Success Score in Notes:
Update the document to mention that the “notes” section may now include an optional success score. This score will later be aggregated (once adaptivity is implemented) to inform future matching decisions.
Automatic Retry Note:
Emphasize that if an associative matching task fails, the system will automatically retry as with any other TASK_FAILURE.
Diagram Enhancement:
Consider adding a small diagram illustrating the overall context handling flow—from substitution through matching, error detection, and extraction of the success score.
6. system/architecture/questions.md
Changes Recommended:

Update Open Questions:
Remove or reword questions that previously addressed operator‑specific matching (since we now use a uniform approach for atomic tasks) and eliminate any mention of versioning.
Add New Open Question:
Optionally, note whether additional context‐disabling options might be needed in future operator types.
Clarify MVP Scope:
Insert a statement that for the MVP, only atomic tasks are templated, matching logic is uniform, and adaptivity is deferred.
7. components/task-system/spec/types.md
Changes Recommended:

Update “notes” Field Documentation:
Expand the description of the “notes” field in the TaskResult type to state that it may include an optional success score. For example:
“The ‘notes’ field may contain additional metadata such as a success score from task execution. This score will be aggregated over time to support future adaptive template matching.”

Emphasize Atomic Templates Only:
Clearly note that only atomic tasks have templates, and that composite tasks are formed by combining atomic tasks.
Add Example Schemas:
Optionally, include small JSON snippet examples for ContextGenerationInput and AssociativeMatchResult to clarify input/output formats.
8. components/task-system/impl/design.md
Changes Recommended:

New Subsection “Task/Template Matching”:
Create a dedicated subsection that explains:
That matching is done via user-defined associative matching tasks.
Only atomic tasks have templates.
The matching process is heuristic with no precise metric; the system selects the highest‑scoring candidate.
The optional “disable context” flag is available and affects the ContextGenerationInput.
The “notes” field may optionally include a success score for adaptive scoring.
Add a Detailed Diagram:
Insert a mermaid flowchart that traces the call chain from user input to ContextGenerationInput creation, invocation of memorySystem.getRelevantContextFor(), score computation, and selection of the highest‑scoring template.
Reorganize for Clarity:
Reorganize sections to clearly separate design for Handler, Evaluator, Template Matching, and Resource Management. Cross‑reference with the ADRs and patterns for context handling.
9. components/task-system/spec/behaviors.md
Changes Recommended:

Expand “Task Template Matching” Behavior:
Under the section describing matching behavior, add bullet points that state:
Atomic task templates are matched via associative matching.
The process is heuristic and uniform across the system.
Only the highest‑scoring candidate is selected.
If the “disable context” option is enabled, the inherited context is omitted.
The “notes” field may include a success score for later adaptive improvements.
Include a Diagram:
Add a diagram (or flowchart) that summarizes the behavioral flow for matching.
Clarify MVP Assumptions:
Clearly state that operator-specific matching differences or versioning are not part of the MVP.
10. components/task-system/spec/interfaces.md
Changes Recommended:

Clarify Matching-Related APIs:
In the documentation for methods like findMatchingTasks, add comments specifying:
That matching only applies to atomic task templates.
That the input to associative matching is a ContextGenerationInput.
That the system returns the highest‑scoring candidate with no versioning.
Formalize Input/Output Types:
Consider adding a section that formally defines the structures for ContextGenerationInput and AssociativeMatchResult, perhaps including small examples.
Ensure Consistency:
Verify that references to template matching are consistent with the changes made in types.md and design.md.
11. components/evaluator/README.md
Changes Recommended:

Add “Context and Template Matching” Section:
Include a short section describing that before task execution, all placeholder substitutions are done and that associative matching tasks follow the same rules. Explain that the Evaluator will extract an optional success score from the “notes” field for future adaptivity.
Integrate a Diagram:
Add a diagram showing the Evaluator’s role in coordinating context retrieval (via the Memory System) and then selecting the appropriate atomic task template.
Cross‑Reference Context Decisions:
Include references to the decisions documents (e.g., ADRs 002 and 005) that explain context inheritance and the “disable context” option.
12. TODOS.md
Changes Recommended:

Update and Consolidate TODO Items:
Add items such as:
“Update all documentation to include the ‘disable context’ option for atomic tasks.”
“Document that the ‘notes’ field in task results may include an optional success score.”
“Remove TODOs related to template versioning and operator‑specific matching logic.”
Mark Completed Items:
Review and mark any items that have been resolved (e.g., use of a uniform matching strategy for MVP).
Final Notes
Each file should be reviewed for internal consistency. In addition to inserting new sections and diagrams as noted above, it is important to ensure that all cross‑references (to decisions, patterns, types, etc.) are updated to reflect the latest design decisions:

Only atomic tasks have templates.
Associative matching is heuristic with no precise metric.
A “disable context” flag is available.
The highest‑scoring candidate is selected.
The “notes” field may optionally include a success score for future adaptive behavior.
All ambiguity or follow‑up questions (if any) are now handled as tool calls via the Handler.
After updating these documents, a final cross‑reference and consistency check should be performed. This will ensure that our architectural documentation accurately reflects our design decisions and can serve as a reliable reference for future development and enhancements.

Do you need further details or clarifications on any specific file’s recommendations?






You said:
// === IDL-CREATION-GUIDLINES === // Object Oriented: Use OO Design. // Design Patterns: Use Factory, Builder and Strategy patterns where possible // ** Complex parameters JSON : Use JSON where primitive params are not possible and document them in IDL like "Expected JSON format: { "key1": "type1", "key2": "type2" }" // == !! BEGIN IDL TEMPLATE !! === // === CODE-CREATION-RULES === // Strict Typing: Always use strict typing. Avoid using ambiguous or variant types. // Primitive Types: Favor the use of primitive types wherever possible. // Portability Mandate: Python code must be written with the intent to be ported to Java, Go, and JavaScript. Consider language-agnostic logic and avoid platform-specific dependencies. // No Side Effects: Functions should be pure, meaning their output should only be determined by their input without any observable side effects. // Testability: Ensure that every function and method is easily testable. Avoid tight coupling and consider dependency injection where applicable. // Documentation: Every function, method, and module should be thoroughly documented, especially if there's a nuance that's not directly evident from its signature. // Contractual Obligation: The definitions provided in this IDL are a strict contract. All specified interfaces, methods, and constraints must be implemented precisely as defined without deviation. // =======================

module GenericSystemName {

// Interface for a generic entity
interface EntityName {

    // Action/method definition
    // Preconditions:
    // - Define any preconditions here.
    // - Expected JSON format: { "key1": "type1", "key2": "type2" } 
    // Postconditions:
    // - Define the expected outcomes here.
    returnType methodName(parameterType parameterName);

    // Additional methods...
};

// Another entity or component
interface AnotherEntity {

    // Action/method definition
    // Preconditions:
    // - Define any preconditions here.
    // - Expected JSON format: { "key1": "type1", "key2": "type2" } 
    // Postconditions:
    // - Define the expected outcomes here.
    returnType anotherMethodName(parameterType parameterName);

    // Additional methods...
};
// == !! END IDL TEMPLATE !! ===

// EXAMPLE // === CODE-CREATION-RULES === // Strict Typing: Always use strict typing. Avoid using ambiguous or variant types. // Primitive Types: Favor the use of primitive types wherever possible. // Portability Mandate: Python code must be written with the intent to be ported to Java, Go, and JavaScript. Consider language-agnostic logic and avoid platform-specific dependencies. // No Side Effects: Functions should be pure, meaning their output should only be determined by their input without any observable side effects. // Testability: Ensure that every function and method is easily testable. Avoid tight coupling and consider dependency injection where applicable. // Documentation: Every function, method, and module should be thoroughly documented, especially if there's a nuance that's not directly evident from its signature. // Contractual Obligation: The definitions provided in this IDL are a strict contract. All specified interfaces, methods, and constraints must be implemented precisely as defined without deviation. // ======================= // == !! BEGIN TEMPLATE EXAMPLE !! === interface Tweets { // Preconditions: // - userID exists. // - tweetContent is non-null and within allowable size limits. // Postconditions: // - A new tweet is created and stored. // Expected JSON format: { "userID": "string", "content": "string" } void postTweet(string tweetJSON); // Preconditions: // - userID and tweetID exist. // Postconditions: // - The tweet with tweetID is marked as liked by userID. void likeTweet(string userID, string tweetID); // Preconditions: // - userID and tweetID exist. // Postconditions: // - The tweet with tweetID is marked as retweeted by userID. // Expected JSON format: { "userID": "string", "originalTweetID": "string" } void retweet(string retweetJSON); // Preconditions: // - tweetID exists. // Postconditions: // - Returns the details of the tweet as JSON. string getTweetDetails(string tweetID); // Invariants: // - Filesystem storage maintains a list of tweets, likes, and retweets for each tweetID. }; // == !! END TEMPLATE EXAMPLE !! ===


<spec prompt guide>
<spec template>
# Specification Template
> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

- [High level goal goes here - what do you want to build?]

## Mid-Level Objective

- [List of mid-level objectives - what are the steps to achieve the high-level objective?]
- [Each objective should be concrete and measurable]
- [But not too detailed - save details for implementation notes]

## Implementation Notes
- [Important technical details - what are the important technical details?]
- [Dependencies and requirements - what are the dependencies and requirements?]
- [Coding standards to follow - what are the coding standards to follow?]
- [Other technical guidance - what are other technical guidance?]

## Context

### Beginning context
- [List of files that exist at start - what files exist at start?]

### Ending context  
- [List of files that will exist at end - what files will exist at end?]

## Low-Level Tasks
> Ordered from start to finish

1. [First task - what is the first task?]
aider
What prompt would you run to complete this task?
What file do you want to CREATE or UPDATE?
What function do you want to CREATE or UPDATE?
What are details, including type hints / signatures, that you want to add to drive the code changes?

2. [Second task - what is the second task?]
aider
What prompt would you run to complete this task?
What file do you want to CREATE or UPDATE?
What function do you want to CREATE or UPDATE?
What are details you want to add to drive the code changes?

3. [Third task - what is the third task?]
aider
What prompt would you run to complete this task?
What file do you want to CREATE or UPDATE?
What function do you want to CREATE or UPDATE?
What are details you want to add to drive the code changes?

</spec template>

<spec examples>
<example 1>
# Transcript Analytics - New Chart Type Specification
> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

- Add a new chart type to the transcript analytics application.

## Mid-Level Objective

- Implement a new chart function in chart.py based on the provided description.
- Update the CLI application to support generating the new chart type.
- Ensure the new chart integrates smoothly with existing functionality.

## Implementation Notes

- Use only the dependencies listed in pyproject.toml.
- Comment every function thoroughly.
- Carefully review each low-level task for precise code changes.

## Context

### Beginning Context

- src/aider_has_a_secret/main.py
- src/aider_has_a_secret/chart.py
- pyproject.toml (readonly)

### Ending Context

- src/aider_has_a_secret/main.py (updated)
- src/aider_has_a_secret/chart.py (updated)
- pyproject.toml

## Low-Level Tasks
> Ordered from start to finish

1. Create a New Chart Function in chart.py

aider
UPDATE src/aider_has_a_secret/chart.py:
    ADD a new function `create_<chart_type>_chart(word_counts: WordCounts)` that implements the new chart type based on the following 
    description: '<description>'


2. Update the CLI Application to Support the New Chart Type

aider
UPDATE src/aider_has_a_secret/main.py:
    UPDATE the analyze_transcript(...):
        ADD new chart type in the `chart_type` parameter
        Call the new chart function based on the new chart type

</example 1>

<example 2>
# GitHub Gist Creation Tool Specification
> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

- Create a Python-based tool for programmatically creating GitHub Gists from local files

## Mid-Level Objective

- Implement secure GitHub API integration for Gist creation
- Develop modular system for file handling and HTTP requests
- Create type-safe data structures for Gist management
- Support environment-based configuration for secure token handling

## Implementation Notes
- Use python-dotenv for environment variable management
- Implement proper error handling for API and file operations
- Use Pydantic (BaseModel) for type validation
- Follow GitHub API v2022-11-28 specifications
- Handle both single and multiple file Gist creation
- Implement proper HTTP error handling and retries
- Use type hints throughout the codebase

## Context

### Beginning context
- No existing files (new project)
- Required .env file with GITHUB_GIST_TOKEN

### Ending context  
- /modules/http.py
- /modules/data_types.py
- /modules/files.py
- /modules/gist.py
- .env (with GitHub token)

## Low-Level Tasks
> Ordered from start to finish

1. Build module level support
    
aider
    CREATE modules/http.py
        CREATE def post(url, headers, body) -> dict or throw
    
    UPDATE modules/data_types.py
        CREATE class GistFiles (BaseModel) to support the following structure:
            {"files":
                {"README.md": {"content": "Hello World"}}}
        CREATE class Gist (BaseModel) to support the following structure:
            {"description":"Example of a gist", "public": false, "files": Files}
    
    CREATE modules/files.py
        CREATE def pull_files (directory_path) -> GistFiles [] or throw


2. Create gist support
    
aider
    CREATE modules/gist.py
        CREATE def create_gist(gist: Gist) -> dict or throw
            call modules/http.post(url, headers, body) -> dict or throw
            use env python-dotenv to get GITHUB_GIST_TOKEN
            call dotenv load at top of file
    
    example code:
        curl -L \
            -X POST \
            -H "Accept: application/vnd.github+json" \
            -H "Authorization: Bearer <YOUR-TOKEN>" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            https://api.github.com/gists

</example 2>

<example 3>
Use type signatures when appropriate. For example:
python
# Example Task with Type Hints

1. Create Data Processing Function
aider
UPDATE src/process.py:
    CREATE process_batch(data: List[np.ndarray], config: Dict[str, Any]) -> Tuple[np.ndarray, float]:
        Input types:
        - data: List of numpy arrays containing raw sensor data
        - config: Dictionary of processing parameters
        
        Return type:
        - Tuple of processed array and quality metric
        
        Implementation:
        ADD validation of input shapes and types
        ADD processing pipeline
        ADD quality calculation
        RETURN (processed_data, quality_score)
</example 3>

</spec examples>
</spec prompt guide>

---

<instructions>
now, write a series of detailed spec prompts -- two .md files per spec prompt -- based on your final recommended changes. your final output should be json containing all the spec prompts.

example format:

[
  {
    "full_prompt_text": "Spec Prompt for system/architecture/overview.md and system/architecture/patterns/context-frames.md .......",
    "files": ["system/architecture/overview.md", 
      "system/architecture/patterns/context-frames.md"]
    ]
  }
]

follow the <spec prompt guide> format guide
</instructions>

7/7

Reasoned for 8 seconds
json
Copy
[
  {
    "full_prompt_text": "Spec Prompt for system/architecture/overview.md and system/architecture/patterns/context-frames.md\n\nHigh-Level Objective:\n- Update the overall architecture documentation to clearly describe how atomic task template matching is performed using associative matching tasks.\n\nMid-Level Objectives:\n- In the overview document, add a dedicated section (or bullet point) that explains that only atomic tasks have templates, and that matching is performed heuristically based on fixed input/output signatures. Mention that the system selects the highest-scoring candidate and that an optional 'disable context' flag is available.\n- In the context-frames document, add a subsection (or table) detailing the available context inheritance modes (full, subset, and a disable option) and include a diagram showing the difference between standard inheritance and when context is disabled.\n\nImplementation Notes:\n- Insert a mermaid flowchart in the overview document to illustrate the call chain from user input through context generation and associative matching to template selection.\n- Cross-reference the new context inheritance options with the decisions documents (e.g., ADR 002 and ADR 005) to ensure consistency.\n- Use clear bullet points and headings to separate the discussion of template matching and context handling.\n\nBeginning Context:\n- Existing files: system/architecture/overview.md, system/architecture/patterns/context-frames.md\n\nEnding Context:\n- Updated files with new sections and diagrams detailing atomic task template matching and context inheritance/disabling.\n\nLow-Level Tasks:\n1. Update system/architecture/overview.md:\n   - ADD a new section or bullet under 'Key Patterns' explaining that only atomic tasks have templates. Describe that matching is done heuristically and the highest-scoring candidate is selected, with an optional disable context flag.\n   - INSERT a mermaid flowchart diagram illustrating the call chain for associative matching.\n\n2. Update system/architecture/patterns/context-frames.md:\n   - ADD a subsection that defines the available context inheritance modes: full, subset, and a disable option. Explain what happens when context is disabled.\n   - INSERT a diagram showing two flows: one with standard inheritance and one where no parent context is passed (disable context).\n\nPlease update the two files accordingly.",
    "files": [
      "system/architecture/overview.md",
      "system/architecture/patterns/context-frames.md"
    ]
  },
  {
    "full_prompt_text": "Spec Prompt for system/architecture/patterns/errors.md and system/architecture/decisions/002-context-management.md\n\nHigh-Level Objective:\n- Enhance the error handling and context management documentation to reflect the new handling for associative matching failures and the option to disable context.\n\nMid-Level Objectives:\n- In the errors.md document, add clarification under the recovery process that if an associative matching task fails (e.g., insufficient context retrieval), the system will automatically trigger a retry. Include a brief flow diagram to illustrate this error path.\n- In the 002-context-management.md document, add a new decision item explaining that atomic tasks (and associative matching tasks) can now use a dedicated flag to completely disable context inheritance, and clarify that the same inheritance semantics (full, subset, none) apply uniformly.\n\nImplementation Notes:\n- Add a new bullet point or subsection in 002-context-management.md that explicitly states the availability of a disable context option.\n- Enhance errors.md with a small diagram showing the error detection and automatic retry flow for associative matching failures.\n\nBeginning Context:\n- Existing files: system/architecture/patterns/errors.md, system/architecture/decisions/002-context-management.md\n\nEnding Context:\n- Updated error handling documentation and context management decision files that incorporate the automatic retry on failure and the disable context option.\n\nLow-Level Tasks:\n1. Update system/architecture/patterns/errors.md:\n   - ADD a bullet under the Recovery Process section stating that associative matching failures trigger an automatic retry. Insert a diagram outlining this error flow.\n\n2. Update system/architecture/decisions/002-context-management.md:\n   - ADD a new decision item or bullet point that specifies the option to disable context entirely for atomic and associative matching tasks using a dedicated flag.\n   - Ensure that examples and discussion clearly show that the same inheritance modes (full, subset, none) apply.\n\nPlease update the two files accordingly.",
    "files": [
      "system/architecture/patterns/errors.md",
      "system/architecture/decisions/002-context-management.md"
    ]
  },
  {
    "full_prompt_text": "Spec Prompt for system/architecture/decisions/005-context-handling.md and system/architecture/questions.md\n\nHigh-Level Objective:\n- Update context handling decisions and open questions documentation to incorporate the new behavior regarding placeholder substitution, success scoring, and automatic retry on associative matching failures.\n\nMid-Level Objectives:\n- In 005-context-handling.md, add a paragraph clarifying that placeholder substitutions are completed before execution for all tasks (including associative matching tasks) and that the 'notes' field may now contain an optional success score for future adaptive scoring. Also, emphasize that failures in associative matching will automatically trigger a retry.\n- In the questions.md file, update or remove questions that are now resolved (e.g., operator-specific matching concerns and versioning issues) and add a note that for MVP, matching is uniform across atomic tasks with no versioning.\n\nImplementation Notes:\n- Insert a diagram in 005-context-handling.md that shows the flow from placeholder substitution through context handling, matching, and extraction of a success score.\n- Revise open questions to clearly state that for MVP, only uniform matching is supported and that adaptivity via the success score is planned for future versions.\n\nBeginning Context:\n- Existing files: system/architecture/decisions/005-context-handling.md, system/architecture/questions.md\n\nEnding Context:\n- Updated decisions and open questions documents that reflect the current design decisions regarding context handling and template matching.\n\nLow-Level Tasks:\n1. Update system/architecture/decisions/005-context-handling.md:\n   - ADD a paragraph that explains placeholder substitution is completed before task execution and that the 'notes' section may include an optional success score. Emphasize automatic retry on matching failures.\n   - INSERT a diagram illustrating the complete context handling flow.\n\n2. Update system/architecture/questions.md:\n   - REMOVE or reword questions related to operator-specific matching and versioning. Add a statement clarifying that MVP uses uniform matching and that adaptive scoring via success scores is deferred to future versions.\n\nPlease update the two files accordingly.",
    "files": [
      "system/architecture/decisions/005-context-handling.md",
      "system/architecture/questions.md"
    ]
  },
  {
    "full_prompt_text": "Spec Prompt for components/task-system/spec/types.md and components/task-system/impl/design.md\n\nHigh-Level Objective:\n- Update the Task System’s type definitions and design documentation to reflect the new details about atomic task templates, associative matching, and the optional success score in the 'notes' field.\n\nMid-Level Objectives:\n- In types.md, update the description of the 'notes' field in the TaskResult type to mention the optional success score that will be aggregated for adaptive matching. Emphasize that only atomic tasks have templates and that composite tasks are formed by sequencing atomic tasks.\n- In design.md, create a new subsection titled 'Task/Template Matching' that describes the heuristic associative matching process, explains that the system selects the highest-scoring candidate, and outlines the new disable context option. Include a detailed mermaid flowchart of the call chain from user input to template selection.\n\nImplementation Notes:\n- Use precise language to define the expected behavior of the matching process and include examples where helpful.\n- Ensure that the design section is clearly organized with headings and subheadings for matching, context disabling, and future adaptive behavior.\n\nBeginning Context:\n- Existing files: components/task-system/spec/types.md, components/task-system/impl/design.md\n\nEnding Context:\n- Updated type definitions and design documentation that incorporate the new template matching details, disable context option, and success score mechanism.\n\nLow-Level Tasks:\n1. Update components/task-system/spec/types.md:\n   - MODIFY the 'notes' field documentation to include an optional success score and note that only atomic tasks have templates.\n   - Optionally add small JSON examples for ContextGenerationInput and AssociativeMatchResult.\n\n2. Update components/task-system/impl/design.md:\n   - ADD a new subsection 'Task/Template Matching' that explains the associative matching process, describes the disable context option, and specifies that the highest-scoring candidate is chosen.\n   - INSERT a mermaid flowchart diagram that illustrates the call chain for matching.\n\nPlease update the two files accordingly.",
    "files": [
      "components/task-system/spec/types.md",
      "components/task-system/impl/design.md"
    ]
  },
  {
    "full_prompt_text": "Spec Prompt for components/task-system/spec/behaviors.md and components/task-system/spec/interfaces.md\n\nHigh-Level Objective:\n- Enhance the Task System’s behavior and interface documentation to clarify that matching is only applicable to atomic task templates, and to formalize the input/output contracts for associative matching tasks.\n\nMid-Level Objectives:\n- In behaviors.md, expand the 'Task Template Matching' section to state that associative matching is heuristic, uniform across all atomic tasks, and that only the highest-scoring candidate is selected. Also note that if the 'disable context' option is enabled, inherited context is omitted, and that the 'notes' field may include an optional success score.\n- In interfaces.md, add clarifying comments in the API documentation for methods such as findMatchingTasks. Formalize and provide examples for the structures of ContextGenerationInput and AssociativeMatchResult.\n\nImplementation Notes:\n- Ensure that the descriptions in both files are consistent with the updated types and design documents.\n- Use clear examples and, if possible, small code snippets to illustrate the expected input and output formats.\n\nBeginning Context:\n- Existing files: components/task-system/spec/behaviors.md, components/task-system/spec/interfaces.md\n\nEnding Context:\n- Updated behavior and interface documentation that clearly defines the matching process and the associated data structures.\n\nLow-Level Tasks:\n1. Update components/task-system/spec/behaviors.md:\n   - ADD bullet points under 'Task Template Matching' to document the heuristic, uniform matching strategy, the selection of the highest-scoring candidate, and the effect of the disable context flag.\n   - INSERT a diagram summarizing the behavioral flow for matching.\n\n2. Update components/task-system/spec/interfaces.md:\n   - ADD clarifying comments to the findMatchingTasks method, specifying that matching applies only to atomic tasks and that input/output types are defined by ContextGenerationInput and AssociativeMatchResult.\n   - FORMALIZE these type definitions with examples.\n\nPlease update the two files accordingly.",
    "files": [
      "components/task-system/spec/behaviors.md",
      "components/task-system/spec/interfaces.md"
    ]
  },
  {
    "full_prompt_text": "Spec Prompt for components/evaluator/README.md and TODOS.md\n\nHigh-Level Objective:\n- Update the Evaluator documentation and the overall TODO list to reflect the new design decisions regarding associative matching, context disabling, and success scoring for adaptive behavior.\n\nMid-Level Objectives:\n- In components/evaluator/README.md, add a new section (or update an existing one) on 'Context and Template Matching' that explains that placeholder substitutions occur before task execution, that associative matching tasks follow the same rules, and that an optional success score in the 'notes' field is now part of the design. Include a diagram showing the Evaluator's role in this process.\n- In TODOS.md, update and consolidate all items related to template matching and context handling. Add items to document the new 'disable context' option and the success score feature, and remove any outdated items regarding versioning or operator-specific matching.\n\nImplementation Notes:\n- Ensure that the evaluator documentation cross-references the relevant ADRs (e.g., 002 and 005) for context handling.\n- The TODOS.md file should be reviewed for outdated items and revised to reflect the current design.\n\nBeginning Context:\n- Existing files: components/evaluator/README.md, TODOS.md\n\nEnding Context:\n- Updated Evaluator documentation that includes clear sections and diagrams on matching and context handling, and a cleaned-up TODOS.md that accurately reflects the current state of the design.\n\nLow-Level Tasks:\n1. Update components/evaluator/README.md:\n   - ADD a new section titled 'Context and Template Matching' that explains the pre-execution placeholder substitution, uniform associative matching for atomic tasks, and the use of an optional success score in the 'notes' field.\n   - INSERT a diagram illustrating the Evaluator's process in retrieving context and selecting the appropriate template.\n\n2. Update TODOS.md:\n   - REVIEW and update all items related to template matching, context disabling, and success score aggregation. Remove any obsolete items related to versioning and operator-specific matching rules.\n\nPlease update the two files accordingly.",
    "files": [
      "components/evaluator/README.md",
      "TODOS.md"
    ]
  }
]
