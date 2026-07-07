import os
from functions.config import MAX_CHARS, is_safe_path
from google.genai import types

# Description for the function listed in the schema section at the bottom, check out that!
# And, comments left for easy debugging purposes
def get_file_content(working_directory, file_path):
    # print(f"working_directory: {working_directory}")
    # print(f"file_path: {file_path}")
    joint_directory = os.path.join(working_directory, file_path)
    # print(f"joint_directory: {joint_directory}")
    abs_path = os.path.abspath(joint_directory)
    # directories = os.listdir(working_directory)
    # for data in directories:
        # print(data)
    if not is_safe_path(working_directory, file_path):
        return f'Error: Security Violation! Cannot Access {file_path} as it resides outside the permitted sandbox!'
    
    if not os.path.isfile(joint_directory):
        # print(f"joint_directory: {joint_directory}")
        return f'Error: File not found or is not a regular file: "{file_path}"'
    
    ALLOWED_EXTENSIONS = {'.py', '.md', '.json', '.env', '.csv', '.toml'}
    ALLOWED_EXACT_NAMES = {"Makefile", "LICENSE"}

    file_name = os.path.basename(abs_path)
    _, ext = os.path.splittext(abs_path)

    # Blocking the read if the extension isn't whitelisted in the prior Allowed Sets
    if ext.lower() not in ALLOWED_EXTENSIONS and file_name not in ALLOWED_EXACT_NAMES:
        return(
            f"Error: Rerading files with '{ext}' is blocked.",
            f"Allowed Extensions are: {", ".join(ALLOWED_EXTENSIONS)}"
        )
    
    # Updated the reada logic with binary protection!
    try:
        with open(abs_path, 'r') as f:
            file_content_string = f.read(MAX_CHARS+1)
            if len(file_content_string) > MAX_CHARS:
                file_content_string = file_content_string[:-1]
                file_content_string += f'\n[...File "{file_path}" truncated at 10000 characters]'
            return file_content_string
    except UnicodeDecodeError:
        return f"Error: {file_path} appears to be a binary file. Cannot read as text."
    except Exception as e:
        return f"Error reading file '{file_path}': {str(e)}"


schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Returns the contents of the specified files, constrained to the working directory. Only text-based files are allowed.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The relative file path of the file to read the contents of, to the working directory.",
            ),
        },
        required=["file_path"]
    ),
)