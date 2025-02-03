# System Protocols

## Task Template Schema [Contract:Tasks:TemplateSchema:1.0]

Interface: See TaskTemplate interface in [Type:TaskSystem:TaskTemplate:1.0] (spec/types.md)

The task template schema defines the structure for task template XML files and maps to the TaskTemplate interface:

### XML Schema Definition

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="task">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="description" type="xs:string"/>
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
              <xs:element name="accumulate_data" type="xs:boolean" minOccurs="0"/>
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
    </xs:complexType>
  </xs:element>
</xs:schema>
```

### Required Fields

- `instructions`: Task instructions for the LLM (TaskTemplate.taskPrompt)
- `system`: System prompt defining LLM behavior (TaskTemplate.systemPrompt)
- `model`: Target LLM model (TaskTemplate.model)

### Optional Fields

- `inputs`: Named input definitions (TaskTemplate.inputs)
- `manual_xml`: Whether the task uses manual XML structure (TaskTemplate.isManualXML, default: false)
- `disable_reparsing`: Whether to disable automatic reparsing (TaskTemplate.disableReparsing, default: false)

### Example Template

```xml
<task>
  <instructions>Analyze the given code for readability issues.</instructions>
  <system>You are a code quality expert focused on readability.</system>
  <model>claude-3-sonnet</model>
  <inputs>
    <input name="code">The code to analyze</input>
  </inputs>
  <manual_xml>false</manual_xml>
  <disable_reparsing>false</disable_reparsing>
</task>
```

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

### Map Pattern Implementation

Map operations are implemented using sequential tasks:

```xml
<task type="sequential">
  <description>Process multiple items in parallel</description>
  <context_management>
    <inherit_context>false</inherit_context>
    <accumulate_data>true</accumulate_data>
    <accumulation_format>full_output</accumulation_format>
  </context_management>
  <steps>
    <task>
      <description>Process item 1</description>
      <inputs>
        <input name="data">data1</input>
      </inputs>
    </task>
    <task>
      <description>Process item 2</description>
      <inputs>
        <input name="data">data2</input>
      </inputs>
    </task>
  </steps>
</task>
```
