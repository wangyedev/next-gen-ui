from langchain.tools import Tool
from typing import Dict, Any, List, Callable
from pydantic import BaseModel, Field, create_model
import json


class DynamicToolGenerator:
    """
    Generates LangChain tools dynamically from JSON schemas.
    """

    @staticmethod
    def create_tool_from_schema(schema: Dict[str, Any]) -> Tool:
        """
        Create a LangChain tool from a component schema.
        """
        tool_def = schema.get("tool_definition", {})
        tool_name = tool_def.get("name", f"render_{schema['name'].lower()}")
        tool_description = tool_def.get("description", f"Render {schema['name']} component")
        
        # Create the tool function
        def tool_function(**kwargs) -> str:
            """
            The actual tool function that gets called by the LLM.
            Returns a JSON string representing the component.
            """
            # Validate input against schema (basic validation)
            required_params = tool_def.get("parameters", {}).get("required", [])
            for param in required_params:
                if param not in kwargs:
                    return json.dumps({
                        "error": f"Missing required parameter: {param}"
                    })
            
            # Create component response
            component_data = {
                "type": schema["name"].lower().replace(" ", "_"),
                **kwargs
            }
            
            return json.dumps({
                "component": component_data,
                "reasoning": f"Selected {schema['name']} component based on the provided data"
            })

        # Create parameter schema for the tool
        parameters_schema = DynamicToolGenerator._create_parameter_schema(tool_def)
        
        # Create the tool
        tool = Tool(
            name=tool_name,
            description=tool_description,
            func=tool_function,
            args_schema=parameters_schema
        )
        
        return tool

    @staticmethod
    def _create_parameter_schema(tool_def: Dict[str, Any]) -> BaseModel:
        """
        Create a Pydantic model for tool parameters from the schema definition.
        """
        parameters = tool_def.get("parameters", {})
        properties = parameters.get("properties", {})
        required_fields = set(parameters.get("required", []))
        
        # Build field definitions for Pydantic model
        field_definitions = {}
        
        for param_name, param_def in properties.items():
            param_type = DynamicToolGenerator._get_python_type(param_def)
            
            # Determine if field is required
            if param_name in required_fields:
                field_definitions[param_name] = (
                    param_type,
                    Field(description=param_def.get("description", ""))
                )
            else:
                field_definitions[param_name] = (
                    param_type,
                    Field(default=None, description=param_def.get("description", ""))
                )
        
        # Create dynamic Pydantic model
        if field_definitions:
            return create_model("ToolParameters", **field_definitions)
        else:
            # Return empty model if no parameters
            class EmptyParameters(BaseModel):
                pass
            return EmptyParameters

    @staticmethod
    def _get_python_type(param_def: Dict[str, Any]):
        """
        Convert JSON schema type to Python type for Pydantic.
        """
        param_type = param_def.get("type", "string")
        
        if param_type == "string":
            return str
        elif param_type == "integer":
            return int
        elif param_type == "number":
            return float
        elif param_type == "boolean":
            return bool
        elif param_type == "array":
            return List[Dict[str, Any]]  # Simplified array type
        elif param_type == "object":
            return Dict[str, Any]
        else:
            return str  # Default fallback

    @staticmethod
    def create_tools_from_schemas(schemas: List[Dict[str, Any]]) -> List[Tool]:
        """
        Create multiple tools from a list of schemas.
        """
        tools = []
        
        for schema in schemas:
            try:
                tool = DynamicToolGenerator.create_tool_from_schema(schema)
                tools.append(tool)
            except Exception as e:
                print(f"Error creating tool for schema {schema.get('name', 'unknown')}: {e}")
                continue
        
        return tools

    @staticmethod
    def get_tool_names(schemas: List[Dict[str, Any]]) -> List[str]:
        """
        Get list of tool names that would be generated from schemas.
        """
        tool_names = []
        
        for schema in schemas:
            tool_def = schema.get("tool_definition", {})
            tool_name = tool_def.get("name", f"render_{schema['name'].lower()}")
            tool_names.append(tool_name)
        
        return tool_names