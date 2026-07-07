import os
from functions.config import is_safe_path
from google.genai import types

def delete_file(working_directory: str, file_path: str) -> None:
    """Safely deletes a specificed file within the working directory"""
    joint_directory = os.path.join(working_directory, file_path)
    abs_path = os.path.abspath(joint_directory)

    # 1. An Absolute Security Failsafe!
    if not is_safe_path(working_directory, file_path):
        return f"Error: Security Violation! Cannot delete {file_path} as it resides outside the permitted sandbox!"
    
    # 2. Checking if the file actually exists?
    if not os.path.exists(abs_path):
        return f"Error: Cannot delete '{file_path}' because it does not exist."
    
    # 3. Ensuring its actually a file & not a directory!
    if not os.path.isfile(abs_path):
        return f"Error: '{file_path}' is a directory & not a file. This tool only deletes individual files"
    
    try:
        os.remove(abs_path)
        return f"Success: File '{file_path}' has been permanently deleted."
    except PermissionError:
        return f"Error: Permission denied when trying to delete '{file_path}'!"
    except Exception as e:
        return f"Error deleting file '{file_path}': {str(e)}"

schema_delete_file = types.FunctionDeclaration(
    name="delete_file",
    description="Permanently deletes a specified file within the working directory. Use this to clean up old scripts, remove deprecated code, or delete temporary text files.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The relative file path of the file to delete (e.g., 'old_script.py' or 'some_folder/useless.txt')."
            )
        },
        required=["file_path"]
    ),
)