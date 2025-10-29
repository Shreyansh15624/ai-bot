import os
from google.genai import types

def write_file(working_directory, file_path, content):
    joint_directory = os.path.join(working_directory, file_path)
    abs_path = os.path.abspath(joint_directory)
    if working_directory not in abs_path:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    try:
        os.path.exists(file_path)
    except FileExistsError:
        return f'Error: File not found or is not a regular file: "{file_path}"'
    with open(abs_path, 'w') as f:
        f.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes to the specificed file in the specified directory, constrained to the working directory.",
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