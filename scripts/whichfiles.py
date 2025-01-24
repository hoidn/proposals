from pathlib import Path
from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput
import sys

# TODO: 
# REPLACE read-only files with ['context']
# set editable files to empty list
# set architect model to ol-preview

def whichfiles(description: str):
    """
    Create a new chart type based on the given description.

    Args:
        description (str): Description of the new chart type to generate.
    """

    # Read the spec from 'new-chart-type.md'
    spec_path = Path.cwd() / "whichfiles.md"
    if not spec_path.exists():
        raise FileNotFoundError(
            "whichfiles.md not found in current directory - please make sure it exists"
        )
    with open(spec_path, "r") as spec_file:
        spec_content = spec_file.read()

    # Include the description in the spec prompt
    spec_prompt = spec_content.replace("<description>", description)

    # Setup BIG THREE: context, prompt, and model

    # Files to be edited
    context_editable = [
        "tochange.yaml",
    ]

    # Files that are read-only references
    context_read_only = [
        "scripts/context",
    ]

    # Define the prompt for the AI model
    prompt = spec_prompt

    # Initialize the AI model
    model = Model(
        "claude-3-5-sonnet-20241022",
        editor_edit_format="diff",
    )

    # Initialize the AI Coding Assistant
    coder = Coder.create(
        main_model=model,
        edit_format="diff",
        max_reflections=1,
        io=InputOutput(yes=True),
        fnames=context_editable,
        read_only_fnames=context_read_only,
        auto_commits=False,
        suggest_shell_commands=False,
    )

    # Run the code modification
    coder.run(prompt)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python whichfiles.py '<description>'")
        sys.exit(1)

    description = sys.argv[1]
    whichfiles(description)

