import os

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
        