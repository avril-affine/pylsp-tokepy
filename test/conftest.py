import shutil
from pathlib import Path
from unittest.mock import Mock

import pytest
from pylsp import uris
from pylsp.config.config import Config
from pylsp.workspace import Workspace, Document


here = Path(__file__).parent
data_dir = here / "data"


@pytest.fixture
def config(workspace):
    """Return a config object."""
    cfg = Config(workspace.root_uri, {}, 0, {})
    cfg._plugin_settings = {
        "plugins": {
            "pylsp_tokepy": True,
        },
    }
    return cfg


@pytest.fixture
def workspace(tmpdir):
    """Return a workspace."""
    ws = Workspace(uris.from_fs_path(str(tmpdir)), Mock())
    ws._config = Config(ws.root_uri, {}, 0, {})
    return ws


@pytest.fixture
def document(workspace):
    ...
    # return create_document(workspace, "simple.py")


def create_document(workspace, name):
    template_path = data_dir / name
    dest_path = Path(workspace.root_path) / name
    shutil.copy(template_path, dest_path)
    document_uri = uris.from_fs_path(str(dest_path))
    return Document(document_uri, workspace)
