# Claude File Editor Tool

The Claude File Editor Tool allows Claude to view and modify text files, helping you debug, fix, and improve your code or other text documents. This enables Claude to directly interact with your files, providing hands-on assistance rather than just suggesting changes.

## Compatibility

The text editor tool is only available for specific Claude models:

- **Claude 3.7 Sonnet**: `text_editor_20250124`
- **Claude 3.5 Sonnet**: `text_editor_20241022`

Both versions provide identical capabilities - the version you use should match the model you're working with.

## Use Cases

The text editor tool is ideal for:

- **Code debugging**: Identifying and fixing bugs in your code, from syntax errors to logic issues
- **Code refactoring**: Improving code structure, readability, and performance through targeted edits
- **Documentation generation**: Adding docstrings, comments, or README files to your codebase
- **Test creation**: Creating unit tests for your code based on its understanding of the implementation

## Commands

The text editor tool supports several commands for viewing and modifying files:

### view

Examines the contents of a file or lists the contents of a directory.

Parameters:
- `command`: Must be "view"
- `path`: The path to the file or directory to view
- `view_range` (optional): An array of two integers specifying the start and end line numbers to view. Line numbers are 1-indexed, and -1 for the end line means read to the end of the file.

Example:
```json
{
  "type": "tool_use",
  "id": "toolu_01A09q90qw90lq917835lq9",
  "name": "str_replace_editor",
  "input": {
    "command": "view",
    "path": "primes.py"
  }
}
```

### str_replace

Replaces a specific string in a file with a new string.

Parameters:
- `command`: Must be "str_replace"
- `path`: The path to the file to modify
- `old_str`: The text to replace (must match exactly, including whitespace and indentation)
- `new_str`: The new text to insert in place of the old text

Example:
```json
{
  "type": "tool_use",
  "id": "toolu_01A09q90qw90lq917835lq9",
  "name": "str_replace_editor",
  "input": {
    "command": "str_replace",
    "path": "primes.py",
    "old_str": "for num in range(2, limit + 1)",
    "new_str": "for num in range(2, limit + 1):"
  }
}
```

### create

Creates a new file with specified content.

Parameters:
- `command`: Must be "create"
- `path`: The path where the new file should be created
- `file_text`: The content to write to the new file

Example:
```json
{
  "type": "tool_use",
  "id": "toolu_01A09q90qw90lq917835lq9",
  "name": "str_replace_editor",
  "input": {
    "command": "create",
    "path": "test_primes.py",
    "file_text": "import unittest\nimport primes\n\nclass TestPrimes(unittest.TestCase):\n    def test_is_prime(self):\n        self.assertTrue(primes.is_prime(2))\n        self.assertTrue(primes.is_prime(3))\n        self.assertFalse(primes.is_prime(4))\n\nif __name__ == '__main__':\n    unittest.main()"
  }
}
```

### insert

Inserts text at a specific location in a file.

Parameters:
- `command`: Must be "insert"
- `path`: The path to the file to modify
- `insert_line`: The line number after which to insert the text (0 for beginning of file)
- `new_str`: The text to insert

Example:
```json
{
  "type": "tool_use",
  "id": "toolu_01A09q90qw90lq917835lq9",
  "name": "str_replace_editor",
  "input": {
    "command": "insert",
    "path": "primes.py",
    "insert_line": 0,
    "new_str": "\"\"\"Module for working with prime numbers.\n\nThis module provides functions to check if a number is prime\nand to generate a list of prime numbers up to a given limit.\n\"\"\"\n"
  }
}
```

### undo_edit

Reverts the last edit made to a file.

Parameters:
- `command`: Must be "undo_edit"
- `path`: The path to the file whose last edit should be undone

Example:
```json
{
  "type": "tool_use",
  "id": "toolu_01A09q90qw90lq917835lq9",
  "name": "str_replace_editor",
  "input": {
    "command": "undo_edit",
    "path": "primes.py"
  }
}
```

## Error Handling

When using the text editor tool, various errors may occur:

### File not found

If Claude tries to view or modify a file that doesn't exist:

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
      "content": "Error: File not found",
      "is_error": true
    }
  ]
}
```

### Multiple matches for replacement

If Claude's `str_replace` command matches multiple locations in the file:

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
      "content": "Error: Found 3 matches for replacement text. Please provide more context to make a unique match.",
      "is_error": true
    }
  ]
}
```

### No matches for replacement

If Claude's `str_replace` command doesn't match any text in the file:

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
      "content": "Error: No match found for replacement. Please check your text and try again.",
      "is_error": true
    }
  ]
}
```

### Permission errors

If there are permission issues with creating, reading, or modifying files:

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
      "content": "Error: Permission denied. Cannot write to file.",
      "is_error": true
    }
  ]
}
```

## Implementation Best Practices

### Provide clear context

When asking Claude to fix or modify code, be specific about what files need to be examined or what issues need to be addressed.

**Less helpful prompt**: "Can you fix my code?"
**Better prompt**: "There's a syntax error in my primes.py file that prevents it from running. Can you fix it?"

### Be explicit about file paths

Specify file paths clearly when needed, especially if you're working with multiple files or files in different directories.

**Less helpful prompt**: "Review my helper file"
**Better prompt**: "Can you check my utils/helpers.py file for any performance issues?"

### Create backups before editing

Implement a backup system in your application that creates copies of files before allowing Claude to edit them, especially for important or production code.

### Handle unique text replacement carefully

The `str_replace` command requires an exact match for the text to be replaced. Your application should ensure that there is exactly one match for the old text or provide appropriate error messages.

### Verify changes

After Claude makes changes to a file, verify the changes by running tests or checking that the code still works as expected.

## Pricing and Token Usage

The text editor tool uses the same pricing structure as other tools used with Claude. It follows the standard input and output token pricing based on the Claude model you're using.

In addition to the base tokens, the following additional input tokens are needed for the text editor tool:

| Tool | Additional input tokens |
|------|-------------------------|
| `text_editor_20241022` (Claude 3.5 Sonnet) | 700 tokens |
| `text_editor_20250124` (Claude 3.7 Sonnet) | 700 tokens |

## Integration with Other Tools

The text editor tool can be used alongside other Anthropic-defined tools like the computer use tool. When combining these tools, you'll need to:

1. Include the appropriate beta header (if using with computer use)
2. Match the tool version with the model you're using
3. Account for the additional token usage for all tools included in your request
