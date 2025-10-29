import os
from functions.config import MAX_CHARS
from google.genai import types

def get_file_content(working_directory, file_path):
    # print(f"working_directory: {working_directory}")
    # print(f"file_path: {file_path}")
    joint_directory = os.path.join(working_directory, file_path)
    # print(f"joint_directory: {joint_directory}")
    abs_path = os.path.abspath(joint_directory)
    # directories = os.listdir(working_directory)
    # for data in directories:
        # print(data)
    if working_directory not in abs_path:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(joint_directory):
        # joint_directory_path = joint_directory.split("/")
        # print(joint_directory_path)
        # new_working_directory = "/".join(joint_directory_path[:-1])
        # print(f"new_working_directory: {new_working_directory}")
        # print(f"joint_directory: {joint_directory}")
        # directories_2 = os.listdir(new_working_directory)
        # print(directories_2)
        return f'Error: File not found or is not a regular file: "{file_path}"'
    with open(abs_path, 'r') as f:
        file_content_string = f.read(MAX_CHARS+1)
        if len(file_content_string) > MAX_CHARS:
            file_content_string = file_content_string[:-1]
            file_content_string += f'\n[...File "{file_path}" truncated at 10000 characters]'
        return file_content_string


schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Returns the contents of the specified files, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to read and return the contents from, relative to the working directory. If not provided, then do nothing.",
            ),
        },
    ),
)