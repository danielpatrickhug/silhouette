import libcst as cst
from typing import Union, List

def get_function_code(node: Union[cst.FunctionDef, cst.Module]) -> str:
    """
    Extract the code representation of a function or module.
    
    Args:
        node (Union[cst.FunctionDef, cst.Module]): The CST node to extract code from.
    
    Returns:
        str: The string representation of the code.
    """
    if isinstance(node, cst.FunctionDef):
        return cst.Module([node]).code
    return node.code

def find_functions(tree: cst.Module) -> List[cst.FunctionDef]:
    """
    Find all function definitions in a module.
    
    Args:
        tree (cst.Module): The CST of the module to search.
    
    Returns:
        List[cst.FunctionDef]: A list of all function definitions found.
    """
    functions = []
    
    class FunctionFinder(cst.CSTVisitor):
        def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
            functions.append(node)
    
    tree.visit(FunctionFinder())
    return functions

def has_docstring(node: cst.FunctionDef) -> bool:
    """
    Check if a function has a docstring.
    
    Args:
        node (cst.FunctionDef): The function node to check.
    
    Returns:
        bool: True if the function has a docstring, False otherwise.
    """
    return node.get_docstring() is not None

def add_import(tree: cst.Module, import_statement: str) -> cst.Module:
    """
    Add an import statement to the module if it doesn't already exist.
    
    Args:
        tree (cst.Module): The CST of the module to modify.
        import_statement (str): The import statement to add.
    
    Returns:
        cst.Module: The modified CST with the new import statement.
    """
    new_import = cst.parse_statement(import_statement)
    
    class ImportAdder(cst.CSTTransformer):
        def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
            for stmt in updated_node.body:
                if isinstance(stmt, cst.SimpleStatementLine) and isinstance(stmt.body[0], (cst.Import, cst.ImportFrom)):
                    if stmt.body[0].code == import_statement:
                        return updated_node
            
            return updated_node.with_changes(
                body=(cst.SimpleStatementLine([new_import]),) + updated_node.body
            )
    
    return tree.visit(ImportAdder())


def add_type_annotation(node: cst.Param, type_annotation: str) -> cst.Param:
    """
    Add a type annotation to a function parameter.
    
    Args:
        node (cst.Param): The parameter node to modify.
        type_annotation (str): The type annotation to add.
    
    Returns:
        cst.Param: The modified parameter node with the new type annotation.
    """
    return node.with_changes(
        annotation=cst.Annotation(
            cst.parse_expression(type_annotation)
        )
    )

def add_return_annotation(node: cst.FunctionDef, return_type: str) -> cst.FunctionDef:
    """
    Add a return type annotation to a function.
    
    Args:
        node (cst.FunctionDef): The function node to modify.
        return_type (str): The return type annotation to add.
    
    Returns:
        cst.FunctionDef: The modified function node with the new return type annotation.
    """
    return node.with_changes(
        returns=cst.Annotation(cst.parse_expression(return_type))
    )