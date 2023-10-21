import textwrap

from pylsp_tokepy.parser import parse
from pylsp_tokepy.testhelpers import create_token
from pylsp_tokepy.tokens import TokenModifiers, TokenType, tokens_to_lsp


def test_builtin():
    tokens = parse("int(1)")
    expected = [create_token("int", 0, 0, TokenType.BUILTIN, [TokenModifiers.GLOBAL])]
    assert tokens_to_lsp(tokens) == tokens_to_lsp(expected)


def test_unresolved():
    tokens = parse("a in b")
    expected = [
        create_token("a", 0, 0, TokenType.UNRESOLVED, [TokenModifiers.GLOBAL]),
        create_token("In", 0, 2, TokenType.KEYWORD),
        create_token("b", 0, 5, TokenType.UNRESOLVED, [TokenModifiers.GLOBAL]),
    ]
    assert tokens_to_lsp(tokens) == tokens_to_lsp(expected)


def test_class():
    tokens = parse(
        textwrap.dedent(
            """
            class DankNug: ...
            x = DankNug()
            """
        )
    )
    expected = [
        create_token("DankNug", 1, 6, TokenType.CLASS, [TokenModifiers.GLOBAL]),
        create_token("x", 2, 0, TokenType.VARIABLE, [TokenModifiers.GLOBAL]),
        create_token("DankNug", 2, 4, TokenType.CLASS, [TokenModifiers.GLOBAL]),
    ]
    assert tokens_to_lsp(tokens) == tokens_to_lsp(expected)


def test_class_impl():
    tokens = parse(
        textwrap.dedent(
            """
            class DankNug:
                def __init__(self):
                    self.amount = 69

                def toke(self):
                    self.amount = 0
            """
        )
    )
    expected = [
        create_token("DankNug", 1, 6, TokenType.CLASS, [TokenModifiers.GLOBAL]),
        create_token("__init__", 2, 8, TokenType.FUNCTION),
        create_token("self", 2, 17, TokenType.SELF),
        create_token("self", 3, 8, TokenType.SELF),
        create_token("amount", 3, 13, TokenType.ATTRIBUTE),
        create_token("toke", 5, 8, TokenType.FUNCTION),
        create_token("self", 5, 13, TokenType.SELF),
        create_token("self", 6, 8, TokenType.SELF),
        create_token("amount", 6, 13, TokenType.ATTRIBUTE),
    ]
    assert tokens_to_lsp(tokens) == tokens_to_lsp(expected)


def test_unused_parameter():
    tokens = parse("def get_blunted(x): ...")
    expected = [
        create_token("get_blunted", 0, 4, TokenType.FUNCTION, [TokenModifiers.GLOBAL]),
        create_token("x", 0, 16, TokenType.PARAMETER, [TokenModifiers.UNUSED]),
    ]
    assert tokens_to_lsp(tokens) == tokens_to_lsp(expected)


def test_unused_variable():
    tokens = parse(
        textwrap.dedent(
            """
            def get_blunted():
                x = 420
            """
        )
    )
    expected = [
        create_token("get_blunted", 1, 4, TokenType.FUNCTION, [TokenModifiers.GLOBAL]),
        create_token("x", 2, 4, TokenType.VARIABLE, [TokenModifiers.UNUSED]),
    ]
    assert tokens_to_lsp(tokens) == tokens_to_lsp(expected)


def test_used_variable():
    tokens = parse(
        textwrap.dedent(
            """
            def get_blunted():
                x = 420
                x
            """
        )
    )
    expected = [
        create_token("get_blunted", 1, 4, TokenType.FUNCTION, [TokenModifiers.GLOBAL]),
        create_token("x", 2, 4, TokenType.VARIABLE),
        create_token("x", 3, 4, TokenType.VARIABLE),
    ]
    assert tokens_to_lsp(tokens) == tokens_to_lsp(expected)
