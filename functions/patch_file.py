import os
from google.genai import types
from functions.config import is_safe_path

# Description for the function listed in the schema section at the bottom, check out that!
# And, comments left for easy debugging purposes
def patch_file(working_directory, file_path, search_block, replace_block):
    if not is_safe_path(working_directory, file_path):
        return f'Error: Security Violation! Cannot Access {file_path} as it resides outside the permitted sandbox!'
    
    joint_directory = os.path.join(working_directory, file_path)
    abs_path = os.path.abspath(joint_directory)
    
    try:
        os.path.exists(file_path)
    except FileExistsError:
        return f'Error: File not found or is not a regular file: "{file_path}".'
    
    try:
        with open(abs_path, 'r', encoding="utf-8") as f:
            content = f.read()
        
        if search_block not in content:
            return (
                f"Error: The exact search block was not found in '{file_path}'.",
                "Make sure spacing, indentation and characters match perfectly"
            )
        
        # Replacing only the first occurrence to prevent accidental overrides anywhere else!
        updated_content = content.replace(search_block, replace_block, 1)

        with open(abs_path, 'w') as f:
            f.write(updated_content)
        
        return f'Successfully patched "{file_path}".'
    
    except Exception as e:
        return f"Error patching file: '{file_path}': {str(e)}"

schema_patch_file = types.FunctionDeclaration(
    name="patch_file",
    description="Applies targeted modifications to an existing file using a strict search-and-replace block.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to write the supposed data to, relative to the working directory. If not already present, then create new with the provided name for the file.",
            ),
            "search_block": types.Schema(
                type=types.Type.STRING,
                description="This is the exact original block of code to find & it must match the spacing & the indetation perfectly.",
            ),
            "replace_block": types.Schema(
                type=types.Type.STRING,
                description="This is the new block of code to be inserted in place of the search block. Calculate the insertion carefully and make sure that it doesn't cause any errors."
            ),
        },
        required=["file_path", "search_block", "replace_block"]
    ),
)