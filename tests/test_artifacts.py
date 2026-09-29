from __future__ import annotations

import pytest
from fastapi import HTTPException

from sortie_deck.artifacts import ArtifactPathError, ArtifactStore


def test_path_traversal_rejected(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")
    store.write_text("ini_x", "product", "brief.md", "hello")
    with pytest.raises(ArtifactPathError):
        store.read_text("../secrets.txt")
    with pytest.raises(ArtifactPathError):
        store.read_text("ini_x/../../etc/passwd")
    with pytest.raises(ArtifactPathError):
        store.resolve_safe("/etc/passwd")
    assert store.read_text("ini_x/product/brief.md") == "hello"


def test_download_requires_auth():
    from sortie_deck.api.app import require_user

    with pytest.raises(HTTPException) as ei:
        require_user(None)
    assert ei.value.status_code == 401

    with pytest.raises(HTTPException) as ei2:
        require_user("Bearer not-a-valid-token")
    assert ei2.value.status_code == 401
