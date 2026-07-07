import ollama
from engines.schema_mapper import map_gemini_schema_to_ollama

def run_local_model(messages, gemini_tool_schemas, system_prompt, model_name="gemma4"):
    """Handles local execution via Ollama daemon"""

    # 1. Translating the tools
    mapped_tools = map_gemini_schema_to_ollama(gemini_tool_schemas)

    # 2. Formatting the messages
    # Gemini uses a specific Part/Content structure. We need to extract the raw text
    # for Ollama's simple [{'role': '...', 'content': '...'}]
    ollama_messages = [{"role": "system", "content": system_prompt}]

    for msg in messages:
        if not hasattr(msg, 'role'):
            continue

        content = ""
        tool_calls = []

        for part in msg.parts:
            # 1. Catching the standard texts
            if hasattr(part, 'text') and part.text:
                content += part.text
            
            # 2. Catching previous tool incvocations
            elif hasattr(part, 'function_call') and part.function_call:
                tool_calls.append({
                    "function": {
                        "name": part.function_call.name,
                        "arguments": dict(part.function_call.args)
                    }
                })
            
            # 3. Catching the raw tool responses
            elif hasattr(part, 'function_response') and part.function_response:
                content += f"\nTool Result: ({part.function_response.name}): {part.function_response.response}"
        
        # Building a clean dictionary for Ollama
        message_dict = {'role': msg.role, 'content': content.strip()}

        if tool_calls:
            # Attaching the 'tool calls' only if the assistant actually made them!
            message_dict['tool_calls'] = tool_calls
        
        ollama_messages.append(message_dict)
    
    # 3. Calling the Local Daemon
    response = ollama.chat(
        model=model_name,
        messages=ollama_messages,
        tools=mapped_tools,
    )
    
    return response