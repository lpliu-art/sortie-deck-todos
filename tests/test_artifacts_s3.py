from __future__ import annotations

import pytest

from sortie_deck.artifacts import ArtifactPathError, LocalArtifactStore
from sortie_deck.artifacts_s3 import S3ArtifactStore, _safe_key, build_artifact_store
from sortie_deck.settings import Settings


def test_local_artifact_store_still_works(tmp_path):
    store = LocalArtifactStore(tmp_path / "artifacts")
    ref = store.write_text("ini_1", "product", "prd.md", "# hi")
    assert store.read_text(ref.path) == "# hi"


def test_s3_safe_key_rejects_traversal():
    with pytest.raises(ArtifactPathError):
        _safe_key("artifacts", "../etc/passwd")
    assert _safe_key("artifacts", "ini/a/b.md") == "artifacts/ini/a/b.md"


def test_build_artifact_store_local(tmp_path):
    cfg = Settings(data_dir=tmp_path / "data", artifact_backend="local")
    store = build_artifact_store(cfg)
    assert isinstance(store, LocalArtifactStore)


def test_build_artifact_store_s3_requires_bucket(tmp_path):
    cfg = Settings(data_dir=tmp_path / "data", artifact_backend="s3", s3_bucket=None)
    with pytest.raises(RuntimeError, match="TDT_S3_BUCKET"):
        build_artifact_store(cfg)


def test_s3_store_requires_boto3(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "boto3":
            raise ImportError("no boto3")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(RuntimeError, match="boto3"):
        S3ArtifactStore(bucket="b")
