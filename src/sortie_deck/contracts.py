from __future__ import annotations

_ENG_BUILD_ARTIFACTS = ["implementation.md", "tasks.json", "diff.patch"]

REQUIRED: dict[str, list[str]] = {
    "product_prd": ["prd.md", "acceptance.json"],
    "design_ui": ["design.md", "screens.json"],
    "qa_cases": ["test_plan.md", "test_cases.md"],
    "eng_implement": list(_ENG_BUILD_ARTIFACTS),
    "eng_ios": list(_ENG_BUILD_ARTIFACTS),
    "eng_android": list(_ENG_BUILD_ARTIFACTS),
    "eng_web": list(_ENG_BUILD_ARTIFACTS),
    "eng_backend": list(_ENG_BUILD_ARTIFACTS),
    "eng_agent": list(_ENG_BUILD_ARTIFACTS),
    "eng_selftest": ["selftest.md"],
    "eng_ios_selftest": ["selftest.md"],
    "eng_android_selftest": ["selftest.md"],
    "eng_web_selftest": ["selftest.md"],
    "eng_backend_selftest": ["selftest.md"],
    "eng_agent_selftest": ["selftest.md"],
    "eng_integrate": ["integrate.md"],
    "qa_handoff": ["handoff.md"],
    "qa_verify": ["test_report.json", "test_cases.md"],
    "deploy_preview": ["deploy_plan.md", "deploy_result.json"],
}


class ContractError(ValueError):
    pass


def validate_stage_artifacts(stage: str, artifacts: dict[str, str]) -> None:
    required = REQUIRED.get(stage, [])
    missing = [name for name in required if name not in artifacts]
    if missing:
        raise ContractError(f"Stage `{stage}` missing artifacts: {', '.join(missing)}")
