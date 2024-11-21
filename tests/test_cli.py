# tests/test_cli.py

import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
from io import StringIO

# Import the main function from the CLI module
from silhouette.cli import main

class TestCLI(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory and test files
        self.test_dir = 'temp_test_dir'
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Valid Python file
        self.valid_file = os.path.join(self.test_dir, 'test.py')
        with open(self.valid_file, 'w') as f:
            f.write('def foo(): pass')
        
        # Invalid non-Python file
        self.invalid_file = os.path.join(self.test_dir, 'test.txt')
        with open(self.invalid_file, 'w') as f:
            f.write('This is not a Python file.')
        
        # Redirect stdout and stderr to capture output and error messages
        self.patcher_stdout = patch('sys.stdout', new_callable=StringIO)
        self.mock_stdout = self.patcher_stdout.start()
        
        self.patcher_stderr = patch('sys.stderr', new_callable=StringIO)
        self.mock_stderr = self.patcher_stderr.start()

    def tearDown(self):
        # Remove temporary directory and its contents
        if os.path.exists(self.test_dir):
            for root, dirs, files in os.walk(self.test_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.test_dir)
        
        # Stop patchers
        patch.stopall()

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key(self):
        """
        Test that the CLI exits with an error when no API key is provided.
        """
        # Simulate command-line arguments without API key
        test_args = ['cli.py', self.valid_file, '--docstrings']
        with patch.object(sys, 'argv', test_args):
            with self.assertRaises(SystemExit) as cm:
                main()
        
        # Check that the exit code is 2 (argparse error)
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("An OpenAI API key must be provided", self.mock_stderr.getvalue())

    @patch('silhouette.cli.CodeProcessor')
    def test_invalid_file_type(self, mock_code_processor):
        """
        Test that the CLI exits with an error when a non-Python file is provided.
        """
        # Simulate command-line arguments with a non-Python file
        test_args = ['cli.py', self.invalid_file, '--docstrings', '--api-key', 'dummy_api_key']
        with patch.object(sys, 'argv', test_args):
            with self.assertRaises(SystemExit) as cm:
                main()
        
        # Check that the exit code is 2 (argparse error)
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("The specified file is not a Python (.py) file.", self.mock_stderr.getvalue())
        
        # Ensure that CodeProcessor was not called
        mock_code_processor.assert_not_called()

    @patch('silhouette.cli.CodeProcessor')
    @patch('silhouette.cli.open', new_callable=mock_open, read_data='def foo(): pass')
    def test_valid_operation(self, mock_file, mock_code_processor):
        """
        Test that the CLI processes a valid Python file correctly when an API key is provided.
        """
        # Configure CodeProcessor mock to return modified code with a docstring
        mock_processor_instance = MagicMock()
        mock_processor_instance.process.return_value = 'def foo():\n    """Docstring."""\n    pass'
        mock_code_processor.return_value = mock_processor_instance

        # Simulate command-line arguments with --docstrings and API key
        test_args = ['cli.py', '--docstrings', self.valid_file, '--api-key', 'dummy_api_key']
        with patch.object(sys, 'argv', test_args):
            main()
        
        # Assert that CodeProcessor.process was called with correct parameters
        mock_code_processor.assert_called_once_with(
            source_code='def foo(): pass',
            api_key='dummy_api_key',
            add_docstrings=True,
            add_type_hints=False,
            verbose=False
        )
        
        # Assert that the file was opened for reading and writing
        mock_file.assert_any_call(self.valid_file, 'r')
        mock_file.assert_any_call(self.valid_file, 'w')
        
        # Get the file handle and check write was called with expected data
        handle = mock_file()
        handle.write.assert_called_once_with('def foo():\n    """Docstring."""\n    pass')

    @patch('silhouette.cli.CodeProcessor')
    def test_no_options_provided(self, mock_code_processor):
        """
        Test that the CLI requires at least one of --docstrings or --type-hints.
        """
        # Simulate command-line arguments without --docstrings or --type-hints
        test_args = ['cli.py', '--api-key', 'dummy_api_key', self.valid_file]
        with patch.object(sys, 'argv', test_args):
            with self.assertRaises(SystemExit) as cm:
                main()
        
        # Check that the exit code is 2 (argparse error)
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("At least one of --docstrings or --type-hints must be specified.", self.mock_stderr.getvalue())
        
        # Ensure that CodeProcessor was not called
        mock_code_processor.assert_not_called()

    @patch('silhouette.cli.CodeProcessor')
    @patch('silhouette.cli.open', new_callable=mock_open, read_data='def foo(): pass')
    def test_verbose_flag(self, mock_file, mock_code_processor):
        """
        Test that verbose messages are printed when the --verbose flag is used.
        """
        # Configure CodeProcessor mock to return modified code with a docstring
        mock_processor_instance = MagicMock()
        mock_processor_instance.process.return_value = 'def foo():\n    """Docstring."""\n    pass'
        mock_code_processor.return_value = mock_processor_instance

        # Simulate command-line arguments with --docstrings, --verbose, and API key
        test_args = ['cli.py', '--docstrings', self.valid_file, '--verbose', '--api-key', 'dummy_api_key']
        with patch.object(sys, 'argv', test_args):
            main()
        
        # Assert that CodeProcessor.process was called with verbose=True
        mock_code_processor.assert_called_once_with(
            source_code='def foo(): pass',
            api_key='dummy_api_key',
            add_docstrings=True,
            add_type_hints=False,
            verbose=True
        )
        
        # Check that verbose messages are printed
        self.assertIn("Processing 1 files...", self.mock_stdout.getvalue())
        self.assertIn(f"Processing {self.valid_file}...", self.mock_stdout.getvalue())
        self.assertIn("Processing completed.", self.mock_stdout.getvalue())

if __name__ == '__main__':
    unittest.main()
