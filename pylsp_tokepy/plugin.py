import logging

from pylsp import hookimpl, uris
from pylsp.config.config import Config
from pylsp.workspace import Document, Workspace

from pylsp_tokepy.parser import parse
from pylsp_tokepy.tokens import TokenType, TokenModifiers, tokens_to_lsp


logger = logging.getLogger(__name__)


@hookimpl
def pylsp_capabilities(config: Config) -> dict:
    return {
        "semanticTokensProvider": {
            "legend": {
                "tokenTypes": [t.name for t in TokenType],
                "tokenModifiers": [t.name for t in TokenModifiers if t],
            },
            "full": True,
        },
    }


@hookimpl
def pylsp_semantic_tokens(config: Config, workspace: Workspace, document: Document) -> dict:
    ...
    # with open(document.uri) as f:
    #     tokens = parse(f.read())
    # return tokens_to_lsp(tokens)
