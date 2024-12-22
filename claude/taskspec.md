# Task System Technical Specification

## 4. Internal Architecture

### 4.1 Key Components

### Core Types

// For template XML schema, see [Contract:Tasks:TemplateSchema:1.0] in docs/system/contracts/protocols.md

interface TaskTemplate {
  readonly taskPrompt: string;    // Maps to <instructions> in schema
  readonly systemPrompt: string;  // Maps to <system> in schema
  readonly model: string;         // Maps to <model> in schema
  readonly inputs?: Record<string, string>;
  readonly isManualXML?: boolean;     // Maps to <manual_xml> in schema
  readonly disableReparsing?: boolean;  // Maps to <disable_reparsing> in schema
}

// Error types
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

[Rest of original content...]