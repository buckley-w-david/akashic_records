import ast, _ast
from types import CodeType


class RemovePrints(ast.NodeTransformer):
    def visit_Expr(self, node):
        if (
            isinstance(node, _ast.Expr)
            and isinstance(node.value, _ast.Call)
            and isinstance(node.value.func, _ast.Name)
            and node.value.func.id == "print"
        ):
            return (
                ast.Pass()
            )  # replace prints with noop to help ensure that the result is still syntactically valid
        return node


print_remover = RemovePrints()


def remove_prints(tree: ast.AST) -> ast.AST:
    return print_remover.visit(tree)


def clean_top_level(tree: ast.Module) -> None:
    tree.body = [
        node
        for node in tree.body
        if isinstance(node, _ast.FunctionDef)
        or isinstance(node, _ast.ClassDef)
        or isinstance(node, _ast.Import)
        or isinstance(node, _ast.ImportFrom)
    ]


def parse(code: str) -> ast.Module:
    tree = ast.parse(code)
    remove_prints(tree)
    clean_top_level(tree)
    return tree


def compile_source(code: str) -> CodeType:
    tree = parse(code)
    compiled_code = compile(ast.fix_missing_locations(tree), "<AkashicRecords>", "exec")

    return compiled_code
