import builtins
import logging
from typing import List

import libcst as cst
from libcst.metadata import (
    ExpressionContext,
    ExpressionContextProvider,
    PositionProvider,
    ScopeProvider,
)

from pylsp_tokepy.tokens import SemanticToken, TokenModifiers, TokenType

logger = logging.getLogger(__name__)

kwlist = [
    "in",
    "is",
    "lambda",
    "nonlocal",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "try",
    "while",
    "with",
    "yield",
]
BUILTIN_NAMES = frozenset([*vars(builtins).keys(), "WindowsError"])
KEYWORD_NAMES = frozenset(["False", "True", "None"])


def parse(code: str) -> List[SemanticToken]:
    module = cst.parse_module(code)
    visitor = TokepyVisitor()
    cst.MetadataWrapper(module).visit(visitor)
    return visitor.tokens


class TokenTypeProvider(cst.BatchableMetadataProvider[TokenType]):
    METADATA_DEPENDENCIES = (ScopeProvider,)

    def visit_And(self, node: cst.And) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_AsName(self, node: cst.AsName) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Assert(self, node: cst.Assert) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Asynchronous(self, node: cst.Assert) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Await(self, node: cst.Await) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Break(self, node: cst.Break) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Continue(self, node: cst.Continue) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_If(self, node: cst.If) -> None:
        # TODO: does this mark the span of elif?
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Else(self, node: cst.Else) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_ExceptHandler(self, node: cst.ExceptHandler) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Finally(self, node: cst.Finally) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_From(self, node: cst.From) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Global(self, node: cst.Global) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Import(self, node: cst.Import) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_In(self, node: cst.In) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Is(self, node: cst.Is) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Lambda(self, node: cst.Lambda) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Nonlocal(self, node: cst.Nonlocal) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_NotIn(self, node: cst.NotIn) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Not(self, node: cst.Not) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Or(self, node: cst.Or) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Pass(self, node: cst.Pass) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Raise(self, node: cst.Raise) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Return(self, node: cst.Return) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Try(self, node: cst.Try) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_While(self, node: cst.While) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_With(self, node: cst.With) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Yield(self, node: cst.Yield) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_For(self, node: cst.For) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_Del(self, node: cst.Del) -> None:
        self.set_metadata(node, TokenType.KEYWORD)

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        self.set_metadata(node.name, TokenType.CLASS)

        scope = self.get_metadata(ScopeProvider, node, None)
        if scope:
            for access in scope.accesses:
                self.set_metadata(access.node, TokenType.CLASS)

    def visit_Param(self, node: cst.Param) -> None:
        name = node.name
        if name.value == "self":
            self.set_metadata(name, TokenType.SELF)
        else:
            self.set_metadata(name, TokenType.PARAMETER)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        self.set_metadata(node.name, TokenType.FUNCTION)
        scope = self.get_metadata(ScopeProvider, node, None)
        if scope:
            for access in scope.accesses:
                self.set_metadata(access.node, TokenType.FUNCTION)

    def visit_Attribute(self, node: cst.Attribute) -> None:
        value = node.value
        if isinstance(value, cst.Name) and value.value == "self":
            self.set_metadata(value, TokenType.SELF)
            token_type = self.get_metadata(type(self), value, None)
            if token_type is not None:
                # TODO: should this also mark methods for simplicity?
                self.set_metadata(node.attr, TokenType.ATTRIBUTE)

    def visit_Name(self, node: cst.Name) -> None:
        token_type = self.get_metadata(type(self), node, None)
        if token_type is not None:
            return

        if node.value in BUILTIN_NAMES:
            # builtin
            self.set_metadata(node, TokenType.BUILTIN)
            return

        scope = self.get_metadata(ScopeProvider, node, None)
        if scope:
            # unresolved
            unresolved = True
            while not isinstance(scope, cst.metadata.GlobalScope):
                if len(scope.assignments[node]) > 0:
                    unresolved = False
                scope = scope.parent
            if unresolved and len(scope.assignments[node]) == 0:
                self.set_metadata(node, TokenType.UNRESOLVED)
                return

        # variable
        # TODO: is this correct?
        self.set_metadata(node, TokenType.VARIABLE)


class TokenModifiersProvider(cst.BatchableMetadataProvider[TokenModifiers]):
    METADATA_DEPENDENCIES = (
        TokenTypeProvider,
        ScopeProvider,
        ExpressionContextProvider,
    )

    def visit_Name(self, node: cst.Name) -> None:
        scope = self.get_metadata(ScopeProvider, node, None)
        token_modifier = TokenModifiers.NONE

        if scope and isinstance(scope, cst.metadata.GlobalScope):
            # global
            token_modifier |= TokenModifiers.GLOBAL
        elif (
            scope
            and not isinstance(scope, cst.metadata.ClassScope)
            and not node.value.startswith("_")
        ):
            # unused
            context = self.get_metadata(ExpressionContextProvider, node, None)
            if context == ExpressionContext.STORE:
                if len(scope.accesses[node]) == 0:
                    token_modifier |= TokenModifiers.UNUSED

        self.set_metadata(node, token_modifier)


class TokepyVisitor(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (
        TokenTypeProvider,
        TokenModifiersProvider,
        PositionProvider,
    )

    def __init__(self) -> None:
        self.tokens: List[SemanticToken] = []

    def on_visit(self, node: cst.CSTNode) -> bool:
        token_type = self.get_metadata(TokenTypeProvider, node, None)
        position = self.get_metadata(PositionProvider, node)
        if isinstance(node, cst.And):
            print(node, token_type, position.start, position.end)

        if token_type is not None:
            code_range = self.get_metadata(PositionProvider, node)
            length = code_range.end.column - code_range.start.column
            token_modifier = self.get_metadata(
                TokenModifiersProvider, node, TokenModifiers.NONE
            )
            self.tokens.append(
                SemanticToken(
                    node=node,
                    # position.line is 1-indexed so convert it back to 0-indexed
                    # which neovim will then convert back to 1-indexed :/
                    line=code_range.start.line - 1,
                    column=code_range.start.column,
                    length=length,
                    token_type=token_type,
                    token_modifier=token_modifier,
                )
            )
        return True
