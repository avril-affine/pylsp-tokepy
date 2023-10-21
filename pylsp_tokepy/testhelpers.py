from typing import Iterable, Optional

import libcst as cst

from pylsp_tokepy.tokens import SemanticToken, TokenModifiers, TokenType


def create_token(
    name: str,
    line: int,
    column: int,
    token_type: TokenType,
    token_modifiers: Optional[Iterable[TokenModifiers]] = None,
) -> SemanticToken:
    token_modifiers = token_modifiers or [TokenModifiers.NONE]
    return SemanticToken(
        node=cst.Name(name),
        line=line,
        column=column,
        length=len(name),
        token_type=token_type,
        token_modifier=TokenModifiers.from_list(token_modifiers),
    )
