"""
PolyShift - Python Code Generator
Renders universal IR into idiomatic PEP 8 Python 3.12+ code.
"""
from typing import List, Optional
from app.engines.generators.base import BaseGenerator
from app.engines.ir import (
    Program, FunctionDef, Parameter, ClassDef, VariableDeclaration,
    Assignment, ReturnStatement, IfStatement, WhileLoop, ForLoop,
    TryCatch, BreakStatement, ContinueStatement, ExpressionStatement,
    BinaryOp, UnaryOp, FunctionCall, MethodCall, ArrayAccess, MemberAccess,
    ListLiteral, DictLiteral, Literal, Identifier, TernaryExpr,
    IRType, DataType, IRExpression, IRStatement
)

class PythonGenerator(BaseGenerator):
    @property
    def target_language(self) -> str:
        return "python"

    def generate(self, program: Program) -> str:
        lines: List[str] = []

        # Imports
        if program.imports:
            for imp in program.imports:
                if imp.imported_names:
                    lines.append(f"from {imp.module} import {', '.join(imp.imported_names)}")
                else:
                    lines.append(f"import {imp.module}")
            lines.append("")

        # Classes
        for cls in program.classes:
            lines.extend(self._gen_class(cls))
            lines.append("")

        # Functions
        for fn in program.functions:
            lines.extend(self._gen_function(fn))
            lines.append("")

        # Top-level statements
        if program.statements:
            for stmt in program.statements:
                lines.extend(self._gen_statement(stmt, indent=0))

        result = "\n".join(lines).strip()
        return result if result else "# Empty program"

    def _gen_class(self, cls: ClassDef) -> List[str]:
        base_str = f"({', '.join(cls.base_classes)})" if cls.base_classes else ""
        lines = [f"class {cls.name}{base_str}:"]

        if cls.docstring:
            lines.append(f'    """{cls.docstring}"""')

        # Fields
        for field in cls.fields:
            type_str = f": {self._map_type(field.var_type)}" if field.var_type.kind != DataType.ANY else ""
            init_str = f" = {self._gen_expr(field.init_val)}" if field.init_val else ""
            lines.append(f"    {field.name}{type_str}{init_str}")

        if not cls.methods and not cls.fields:
            lines.append("    pass")
            return lines

        # Methods
        for method in cls.methods:
            method_lines = self._gen_function(method, is_method=True, indent_level=1)
            lines.extend(method_lines)

        return lines

    def _gen_function(self, fn: FunctionDef, is_method: bool = False, indent_level: int = 0) -> List[str]:
        indent = "    " * indent_level
        params = []
        if is_method:
            params.append("self")

        for p in fn.params:
            type_str = f": {self._map_type(p.param_type)}" if p.param_type.kind != DataType.ANY else ""
            def_str = f" = {self._gen_expr(p.default_val)}" if p.default_val else ""
            params.append(f"{p.name}{type_str}{def_str}")

        ret_type_str = ""
        if fn.return_type.kind != DataType.VOID and fn.return_type.kind != DataType.ANY:
            ret_type_str = f" -> {self._map_type(fn.return_type)}"

        async_prefix = "async " if fn.is_async else ""
        lines = [f"{indent}{async_prefix}def {fn.name}({', '.join(params)}){ret_type_str}:"]

        if fn.docstring:
            lines.append(f'{indent}    """{fn.docstring}"""')

        if not fn.body:
            lines.append(f"{indent}    pass")
            return lines

        for stmt in fn.body:
            lines.extend(self._gen_statement(stmt, indent=indent_level + 1))

        return lines

    def _gen_statement(self, stmt: IRStatement, indent: int = 0) -> List[str]:
        p = "    " * indent
        if isinstance(stmt, VariableDeclaration):
            val_str = self._gen_expr(stmt.init_val) if stmt.init_val else "None"
            return [f"{p}{stmt.name} = {val_str}"]

        elif isinstance(stmt, Assignment):
            target = self._gen_expr(stmt.target)
            val = self._gen_expr(stmt.value)
            return [f"{p}{target} {stmt.op} {val}"]

        elif isinstance(stmt, ReturnStatement):
            if stmt.value:
                return [f"{p}return {self._gen_expr(stmt.value)}"]
            return [f"{p}return"]

        elif isinstance(stmt, IfStatement):
            lines = [f"{p}if {self._gen_expr(stmt.condition)}:"]
            if stmt.then_body:
                for s in stmt.then_body:
                    lines.extend(self._gen_statement(s, indent + 1))
            else:
                lines.append(f"{p}    pass")

            for cond, elif_body in stmt.elif_branches:
                lines.append(f"{p}elif {self._gen_expr(cond)}:")
                for s in elif_body:
                    lines.extend(self._gen_statement(s, indent + 1))

            if stmt.else_body:
                lines.append(f"{p}else:")
                for s in stmt.else_body:
                    lines.extend(self._gen_statement(s, indent + 1))

            return lines

        elif isinstance(stmt, WhileLoop):
            lines = [f"{p}while {self._gen_expr(stmt.condition)}:"]
            if stmt.body:
                for s in stmt.body:
                    lines.extend(self._gen_statement(s, indent + 1))
            else:
                lines.append(f"{p}    pass")
            return lines

        elif isinstance(stmt, ForLoop):
            if stmt.is_range:
                start = self._gen_expr(stmt.range_start) if stmt.range_start else "0"
                end = self._gen_expr(stmt.range_end) if stmt.range_end else "0"
                if stmt.range_step:
                    step = self._gen_expr(stmt.range_step)
                    iter_expr = f"range({start}, {end}, {step})"
                elif start == "0":
                    iter_expr = f"range({end})"
                else:
                    iter_expr = f"range({start}, {end})"
            else:
                iter_expr = self._gen_expr(stmt.iterable) if stmt.iterable else "[]"

            lines = [f"{p}for {stmt.iterator_var} in {iter_expr}:"]
            if stmt.body:
                for s in stmt.body:
                    lines.extend(self._gen_statement(s, indent + 1))
            else:
                lines.append(f"{p}    pass")
            return lines

        elif isinstance(stmt, TryCatch):
            lines = [f"{p}try:"]
            for s in stmt.try_body:
                lines.extend(self._gen_statement(s, indent + 1))
            lines.append(f"{p}except Exception as {stmt.error_var}:")
            if stmt.catch_body:
                for s in stmt.catch_body:
                    lines.extend(self._gen_statement(s, indent + 1))
            else:
                lines.append(f"{p}    pass")
            if stmt.finally_body:
                lines.append(f"{p}finally:")
                for s in stmt.finally_body:
                    lines.extend(self._gen_statement(s, indent + 1))
            return lines

        elif isinstance(stmt, BreakStatement):
            return [f"{p}break"]
        elif isinstance(stmt, ContinueStatement):
            return [f"{p}continue"]

        elif isinstance(stmt, ExpressionStatement):
            return [f"{p}{self._gen_expr(stmt.expr)}"]

        return []

    def _gen_expr(self, expr: Optional[IRExpression]) -> str:
        if expr is None:
            return "None"

        if isinstance(expr, Literal):
            if expr.raw_type == DataType.BOOL:
                return "True" if expr.value else "False"
            elif expr.raw_type == DataType.VOID or expr.value is None:
                return "None"
            elif expr.raw_type == DataType.STRING:
                return f'"{expr.value}"'
            return str(expr.value)

        elif isinstance(expr, Identifier):
            return expr.name

        elif isinstance(expr, BinaryOp):
            op = expr.op
            if op == "&&": op = "and"
            elif op == "||": op = "or"
            return f"({self._gen_expr(expr.left)} {op} {self._gen_expr(expr.right)})"

        elif isinstance(expr, UnaryOp):
            op = "not " if expr.op in ("!", "not") else expr.op
            return f"{op}{self._gen_expr(expr.operand)}"

        elif isinstance(expr, FunctionCall):
            callee = "print" if expr.callee in ("print", "println", "console.log") else expr.callee
            args = [self._gen_expr(a) for a in expr.args]
            return f"{callee}({', '.join(args)})"

        elif isinstance(expr, MethodCall):
            receiver = self._gen_expr(expr.receiver)
            method = expr.method
            if method in ("push", "push_back", "append"):
                method = "append"
            elif method == "len":
                return f"len({receiver})"
            args = [self._gen_expr(a) for a in expr.args]
            return f"{receiver}.{method}({', '.join(args)})"

        elif isinstance(expr, ArrayAccess):
            return f"{self._gen_expr(expr.array)}[{self._gen_expr(expr.index)}]"

        elif isinstance(expr, MemberAccess):
            return f"{self._gen_expr(expr.receiver)}.{expr.member}"

        elif isinstance(expr, ListLiteral):
            elems = [self._gen_expr(e) for e in expr.elements]
            return f"[{', '.join(elems)}]"

        elif isinstance(expr, DictLiteral):
            entries = [f"{self._gen_expr(e.key)}: {self._gen_expr(e.value)}" for e in expr.entries]
            return "{" + ", ".join(entries) + "}"

        elif isinstance(expr, TernaryExpr):
            return f"({self._gen_expr(expr.true_expr)} if {self._gen_expr(expr.condition)} else {self._gen_expr(expr.false_expr)})"

        return ""

    def _map_type(self, t: IRType) -> str:
        if t.kind == DataType.INT: return "int"
        if t.kind == DataType.FLOAT: return "float"
        if t.kind == DataType.STRING: return "str"
        if t.kind == DataType.BOOL: return "bool"
        if t.kind == DataType.VOID: return "None"
        if t.kind == DataType.LIST:
            elem = self._map_type(t.element_type) if t.element_type else "Any"
            return f"list[{elem}]"
        if t.kind == DataType.DICT: return "dict"
        if t.kind == DataType.CUSTOM: return t.custom_name or "Any"
        return "Any"
