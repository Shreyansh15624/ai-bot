import os
import ast
from functions.config import is_safe_path
from google.genai import types

# Description for the function listed in the schema section at the bottom, check out that!
# And, comments left for easy debugging purposes
def get_code_outline(working_directory, file_path):
    if not is_safe_path(working_directory, file_path):
        return f"Error: Security Violation! Casnnot access {file_path} as it resides outside the permitted sandbox!"

    joint_directory = os.path.join(working_directory, file_path)
    abs_path = os.path.abspath(joint_directory)
    
    if not os.path.isfile(abs_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    
    # The AST parser only works on the Python Code
    if not abs_path.endswith(".py"):
        return "Error: 'get_code_outline' only works on python (.py) files!"
    
    try:
        with open(abs_path, 'r', encoding="utf-8") as f:
            source = f.read()
        
        tree = ast.parse(source)
        outline = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                outline.append(f"class {node.name}:")
                for sub_node in node.body:
                    if isinstance(sub_node, ast.FunctionDef):
                        args = ast.unparse(sub_node.args)
                        outline.append(f"    def {sub_node.name}({args}):")
            elif isinstance(node, ast.FunctionDef):
                args = args.unparse(node.args)
                outline.append(f"def {node.name}({args}):")
        
        if not outline:
            return f"File '{file_path}' containes no classes or functions."
        
        return "\n".join(outline)
    
    except SyntaxError as e:
        return f"Error: Syntax error in file '{file_path}'. Cannot parse AST. Details: {str(e)}"
    except Exception as e:
        return f"Error parsing file '{file_path}': {str(e)}"

schema_get_code_outline = types.FunctionDeclaration(
    name="get_code_outline",
    description="Reads a python file and returns a lightweight structural map of the classes and fucntions using AST.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The relative path to the python file you want to outline."
            )
        },
        required=["file_path"]
    ),
)