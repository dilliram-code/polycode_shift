"""
PolyShift - JavaScript Code Generator
Renders universal IR into idiomatic modern ES6+ JavaScript.
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

class JavaScriptGenerator(BaseGenerator):
    @property
    def target_language(self) -> str:
        return "javascript"

    def generate(self, program: Program) -> str:
        lines: List[str] = []

        # Classes
        for cls in program.classes:
            lines.extend(self._gen_class(cls))
            lines.append("")

        # Functions
        for fn in program.functions:
            lines.extend(self._gen_function(fn))
            lines.append("")

        # Statements
        for stmt in program.statements:
            lines.extend(self._gen_statement(stmt, indent=0))

        result = "\n".join(lines).strip()
        return result if result else "// Empty program"

    def _gen_class(self, cls: ClassDef) -> List[str]:
        ext = f" extends {cls.base_classes[0]}" if cls.base_classes else ""
        lines = [f"class {cls.name}{ext} {{"]

        for field in cls.fields:
            init = f" = {self._gen_expr(field.init_val)}" if field.init_val else ""
            lines.append(f"    {field.name}{init};")

        for method in cls.methods:
            method_lines = self._gen_function(method, is_method=True, indent_level=1)
            lines.extend(method_lines)

        lines.append("}")
        return lines

    def _gen_function(self, fn: FunctionDef, is_method: bool = False, indent_level: int = 0) -> List[str]:
        indent = "    " * indent_level
        params = [p.name for p in fn.params]
        async_str = "async " if fn.is_async else ""
        prefix = "" if is_method else f"{async_str}function "

        lines = [f"{indent}{prefix}{fn.name}({', '.join(params)}) {{"]

        if not fn.body:
            lines.append(f"{indent}}}")
            return lines

        for stmt in fn.body:
            lines.extend(self._gen_statement(stmt, indent=indent_level + 1))

        lines.append(f"{indent}}}")
        return lines

    def _gen_statement(self, stmt: IRStatement, indent: int = 0) -> List[str]:
        p = "    " * indent
        if isinstance(stmt, VariableDeclaration):
            kw = "const" if stmt.is_const else "let"
            val = self._gen_expr(stmt.init_val) if stmt.init_val else "undefined"
            return [f"{p}{kw} {stmt.name} = {val};"]

        elif isinstance(stmt, Assignment):
            target = self._gen_expr(stmt.target)
            val = self._gen_expr(stmt.value)
            return [f"{p}{target} {stmt.op} {val};"]

        elif isinstance(stmt, ReturnStatement):
            if stmt.value:
                return [f"{p}return {self._gen_expr(stmt.value)};"]
            return [f"{p}return;"]

        elif isinstance(stmt, IfStatement):
            lines = [f"{p}if ({self._gen_expr(stmt.condition)}) {{"]
            for s in stmt.then_body:
                lines.extend(self._gen_statement(s, indent + 1))
            lines.append(f"{p}}}")

            for cond, elif_body in stmt.elif_branches:
                lines.append(f"{p}else if ({self._gen_expr(cond)}) {{")
                for s in elif_body:
                    lines.extend(self._gen_statement(s, indent + 1))
                lines.append(f"{p}}}")

            if stmt.else_body:
                lines.append(f"{p}else {{")
                for s in stmt.else_body:
                    lines.extend(self._gen_statement(s, indent + 1))
                lines.append(f"{p}}}")

            return lines

        elif isinstance(stmt, WhileLoop):
            lines = [f"{p}while ({self._gen_expr(stmt.condition)}) {{"]
            for s in stmt.body:
                lines.extend(self._gen_statement(s, indent + 1))
            lines.append(f"{p}}}")
            return lines

        elif isinstance(stmt, ForLoop):
            if stmt.is_range:
                start = self._gen_expr(stmt.range_start) if stmt.range_start else "0"
                end = self._gen_expr(stmt.range_end) if stmt.range_end else "0"
                lines = [f"{p}for (let {stmt.iterator_var} = {start}; {stmt.iterator_var} < {end}; {stmt.iterator_var}++) {{"]
            else:
                iter_expr = self._gen_expr(stmt.iterable) if stmt.iterable else "[]"
                lines = [f"{p}for (const {stmt.iterator_var} of {iter_expr}) {{"]

            for s in stmt.body:
                lines.extend(self._gen_statement(s, indent + 1))
            lines.append(f"{p}}}")
            return lines

        elif isinstance(stmt, TryCatch):
            lines = [f"{p}try {{"]
            for s in stmt.try_body:
                lines.extend(self._gen_statement(s, indent + 1))
            lines.append(f"{p}}} catch ({stmt.error_var}) {{")
            for s in stmt.catch_body:
                lines.extend(self._gen_statement(s, indent + 1))
            if stmt.finally_body:
                lines.append(f"{p}}} finally {{")
                for s in stmt.finally_body:
                    lines.extend(self._gen_statement(s, indent + 1))
            lines.append(f"{p}}}")
            return lines

        elif isinstance(stmt, BreakStatement):
            return [f"{p}break;"]
        elif isinstance(stmt, ContinueStatement):
            return [f"{p}continue;"]

        elif isinstance(stmt, ExpressionStatement):
            # Console.log
            if isinstance(stmt.expr, FunctionCall) and stmt.expr.callee in ("print", "println", "console.log"):
                args = [self._gen_expr(a) for a in stmt.expr.args]
                return [f"{p}console.log({', '.join(args)} packing);" if False else f"{p}console.log({', '.join(args)});" ]
            return [f"{p}{self._gen_expr(stmt.expr)};"]

        return []

    def _gen_expr(self, expr: Optional[IRExpression]) -> str:
        if expr is None:
            return "null"

        if isinstance(expr, Literal):
            if expr.raw_type == DataType.BOOL:
                return "true" if expr.value else "false"
            elif expr.raw_type == DataType.VOID or expr.value is None:
                return "null"
            elif expr.raw_type == DataType.STRING:
                return f'"{expr.value}"'
            return str(expr.value)

        elif isinstance(expr, Identifier):
            return expr.name

        elif isinstance(expr, BinaryOp):
            op = expr.op
            if op == "==": op = "==="
            elif op == "!=": op = "!=="
            return f"({self._gen_expr(expr.left)} {op} {self._gen_expr(expr.right)})"

        elif isinstance(expr, UnaryOp):
            return f"{expr.op}{self._gen_expr(expr.operand)}"

        elif isinstance(expr, FunctionCall):
            if expr.callee in ("print", "println", "console.log"):
                args = [self._gen_expr(a) for a in expr.args]
                return f"console.log({', '.join(args)})"
            args = [self._gen_expr(a) for a in expr.args]
            return f"{expr.callee}({', '.join(args)})"

        elif isinstance(expr, MethodCall):
            receiver = self._gen_expr(expr.receiver)
            method = expr.method
            if method in ("append", "push_back"):
                method = "push"
            elif method == "len":
                return f"{receiver}.length"
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
            return f"({self._gen_expr(expr.condition)} ? {self._gen_expr(expr.true_expr)} : {self._gen_expr(expr.false_expr)})"

        return ""

