"""
PolyShift - Rust Syntax and Structure Parser
Parses Rust source code into the PolyShift Universal Intermediate Representation.
"""
import re
import subprocess
import shutil
from typing import List, Tuple, Optional

from app.engines.parsers.base import BaseParser
from app.engines.ir import (
    Program, FunctionDef, Parameter, ClassDef, VariableDeclaration,
    Assignment, ReturnStatement, IfStatement, WhileLoop, ForLoop,
    ExpressionStatement, BinaryOp, FunctionCall, MethodCall, ArrayAccess, MemberAccess,
    ListLiteral, Literal, Identifier,
    IRType, DataType, IRExpression, IRStatement
)

class RustParser(BaseParser):
    @property
    def language_name(self) -> str:
        return "rust"

    def validate_syntax(self, code: str) -> Tuple[bool, List[str]]:
        rustc_bin = shutil.which("rustc")
        if rustc_bin:
            try:
                proc = subprocess.run(
                    [rustc_bin, "--crate-type=lib", "--emit=metadata", "-"],
                    input=code,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if proc.returncode == 0:
                    return True, []
                return False, [proc.stderr.strip()[:500]]
            except Exception:
                pass

        # Fallback brace check
        open_braces = code.count("{") - code.count("}")
        if open_braces != 0:
            return False, ["Mismatched curly braces in Rust code."]
        return True, []

    def parse(self, code: str) -> Program:
        program = Program(raw_source=code, source_language="rust")
        cleaned = self._strip_comments(code)
        self._parse_rust_structure(cleaned, program)
        return program

    def _strip_comments(self, code: str) -> str:
        no_multiline = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
        lines = []
        for line in no_multiline.splitlines():
            line_no_comment = re.sub(r"//.*$", "", line)
            lines.append(line_no_comment)
        return "\n".join(lines)

    def _parse_rust_structure(self, code: str, program: Program):
        # Match functions: (pub )?fn name(params) (-> ret)? {
        fn_regex = re.compile(r"(?:pub\s+)?fn\s+([a-zA-Z_]\w*)\s*\((.*?)\)(?:\s*->\s*([a-zA-Z_0-9<>&]+))?\s*\{")

        for match in fn_regex.finditer(code):
            fn_name = match.group(1).strip()
            raw_params = match.group(2).strip()
            ret_type_str = match.group(3).strip() if match.group(3) else "()"

            params = self._parse_param_list(raw_params)
            ret_type = self._map_rust_type(ret_type_str)

            body_code = self._extract_matching_block(code, match.end() - 1)
            body_stmts = self._parse_statements_block(body_code)

            program.functions.append(
                FunctionDef(
                    name=fn_name,
                    params=params,
                    return_type=ret_type,
                    body=body_stmts
                )
            )

        # Match top-level statements
        for stmt in self._parse_statements_block(code):
            if not isinstance(stmt, (IfStatement, ForLoop, WhileLoop)):
                program.statements.append(stmt)

    def _extract_matching_block(self, text: str, start_brace_pos: int) -> str:
        depth = 0
        start = -1
        for i in range(start_brace_pos, len(text)):
            if text[i] == "{":
                if depth == 0:
                    start = i + 1
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i].strip()
        return ""

    def _map_rust_type(self, type_str: str) -> IRType:
        t = type_str.strip()
        if t in ("i32", "i64", "u32", "u64", "usize", "isize"):
            return IRType.int_type()
        elif t in ("f32", "f64"):
            return IRType.float_type()
        elif t in ("String", "&str"):
            return IRType.string_type()
        elif t == "bool":
            return IRType.bool_type()
        elif t == "()":
            return IRType.void_type()
        elif t.startswith("Vec<"):
            inner = t[4:-1].strip()
            return IRType.list_type(self._map_rust_type(inner))
        return IRType.custom(t)

    def _parse_param_list(self, params_str: str) -> List[Parameter]:
        if not params_str.strip():
            return []
        params = []
        for p in params_str.split(","):
            tokens = p.strip().split(":")
            if len(tokens) == 2:
                p_name = tokens[0].replace("&mut", "").replace("&", "").strip()
                p_type = self._map_rust_type(tokens[1])
                params.append(Parameter(name=p_name, param_type=p_type))
            elif tokens[0] in ("self", "&self", "&mut self"):
                continue
            else:
                params.append(Parameter(name=tokens[0].strip()))
        return params

    def _parse_statements_block(self, block_text: str) -> List[IRStatement]:
        stmts: List[IRStatement] = []
        if not block_text.strip():
            return stmts

        # For loop: for i in 0..n { ... }
        for_match = re.search(r"\bfor\s+([a-zA-Z_]\w*)\s+in\s+(\d+)\.\.(.*?)\s*\{", block_text)
        if for_match:
            var_name = for_match.group(1)
            start_val = int(for_match.group(2))
            end_expr = self._parse_expr_str(for_match.group(3))
            body_code = self._extract_matching_block(block_text, for_match.end() - 1)
            stmts.append(ForLoop(
                iterator_var=var_name,
                is_range=True,
                range_start=Literal(start_val, DataType.INT),
                range_end=end_expr,
                body=self._parse_statements_block(body_code)
            ))

        # If statement: if cond { ... }
        if_match = re.search(r"\bif\s+(.*?)\s*\{", block_text)
        if if_match and not if_match.group(1).startswith("let"):
            cond_str = if_match.group(1)
            body_code = self._extract_matching_block(block_text, if_match.end() - 1)
            cond_expr = self._parse_expr_str(cond_str)
            stmts.append(IfStatement(condition=cond_expr, then_body=self._parse_statements_block(body_code)))

        # Semicolon-delimited statements
        for part in block_text.split(";"):
            s = self._parse_single_statement(part.strip())
            if s:
                stmts.append(s)

        return stmts

    def _parse_single_statement(self, s: str) -> Optional[IRStatement]:
        if not s or s.startswith("use ") or s.startswith("mod "):
            return None

        # Return
        if s.startswith("return"):
            val_str = s[6:].strip()
            return ReturnStatement(value=self._parse_expr_str(val_str) if val_str else None)

        # println!(...)
        if s.startswith("println!") or s.startswith("print!"):
            m = re.match(r"^println!\s*\((.*?)\)$", s)
            if m:
                raw_args = m.group(1).split(",")
                # If first argument is format string like "{}", get rest
                args = []
                for a in raw_args[1:] if len(raw_args) > 1 else raw_args:
                    arg_str = a.strip()
                    if arg_str and not (arg_str.startswith('"') and "{}" in arg_str):
                        args.append(self._parse_expr_str(arg_str))
                return ExpressionStatement(expr=FunctionCall(callee="print", args=args))

        # Variable declaration: let (mut)? x (: type)? = val
        let_match = re.match(r"^let(?:\s+mut)?\s+([a-zA-Z_]\w*)(?:\s*:\s*([a-zA-Z0-9<>&_]+))?\s*(?:=\s*(.+))?$", s)
        if let_match:
            var_name = let_match.group(1)
            type_str = let_match.group(2)
            val_str = let_match.group(3)
            var_type = self._map_rust_type(type_str) if type_str else IRType.any_type()
            init_val = self._parse_expr_str(val_str) if val_str else None
            return VariableDeclaration(name=var_name, var_type=var_type, init_val=init_val, is_mut=True)

        # Assignment
        assign_match = re.match(r"^([a-zA-Z_]\w*(?:\[.*?\])?)\s*(\+=|-=|\*=|/=|%=|=)\s*(.+)$", s)
        if assign_match:
            target_str, op, val_str = assign_match.groups()
            return Assignment(target=self._parse_expr_str(target_str), op=op, value=self._parse_expr_str(val_str))

        # Function call
        call_match = re.match(r"^([a-zA-Z_]\w*)\s*\((.*?)\)$", s)
        if call_match:
            fn_name = call_match.group(1)
            args = [self._parse_expr_str(a.strip()) for a in call_match.group(2).split(",") if a.strip()]
            return ExpressionStatement(expr=FunctionCall(callee=fn_name, args=args))

        return None

    def _parse_expr_str(self, s: str) -> IRExpression:
        s = s.strip()
        if not s:
            return Literal(None, DataType.VOID)

        if s in ("true", "false"):
            return Literal(s == "true", DataType.BOOL)
        if re.match(r"^-?\d+$", s):
            return Literal(int(s), DataType.INT)
        if re.match(r"^-?\d+\.\d+$", s):
            return Literal(float(s), DataType.FLOAT)
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return Literal(s[1:-1], DataType.STRING)

        # vec![1, 2, 3]
        if s.startswith("vec![") and s.endswith("]"):
            inner = s[5:-1].strip()
            elems = [self._parse_expr_str(x.strip()) for x in inner.split(",") if x.strip()]
            return ListLiteral(elements=elems)

        # Binary ops
        for op in ["==", "!=", "<=", ">=", "<", ">", "+", "-", "*", "/", "%", "&&", "||"]:
            parts = s.split(f" {op} ")
            if len(parts) == 2:
                return BinaryOp(left=self._parse_expr_str(parts[0]), op=op, right=self._parse_expr_str(parts[1]))

        # Method call: v.push(...) or v.len()
        m_meth = re.match(r"^([a-zA-Z_]\w*)\.([a-zA-Z_]\w*)\s*\((.*?)\)$", s)
        if m_meth:
            recv = Identifier(m_meth.group(1))
            meth = m_meth.group(2)
            args = [self._parse_expr_str(a.strip()) for a in m_meth.group(3).split(",") if a.strip()]
            return MethodCall(receiver=recv, method=meth, args=args)

        # Indexing: arr[i]
        m_idx = re.match(r"^([a-zA-Z_]\w*)\[(.*?)\]$", s)
        if m_idx:
            return ArrayAccess(array=Identifier(m_idx.group(1)), index=self._parse_expr_str(m_idx.group(2)))

        return Identifier(name=s)
