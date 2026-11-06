"""
PolyShift - Universal Intermediate Representation (IR)
Defines semantic AST nodes representing universal programming language constructs.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Any, Union, Dict

class DataType(str, Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOL = "bool"
    VOID = "void"
    CHAR = "char"
    LIST = "list"
    DICT = "dict"
    SET = "set"
    TUPLE = "tuple"
    ANY = "any"
    CUSTOM = "custom"

@dataclass
class IRType:
    kind: DataType = DataType.ANY
    custom_name: Optional[str] = None
    element_type: Optional[IRType] = None
    key_type: Optional[IRType] = None
    val_type: Optional[IRType] = None
    is_mut: bool = False
    is_ref: bool = False

    @classmethod
    def int_type(cls) -> IRType:
        return cls(kind=DataType.INT)

    @classmethod
    def float_type(cls) -> IRType:
        return cls(kind=DataType.FLOAT)

    @classmethod
    def string_type(cls) -> IRType:
        return cls(kind=DataType.STRING)

    @classmethod
    def bool_type(cls) -> IRType:
        return cls(kind=DataType.BOOL)

    @classmethod
    def void_type(cls) -> IRType:
        return cls(kind=DataType.VOID)

    @classmethod
    def any_type(cls) -> IRType:
        return cls(kind=DataType.ANY)

    @classmethod
    def list_type(cls, elem_type: Optional[IRType] = None) -> IRType:
        return cls(kind=DataType.LIST, element_type=elem_type or cls.any_type())

    @classmethod
    def dict_type(cls, key_type: Optional[IRType] = None, val_type: Optional[IRType] = None) -> IRType:
        return cls(kind=DataType.DICT, key_type=key_type or cls.string_type(), val_type=val_type or cls.any_type())

    @classmethod
    def custom(cls, name: str) -> IRType:
        return cls(kind=DataType.CUSTOM, custom_name=name)

# --- Expressions ---

@dataclass
class IRExpression:
    """Base class for all expressions."""
    inferred_type: Optional[IRType] = None

@dataclass
class Literal(IRExpression):
    value: Any = None
    raw_type: DataType = DataType.ANY

@dataclass
class Identifier(IRExpression):
    name: str = ""

@dataclass
class BinaryOp(IRExpression):
    left: IRExpression = field(default_factory=lambda: Identifier())
    op: str = "+"  # +, -, *, /, %, ==, !=, <, <=, >, >=, &&, ||, and, or
    right: IRExpression = field(default_factory=lambda: Identifier())

@dataclass
class UnaryOp(IRExpression):
    op: str = "-"  # -, !, not
    operand: IRExpression = field(default_factory=lambda: Identifier())

@dataclass
class FunctionCall(IRExpression):
    callee: str = ""
    args: List[IRExpression] = field(default_factory=list)

@dataclass
class MethodCall(IRExpression):
    receiver: IRExpression = field(default_factory=lambda: Identifier())
    method: str = ""
    args: List[IRExpression] = field(default_factory=list)

@dataclass
class ArrayAccess(IRExpression):
    array: IRExpression = field(default_factory=lambda: Identifier())
    index: IRExpression = field(default_factory=lambda: Literal(0, DataType.INT))

@dataclass
class MemberAccess(IRExpression):
    receiver: IRExpression = field(default_factory=lambda: Identifier())
    member: str = ""

@dataclass
class ListLiteral(IRExpression):
    elements: List[IRExpression] = field(default_factory=list)

@dataclass
class DictEntry:
    key: IRExpression
    value: IRExpression

@dataclass
class DictLiteral(IRExpression):
    entries: List[DictEntry] = field(default_factory=list)

@dataclass
class TernaryExpr(IRExpression):
    condition: IRExpression = field(default_factory=lambda: Identifier())
    true_expr: IRExpression = field(default_factory=lambda: Identifier())
    false_expr: IRExpression = field(default_factory=lambda: Identifier())

# --- Statements ---

@dataclass
class IRStatement:
    """Base class for statements."""
    pass

@dataclass
class ExpressionStatement(IRStatement):
    expr: IRExpression

@dataclass
class VariableDeclaration(IRStatement):
    name: str
    var_type: IRType = field(default_factory=IRType.any_type)
    init_val: Optional[IRExpression] = None
    is_const: bool = False
    is_mut: bool = True

@dataclass
class Assignment(IRStatement):
    target: IRExpression
    op: str = "="  # =, +=, -=, *=, /=
    value: IRExpression = field(default_factory=lambda: Literal(0, DataType.INT))

@dataclass
class ReturnStatement(IRStatement):
    value: Optional[IRExpression] = None

@dataclass
class IfStatement(IRStatement):
    condition: IRExpression
    then_body: List[IRStatement] = field(default_factory=list)
    elif_branches: List[tuple[IRExpression, List[IRStatement]]] = field(default_factory=list)
    else_body: List[IRStatement] = field(default_factory=list)

@dataclass
class WhileLoop(IRStatement):
    condition: IRExpression
    body: List[IRStatement] = field(default_factory=list)

@dataclass
class ForLoop(IRStatement):
    iterator_var: str
    is_range: bool = True
    range_start: Optional[IRExpression] = None
    range_end: Optional[IRExpression] = None
    range_step: Optional[IRExpression] = None
    iterable: Optional[IRExpression] = None
    body: List[IRStatement] = field(default_factory=list)

@dataclass
class TryCatch(IRStatement):
    try_body: List[IRStatement] = field(default_factory=list)
    error_var: str = "err"
    catch_body: List[IRStatement] = field(default_factory=list)
    finally_body: List[IRStatement] = field(default_factory=list)

@dataclass
class BreakStatement(IRStatement):
    pass

@dataclass
class ContinueStatement(IRStatement):
    pass

@dataclass
class Comment(IRStatement):
    text: str = ""

# --- Higher level definitions ---

@dataclass
class Parameter:
    name: str
    param_type: IRType = field(default_factory=IRType.any_type)
    default_val: Optional[IRExpression] = None

@dataclass
class FunctionDef:
    name: str
    params: List[Parameter] = field(default_factory=list)
    return_type: IRType = field(default_factory=IRType.void_type)
    body: List[IRStatement] = field(default_factory=list)
    docstring: Optional[str] = None
    is_async: bool = False
    is_method: bool = False
    is_static: bool = False

@dataclass
class ClassDef:
    name: str
    base_classes: List[str] = field(default_factory=list)
    fields: List[VariableDeclaration] = field(default_factory=list)
    methods: List[FunctionDef] = field(default_factory=list)
    docstring: Optional[str] = None

@dataclass
class ImportItem:
    module: str
    imported_names: List[str] = field(default_factory=list)
    alias: Optional[str] = None

@dataclass
class Program:
    imports: List[ImportItem] = field(default_factory=list)
    classes: List[ClassDef] = field(default_factory=list)
    functions: List[FunctionDef] = field(default_factory=list)
    statements: List[IRStatement] = field(default_factory=list)
    raw_source: str = ""
    source_language: str = "python"
