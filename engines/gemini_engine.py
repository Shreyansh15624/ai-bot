import os
from google import genai
from google.genai import types

def run_gemini(messages, available_functions, system_prompt):
    """Handle's the API calls to Google Gemini servers"""
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        content=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
        ),
    )
    return response