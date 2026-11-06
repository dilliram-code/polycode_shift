"""
PolyShift - JavaScript AST Parser
Parses modern JavaScript (ES6+) into the PolyShift Universal Intermediate Representation.
"""
import re
import subprocess
import shutil
from typing import List, Tuple, Optional, Any

from app.engines.parsers.base import BaseParser
from app.engines.ir import (
    Program, FunctionDef, Parameter, ClassDef, VariableDeclaration,
    Assignment, ReturnStatement, IfStatement, WhileLoop, ForLoop,
    TryCatch, BreakStatement, ContinueStatement, ExpressionStatement,
    BinaryOp, UnaryOp, FunctionCall, MethodCall, ArrayAccess, MemberAccess,
    ListLiteral, DictLiteral, DictEntry, Literal, Identifier,
    IRType, DataType, IRExpression, IRStatement
)

class JavaScriptParser(BaseParser):
    @property
    def language_name(self) -> str:
        return "javascript"

    def validate_syntax(self, code: str) -> Tuple[bool, List[str]]:
        node_bin = shutil.which("node")
        if node_bin:
            try:
                proc = subprocess.run(
                    [node_bin, "--check", "-e", code],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if proc.returncode == 0:
                    return True, []
                return False, [proc.stderr.strip() or "Syntax error in JavaScript"]
            except Exception as e:
                pass
        # Fallback brace/bracket balance check
        open_braces = code.count("{") - code.count("}")
        open_parens = code.count("(") - code.count(")")
        open_brackets = code.count("[") - code.count("]")
        if open_braces != 0 or open_parens != 0 or open_brackets != 0:
            return False, ["Mismatched braces, parentheses, or brackets."]
        return True, []

    def parse(self, code: str) -> Program:
        program = Program(raw_source=code, source_language="javascript")
        cleaned_lines = self._strip_comments(code)
        
        # Tokenize and parse top-level blocks
        self._parse_code_block(cleaned_lines, program)
        return program

    def _strip_comments(self, code: str) -> str:
        # Remove single line comments // ... and multi-line /* ... */
        code_no_multiline = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
        lines = []
        for line in code_no_multiline.splitlines():
            line_no_comment = re.sub(r"//.*$", "", line)
            lines.append(line_no_comment)
        return "\n".join(lines)

    def _parse_code_block(self, code: str, program: Program):
        # Look for classes
        class_regex = re.compile(r"class\s+([a-zA-Z_]\w*)(?:\s+extends\s+([a-zA-Z_]\w*))?\s*\{")
        # Look for functions: function name(args) { or const/let name = (args) => {
        func_regex = re.compile(r"(?:async\s+)?function\s+([a-zA-Z_]\w*)\s*\((.*?)\)\s*\{")
        arrow_func_regex = re.compile(r"(?:const|let|var)\s+([a-zA-Z_]\w*)\s*=\s*(?:async\s+)?\((.*?)\)\s*=>\s*\{")
        
        # Parse functions
        for match in func_regex.finditer(code):
            func_name = match.group(1)
            raw_params = match.group(2)
            params = self._parse_param_list(raw_params)
            body_code = self._extract_matching_block(code, match.end() - 1)
            body_stmts = self._parse_statements_block(body_code)
            program.functions.append(FunctionDef(name=func_name, params=params, body=body_stmts))

        for match in arrow_func_regex.finditer(code):
            func_name = match.group(1)
            raw_params = match.group(2)
            params = self._parse_param_list(raw_params)
            body_code = self._extract_matching_block(code, match.end() - 1)
            body_stmts = self._parse_statements_block(body_code)
            program.functions.append(FunctionDef(name=func_name, params=params, body=body_stmts))

        for match in class_regex.finditer(code):
            cls_name = match.group(1)
            base_cls = [match.group(2)] if match.group(2) else []
            body_code = self._extract_matching_block(code, match.end() - 1)
            methods = []
            method_matches = re.finditer(r"([a-zA-Z_]\w*)\s*\((.*?)\)\s*\{", body_code)
            for m in method_matches:
                m_name = m.group(1)
                m_params = self._parse_param_list(m.group(2))
                m_body = self._extract_matching_block(body_code, m.end() - 1)
                methods.append(FunctionDef(name=m_name, params=m_params, body=self._parse_statements_block(m_body), is_method=True))
            program.classes.append(ClassDef(name=cls_name, base_classes=base_cls, methods=methods))

        # Parse statements that are outside functions and classes
        lines = code.split(";")
        for part in lines:
            stmt = self._parse_single_statement(part.strip())
            if stmt:
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

    def _parse_param_list(self, params_str: str) -> List[Parameter]:
        if not params_str.strip():
            return []
        items = params_str.split(",")
        params = []
        for it in items:
            name = it.strip().split("=")[0].strip()
            if name:
                params.append(Parameter(name=name, param_type=IRType.any_type()))
        return params

    def _parse_statements_block(self, block_text: str) -> List[IRStatement]:
        stmts: List[IRStatement] = []
        if not block_text.strip():
            return stmts

        # If statement match
        if_match = re.search(r"\bif\s*\((.*?)\)\s*\{", block_text)
        if if_match:
            cond_str = if_match.group(1)
            body_code = self._extract_matching_block(block_text, if_match.end() - 1)
            cond_expr = self._parse_expr_str(cond_str)
            stmts.append(IfStatement(condition=cond_expr, then_body=self._parse_statements_block(body_code)))

        # For loop match
        for_match = re.search(r"\bfor\s*\(\s*(?:let|var|const)?\s*([a-zA-Z_]\w*)\s*=\s*(\d+)\s*;\s*\1\s*<\s*(.*?)\s*;\s*\1\+\+\s*\)\s*\{", block_text)
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

        # Line by line statements
        parts = block_text.split(";")
        for p in parts:
            p_str = p.strip()
            s = self._parse_single_statement(p_str)
            if s and not isinstance(s, (IfStatement, ForLoop)):
                stmts.append(s)

        return stmts

    def _parse_single_statement(self, s: str) -> Optional[IRStatement]:
        if not s or s.startswith("function") or s.startswith("class"):
            return None

        # Return statement
        if s.startswith("return"):
            rest = s[6:].strip()
            val = self._parse_expr_str(rest) if rest else None
            return ReturnStatement(value=val)

        # Variable declaration
        decl_match = re.match(r"^(const|let|var)\s+([a-zA-Z_]\w*)\s*=\s*(.+)$", s)
        if decl_match:
            kw, name, val_str = decl_match.groups()
            init_val = self._parse_expr_str(val_str)
            is_const = (kw == "const")
            return VariableDeclaration(name=name, var_type=init_val.inferred_type or IRType.any_type(), init_val=init_val, is_const=is_const)

        # Assignment
        assign_match = re.match(r"^([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*|\[.*?\])?)\s*(\+=|-=|\*=|/=|%=|=)\s*(.+)$", s)
        if assign_match:
            target_str, op, val_str = assign_match.groups()
            target_expr = self._parse_expr_str(target_str)
            val_expr = self._parse_expr_str(val_str)
            return Assignment(target=target_expr, op=op, value=val_expr)

        # Console.log
        if s.startswith("console.log"):
            m = re.match(r"^console\.log\s*\((.*?)\)$", s)
            if m:
                args = [self._parse_expr_str(a.strip()) for a in m.group(1).split(",") if a.strip()]
                return ExpressionStatement(expr=FunctionCall(callee="print", args=args))

        # Function call
        call_match = re.match(r"^([a-zA-Z_]\w*)\s*\((.*?)\)$", s)
        if call_match:
            fn_name = call_match.group(1)
            raw_args = call_match.group(2)
            args = [self._parse_expr_str(a.strip()) for a in raw_args.split(",") if a.strip()]
            return ExpressionStatement(expr=FunctionCall(callee=fn_name, args=args))

        return None

    def _parse_expr_str(self, s: str) -> IRExpression:
        s = s.strip()
        if not s:
            return Literal(None, DataType.VOID)

        # Literals
        if s in ("true", "false"):
            return Literal(value=(s == "true"), raw_type=DataType.BOOL, inferred_type=IRType.bool_type())
        if s == "null" or s == "undefined":
            return Literal(value=None, raw_type=DataType.VOID, inferred_type=IRType.void_type())
        if re.match(r"^-?\d+$", s):
            return Literal(value=int(s), raw_type=DataType.INT, inferred_type=IRType.int_type())
        if re.match(r"^-?\d+\.\d+$", s):
            return Literal(value=float(s), raw_type=DataType.FLOAT, inferred_type=IRType.float_type())
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return Literal(value=s[1:-1], raw_type=DataType.STRING, inferred_type=IRType.string_type())

        # List / Array literal
        if s.startswith("[") and s.endswith("]"):
            inner = s[1:-1].strip()
            elems = [self._parse_expr_str(x.strip()) for x in inner.split(",") if x.strip()]
            return ListLiteral(elements=elems, inferred_type=IRType.list_type())

        # Console.log
        if s.startswith("console.log"):
            m = re.match(r"^console\.log\s*\((.*?)\)$", s)
            if m:
                args = [self._parse_expr_str(a.strip()) for a in m.group(1).split(",") if a.strip()]
                return FunctionCall(callee="print", args=args)

        # Binary op
        for op in ["===", "==", "!==", "!=", "<=", ">=", "<", ">", "+", "-", "*", "/", "%", "&&", "||"]:
            parts = s.split(f" {op} ")
            if len(parts) == 2:
                left = self._parse_expr_str(parts[0])
                right = self._parse_expr_str(parts[1])
                clean_op = "==" if op == "===" else ("!=" if op == "!==" else op)
                return BinaryOp(left=left, op=clean_op, right=right)

        # Function Call
        m_call = re.match(r"^([a-zA-Z_]\w*)\s*\((.*?)\)$", s)
        if m_call:
            fn_name = m_call.group(1)
            raw_args = m_call.group(2)
            args = [self._parse_expr_str(a.strip()) for a in raw_args.split(",") if a.strip()]
            return FunctionCall(callee=fn_name, args=args)

        # Member access
        if "." in s:
            parts = s.split(".")
            return MemberAccess(receiver=Identifier(name=parts[0]), member=parts[1])

        # Array indexing
        m_idx = re.match(r"^([a-zA-Z_]\w*)\[(.*?)\]$", s)
        if m_idx:
            arr_name = m_idx.group(1)
            idx_expr = self._parse_expr_str(m_idx.group(2))
            return ArrayAccess(array=Identifier(name=arr_name), index=idx_expr)

        return Identifier(name=s)

