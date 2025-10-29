import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
    ]
)


arguments = sys.argv
if len(arguments) < 2:
    print("Prompt is empty!")
    sys.exit(1)


user_prompt = arguments[1]


messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]


response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=messages,
    config=types.GenerateContentConfig(tools=[available_functions],system_instruction=system_prompt),
)

if '--verbose' in arguments:
    print(f"User prompt: {user_prompt}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
print(response.text)
# print(response.function_calls)
for function_call_part in response.function_calls:
    print(f"Calling function: {function_call_part.name}({function_call_part.args})")
sys.exit(0)