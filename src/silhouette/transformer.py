# src/silhouette/transformer.py

import libcst as cst
from typing import Optional
from silhouette.gpt_interface import GPTInterface
from silhouette.cst_transformers import DocstringAdder, TypeHintAdder

class Transformer:
    def __init__(self, gpt_interface: GPTInterface):
        self.tree: Optional[cst.Module] = None
        self.gpt = gpt_interface

    def load_source(self, source_code: str):
        self.tree = cst.parse_module(source_code)

    def add_docstrings(self):
        if self.tree is None:
            raise ValueError("No source code loaded. Call load_source() first.")
        
        self.tree = self.tree.visit(DocstringAdder(self.gpt))
        return self

    def add_type_hints(self):
        if self.tree is None:
            raise ValueError("No source code loaded. Call load_source() first.")
        
        self.tree = self.tree.visit(TypeHintAdder(self.gpt))
        return self

    def transform(self) -> str:
        if self.tree is None:
            raise ValueError("No source code loaded. Call load_source() first.")
        
        return self.tree.code