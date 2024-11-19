# tests/test_cst_helpers.py

import libcst as cst
from silhouette.utils.cst_helpers import get_function_code, find_functions, has_docstring, add_import

def test_get_function_code():
    code = """
def test_func(x, y):
    return x + y
"""
    node = cst.parse_module(code)
    assert get_function_code(node) == code

def test_find_functions():
    module = cst.parse_module("""
def func1():
    pass

class TestClass:
    def method1(self):
        pass

def func2():
    pass
""")
    functions = find_functions(module)
    assert len(functions) == 3
    assert [f.name.value for f in functions] == ["func1", "method1", "func2"]

def test_has_docstring():
    with_docstring = cst.parse_statement('''
def func_with_docstring():
    """This is a docstring."""
    pass
''')
    without_docstring = cst.parse_statement('def func_without_docstring(): pass')

    assert has_docstring(with_docstring)
    assert not has_docstring(without_docstring)

def test_add_import():
    module = cst.parse_module("def test(): pass")
    updated_module = add_import(module, "import os")
    assert "import os" in updated_module.code