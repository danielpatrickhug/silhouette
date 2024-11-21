from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class TypeHints(BaseModel):
    """Model for type hints response."""
    param_types: Dict[str, str]
    return_type: str

class Docstring(BaseModel):
    """Model for docstring generation response."""
    content: str = Field(description="The docstring content")