# src/silhouette/cst_transformers.py

import libcst as cst
from silhouette.gpt_interface import GPTInterface, TypeHints
from silhouette.utils.cst_helpers import has_docstring

class DocstringAdder(cst.CSTTransformer):
    def __init__(self, gpt: GPTInterface):
        self.gpt = gpt
        super().__init__()

    def _create_docstring_node(self, docstring: str) -> cst.SimpleStatementLine:
        """Create a CST node for a docstring."""
        # Properly format the docstring with consistent indentation
        lines = docstring.strip().split('\n')
        if len(lines) > 1:
            # For multi-line docstrings, ensure proper indentation
            formatted_lines = [lines[0]] + [f"    {line}" for line in lines[1:]]
            formatted_docstring = '\n'.join(formatted_lines)
            docstring_value = f'"""{formatted_docstring}\n    """'
        else:
            # For single-line docstrings
            docstring_value = f'"""{docstring.strip()}"""'
            
        return cst.SimpleStatementLine([
            cst.Expr(value=cst.SimpleString(docstring_value))
        ])

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        # Skip if function already has a docstring
        if has_docstring(updated_node):
            return updated_node

        try:
            # Get function code
            code = cst.Module([original_node]).code
            
            # Generate docstring
            docstring = self.gpt.generate_docstring(code)
            
            # Create docstring node
            docstring_node = self._create_docstring_node(docstring)
            
            # Add docstring to function body
            body = cst.ensure_type(updated_node.body, cst.IndentedBlock)
            new_body = body.with_changes(
                body=(docstring_node,) + body.body
            )
            
            return updated_node.with_changes(body=new_body)
            
        except Exception as e:
            print(f"Error adding docstring to function {original_node.name.value}: {str(e)}")
            return updated_node

def add_docstrings(source_code: str, api_key: str) -> str:
    """
    Apply docstrings to Python source code using GPT.
    
    Args:
        source_code: The Python source code to process
        api_key: OpenAI API key
    
    Returns:
        The processed source code with docstrings added
    """
    try:
        source_tree = cst.parse_module(source_code)
        gpt_interface = GPTInterface(api_key)
        transformer = DocstringAdder(gpt_interface)
        modified_tree = source_tree.visit(transformer)
        return modified_tree.code
    except Exception as e:
        print(f"Error processing source code: {str(e)}")
        return source_code

class TypeHintAdder(cst.CSTTransformer):
    def __init__(self, gpt: GPTInterface):
        self.gpt = gpt
        super().__init__()

    def _create_annotation(self, type_str: str) -> cst.Annotation:
        """Create a CST annotation node from a type string."""
        return cst.Annotation(
            annotation=cst.parse_expression(type_str)
        )

    def _add_param_annotation(self, param: cst.Param, type_str: str) -> cst.Param:
        """Add type annotation to a parameter."""
        return param.with_changes(
            annotation=self._create_annotation(type_str)
        )

    def _add_return_annotation(self, node: cst.FunctionDef, return_type: str) -> cst.FunctionDef:
        """Add return type annotation to a function."""
        return node.with_changes(
            returns=self._create_annotation(return_type)
        )

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        # Skip if function already has type hints
        if all(param.annotation for param in updated_node.params.params) and updated_node.returns:
            return updated_node

        try:
            # Get function code
            code = cst.Module([original_node]).code

            # Generate type hints using GPT
            type_hints = self.gpt.generate_type_hints(code)

            # Add parameter type hints
            new_params = []
            for param in updated_node.params.params:
                param_name = param.name.value
                if param_name in type_hints.param_types:
                    new_param = self._add_param_annotation(
                        param, type_hints.param_types[param_name]
                    )
                    new_params.append(new_param)
                else:
                    new_params.append(param)

            # Update parameters
            updated_node = updated_node.with_changes(
                params=updated_node.params.with_changes(params=new_params)
            )

            # Add return type annotation
            if type_hints.return_type:
                updated_node = self._add_return_annotation(
                    updated_node, type_hints.return_type
                )

            return updated_node

        except Exception as e:
            print(f"Error adding type hints to function {original_node.name.value}: {str(e)}")
            return updated_node

# Helper function to apply the transformer
def add_type_hints(source_code: str, api_key: str) -> str:
    """
    Apply type hints to Python source code using GPT.
    
    Args:
        source_code: The Python source code to process
        api_key: OpenAI API key
    
    Returns:
        The processed source code with type hints added
    """
    try:
        # Parse the source code into a CST
        source_tree = cst.parse_module(source_code)
        
        # Create and apply the transformer
        gpt_interface = GPTInterface(api_key)
        transformer = TypeHintAdder(gpt_interface)
        modified_tree = source_tree.visit(transformer)
        
        # Return the modified code
        return modified_tree.code
    except Exception as e:
        print(f"Error processing source code: {str(e)}")
        return source_code
