from __future__ import annotations

from sortie_deck.runtime import ensure_runtime_dirs, run_doctor, validate_settings
from sortie_deck.settings import Settings


def test_doctor_ok(tmp_path):
    cfg = Settings(data_dir=tmp_path / "data", host="127.0.0.1", port=18787)
    ensure_runtime_dirs(cfg)
    validate_settings(cfg)
    report = run_doctor(cfg)
    assert report.ok
    assert any(c.name == "data_dir" and c.ok for c in report.checks)


def test_production_validate_rejects_default_secret(tmp_path):
    cfg = Settings(
        data_dir=tmp_path / "data",
        env="production",
        token_secret="tdt-dev-secret",
    )
    try:
        validate_settings(cfg)
        raised = False
    except RuntimeError:
        raised = True
    assert raised
