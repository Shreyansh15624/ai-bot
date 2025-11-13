import os
import sys
import subprocess
from google.genai import types

# Descrption for the function listed in the schema section at the bottom, check out that!
# And, comments left for easy debugging purposes
def run_python_file(working_directory, file_path, args=[]):
    joint_directory = os.path.join(working_directory, file_path)
    # print(f"joint_directory: {joint_directory}; type: {type(joint_directory)}")
    abs_path = os.path.abspath(joint_directory)
    if working_directory not in abs_path:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(joint_directory):
        return f'Error: File "{file_path}" not found.'
    if not file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    try:
        command = [sys.executable]
        command.append(file_path)
        # print(command)
        if args:
            # print(f'args: {args}')
            command.extend(args)
            # print(command)
            completed_process = subprocess.run(command, shell=False, capture_output=True, timeout=30, cwd=working_directory)
        else:
            # print(command)
            completed_process = subprocess.run(command, shell=False, capture_output=True, timeout=30, cwd=working_directory)
        stdout = completed_process.stdout.decode()
        stderr = completed_process.stderr.decode()
        formatted_lines = []
        if stdout:
            formatted_lines.append(f'STDOUT: {stdout}')
        if stderr:
            formatted_lines.append(f'STDERR: {stderr}')
        if completed_process.returncode != 0:
            formatted_lines.append(f'Process exited with code {completed_process.returncode}')
        if not formatted_lines:
            return 'No output is produced'
        final_output = "\n".join(formatted_lines)
        print(final_output)
        return final_output
    except Exception as e:
        return f"Error: executing Python file: {e}"

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes the specified python file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to execute and take output from, relative to the working directory. If not provided, then do nothing.",
            ),
            "args": types.Schema(
                type=types.Type.STRING,
                description="Optional, only pass anything at all if anything is already specified. If not specified, then do not pass anything."
            ),
        },
    ),
)