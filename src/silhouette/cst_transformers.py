# src/silhouette/cst_transformers.py

import libcst as cst
from silhouette.gpt_interface import GPTInterface, TypeHints
from silhouette.utils.cst_helpers import get_function_code, add_type_annotation, add_return_annotation

class DocstringAdder(cst.CSTTransformer):
    def __init__(self, gpt: GPTInterface):
        self.gpt = gpt

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        if not has_docstring(updated_node):
            code = get_function_code(original_node)
            docstring = self.gpt.generate_docstring(code)
            
            new_body = cst.ensure_type(updated_node.body, cst.IndentedBlock)
            new_body = new_body.with_changes(
                body=(cst.SimpleStatementLine([cst.Expr(cst.SimpleString(f'"""{docstring}"""'))]),) + new_body.body
            )
            return updated_node.with_changes(body=new_body)




class TypeHintAdder(cst.CSTTransformer):
    def __init__(self, gpt: GPTInterface):
        self.gpt = gpt

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        code = get_function_code(original_node)
        type_hints: TypeHints = self.gpt.generate_type_hints(code)
        
        # Add parameter type hints
        new_params = [
            add_type_annotation(param, type_hints.param_types[param.name.value])
            if param.name.value in type_hints.param_types
            else param
            for param in updated_node.params.params
        ]
        
        # Add return type hint
        updated_node = add_return_annotation(updated_node, type_hints.return_type)
        
        return updated_node.with_changes(
            params=updated_node.params.with_changes(params=new_params)
