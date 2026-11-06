"""
PolyShift - C++ Code Generator
Renders universal IR into idiomatic C++17/20 code.
"""
from typing import List, Set, Optional
from app.engines.generators.base import BaseGenerator
from app.engines.ir import (
    Program, FunctionDef, Parameter, ClassDef, VariableDeclaration,
    Assignment, ReturnStatement, IfStatement, WhileLoop, ForLoop,
    TryCatch, BreakStatement, ContinueStatement, ExpressionStatement,
    BinaryOp, UnaryOp, FunctionCall, MethodCall, ArrayAccess, MemberAccess,
    ListLiteral, DictLiteral, Literal, Identifier, TernaryExpr,
    IRType, DataType, IRExpression, IRStatement
)

class CppGenerator(BaseGenerator):
    @property
    def target_language(self) -> str:
        return "cpp"

    def generate(self, program: Program) -> str:
        includes: Set[str] = {"<iostream>"}
        has_vectors = False
        has_strings = False
        has_maps = False

        # Scan for needed headers
        for fn in program.functions:
            if fn.return_type.kind == DataType.LIST:
                has_vectors = True
            for p in fn.params:
                if p.param_type.kind == DataType.LIST:
                    has_vectors = True
                elif p.param_type.kind == DataType.STRING:
                    has_strings = True

        if has_vectors: includes.add("<vector>")
        if has_strings: includes.add("<string>")
        if has_maps: includes.add("<map>")

        lines: List[str] = [f"#include {inc}" for inc in sorted(list(includes))]
        lines.append("")

        # Classes
        for cls in program.classes:
            lines.extend(self._gen_class(cls))
            lines.append("")

        # Normal functions (except main)
        main_fn = None
        for fn in program.functions:
            if fn.name == "main":
                main_fn = fn
            else:
                lines.extend(self._gen_function(fn))
                lines.append("")

        # If there are top-level statements or a main function, generate int main()
        if main_fn:
            lines.extend(self._gen_function(main_fn))
        elif program.statements:
            lines.append("int main() {")
            for stmt in program.statements:
                lines.extend(self._gen_statement(stmt, indent=1))
            lines.append("    return 0;")
            lines.append("}")

        return "\n".join(lines).strip()

    def _gen_class(self, cls: ClassDef) -> List[str]:
        inheritance = ""
        if cls.base_classes:
            inheritance = f" : public {', public '.join(cls.base_classes)}"

        lines = [f"class {cls.name}{inheritance} {{", "public:"]

        # Fields
        for field in cls.fields:
            type_str = self._map_type(field.var_type)
            init_str = f" = {self._gen_expr(field.init_val)}" if field.init_val else ""
            lines.append(f"    {type_str} {field.name}{init_str};")

        # Methods
        for method in cls.methods:
            method_lines = self._gen_function(method, indent_level=1)
            lines.extend(method_lines)

        lines.append("};")
        return lines

    def _gen_function(self, fn: FunctionDef, indent_level: int = 0) -> List[str]:
        indent = "    " * indent_level
        params = []
        for p in fn.params:
            t = self._map_type(p.param_type)
            # Pass vectors and strings by const reference if appropriate
            if t.startswith("std::vector") or t == "std::string":
                p_str = f"const {t}& {p.name}"
            else:
                p_str = f"{t} {p.name}"
            params.append(p_str)

        ret_type = "int" if fn.name == "main" else self._map_type(fn.return_type)
        lines = [f"{indent}{ret_type} {fn.name}({', '.join(params)}) {{"]

        for stmt in fn.body:
            lines.extend(self._gen_statement(stmt, indent=indent_level + 1))

        if fn.name == "main" and not any(isinstance(s, ReturnStatement) for s in fn.body):
            lines.append(f"{indent}    return 0;")

        lines.append(f"{indent}}}")
        return lines

    def _gen_statement(self, stmt: IRStatement, indent: int = 0) -> List[str]:
        p = "    " * indent
        if isinstance(stmt, VariableDeclaration):
            type_str = self._map_type(stmt.var_type)
            if type_str == "auto" and not stmt.init_val:
                type_str = "int"
            init_str = f" = {self._gen_expr(stmt.init_val)}" if stmt.init_val else ""
            const_prefix = "const " if stmt.is_const else ""
            return [f"{p}{const_prefix}{type_str} {stmt.name}{init_str};"]

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
                step_str = f"{stmt.iterator_var} += {self._gen_expr(stmt.range_step)}" if stmt.range_step else f"{stmt.iterator_var}++"
                lines = [f"{p}for (int {stmt.iterator_var} = {start}; {stmt.iterator_var} < {end}; {step_str}) {{"]
            else:
                iter_expr = self._gen_expr(stmt.iterable) if stmt.iterable else "{}"
                lines = [f"{p}for (const auto& {stmt.iterator_var} : {iter_expr}) {{"]

            for s in stmt.body:
                lines.extend(self._gen_statement(s, indent + 1))
            lines.append(f"{p}}}")
            return lines

        elif isinstance(stmt, ExpressionStatement):
            # Check if this is a print statement
            if isinstance(stmt.expr, FunctionCall) and stmt.expr.callee in ("print", "println", "console.log"):
                if not stmt.expr.args:
                    return [f"{p}std::cout << std::endl;"]
                parts = [self._gen_expr(a) for a in stmt.expr.args]
                return [f"{p}std::cout << {' << \" \" << '.join(parts)} << std::endl;"]
            return [f"{p}{self._gen_expr(stmt.expr)};"]

        elif isinstance(stmt, BreakStatement):
            return [f"{p}break;"]
        elif isinstance(stmt, ContinueStatement):
            return [f"{p}continue;"]

        return []

    def _gen_expr(self, expr: Optional[IRExpression]) -> str:
        if expr is None:
            return "nullptr"

        if isinstance(expr, Literal):
            if expr.raw_type == DataType.BOOL:
                return "true" if expr.value else "false"
            elif expr.raw_type == DataType.VOID or expr.value is None:
                return "nullptr"
            elif expr.raw_type == DataType.STRING:
                return f'std::string("{expr.value}")'
            return str(expr.value)

        elif isinstance(expr, Identifier):
            return expr.name

        elif isinstance(expr, BinaryOp):
            return f"({self._gen_expr(expr.left)} {expr.op} {self._gen_expr(expr.right)})"

        elif isinstance(expr, UnaryOp):
            return f"{expr.op}{self._gen_expr(expr.operand)}"

        elif isinstance(expr, FunctionCall):
            args = [self._gen_expr(a) for a in expr.args]
            return f"{expr.callee}({', '.join(args)})"

        elif isinstance(expr, MethodCall):
            receiver = self._gen_expr(expr.receiver)
            method = expr.method
            if method in ("append", "push"):
                method = "push_back"
            elif method == "len":
                return f"{receiver}.size()"
            args = [self._gen_expr(a) for a in expr.args]
            return f"{receiver}.{method}({', '.join(args)})"

        elif isinstance(expr, ArrayAccess):
            return f"{self._gen_expr(expr.array)}[{self._gen_expr(expr.index)}]"

        elif isinstance(expr, MemberAccess):
            return f"{self._gen_expr(expr.receiver)}.{expr.member}"

        elif isinstance(expr, ListLiteral):
            elems = [self._gen_expr(e) for e in expr.elements]
            return f"{{{', '.join(elems)}}}"

        elif isinstance(expr, TernaryExpr):
            return f"({self._gen_expr(expr.condition)} ? {self._gen_expr(expr.true_expr)} : {self._gen_expr(expr.false_expr)})"

        return ""

    def _map_type(self, t: IRType) -> str:
        if t.kind == DataType.INT: return "int"
        if t.kind == DataType.FLOAT: return "double"
        if t.kind == DataType.STRING: return "std::string"
        if t.kind == DataType.BOOL: return "bool"
        if t.kind == DataType.VOID: return "void"
        if t.kind == DataType.LIST:
            elem = self._map_type(t.element_type) if t.element_type and t.element_type.kind != DataType.ANY else "int"
            return f"std::vector<{elem}>"
        if t.kind == DataType.DICT: return "std::map<std::string, auto>"
        if t.kind == DataType.CUSTOM: return t.custom_name or "auto"
        return "auto"
