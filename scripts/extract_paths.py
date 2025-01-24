from pathlib import Path
from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput
import sys

def extract():
    """
    Create a new chart type based on the given description.
    """

    # Read the spec from 'new-chart-type.md'
    spec_path = Path.cwd() / "extract_paths.md"
    if not spec_path.exists():
        raise FileNotFoundError(
            "extract_paths.md not found in current directory - please make sure it exists"
        )
    with open(spec_path, "r") as spec_file:
        spec_content = spec_file.read()

    # Include the description in the spec prompt
    spec_prompt = spec_content

    # Setup BIG THREE: context, prompt, and model

    # Files to be edited
    context_editable = [
        "scripts/edit_paths.txt",
    ]

    # Files that are read-only references
    context_read_only = [
        "scripts/tochange.yaml",
    ]

    # Define the prompt for the AI model
    prompt = spec_prompt

    # Initialize the AI model
    model = Model(
        "claude-3-5-sonnet-20241022",
        editor_edit_format="whole",
    )

    # Initialize the AI Coding Assistant
    coder = Coder.create(
        main_model=model,
        edit_format="whole",
        io=InputOutput(yes=True),
        fnames=context_editable,
        read_only_fnames=context_read_only,
        auto_commits=False,
        suggest_shell_commands=False,
    )

    # Run the code modification
    coder.run(prompt)


if __name__ == "__main__":
    extract()


