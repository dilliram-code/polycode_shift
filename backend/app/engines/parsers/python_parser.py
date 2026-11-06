"""
PolyShift - Python AST Parser
Translates Python source code into the PolyShift Universal Intermediate Representation.
"""
import ast
from typing import List, Optional, Tuple, Any

from app.engines.parsers.base import BaseParser
from app.engines.ir import (
    Program, FunctionDef, Parameter, ClassDef, VariableDeclaration,
    Assignment, ReturnStatement, IfStatement, WhileLoop, ForLoop,
    TryCatch, BreakStatement, ContinueStatement, ExpressionStatement,
    BinaryOp, UnaryOp, FunctionCall, MethodCall, ArrayAccess, MemberAccess,
    ListLiteral, DictLiteral, DictEntry, Literal, Identifier, TernaryExpr,
    IRType, DataType, IRExpression, IRStatement, ImportItem
)

class PythonParser(BaseParser):
    @property
    def language_name(self) -> str:
        return "python"

    def validate_syntax(self, code: str) -> Tuple[bool, List[str]]:
        try:
            ast.parse(code)
            return True, []
        except SyntaxError as e:
            return False, [f"SyntaxError at line {e.lineno}, col {e.offset}: {e.msg}"]
        except Exception as e:
            return False, [str(e)]

    def parse(self, code: str) -> Program:
        try:
            tree = ast.parse(code)
        except Exception:
            return Program(raw_source=code, source_language="python")

        program = Program(raw_source=code, source_language="python")

        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                program.imports.append(self._parse_import(node))
            elif isinstance(node, ast.ClassDef):
                program.classes.append(self._parse_class(node))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                program.functions.append(self._parse_function(node))
            else:
                stmt = self._parse_statement(node)
                if stmt:
                    program.statements.append(stmt)

        return program

    def _parse_import(self, node: ast.AST) -> ImportItem:
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
            return ImportItem(module=names[0] if names else "", imported_names=names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = [alias.name for alias in node.names]
            return ImportItem(module=module, imported_names=names)
        return ImportItem(module="")

    def _parse_class(self, node: ast.ClassDef) -> ClassDef:
        bases = [self._expr_to_str(b) for b in node.bases]
        methods = []
        fields = []

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._parse_function(item, is_method=True))
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                init_expr = self._parse_expression(item.value) if item.value else None
                var_type = self._parse_type_annotation(item.annotation)
                fields.append(VariableDeclaration(name=item.target.id, var_type=var_type, init_val=init_expr))

        docstring = ast.get_docstring(node)
        return ClassDef(name=node.name, base_classes=bases, fields=fields, methods=methods, docstring=docstring)

    def _parse_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_method: bool = False) -> FunctionDef:
        params = []
        for arg in node.args.args:
            if is_method and arg.arg in ("self", "cls"):
                continue
            param_type = self._parse_type_annotation(arg.annotation) if arg.annotation else IRType.any_type()
            params.append(Parameter(name=arg.arg, param_type=param_type))

        ret_type = self._parse_type_annotation(node.returns) if node.returns else IRType.void_type()
        body = [self._parse_statement(stmt) for stmt in node.body if self._parse_statement(stmt) is not None]
        docstring = ast.get_docstring(node)

        return FunctionDef(
            name=node.name,
            params=params,
            return_type=ret_type,
            body=[b for b in body if b is not None],
            docstring=docstring,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            is_method=is_method
        )

    def _parse_type_annotation(self, node: Optional[ast.AST]) -> IRType:
        if not node:
            return IRType.any_type()
        if isinstance(node, ast.Name):
            name = node.id.lower()
            if name in ("int", "integer"):
                return IRType.int_type()
            elif name in ("float", "double"):
                return IRType.float_type()
            elif name in ("str", "string"):
                return IRType.string_type()
            elif name in ("bool", "boolean"):
                return IRType.bool_type()
            elif name in ("none", "void"):
                return IRType.void_type()
            return IRType.custom(node.id)
        elif isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Name):
                container = node.value.id.lower()
                if container in ("list", "sequence"):
                    elem_type = self._parse_type_annotation(node.slice)
                    return IRType.list_type(elem_type)
                elif container in ("dict", "mapping"):
                    return IRType.dict_type()
        return IRType.any_type()

    def _parse_statement(self, node: ast.AST) -> Optional[IRStatement]:
        if isinstance(node, ast.Assign):
            target = self._parse_expression(node.targets[0])
            val = self._parse_expression(node.value)
            if isinstance(target, Identifier):
                inferred_type = val.inferred_type if val and val.inferred_type else IRType.any_type()
                return VariableDeclaration(name=target.name, var_type=inferred_type, init_val=val)
            return Assignment(target=target, op="=", value=val)

        elif isinstance(node, ast.AnnAssign):
            target = self._parse_expression(node.target)
            val = self._parse_expression(node.value) if node.value else None
            var_type = self._parse_type_annotation(node.annotation)
            if isinstance(target, Identifier):
                return VariableDeclaration(name=target.name, var_type=var_type, init_val=val)
            return Assignment(target=target, op="=", value=val or Literal(None, DataType.VOID))

        elif isinstance(node, ast.AugAssign):
            target = self._parse_expression(node.target)
            val = self._parse_expression(node.value)
            op = self._binop_to_str(node.op) + "="
            return Assignment(target=target, op=op, value=val)

        elif isinstance(node, ast.Return):
            val = self._parse_expression(node.value) if node.value else None
            return ReturnStatement(value=val)

        elif isinstance(node, ast.If):
            cond = self._parse_expression(node.test)
            then_body = [self._parse_statement(s) for s in node.body if self._parse_statement(s) is not None]
            else_body = [self._parse_statement(s) for s in node.orelse if self._parse_statement(s) is not None]
            return IfStatement(condition=cond, then_body=then_body, else_body=else_body)

        elif isinstance(node, ast.While):
            cond = self._parse_expression(node.test)
            body = [self._parse_statement(s) for s in node.body if self._parse_statement(s) is not None]
            return WhileLoop(condition=cond, body=body)

        elif isinstance(node, ast.For):
            iter_var = node.target.id if isinstance(node.target, ast.Name) else "item"
            body = [self._parse_statement(s) for s in node.body if self._parse_statement(s) is not None]

            # Detect range()
            if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == "range":
                args = [self._parse_expression(a) for a in node.iter.args]
                if len(args) == 1:
                    return ForLoop(iterator_var=iter_var, is_range=True, range_start=Literal(0, DataType.INT), range_end=args[0], body=body)
                elif len(args) == 2:
                    return ForLoop(iterator_var=iter_var, is_range=True, range_start=args[0], range_end=args[1], body=body)
                elif len(args) == 3:
                    return ForLoop(iterator_var=iter_var, is_range=True, range_start=args[0], range_end=args[1], range_step=args[2], body=body)

            iterable = self._parse_expression(node.iter)
            return ForLoop(iterator_var=iter_var, is_range=False, iterable=iterable, body=body)

        elif isinstance(node, ast.Try):
            try_body = [self._parse_statement(s) for s in node.body if self._parse_statement(s) is not None]
            err_var = "err"
            catch_body = []
            if node.handlers:
                h = node.handlers[0]
                if h.name:
                    err_var = h.name
                catch_body = [self._parse_statement(s) for s in h.body if self._parse_statement(s) is not None]
            finally_body = [self._parse_statement(s) for s in node.finalbody if self._parse_statement(s) is not None]
            return TryCatch(try_body=try_body, error_var=err_var, catch_body=catch_body, finally_body=finally_body)

        elif isinstance(node, ast.Break):
            return BreakStatement()
        elif isinstance(node, ast.Continue):
            return ContinueStatement()

        elif isinstance(node, ast.Expr):
            expr = self._parse_expression(node.value)
            return ExpressionStatement(expr=expr)

        return None

    def _parse_expression(self, node: Optional[ast.AST]) -> IRExpression:
        if node is None:
            return Literal(None, DataType.VOID)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return Literal(value=node.value, raw_type=DataType.BOOL, inferred_type=IRType.bool_type())
            elif isinstance(node.value, int):
                return Literal(value=node.value, raw_type=DataType.INT, inferred_type=IRType.int_type())
            elif isinstance(node.value, float):
                return Literal(value=node.value, raw_type=DataType.FLOAT, inferred_type=IRType.float_type())
            elif isinstance(node.value, str):
                return Literal(value=node.value, raw_type=DataType.STRING, inferred_type=IRType.string_type())
            elif node.value is None:
                return Literal(value=None, raw_type=DataType.VOID, inferred_type=IRType.void_type())

        elif isinstance(node, ast.Name):
            return Identifier(name=node.id)

        elif isinstance(node, ast.BinOp):
            left = self._parse_expression(node.left)
            right = self._parse_expression(node.right)
            op = self._binop_to_str(node.op)
            return BinaryOp(left=left, op=op, right=right)

        elif isinstance(node, ast.Compare):
            left = self._parse_expression(node.left)
            op = self._cmpop_to_str(node.ops[0])
            right = self._parse_expression(node.comparators[0])
            return BinaryOp(left=left, op=op, right=right, inferred_type=IRType.bool_type())

        elif isinstance(node, ast.BoolOp):
            op = "&&" if isinstance(node.op, ast.And) else "||"
            vals = [self._parse_expression(v) for v in node.values]
            expr = vals[0]
            for v in vals[1:]:
                expr = BinaryOp(left=expr, op=op, right=v, inferred_type=IRType.bool_type())
            return expr

        elif isinstance(node, ast.UnaryOp):
            operand = self._parse_expression(node.operand)
            op = "!" if isinstance(node.op, ast.Not) else "-"
            return UnaryOp(op=op, operand=operand)

        elif isinstance(node, ast.Call):
            args = [self._parse_expression(a) for a in node.args]
            if isinstance(node.func, ast.Name):
                callee_name = node.func.id
                if callee_name == "print":
                    callee_name = "print"
                return FunctionCall(callee=callee_name, args=args)
            elif isinstance(node.func, ast.Attribute):
                recv = self._parse_expression(node.func.value)
                return MethodCall(receiver=recv, method=node.func.attr, args=args)

        elif isinstance(node, ast.Attribute):
            recv = self._parse_expression(node.value)
            return MemberAccess(receiver=recv, member=node.attr)

        elif isinstance(node, ast.Subscript):
            arr = self._parse_expression(node.value)
            idx = self._parse_expression(node.slice)
            return ArrayAccess(array=arr, index=idx)

        elif isinstance(node, ast.List):
            elems = [self._parse_expression(e) for e in node.elts]
            elem_type = elems[0].inferred_type if elems and elems[0].inferred_type else IRType.any_type()
            return ListLiteral(elements=elems, inferred_type=IRType.list_type(elem_type))

        elif isinstance(node, ast.Dict):
            entries = []
            for k, v in zip(node.keys, node.values):
                if k:
                    entries.append(DictEntry(key=self._parse_expression(k), value=self._parse_expression(v)))
            return DictLiteral(entries=entries, inferred_type=IRType.dict_type())

        elif isinstance(node, ast.IfExp):
            cond = self._parse_expression(node.test)
            body = self._parse_expression(node.body)
            orelse = self._parse_expression(node.orelse)
            return TernaryExpr(condition=cond, true_expr=body, false_expr=orelse)

        return Identifier(name=self._expr_to_str(node))

    def _binop_to_str(self, op: ast.AST) -> str:
        if isinstance(op, ast.Add): return "+"
        if isinstance(op, ast.Sub): return "-"
        if isinstance(op, ast.Mult): return "*"
        if isinstance(op, ast.Div): return "/"
        if isinstance(op, ast.Mod): return "%"
        return "+"

    def _cmpop_to_str(self, op: ast.AST) -> str:
        if isinstance(op, ast.Eq): return "=="
        if isinstance(op, ast.NotEq): return "!="
        if isinstance(op, ast.Lt): return "<"
        if isinstance(op, ast.LtE): return "<="
        if isinstance(op, ast.Gt): return ">"
        if isinstance(op, ast.GtE): return ">="
        if isinstance(op, ast.In): return "in"
        return "=="

    def _expr_to_str(self, node: ast.AST) -> str:
        try:
            return ast.unparse(node)
        except Exception:
            return ""
