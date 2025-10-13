"""
Utilities for enhancing MCP tool descriptions with Pydantic schema information.
"""

from typing import Any, Dict, Type, Union, List
from pydantic import BaseModel
import json


def create_enhanced_tool_description(
    base_description: str,
    model_class_or_list: Union[Type[BaseModel], List[Type[BaseModel]]],
    parameter_name: str = "data",
    include_full_schema: bool = False
) -> str:
    """
    Create an enhanced tool description that includes Pydantic model schema information
    to help AI agents understand parameter requirements and constraints.
    Handles both a single Pydantic model class and a list of them.
    
    Args:
        base_description: The basic description of what the tool does
        model_class_or_list: The Pydantic model class or a list of Pydantic model classes
        parameter_name: The name of the parameter that uses this model
        include_full_schema: Whether to include the complete JSON schema
        
    Returns:
        Enhanced description with schema information
    """
    
    description_parts = [base_description]
    
    models_to_process = []
    if isinstance(model_class_or_list, list):
        models_to_process = model_class_or_list
    else:
        models_to_process = [model_class_or_list]
    
    if len(models_to_process) > 1:
        description_parts.append(
            f"\nThe structure of the '{parameter_name}' parameter can be one of the following, "
            f"depending on context (e.g., another parameter like 'config_type'):"
        )

    for model_class in models_to_process:
        # This is the line that caused the error. Now it's inside a loop and model_class is guaranteed to be a model.
        schema = model_class.model_json_schema()
        model_name = schema.get('title', model_class.__name__)

        if len(models_to_process) > 1:
            description_parts.append(f"\n--- Schema for '{model_name}' ---")
        
        # Extract key information
        required_fields = schema.get('required', [])
        properties = schema.get('properties', {})
        
        # Add a blank line for single model descriptions to match original formatting
        if len(models_to_process) == 1:
            description_parts.append("")

        if required_fields:
            description_parts.append(f"REQUIRED fields for {parameter_name}:")
            for field in required_fields:
                field_info = properties.get(field, {})
                field_type = field_info.get('type', 'unknown')
                
                # Handle enum/literal values
                if 'enum' in field_info:
                    enum_values = field_info['enum']
                    description_parts.append(f"  • {field}: {field_type} - Must be one of: {enum_values}")
                else:
                    description_parts.append(f"  • {field}: {field_type}")
                    
                # Add field description if available
                if 'description' in field_info:
                    description_parts.append(f"    {field_info['description']}")
        
        # List optional fields with constraints
        optional_fields = []
        for field_name, field_info in properties.items():
            if field_name not in required_fields:
                # Check if field has enum constraints
                if 'enum' in field_info:
                    enum_values = field_info['enum']
                    optional_fields.append(f"  • {field_name}: Must be one of: {enum_values}")
                elif field_info.get('type') == 'string' and 'examples' in field_info:
                    examples = field_info['examples']
                    optional_fields.append(f"  • {field_name}: Examples: {examples}")
        
        if optional_fields:
            if required_fields:
                description_parts.append("") # Add separator
            description_parts.append("Optional fields with constraints:")
            description_parts.extend(optional_fields)
        
        if include_full_schema:
            description_parts.extend([
                "",
                f"Complete JSON Schema for {parameter_name} (as '{model_name}'):",
                json.dumps(schema, indent=2)
            ])
    
    return "\n".join(description_parts)


def get_literal_constraints(model_class: Type[BaseModel]) -> Dict[str, Any]:
    """
    Extract all Literal/enum constraints from a Pydantic model.
    
    Returns:
        Dictionary mapping field names to their allowed values
    """
    schema = model_class.model_json_schema()
    properties = schema.get('properties', {})
    
    constraints = {}
    for field_name, field_info in properties.items():
        if 'enum' in field_info:
            constraints[field_name] = field_info['enum']
    
    return constraints


def validate_model_data(model_class: Type[BaseModel], data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate data against a Pydantic model and return helpful error messages.
    
    Returns:
        Dictionary with validation results and user-friendly error messages
    """
    try:
        instance = model_class.model_validate(data)
        return {
            "valid": True,
            "data": instance.model_dump(exclude_none=True),
            "errors": []
        }
    except Exception as e:
        # Extract helpful error information
        errors = []
        if hasattr(e, 'errors'):
            for error in e.errors():
                field = ".".join(str(loc) for loc in error.get('loc', []))
                message = error.get('msg', 'Unknown error')
                input_value = error.get('input', 'N/A')
                
                # Enhance message for common validation errors
                if 'literal_error' in error.get('type', ''):
                    expected = error.get('ctx', {}).get('expected', 'Unknown')
                    message = f"Field '{field}' must be one of: {expected}. Got: {input_value}"
                elif 'missing' in error.get('type', ''):
                    message = f"Required field '{field}' is missing"
                
                errors.append({
                    "field": field,
                    "message": message,
                    "input": input_value
                })
        
        return {
            "valid": False,
            "data": None,
            "errors": errors
        }