from __future__ import annotations

from sortie_deck.contracts import REQUIRED, validate_stage_artifacts
from sortie_deck.pipeline import stage_catalog


def _mock_files(names: list[str]) -> dict[str, str]:
    return {name: "ok" for name in names}


def test_required_stages_validate_with_mock_artifacts() -> None:
    for stage, files in REQUIRED.items():
        validate_stage_artifacts(stage, _mock_files(files))


def test_catalog_stages_with_output_contract_validate() -> None:
    for spec in stage_catalog():
        sid = spec["id"]
        required = list(REQUIRED.get(sid) or spec.get("output_contract") or [])
        if not required:
            continue
        validate_stage_artifacts(sid, _mock_files(required))
