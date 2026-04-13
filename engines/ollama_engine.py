import ollama
from engines.schema_mapper import map_gemini_schema_to_ollama

def run_local_model(messages, gemini_tool_schemas, system_prompt):
    """Handles local execution via Ollama daemon"""

    # 1. Translating the tools
    mapped_tools = map_gemini_schema_to_ollama(gemini_tool_schemas)

    # 2. Formatting the messages
    # Gemini uses a specific Part/Content structure. We need to extract the raw text
    # for Ollama's simple [{'role': '...', 'content': '...'}]
    ollama_messages = [{"role": "system", "content": system_prompt}]

    for msg in messages:
        if hasattr(msg, 'role') and hasattr(msg, 'role'):
            # Basic extraction for standard text messages
            for part in msg.parts:
                if hasattr(part, 'text') and part.text:
                    ollama_messages.append({'role': msg.role, 'content': part.text})
    
    # 3. Calling the Local Daemon
    response = ollama.chat(
        model='gemma4', # This statement assumes we already have `ollama run gemma` in our terminal
        messages=ollama_messages,
        tools=mapped_tools,
    )
    
    return response