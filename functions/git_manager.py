import subprocess
from google.genai import types

def manage_git(working_directory: str, git_command: str) -> str:
    """Executes a git command safely inside the Project Directory"""
    try:
        # Stripping Git from the start if the model accidentally included it
        if git_command.startswith("git "):
            git_command = git_command[4:]
        
        command = ["git"] + git_command.split()
        print(f"Executing Git: {' '.join(command)}")

        result = subprocess.run(
            command,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            return f"Git output:\n{result.stdout.strip()}"
        else:
            return f"Git Error:\n{result.stderr.strip()}"
    
    except subprocess.TimeoutExpired:
        return "Error: Git command timed out."
    except Exception as e:
        return f"System failure during git execution: {e}"

schema_manage_git = types.FunctionDeclaration(
    name="manage_git",
    description="Executes a git command of choosing inside the working directory. Use this to stage file, commit changes, check status or restore broken files.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "git_command": types.Schema(
                type=types.Type.STRING,
                description="The exact git arguments to run (e.g., 'status', 'commit -m\"fixed bugs\"', 'restore main.py'). Do not include the word 'git' at the beginning.",
            )
        },
        required=["git_command"]
    ),
)