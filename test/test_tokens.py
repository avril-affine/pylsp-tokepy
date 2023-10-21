from pylsp_tokepy.testhelpers import create_token
from pylsp_tokepy.tokens import TokenType, tokens_to_lsp


def test_tokens_to_lsp():
    tokens = [
        create_token("foo", 2, 5, TokenType.VARIABLE),
        create_token("dank", 2, 10, TokenType.VARIABLE),
        create_token("nugz420", 5, 2, TokenType.VARIABLE),
    ]
    # (delta_line, delta_char, length, token_type, token_modifier)
    expected = [
        *(2, 5, 3, int(TokenType.VARIABLE), 0),
        *(0, 5, 4, int(TokenType.VARIABLE), 0),
        *(3, 2, 7, int(TokenType.VARIABLE), 0),
    ]
    assert tokens_to_lsp(tokens)["data"] == expected
