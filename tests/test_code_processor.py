# tests/test_code_processor.py

import unittest
from unittest.mock import MagicMock, patch
from silhouette.code_processor import CodeProcessor
from silhouette.gpt_interface import GPTInterface, TypeHints

class TestCodeProcessor(unittest.TestCase):
    @patch('silhouette.code_processor.GPTInterface')
    def test_process_add_docstrings(self, MockGPTInterface):
        source_code = '''
def greet(name):
    print(f"Hello, {name}!")
'''
        expected_code = '''
def greet(name):
    """Greets a person by name."""
    print(f"Hello, {name}!")
'''.strip()

        mock_gpt = MockGPTInterface.return_value
        mock_gpt.generate_docstring.return_value = "Greets a person by name."

        processor = CodeProcessor(
            source_code=source_code,
            api_key="dummy_api_key",
            add_docstrings=True,
            add_type_hints=False
        )

        modified_code = processor.process()

        self.assertEqual(modified_code.strip(), expected_code)

    @patch('silhouette.code_processor.GPTInterface')
    def test_process_add_type_hints(self, MockGPTInterface):
        source_code = '''
def greet(name):
    print(f"Hello, {name}!")
'''
        expected_code = '''
def greet(name: str) -> None:
    print(f"Hello, {name}!")
'''.strip()

        mock_gpt = MockGPTInterface.return_value
        mock_gpt.generate_type_hints.return_value = TypeHints(
            param_types={"name": "str"},
            return_type="None"
        )

        processor = CodeProcessor(
            source_code=source_code,
            api_key="dummy_api_key",
            add_docstrings=False,
            add_type_hints=True
        )

        modified_code = processor.process()

        self.assertEqual(modified_code.strip(), expected_code)

    @patch('silhouette.code_processor.GPTInterface')
    def test_process_add_both(self, MockGPTInterface):
        source_code = '''
def greet(name):
    print(f"Hello, {name}!")
'''
        expected_code = '''
def greet(name: str) -> None:
    """Greets a person by name."""
    print(f"Hello, {name}!")
'''.strip()

        mock_gpt = MockGPTInterface.return_value
        mock_gpt.generate_docstring.return_value = "Greets a person by name."
        mock_gpt.generate_type_hints.return_value = TypeHints(
            param_types={"name": "str"},
            return_type="None"
        )

        processor = CodeProcessor(
            source_code=source_code,
            api_key="dummy_api_key",
            add_docstrings=True,
            add_type_hints=True
        )

        modified_code = processor.process()

        self.assertEqual(modified_code.strip(), expected_code)

if __name__ == '__main__':
    unittest.main()
