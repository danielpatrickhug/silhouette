from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from openai import OpenAI
import instructor

class TypeHints(BaseModel):
    """Model for type hints response."""
    param_types: Dict[str, str]
    return_type: str

class Docstring(BaseModel):
    """Model for docstring generation response."""
    content: str = Field(description="The docstring content")

class GPTInterface:
    def __init__(self, api_key: str):
        self.client = instructor.patch(OpenAI(api_key=api_key))

    def generate_type_hints(self, code: str) -> TypeHints:
        """Generate type hints for the given code."""
        prompt = """
        Analyze the following Python function and provide type hints.
        Return a JSON object with:
        1. param_types: a dictionary mapping parameter names to their types
        2. return_type: the function's return type
        
        Use standard Python type annotations (e.g., str, int, List[str], Dict[str, Any], etc.).
        If a type is unclear, use 'Any'. but be detail oriented when looking at the code. 
        If the function doesn't return anything explicitly, use 'None'.
        
        Function to analyze:
        {code}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                response_model=TypeHints,
                messages=[
                    {"role": "system", "content": "You are a Python type inference expert."},
                    {"role": "user", "content": prompt.format(code=code)}
                ]
            )
            return response
        except Exception as e:
            raise RuntimeError(f"Failed to generate type hints: {str(e)}")

    def generate_docstring(self, code: str) -> str:
        """Generate a docstring for the given code."""
        prompt = """
        Generate a detailed docstring for the following Python function.
        Include a brief description, Args section describing each parameter, and Returns section.
        Do not include any quotes or formatting - just the raw docstring content.
        
        Example format (without the quotes):
        Brief description of the function.

        Args:
            param1: Description of first parameter
            param2: Description of second parameter

        Returns:
            Description of return value
        
        Function to document:
        {code}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Python documentation expert. Generate only the docstring content."},
                    {"role": "user", "content": prompt.format(code=code)}
                ],
                max_tokens=500,
                temperature=0.2
            )
            # Extract the content directly from the message
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to generate docstring: {str(e)}")