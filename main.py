import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import get_files_info, schema_get_files_info
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.write_file import write_file, schema_write_file
from functions.run_python_file import run_python_file, schema_run_python_file
from enum import Enum
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ]
)


available_functions_dict = {
    "get_files_info" : get_files_info,
    "get_file_content" : get_file_content,
    "write_file" : write_file,
    "run_python_file" : run_python_file
}

available_functions_enum = Enum("available_functions_enum", ["get_files_info", "get_file_content", "write_file", "run_python_file"])

global arguments
arguments = sys.argv
if len(arguments) < 2:
    print("Prompt is empty!")
    sys.exit(1)


def call_function(function_call_part, working_directory, verbose=False):
    try:
        if verbose:
            print(f"Calling function: {function_call_part.name}({function_call_part.args})")
        else:
            print(f" - Calling function: {function_call_part.name}")
        match function_call_part.name:
            case available_functions_enum.write_file.name:
                arg_dict_2 = {
                    "working_directory" : working_directory,
                    "file_path" : function_call_part.args["file_path"],
                    "content" : function_call_part.args["content"]
                }
                function_result = available_functions_dict[function_call_part.name](**arg_dict_2)
            case available_functions_enum.get_file_content.name:
                arg_dict_2 = {
                    "working_directory" : working_directory,
                    "file_path" : function_call_part.args["file_path"]
                }
                function_result = available_functions_dict[function_call_part.name](**arg_dict_2)
            case available_functions_enum.get_files_info.name:
                arg_dict_2 = {
                    "working_directory" : working_directory,
                    "directory" : (function_call_part.args["directory"] if "directory" in function_call_part.args else ".")
                }
                function_result = available_functions_dict[function_call_part.name](**arg_dict_2)
            case available_functions_enum.run_python_file.name:
                arg_dict_2 = {
                    "working_directory" : working_directory,
                    "file_path": function_call_part.args["file_path"]
                }
                function_result = available_functions_dict[function_call_part.name](**arg_dict_2)
        if not function_call_part.name:
            function_call_result = types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=available_functions_dict[function_call_part.name],
                        response={"error": f"Unknown function: {function_call_part.name}"},
                    )
                ],
            )
            return function_call_result.parts[0].function_response.response["result"]
        else:
            function_call_result = types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_call_part.name,
                        response={"result":function_result},
                    )
                ],
            )
            return function_call_result.parts[0].function_response.response["result"]
    except Exception as e:
        return f'Error: Executing Function: {e}'


user_prompt = arguments[1]


messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)]), ]
for message in messages:
    print(f"message:\n{messages}\n")
print("DEBUG: About to start main loop")
for i in range(20):
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt
        ),
    )
    verbose = False
    if '--verbose' in arguments:
        verbose = True
        print("------------------------------------------------------------------")
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    for candidate in response.candidates:
        messages.append(candidate.content)
    # print(f"\nresponse.function_calls:\n{response.function_calls}")
    function_call_responses = []
    if response.function_calls:
        for function_call_part in response.function_calls:
            print(f"Calling function: {function_call_part.name}({function_call_part.args})")
            arg_dict = {
                "function_call_part" : function_call_part,
                "working_directory" : "calculator",
                "verbose" : verbose,
            }
            # print("\n")
            function_call_result = call_function(**arg_dict)
            print(function_call_result)
            call_responses = types.Part.from_function_response(
                name=function_call_part.name,
                response={"result": function_call_result}
            )
            function_call_responses.append(call_responses)
        packaged_function_call_result = types.Content(
            role="user",
            parts=function_call_responses
        )
        messages.append(packaged_function_call_result)
    else:
        if response.text:
            print(f"\nModel's response.text:\n{response.text}")
            break

sys.exit(0)
