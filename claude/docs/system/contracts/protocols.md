# System Protocols

## Task Template Schema [Contract:Tasks:TemplateSchema:1.0]

**Note:** This document is the authoritative specification for the XML schema used in task template definitions. All field definitions, allowed enumerations (such as for `<inherit_context>` and `<accumulation_format>`), and validation rules are defined here. For complete validation guidelines, please see Appendix A in [Contract:Resources:1.0].

The task template schema defines the structure for XML task template files and maps to the TaskTemplate interface.

### XML Schema Definition

```xml
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
        <xs:element name="output_format" minOccurs="0">
          <xs:complexType>
            <xs:attribute name="type" use="required">
              <xs:simpleType>
                <xs:restriction base="xs:string">
                  <xs:enumeration value="json"/>
                  <xs:enumeration value="text"/>
                </xs:restriction>
              </xs:simpleType>
            </xs:attribute>
            <xs:attribute name="schema" type="xs:string" use="optional"/>
          </xs:complexType>
        </xs:element>
        <xs:element name="output_format" minOccurs="0">
          <xs:complexType>
            <xs:attribute name="type" use="required">
              <xs:simpleType>
                <xs:restriction base="xs:string">
                  <xs:enumeration value="json"/>
                  <xs:enumeration value="text"/>
                </xs:restriction>
              </xs:simpleType>
            </xs:attribute>
            <xs:attribute name="schema" type="xs:string" use="optional"/>
          </xs:complexType>
        </xs:element>
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
              <xs:element name="accumulate_data" type="xs:boolean"/>
              <xs:element name="accumulation_format">
                <xs:simpleType>
                  <xs:restriction base="xs:string">
                    <xs:enumeration value="full_output"/>
                    <xs:enumeration value="notes_only"/>
                  </xs:restriction>
                </xs:simpleType>
              </xs:element>
              <xs:element name="fresh_context">
                <xs:simpleType>
                  <xs:restriction base="xs:string">
                    <xs:enumeration value="enabled"/>
                    <xs:enumeration value="disabled"/>
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
      <xs:attribute name="type" use="required">
        <xs:simpleType>
          <xs:restriction base="xs:string">
            <xs:enumeration value="atomic"/>
            <xs:enumeration value="sequential"/>
            <xs:enumeration value="reduce"/>
            <xs:enumeration value="script"/>
            <xs:enumeration value="director_evaluator_loop"/>
          </xs:restriction>
        </xs:simpleType>
      </xs:attribute>
    </xs:complexType>
  </xs:element>
  
  <xs:element name="template">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="name" type="xs:string"/>
        <xs:element name="params" type="xs:string"/>
        <xs:element name="returns" type="xs:string" minOccurs="0"/>
        <xs:element name="task" type="TaskType"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>

  <xs:element name="call">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="template" type="xs:string"/>
        <xs:element name="arg" type="xs:string" maxOccurs="unbounded"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
  
  <xs:element name="template">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="name" type="xs:string"/>
        <xs:element name="params" type="xs:string"/>
        <xs:element name="returns" type="xs:string" minOccurs="0"/>
        <xs:element name="task" type="TaskType"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>

  <xs:element name="call">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="template" type="xs:string"/>
        <xs:element name="arg" type="xs:string" maxOccurs="unbounded"/>
      </xs:sequence>
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
<!-- Director-Evaluator Loop Task Definition -->
<xs:element name="director_evaluator_loop">
  <xs:complexType>
    <xs:sequence>
      <xs:element name="description" type="xs:string"/>
      <xs:element name="max_iterations" type="xs:integer" minOccurs="0"/>
      <xs:element ref="context_management"/>
      <xs:element name="director" type="TaskType"/>
      <xs:element name="evaluator" type="TaskType"/>
      <xs:element name="script_execution" minOccurs="0">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="command" type="xs:string"/>
            <xs:element name="timeout" type="xs:integer" minOccurs="0"/>
            <xs:element name="inputs" type="InputsType"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
      <xs:element name="termination_condition" minOccurs="0">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="condition" type="xs:string"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
    </xs:sequence>
  </xs:complexType>
</xs:element>
</xs:schema>
```

### Script Execution Support

The XML task template schema now supports defining tasks for script execution within sequential tasks. These tasks enable:
 - Command Specification: Defining external commands (e.g. bash scripts) to be executed.
 - Input/Output Contracts: Passing the director's output as input to the script task, and capturing the script's output for subsequent evaluation.
Script execution errors (e.g. non-zero exit codes) are treated as generic TASK_FAILURE conditions. The evaluator captures the script's stdout and stderr in a designated notes field for downstream decision-making.

Example:
```xml
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
```

### Output Format Specification

Tasks can specify structured output format:

```xml
<task>
  <description>List files in directory</description>
  <output_format type="json" schema="string[]" />
</task>
```

The `schema` attribute provides basic type information:
- "object" - JSON object
- "array" or "[]" - JSON array
- "string[]" - Array of strings
- "number" - Numeric value
- "boolean" - Boolean value

Output validation ensures the result matches the specified type.

### Function-Based Templates

The XML schema now supports function-based templates with explicit parameter declarations:

```xml
<template name="analyze_data" params="dataset,config">
  <task>
    <description>Analyze {{dataset}} using {{config}}</description>
  </task>
</template>
```

And function calls with positional arguments:

```xml
<call template="analyze_data">
  <arg>weather_data</arg>
  <arg>standard_config</arg>
</call>
```

This enforces strict scope boundaries - templates can only access explicitly passed parameters.

#### Parameter Resolution

- Parameter names are declared in the comma-separated `params` attribute
- Inside templates, `{{...}}` placeholders only reference declared parameters
- Arguments are evaluated in the caller's environment before being passed to the template
- String arguments can be either variable references or literal values

#### Return Types

Templates can optionally specify a return type using the `returns` attribute:

```xml
<template name="get_file_info" params="filepath" returns="object">
  <task>
    <description>Get metadata for {{filepath}}</description>
    <output_format type="json" schema="object" />
  </task>
</template>
```

This aids in type validation and enables better composition between templates.

### Output Format Specification

Tasks can specify structured output format:

```xml
<task>
  <description>List files in directory</description>
  <output_format type="json" schema="string[]" />
</task>
```

The `schema` attribute provides basic type information:
- "object" - JSON object
- "array" or "[]" - JSON array
- "string[]" - Array of strings
- "number" - Numeric value
- "boolean" - Boolean value

Output validation ensures the result matches the specified type.

### Field Definitions

- The optional `ref` attribute is used to reference a pre-registered task in the TaskLibrary.
- The optional `subtype` attribute refines the task type (for example, indicating "director", "evaluator", etc.)
- The `output_format` element specifies structured output format and validation requirements.
- The `template` element defines a function-like template with explicit parameters.
- The `call` element invokes a function template with positional arguments.

Example:
```xml
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
```
All required and optional fields (including `instructions`, `system`, `model`, and `inputs`) are defined by this schema. For full details and allowed values, please see Appendix A in [Contract:Resources:1.0].

### Example Template

```xml
<task>
  <instructions>Analyze the given code for readability issues.</instructions>
  <system>You are a code quality expert focused on readability.</system>
  <model>claude-3-sonnet</model>
  <!-- The criteria element provides a free-form description used for dynamic evaluation template selection via associative matching -->
  <criteria>validate, log</criteria>
  <inputs>
    <input name="code">The code to analyze</input>
  </inputs>
  <output_format type="json" schema="object" />
  <manual_xml>false</manual_xml>
  <disable_reparsing>false</disable_reparsing>
</task>
```

### Validation Rules

1. All required fields must be present
2. Input names must be unique
3. Boolean fields must be "true" or "false"
4. Model must be a valid LLM identifier
5. Output schema must match basic type validation rules
6. Template parameters must match call arguments

### Error Response Schema

```xml
<xs:complexType name="TaskError">
  <xs:choice>
    <xs:element name="resource_exhaustion">
      <xs:complexType>
        <xs:sequence>
          <xs:element name="resource" type="xs:string"/>
          <xs:element name="message" type="xs:string"/>
          <xs:element name="metrics" type="MetricsType" minOccurs="0"/>
        </xs:sequence>
      </xs:complexType>
    </xs:element>
    <xs:element name="task_failure">
      <xs:complexType>
        <xs:sequence>
          <xs:element name="reason" type="TaskFailureReason"/>
          <xs:element name="message" type="xs:string"/>
          <xs:element name="details" type="DetailsType" minOccurs="0"/>
        </xs:sequence>
      </xs:complexType>
    </xs:element>
  </xs:choice>
</xs:complexType>

<xs:simpleType name="TaskFailureReason">
  <xs:restriction base="xs:string">
    <xs:enumeration value="context_retrieval_failure"/>
    <xs:enumeration value="context_matching_failure"/>
    <xs:enumeration value="context_parsing_failure"/>
    <xs:enumeration value="xml_validation_failure"/>
    <xs:enumeration value="output_format_failure"/>
    <xs:enumeration value="execution_timeout"/>
    <xs:enumeration value="execution_halted"/>
    <xs:enumeration value="subtask_failure"/>
    <xs:enumeration value="input_validation_failure"/>
    <xs:enumeration value="unexpected_error"/>
  </xs:restriction>
</xs:simpleType>
```

### Interface Mapping

This schema is used by the TaskSystem component. For implementation details and interface definitions, see:
- TaskTemplate interface in spec/types.md [Type:TaskSystem:TaskTemplate:1.0]
- Template validation in TaskSystem.validateTemplate() 
- Template parsing in TaskSystem constructor

Note: The new XML attributes (`ref` and `subtype`) and the `<cond>` element map to the corresponding types (i.e., TaskDefinition and FunctionCall) used in the Task System.

### Map Pattern Implementation
Refer to the XML schema for correct usage. For a complete example, please see the Task System documentation.
