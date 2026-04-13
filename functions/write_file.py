import os
from google.genai import types
from functions.config import is_safe_path

# Descrption for the function listed in the schema section at the bottom, check out that!
# And, comments left for easy debugging purposes
def write_file(working_directory, file_path, content):
    if not is_safe_path(working_directory, file_path):
        return f'Error: Security Violation! Cannot Access {file_path} as it resides outside the permitted sandbox!'
    joint_directory = os.path.join(working_directory, file_path)
    abs_path = os.path.abspath(joint_directory)
    try:
        os.path.exists(file_path)
    except FileExistsError:
        return f'Error: File not found or is not a regular file: "{file_path}"'
    with open(abs_path, 'w') as f:
        f.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes to the specified file in the specified directory, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to write the supposed data to, relative to the working directory. If not already present, then create new with the provided name for the file.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content you are supposed to write to the file, relative to the file name in the working directory. If not specified cancel execution"
            )
        },
    ),
)