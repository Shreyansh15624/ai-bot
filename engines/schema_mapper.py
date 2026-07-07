def map_gemini_schema_to_ollama(gemini_function_declarations):
    """
    Translates Google GenAI FunctionDeclarations into Ollama's expected JSOn tool format  
    """
    ollama_tools = []

    for schema in gemini_function_declarations:
        properties = {}

        # Iterating through the proeprties defined within the Gemini Schema
        if schema.parameters and schema.parameters.properties:
            for prop_name, prop_schema in schema.parameters.properties.items():
                # Converting Gemini Enum types to a lowercase string
                prop_type= prop_schema.type.name.lower() if hasattr(prop_schema.type, 'name') else "string"

                properties[prop_name] = {
                    "type": prop_type,
                    "description": prop_schema.description,
                }
            
        # Constructing the final JSON dictionary for Ollama
        ollama_tool = {
            "type": "function",
            "function": {
                "name": schema.name,
                "description": schema.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    # We will enforce that all defined proeprties are required for the local model
                    "required": list(properties.keys()),
                }
            }
        }
        ollama_tools.append(ollama_tool)
    return ollama_tools