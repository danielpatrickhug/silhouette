# tests/test_transformer.py

import unittest
import libcst as cst
from unittest.mock import MagicMock, patch
from silhouette.cst_transformers import DocstringAdder, TypeHintAdder, add_docstrings, add_type_hints
from silhouette.gpt_interface import GPTInterface, TypeHints

class TestTransformers(unittest.TestCase):
    def test_docstring_adder(self):
        source_code = """
def add(x, y):
    return x + y
"""
        expected_code = '''
def add(x, y):
    """Mocked docstring."""
    return x + y
'''.strip()

        # Parse the source code
        source_tree = cst.parse_module(source_code)

        # Mock GPTInterface
        mock_gpt = MagicMock()
        mock_gpt.generate_docstring.return_value = "Mocked docstring."

        # Apply the DocstringAdder transformer
        transformer = DocstringAdder(mock_gpt)
        modified_tree = source_tree.visit(transformer)

        # Check that the modified code matches the expected code
        self.assertEqual(modified_tree.code.strip(), expected_code)

    def test_type_hint_adder(self):
        source_code = """
def add(x, y):
    return x + y
"""
        expected_code = '''
def add(x: int, y: int) -> int:
    return x + y
'''.strip()

        # Parse the source code
        source_tree = cst.parse_module(source_code)

        # Mock GPTInterface
        mock_gpt = MagicMock()
        mock_gpt.generate_type_hints.return_value = TypeHints(
            param_types={"x": "int", "y": "int"},
            return_type="int"
        )

        # Apply the TypeHintAdder transformer
        transformer = TypeHintAdder(mock_gpt)
        modified_tree = source_tree.visit(transformer)

        # Check that the modified code matches the expected code
        self.assertEqual(modified_tree.code.strip(), expected_code)

    @patch('silhouette.cst_transformers.GPTInterface')
    def test_add_docstrings_function(self, MockGPTInterface):
        source_code = """
def add(x, y):
    return x + y
"""
        expected_code = '''
def add(x, y):
    """Mocked docstring."""
    return x + y
'''.strip()

        # Set up the mock
        mock_gpt = MockGPTInterface.return_value
        mock_gpt.generate_docstring.return_value = "Mocked docstring."

        # Call the function under test
        result = add_docstrings(source_code, api_key="dummy_api_key")

        # Check the result
        self.assertEqual(result.strip(), expected_code)

    @patch('silhouette.cst_transformers.GPTInterface')
    def test_add_type_hints_function(self, MockGPTInterface):
        source_code = '''
def add(x, y):
    return x + y
'''
        expected_code = '''
def add(x: int, y: int) -> int:
    return x + y
'''.strip()

        # Set up the mock
        mock_gpt = MockGPTInterface.return_value
        mock_gpt.generate_type_hints.return_value = TypeHints(
            param_types={"x": "int", "y": "int"},
            return_type="int"
        )

        # Call the function under test
        result = add_type_hints(source_code, api_key="dummy_api_key")

        # Check the result
        self.assertEqual(result.strip(), expected_code)

if __name__ == '__main__':
    unittest.main()
