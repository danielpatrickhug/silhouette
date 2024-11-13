import instructor
from openai import OpenAI
from pydantic import BaseModel
from typing import List

class Docstring(BaseModel):
    content: str

class TypeHints(BaseModel):
    param_types: dict[str, str]
    return_type: str

class GPTInterface:
    def __init__(self, api_key: str):
        self.client = instructor.from_openai(OpenAI(api_key=api_key))

    def generate_docstring(self, code: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            response_model=Docstring,
            messages=[
                {"role": "system", "content": "You are an expert Python developer. Generate a concise and informative docstring for the given Python code."},
                {"role": "user", "content": f"Generate a docstring for this Python code:\n\n{code}"}
            ]
        )
        return response.content

    def generate_type_hints(self, code: str) -> TypeHints:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            response_model=TypeHints,
            messages=[
                {"role": "system", "content": "You are an expert Python developer. Analyze the given Python code and provide appropriate type hints for parameters and return value."},
                {"role": "user", "content": f"Provide type hints for this Python code:\n\n{code}"}
            ]
        )
        return response