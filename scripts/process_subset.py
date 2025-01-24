from pathlib import Path
from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput
import sys
import json

def process_subset(description: str):
    """
    Process a subset of files according to the given description.

    Args:
        description (str): Description of the changes to make.
    """
    # Read the spec from process_subset.md
    spec_path = Path.cwd() / "process_subset.md"
    if not spec_path.exists():
        raise FileNotFoundError(
            "process_subset.md not found in current directory - please make sure it exists"
        )
    with open(spec_path, "r") as spec_file:
        spec_content = spec_file.read()

    # Include the description in the spec prompt
    spec_prompt = spec_content.replace("<description>", description)

    # Read the list of files to process from edit_paths.json
    json_path = Path.cwd() / "edit_paths.json"
    if not json_path.exists():
        raise FileNotFoundError(
            "edit_paths.json not found in current directory - please make sure it exists"
        )
    with open(json_path, "r") as json_file:
        file_list = json.load(json_file)["files"]

    # Setup BIG THREE: context, prompt, and model

    # Files to be edited - use the list from edit_paths.json
    context_editable = file_list

    # No read-only files needed
    context_read_only = []

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
    if len(sys.argv) < 2:
        print("Usage: python process_subset.py '<description>'")
        sys.exit(1)

    description = sys.argv[1]
    process_subset(description)
