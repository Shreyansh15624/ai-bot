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

# Importing the new Engines
from engines.gemini_engine import run_gemini
from engines.ollama_engine import run_local_model

load_dotenv()

# The Master Toggle
USE_LOCAL_MODEL = True

# Hypnotizing AI for safety 👁️👄👁️ -> 😵‍💫 -> 🫡
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

# For the Switch case, to simplify code understanding & avoiding if-elif-else ladders
available_functions_enum = Enum("available_functions_enum", ["get_files_info", "get_file_content", "write_file", "run_python_file"])

global arguments # Because we are using in isolated functions too
arguments = sys.argv
if len(arguments) < 2:
    print("Prompt is empty!")
    sys.exit(1)


def call_function(function_call_part, working_directory):
    # This function is for calling the functions that allows our AI model to make changes to
    # the user project, in this case the Provided Example: "calculator/" App 
    try:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
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


user_prompt = arguments[1] if len(arguments) > 2 else "Prompt is empty!"
messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)]), ]

for i in range(20):
    # ---- NEW ROUTER BLOCK ----
    if USE_LOCAL_MODEL:
        print("🤖 Routing to Local Engine (Gemma 4 via Ollama)...")
        raw_response = run_local_model(messages, available_functions.function_declarations, system_prompt)

        class MockResponse: pass
        class MockCall: pass
        response = MockResponse()
        response.text = raw_response['message'].get('content', '')
        response.function_calls = []

        if 'tool_calls' in raw_response['message']:
            for tc in raw_response['message']['tool_calls']:
                mock_call = MockCall()
                mock_call.name = tc['function']['name']
                mock_call.args = tc['function']['arguments']
                response.function_calls.append(mock_call)
    
    else:
        print("☁️ Routing to Remote Engine (Gemini API)...")
        response = run_gemini(messages, available_functions, system_prompt)
    # ------------------------------------------

    print("------------------------------------------------------------------------")
    print(f"User Prompt: {user_prompt}")

    # Safe token printing (Local Models won't have usage_metadata formatted the same way)
    if not USE_LOCAL_MODEL:
        try:
            print(f"Prompt Tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response Tokens: {response.usage_metadata.candidates_token_count}")
            for candidate in response.candidates:
                messages.append(candidate.count)
        except Exception:
            pass

    function_call_responses = []

    if response.function_calls:
        for function_call_part in response.function_calls:
            print(f"Calling function: {function_call_part.name}({function_call_part.args})")
            arg_dict = {
                "function_call_part": function_call_part,
                "working_directory": "projects/calculator", # DO NOT CHANGE!!!
            }
            function_call_result = call_function(**arg_dict)
            print(function_call_result)
            call_responses = types.Part.from_function_response(
                name=function_call_part.name,
                response={"result": function_call_result},
            )
            function_call_responses.append(call_responses)

        packaged_function_call_result = types.Content(
            role="user",
            parts=function_call_responses,
        )
        messages.append(packaged_function_call_result)
    else:
        if response.text:
            print(f"\nModel's response.text: {response.text}")
            break

sys.exit(0)