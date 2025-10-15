import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


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
)

if '--verbose' in arguments:
    print(f"User prompt: {user_prompt}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
print(response.text)

sys.exit(0)