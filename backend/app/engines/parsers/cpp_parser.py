"""
PolyShift - C++ Syntax and Structure Parser
Parses C++ (C++17/20) into the PolyShift Universal Intermediate Representation.
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

class CppParser(BaseParser):
    @property
    def language_name(self) -> str:
        return "cpp"

    def validate_syntax(self, code: str) -> Tuple[bool, List[str]]:
        compiler = shutil.which("g++") or shutil.which("clang++")
        if compiler:
            try:
                proc = subprocess.run(
                    [compiler, "-fsyntax-only", "-std=c++17", "-x", "c++", "-"],
                    input=code,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if proc.returncode == 0:
                    return True, []
                # Return the compiler error message
                return False, [proc.stderr.strip()[:500]]
            except Exception:
                pass

        # Fallback check
        open_braces = code.count("{") - code.count("}")
        if open_braces != 0:
            return False, ["Mismatched curly braces in C++ code."]
        return True, []

    def parse(self, code: str) -> Program:
        program = Program(raw_source=code, source_language="cpp")
        cleaned = self._strip_comments(code)
        self._parse_cpp_structure(cleaned, program)
        return program

    def _strip_comments(self, code: str) -> str:
        no_multiline = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
        lines = []
        for line in no_multiline.splitlines():
            line_no_comment = re.sub(r"//.*$", "", line)
            lines.append(line_no_comment)
        return "\n".join(lines)

    def _parse_cpp_structure(self, code: str, program: Program):
        # Look for functions: e.g. int add(int a, int b) { ... }
        # or void print_sum(...) { ... }
        func_regex = re.compile(
            r"\b([a-zA-Z_]\w*(?:::<.*?>)?|<.*?>|\w+)\s+([a-zA-Z_]\w*)\s*\((.*?)\)\s*\{"
        )

        for match in func_regex.finditer(code):
            ret_type_str = match.group(1).strip()
            fn_name = match.group(2).strip()
            raw_params = match.group(3).strip()

            # Skip control structures masquerading as functions
            if fn_name in ("if", "while", "for", "switch", "catch"):
                continue

            params = self._parse_param_list(raw_params)
            ret_type = self._map_cpp_type(ret_type_str)

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

        # If there's an int main(), its statements can also be reflected
        # Look for top-level statements outside functions
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

    def _map_cpp_type(self, type_str: str) -> IRType:
        t = type_str.replace("std::", "").strip()
        if t in ("int", "long", "short", "size_t", "int32_t", "int64_t"):
            return IRType.int_type()
        elif t in ("double", "float"):
            return IRType.float_type()
        elif t in ("string", "const char*", "char*"):
            return IRType.string_type()
        elif t == "bool":
            return IRType.bool_type()
        elif t == "void":
            return IRType.void_type()
        elif t.startswith("vector<"):
            inner = t[7:-1].strip()
            return IRType.list_type(self._map_cpp_type(inner))
        return IRType.custom(t)

    def _parse_param_list(self, params_str: str) -> List[Parameter]:
        if not params_str.strip() or params_str.strip() == "void":
            return []
        params = []
        for p in params_str.split(","):
            tokens = p.strip().split()
            if len(tokens) >= 2:
                p_type = self._map_cpp_type(tokens[0])
                p_name = tokens[-1].replace("*", "").replace("&", "")
                params.append(Parameter(name=p_name, param_type=p_type))
            elif len(tokens) == 1:
                params.append(Parameter(name=tokens[0]))
        return params

    def _parse_statements_block(self, block_text: str) -> List[IRStatement]:
        stmts: List[IRStatement] = []
        if not block_text.strip():
            return stmts

        # For loop
        for_match = re.search(r"\bfor\s*\(\s*(?:int|size_t|auto)?\s*([a-zA-Z_]\w*)\s*=\s*(\d+)\s*;\s*\1\s*<\s*(.*?)\s*;\s*\1\+\+\s*\)\s*\{", block_text)
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

        # If statement
        if_match = re.search(r"\bif\s*\((.*?)\)\s*\{", block_text)
        if if_match:
            cond_str = if_match.group(1)
            body_code = self._extract_matching_block(block_text, if_match.end() - 1)
            cond_expr = self._parse_expr_str(cond_str)
            stmts.append(IfStatement(condition=cond_expr, then_body=self._parse_statements_block(body_code)))

        # Semicolon statements
        for part in block_text.split(";"):
            s = self._parse_single_statement(part.strip())
            if s:
                stmts.append(s)

        return stmts

    def _parse_single_statement(self, s: str) -> Optional[IRStatement]:
        if not s or s.startswith("#") or s.startswith("using namespace"):
            return None

        # Return
        if s.startswith("return"):
            val_str = s[6:].strip()
            return ReturnStatement(value=self._parse_expr_str(val_str) if val_str else None)

        # std::cout << a << std::endl;
        if "cout" in s and "<<" in s:
            items = s.split("<<")[1:]
            args = []
            for item in items:
                it = item.strip()
                if it in ("std::endl", "endl", "'\\n'", '"\\n"'):
                    continue
                if it:
                    args.append(self._parse_expr_str(it))
            return ExpressionStatement(expr=FunctionCall(callee="print", args=args))

        # Variable declaration: e.g. int x = 5; or std::vector<int> v = {1, 2, 3};
        decl_match = re.match(r"^([a-zA-Z_]\w*(?:<.*?>)?)\s+([a-zA-Z_]\w*)\s*(?:=\s*(.+))?$", s)
        if decl_match:
            type_str, var_name, val_str = decl_match.groups()
            if var_name not in ("main", "if", "for", "while"):
                v_type = self._map_cpp_type(type_str)
                init_val = self._parse_expr_str(val_str) if val_str else None
                return VariableDeclaration(name=var_name, var_type=v_type, init_val=init_val)

        # Assignment: x = 10;
        assign_match = re.match(r"^([a-zA-Z_]\w*(?:\[.*?\])?)\s*(\+=|-=|\*=|/=|%=|=)\s*(.+)$", s)
        if assign_match:
            target_str, op, val_str = assign_match.groups()
            return Assignment(target=self._parse_expr_str(target_str), op=op, value=self._parse_expr_str(val_str))

        # Function call: foo(a, b);
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

        if s in ("true", "false"):
            return Literal(s == "true", DataType.BOOL)
        if re.match(r"^-?\d+$", s):
            return Literal(int(s), DataType.INT)
        if re.match(r"^-?\d+\.\d+$", s):
            return Literal(float(s), DataType.FLOAT)
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return Literal(s[1:-1], DataType.STRING)

        # Initializer list: {1, 2, 3}
        if s.startswith("{") and s.endswith("}"):
            inner = s[1:-1].strip()
            elems = [self._parse_expr_str(x.strip()) for x in inner.split(",") if x.strip()]
            return ListLiteral(elements=elems)

        # Binary ops
        for op in ["==", "!=", "<=", ">=", "<", ">", "+", "-", "*", "/", "%", "&&", "||"]:
            parts = s.split(f" {op} ")
            if len(parts) == 2:
                return BinaryOp(left=self._parse_expr_str(parts[0]), op=op, right=self._parse_expr_str(parts[1]))

        # Method call: vec.push_back(...)
        m_meth = re.match(r"^([a-zA-Z_]\w*)\.([a-zA-Z_]\w*)\s*\((.*?)\)$", s)
        if m_meth:
            recv = Identifier(m_meth.group(1))
            meth = m_meth.group(2)
            args = [self._parse_expr_str(a.strip()) for a in m_meth.group(3).split(",") if a.strip()]
            return MethodCall(receiver=recv, method=meth, args=args)

        # Function call
        m_call = re.match(r"^([a-zA-Z_]\w*)\s*\((.*?)\)$", s)
        if m_call:
            fn_name = m_call.group(1)
            args = [self._parse_expr_str(a.strip()) for a in m_call.group(2).split(",") if a.strip()]
            return FunctionCall(callee=fn_name, args=args)

        # Indexing: arr[i]
        m_idx = re.match(r"^([a-zA-Z_]\w*)\[(.*?)\]$", s)
        if m_idx:
            return ArrayAccess(array=Identifier(m_idx.group(1)), index=self._parse_expr_str(m_idx.group(2)))

        return Identifier(name=s)
