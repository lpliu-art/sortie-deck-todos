from __future__ import annotations

from pathlib import Path

import pytest

from sortie_deck.pipeline import TRACK_FILES, diff_specs, plan_pipeline
from sortie_deck.templates import load_pipeline_template


@pytest.mark.parametrize(
    ("title", "brief", "hint", "expected_track"),
    [
        ("typo", "一行代码改文案 hotfix", None, "express"),
        ("Feature", "账号中心改版，正常需求", "standard", "standard"),
        ("Platform", "支付权限体系重构", None, "standard"),
        ("Bug", "修复登录页样式与交互细节，涉及账号模块", None, "standard"),
        ("Default", "做一个通知中心模块", "default", "default"),
    ],
)
def test_plan_pipeline_track_hint_golden(
    title: str, brief: str, hint: str | None, expected_track: str
) -> None:
    proposal = plan_pipeline(title=title, brief=brief, hint_track=hint)
    assert proposal["track_hint"] == expected_track
    ids = [s["id"] for s in proposal["stages"]]
    assert ids[0] == "intake"
    assert ids[-1] == "done"


@pytest.mark.parametrize("track", ("express", "standard", "default"))
def test_pipeline_yaml_templates_load(track: str) -> None:
    filename = TRACK_FILES[track]
    path = Path(__file__).resolve().parents[1] / "packages" / "templates" / filename
    assert path.is_file(), f"missing {path}"
    tpl = load_pipeline_template(track)
    assert tpl.get("stages")
    assert tpl["stages"][0]["name"] == "intake"


def test_diff_specs_added_removed_changed() -> None:
    base = plan_pipeline(title="t", brief="一行改文案")["stages"]
    trimmed = [s for s in base if s["id"] not in {"qa_verify", "deploy_preview"}]
    d = diff_specs(base, trimmed)
    assert "qa_verify" in d["removed"]
    assert "deploy_preview" in d["removed"]
    assert d["added"] == []

    tweaked = [dict(s) for s in base]
    for s in tweaked:
        if s["id"] == "qa_verify":
            s["hitl_after"] = not bool(s.get("hitl_after"))
    d2 = diff_specs(base, tweaked)
    assert "qa_verify" in d2["changed"]
    assert d2["added"] == []
    assert d2["removed"] == []
