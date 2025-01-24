from pathlib import Path
from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput
import sys
import json

def extract():
    """
    Extract paths and questions from tochange.yaml into JSON files.
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

    # Read the generated tochange.yaml to extract questions
    yaml_path = Path.cwd() / "tochange.yaml"
    if yaml_path.exists():
        with open(yaml_path, "r") as f:
            content = f.read()
            # Extract questions section
            questions_section = ""
            if "# Questions for Clarification" in content:
                questions_section = content.split("# Questions for Clarification")[1].strip()
            
            # Convert bullet points to list
            questions = []
            for line in questions_section.split("\n"):
                line = line.strip()
                if line.startswith("- ") or line.startswith("* "):
                    questions.append(line[2:])
                elif line and not line.startswith("#"):
                    questions.append(line)
            
            # Write questions to JSON
            questions_json = {"questions": questions}
            with open("questions.json", "w") as qf:
                json.dump(questions_json, qf, indent=2)


if __name__ == "__main__":
    extract()


