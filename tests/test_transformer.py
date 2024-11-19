# tests/test_transformer.py

import pytest
from silhouette.transformer import Transformer
from silhouette.gpt_interface import GPTInterface
import libcst as cst

# Mock GPTInterface for testing
class MockGPTInterface(GPTInterface):
    def generate_docstring(self, code: str) -> str:
        return "This is a mock docstring."

    def generate_type_hints(self, code: str) -> dict:
        return {
            "param_types": {"x": "int", "y": "str"},
            "return_type": "bool"
        }

@pytest.fixture
def transformer():
    return Transformer(MockGPTInterface("dummy_api_key"))

def test_add_docstrings(transformer):
    source_code = """
        def example_function(x, y):
            return x + y
        """
    transformer.load_source(source_code)
    transformer.add_docstrings()
    result = transformer.transform()

    expected = '''
        def example_function(x, y):
            """This is a mock docstring."""
            return x + y
        '''
    assert result.strip() == expected.strip()

def test_add_type_hints(transformer):
    source_code = """
def example_function(x, y):
    return x + y
"""
    transformer.load_source(source_code)
    transformer.add_type_hints()
    result = transformer.transform()

    expected = '''
def example_function(x: int, y: str) -> bool:
    return x + y
'''
    assert result.strip() == expected.strip()

def test_full_transformation(transformer):
    source_code = """
def example_function(x, y):
    return x + y
"""
    transformer.load_source(source_code)
    transformer.add_docstrings().add_type_hints()
    result = transformer.transform()

    expected = '''
def example_function(x: int, y: str) -> bool:
    """This is a mock docstring."""
    return x + y
'''
    assert result.strip() == expected.strip()