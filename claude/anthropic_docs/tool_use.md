# Tool Use with Claude

Claude is capable of interacting with external client-side tools and functions, allowing you to equip Claude with your own custom tools to perform a wider variety of tasks.

## How Tool Use Works

Tool use with Claude follows these steps:

1. **Provide Claude with tools and a user prompt**
   - Define tools with names, descriptions, and input schemas in your API request
   - Include a user prompt that might require these tools

2. **Claude decides to use a tool**
   - Claude assesses if any tools can help with the user's query
   - If yes, Claude constructs a properly formatted tool use request
   - The API response has a `stop_reason` of `tool_use`, signaling Claude's intent

3. **Extract tool input, run code, and return results**
   - Extract the tool name and input from Claude's request
   - Execute the actual tool code client-side
   - Continue the conversation with a new `user` message containing a `tool_result` content block

4. **Claude uses tool result to formulate a response**
   - Claude analyzes the tool results to craft its final response to the original user prompt

**Important**: Claude does not have access to any built-in server-side tools. All tools must be explicitly provided by you in each API request.

## Implementing Tool Use

### Choosing a Model

- **For complex tools and ambiguous queries**: Use Claude 3.7 Sonnet, Claude 3.5 Sonnet, or Claude 3 Opus
- **For straightforward tools**: Use Claude 3.5 Haiku or Claude 3 Haiku (but note they may infer missing parameters)

### Specifying Tools

Tools are specified in the `tools` top-level parameter of the API request. Each tool definition includes:

| Parameter | Description |
|-----------|-------------|
| `name` | The name of the tool. Must match the regex `^[a-zA-Z0-9_-]{1,64}$`. |
| `description` | A detailed plaintext description of what the tool does, when it should be used, and how it behaves. |
| `input_schema` | A JSON Schema object defining the expected parameters for the tool. |

Example tool definition:

```json
{
  "name": "get_weather",
  "description": "Get the current weather in a given location",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "The city and state, e.g. San Francisco, CA"
      },
      "unit": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "The unit of temperature, either 'celsius' or 'fahrenheit'"
      }
    },
    "required": ["location"]
  }
}
```

### Best Practices for Tool Definitions

- **Provide extremely detailed descriptions** (most important factor)
- Explain:
  - What the tool does
  - When it should be used (and when it shouldn't)
  - What each parameter means and how it affects the tool's behavior
  - Any important caveats or limitations
- Aim for at least 3-4 sentences per tool description, more for complex tools

### Controlling Claude's Output

#### Tool Choice Options

The `tool_choice` parameter controls how Claude selects tools:

- `auto`: Claude decides whether to use any provided tools (default when tools are provided)
- `any`: Claude must use one of the provided tools, but can choose which one
- `tool`: Claude must use a specific tool
- `none`: Claude cannot use any tools (default when no tools are provided)

Example of forcing a specific tool:
```json
tool_choice = {"type": "tool", "name": "get_weather"}
```

#### Chain of Thought

Claude often shows its reasoning process when using tools, especially with Claude 3 Opus. You can prompt Claude to show its reasoning by adding something like `"Before answering, explain your reasoning step-by-step in tags."` to the user message or system prompt.

#### Parallel Tool Use

By default, Claude may use multiple tools to answer a user query. You can disable this with `disable_parallel_tool_use=true` in the `tool_choice` field.

### Handling Tool Use and Tool Results

When Claude decides to use a tool, it returns a response with:
- `stop_reason` of `tool_use`
- One or more `tool_use` content blocks containing:
  - `id`: A unique identifier for this tool use
  - `name`: The name of the tool being used
  - `input`: An object with the input parameters

To respond with tool results:
1. Extract the tool name, ID, and input
2. Run the actual tool in your codebase
3. Continue the conversation with a new message containing a `tool_result` block with:
   - `tool_use_id`: The ID from the original tool use request
   - `content`: The result as a string or list of content blocks
   - `is_error` (optional): Set to `true` if the tool execution failed

### Troubleshooting Errors

Common error types:
- **Tool execution errors**: Return with `"is_error": true` and the error message
- **Max tokens exceeded**: Retry with a higher `max_tokens` value
- **Invalid tool name or missing parameters**: Return an error result and Claude will try again

## Pricing

Tool use requests are priced like other Claude API requests, based on:
- Input tokens (including tool definitions)
- Output tokens generated
- A special system prompt (varies by model)

## Example Use Cases

- **Single tool**: Weather lookup, calculator, database query
- **Multiple tools**: Weather + time lookup, search + summarize
- **Sequential tools**: Get location → get weather for that location
- **JSON output**: Use tools to get structured data following a schema
