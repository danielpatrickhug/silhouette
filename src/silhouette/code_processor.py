# src/silhouette/code_processor.py

import libcst as cst
from silhouette.cst_transformers import DocstringAdder, TypeHintAdder
from silhouette.gpt_interface import GPTInterface

class CodeProcessor:
    def __init__(
        self,
        source_code: str,
        api_key: str,
        add_docstrings: bool = False,
        add_type_hints: bool = False,
        verbose: bool = False,
    ):
        self.source_code = source_code
        self.api_key = api_key
        self.add_docstrings = add_docstrings
        self.add_type_hints = add_type_hints
        self.verbose = verbose
        self.gpt_interface = GPTInterface(api_key)
        self.parsed_module = cst.parse_module(source_code)

    def process(self) -> str:
        transformed_tree = self.parsed_module

        if self.add_docstrings:
            if self.verbose:
                print("Adding docstrings...")
            docstring_adder = DocstringAdder(self.gpt_interface)
            transformed_tree = transformed_tree.visit(docstring_adder)

        if self.add_type_hints:
            if self.verbose:
                print("Adding type hints...")
            type_hint_adder = TypeHintAdder(self.gpt_interface)
            transformed_tree = transformed_tree.visit(type_hint_adder)

        return transformed_tree.code
