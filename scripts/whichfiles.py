from pathlib import Path
from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput
import sys

def main(description: str):
    """
    """

    spec_path = Path.cwd() / "whichfiles.md"
    if not spec_path.exists():
        raise FileNotFoundError(
            "whichfiles.md not found in current directory - please make sure it exists"
        )
    with open(spec_path, "r") as spec_file:
        spec_content = spec_file.read()

    # Include the description in the spec prompt
    # TODO: for each yaml key in the yaml file, replace the corresponding <key> with the value
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
        auto_commits=True,
        suggest_shell_commands=False,
    )

    # Run the code modification
    coder.run(prompt)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py '<description>'")
        sys.exit(1)

    # TODO: generalize to take a positional argument, a yaml file path 
    # the yaml file can contain an arbitrary number of key-value pairs
    # in this case, it would just be ('description', whatever the user typed)
    # TODO: the yaml file should also contain the following key: list of values maps,
    # replacing the current hard-coded values:
    # - context_editable
    # - context_read_only
    # TODO: the cli script should also take the spec path as an argument (hard-coded 
    # as 'whichfiles.md' currently)
    # TODO: use argparse for all this instead of simple sys.argv
    description = sys.argv[1]
    main(description)

