import logging
import operator
from enum import IntEnum, IntFlag, auto
from functools import reduce
from types import DynamicClassAttribute
from typing import Optional, List

import libcst as cst

logger = logging.getLogger(__name__)


class TokenType(IntEnum):
    BUILTIN = 0
    KEYWORD = auto()
    CLASS = auto()
    FUNCTION = auto()
    SELF = auto()
    PARAMETER = auto()
    ATTRIBUTE = auto()
    VARIABLE = auto()
    UNRESOLVED = auto()
    # TODO: keyword? for,in,etc. are in separate nodes so can't use keyword.iskeyword

    @DynamicClassAttribute
    def name(self):
        """Override enum's name"""
        if isinstance(self._name_, str):
            return self._name_.lower()
        return self._name_


class TokenModifiers(IntFlag):
    NONE = 0
    GLOBAL = auto()
    UNUSED = auto()

    @DynamicClassAttribute
    def name(self):
        """Override enum's name"""
        if isinstance(self._name_, str):
            return self._name_.lower()
        return self._name_

    @classmethod
    def from_list(cls, token_modifiers: List["TokenModifiers"]) -> "TokenModifiers":
        return reduce(operator.or_, token_modifiers, TokenModifiers.NONE)


class SemanticToken:
    def __init__(
        self,
        node: cst.CSTNode,
        line: int,
        column: int,
        length: int,
        token_type: TokenType,
        token_modifier: TokenModifiers = TokenModifiers.NONE,
    ) -> None:
        self._node = node
        self.name = node.value if isinstance(node, cst.Name) else type(node).__name__
        self.line = line
        self.column = column
        self.length = length
        self.token_type = token_type
        self.token_modifier = token_modifier

    def __repr__(self) -> str:
        name = self.name
        line = self.line
        column = self.column
        token_type = self.token_type
        token_modifier = self.token_modifier
        return f"SemanticToken({name=}, {line=}, {column=}, {token_type=}, {token_modifier=})"

    def __lt__(self, other: "SemanticToken") -> bool:
        return (self.line, self.column) < (other.line, other.column)


def tokens_to_lsp(tokens: List[SemanticToken]) -> Optional[dict]:
    """
    Convert to list of deltas according to LSP spec.
    """
    prev = None
    res = []
    for token in sorted(tokens):
        delta_line = token.line
        delta_char = token.column
        if prev:
            delta_line -= prev.line
            if delta_line == 0:
                delta_char -= prev.column
        res.extend(
            [
                delta_line,
                delta_char,
                token.length,
                int(token.token_type),
                int(token.token_modifier),
            ]
        )
        prev = token
    if res:
        return {"data": res}
    return None
