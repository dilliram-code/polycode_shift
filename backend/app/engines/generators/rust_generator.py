"""
PolyShift - Rust Code Generator
Renders universal IR into idiomatic, ownership-conscious Rust code.
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

class RustGenerator(BaseGenerator):
    @property
    def target_language(self) -> str:
        return "rust"

    def generate(self, program: Program) -> str:
        lines: List[str] = []

        # Classes mapped to Structs and Impls
        for cls in program.classes:
            lines.extend(self._gen_struct(cls))
            lines.append("")

        # Normal functions (except main)
        main_fn = None
        for fn in program.functions:
            if fn.name == "main":
                main_fn = fn
            else:
                lines.extend(self._gen_function(fn))
                lines.append("")

        # Generate fn main()
        if main_fn:
            lines.extend(self._gen_function(main_fn))
        elif program.statements:
            lines.append("fn main() {")
            for stmt in program.statements:
                lines.extend(self._gen_statement(stmt, indent=1))
            lines.append("}")

        result = "\n".join(lines).strip()
        return result if result else "// Empty program"

    def _gen_struct(self, cls: ClassDef) -> List[str]:
        lines = [f"#[derive(Debug, Clone)]", f"pub struct {cls.name} {{"]
        for field in cls.fields:
            type_str = self._map_type(field.var_type)
            lines.append(f"    pub {field.name}: {type_str},")
        lines.append("}")

        if cls.methods:
            lines.append(f"\nimpl {cls.name} {{")
            for method in cls.methods:
                lines.extend(self._gen_function(method, is_method=True, indent_level=1))
            lines.append("}")

        return lines

    def _gen_function(self, fn: FunctionDef, is_method: bool = False, indent_level: int = 0) -> List[str]:
        indent = "    " * indent_level
        params = []
        if is_method:
            params.append("&self")

        for p in fn.params:
            t = self._map_type(p.param_type)
            params.append(f"{p.name}: {t}")

        ret_str = ""
        if fn.return_type.kind != DataType.VOID and fn.return_type.kind != DataType.ANY:
            ret_str = f" -> {self._map_type(fn.return_type)}"

        lines = [f"{indent}pub fn {fn.name}({', '.join(params)}){ret_str} {{"]

        for stmt in fn.body:
            lines.extend(self._gen_statement(stmt, indent=indent_level + 1))

        lines.append(f"{indent}}}")
        return lines

    def _gen_statement(self, stmt: IRStatement, indent: int = 0) -> List[str]:
        p = "    " * indent
        if isinstance(stmt, VariableDeclaration):
            mut_kw = "mut " if stmt.is_mut else ""
            type_ann = ""
            if stmt.var_type.kind != DataType.ANY:
                type_ann = f": {self._map_type(stmt.var_type)}"
            val = self._gen_expr(stmt.init_val) if stmt.init_val else "Default::default()"
            return [f"{p}let {mut_kw}{stmt.name}{type_ann} = {val};"]

        elif isinstance(stmt, Assignment):
            target = self._gen_expr(stmt.target)
            val = self._gen_expr(stmt.value)
            return [f"{p}{target} {stmt.op} {val};"]

        elif isinstance(stmt, ReturnStatement):
            if stmt.value:
                return [f"{p}return {self._gen_expr(stmt.value)};"]
            return [f"{p}return;"]

        elif isinstance(stmt, IfStatement):
            lines = [f"{p}if {self._gen_expr(stmt.condition)} {{"]
            for s in stmt.then_body:
                lines.extend(self._gen_statement(s, indent + 1))
            lines.append(f"{p}}}")

            for cond, elif_body in stmt.elif_branches:
                lines.append(f"{p}else if {self._gen_expr(cond)} {{")
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
            lines = [f"{p}while {self._gen_expr(stmt.condition)} {{"]
            for s in stmt.body:
                lines.extend(self._gen_statement(s, indent + 1))
            lines.append(f"{p}}}")
            return lines

        elif isinstance(stmt, ForLoop):
            if stmt.is_range:
                start = self._gen_expr(stmt.range_start) if stmt.range_start else "0"
                end = self._gen_expr(stmt.range_end) if stmt.range_end else "0"
                lines = [f"{p}for {stmt.iterator_var} in {start}..{end} {{"]
            else:
                iter_expr = self._gen_expr(stmt.iterable) if stmt.iterable else "&[]"
                lines = [f"{p}for {stmt.iterator_var} in {iter_expr} {{"]

            for s in stmt.body:
                lines.extend(self._gen_statement(s, indent + 1))
            lines.append(f"{p}}}")
            return lines

        elif isinstance(stmt, ExpressionStatement):
            # Println!
            if isinstance(stmt.expr, FunctionCall) and stmt.expr.callee in ("print", "println", "console.log"):
                if not stmt.expr.args:
                    return [f"{p}println!();"]
                placeholders = " ".join(["{}"] * len(stmt.expr.args))
                args = [self._gen_expr(a) for a in stmt.expr.args]
                return [f'{p}println!("{placeholders}", {", ".join(args)});']

            return [f"{p}{self._gen_expr(stmt.expr)};"]

        elif isinstance(stmt, BreakStatement):
            return [f"{p}break;"]
        elif isinstance(stmt, ContinueStatement):
            return [f"{p}continue;"]

        return []

    def _gen_expr(self, expr: Optional[IRExpression]) -> str:
        if expr is None:
            return "()"

        if isinstance(expr, Literal):
            if expr.raw_type == DataType.BOOL:
                return "true" if expr.value else "false"
            elif expr.raw_type == DataType.VOID or expr.value is None:
                return "()"
            elif expr.raw_type == DataType.STRING:
                return f'String::from("{expr.value}")'
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
            if method in ("append", "push_back"):
                method = "push"
            elif method == "len":
                return f"{receiver}.len()"
            args = [self._gen_expr(a) for a in expr.args]
            return f"{receiver}.{method}({', '.join(args)})"

        elif isinstance(expr, ArrayAccess):
            return f"{self._gen_expr(expr.array)}[{self._gen_expr(expr.index)}]"

        elif isinstance(expr, MemberAccess):
            return f"{self._gen_expr(expr.receiver)}.{expr.member}"

        elif isinstance(expr, ListLiteral):
            elems = [self._gen_expr(e) for e in expr.elements]
            return f"vec![{', '.join(elems)}]"

        elif isinstance(expr, TernaryExpr):
            return f"(if {self._gen_expr(expr.condition)} {{ {self._gen_expr(expr.true_expr)} }} else {{ {self._gen_expr(expr.false_expr)} }})"

        return ""

    def _map_type(self, t: IRType) -> str:
        if t.kind == DataType.INT: return "i32"
        if t.kind == DataType.FLOAT: return "f64"
        if t.kind == DataType.STRING: return "String"
        if t.kind == DataType.BOOL: return "bool"
        if t.kind == DataType.VOID: return "()"
        if t.kind == DataType.LIST:
            elem = self._map_type(t.element_type) if t.element_type and t.element_type.kind != DataType.ANY else "i32"
            return f"Vec<{elem}>"
        if t.kind == DataType.CUSTOM: return t.custom_name or "String"
        return "i32"
