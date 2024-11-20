import libcst as cst
import libcst.matchers as m
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
    Check if a function already has a docstring.
    
    Args:
        node: The function definition node to check
        
    Returns:
        True if the function has a docstring, False otherwise
    """
    if not node.body.body:
        return False
    
    first_stmt = node.body.body[0]
    if isinstance(first_stmt, cst.SimpleStatementLine):
        if len(first_stmt.body) == 1 and isinstance(first_stmt.body[0], cst.Expr):
            return isinstance(first_stmt.body[0].value, cst.SimpleString)
    return False


def add_import(source_code: str, import_statement: str) -> cst.Module:
    """
    Add an import statement to the module if it doesn't already exist.

    Args:
        tree (cst.Module): The CST of the module to modify.
        import_statement (str): The import statement to add.

    Returns:
        cst.Module: The modified CST with the new import statement.
    """
    tree = cst.parse_module(source_code)
    new_import = cst.parse_statement(import_statement)
    import_code = cst.Module([]).code_for_node(new_import).strip()

    class ImportAdder(cst.CSTTransformer):
        def __init__(self):
            self.import_exists = False

        def visit_SimpleStatementLine(self, node: cst.SimpleStatementLine) -> bool:
            if any(
                m.matches(stmt, m.Import() | m.ImportFrom())
                and cst.Module([]).code_for_node(stmt).strip() == import_code
                for stmt in node.body
            ):
                self.import_exists = True
            return not self.import_exists  # Stop visiting if the import already exists.

        def leave_Module(
            self, original_node: cst.Module, updated_node: cst.Module
        ) -> cst.Module:
            if not self.import_exists:
                new_body = [new_import] + list(updated_node.body)
                return updated_node.with_changes(body=new_body)
            return updated_node

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