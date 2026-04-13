import subprocess
from google.genai import types

def search_codebase(working_directory: str, keyword: str):
    """
    Safely executes a read-only shell command to search the codebase.
    """
    tt = 5 # dynamic definition
    try:
        # We construct the shell command safely as a list to prevent shell injection
        command = ['grep', '-r', keyword, '.']

        print(f"Executing Shell: {' '.join(command)}")

        # subprocess.run is strictly locked to the working directory
        result = subprocess.run(
            command,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=tt, # A 5 second guillotine, so the LLM doesn't hang the system up
        )

        # Return codes: 0 is 'found', 1 is 'not found', >1 is an 'error'
        if result.returncode == 0 and result.stdout:
            # Truncating to 2000 chars so the massive grep outputs don't crash the context window
            return result.stdout[:2000]
        elif result.returncode == 1:
            return f"No matches foud for '{keyword}'."
        else:
            return f"Search error: {result.stderr}."
        
    except subprocess.TimeoutExpired:
        return f"Error: Shell execution after timeout of {tt} seconds"
    
    except Exception as e:
        return f"Error: System failure during shell execution: {e}"
    
schema_search_codebase = types.FunctionDeclaration(
    name="search_codebase",
    description="Searched the entire project directory for a specific keyword or string using a secure shell command. Returns the file names, line numbers, and the matching code.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "keyword": types.Schema(
                type=types.Type.STRING,
                description="This is the specific keyword, variable name or string value you want to search for."
            )
        },
        required=["keyword"]
    )
)