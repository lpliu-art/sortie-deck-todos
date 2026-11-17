from sortie_deck.avatars import default_avatar_for_role, list_avatar_presets
from sortie_deck.stage_consult import _heuristic_plan


def test_avatar_presets_cover_core_roles():
    ids = {p["id"] for p in list_avatar_presets()}
    assert "preset:product" in ids
    assert "preset:eng_web" in ids
    assert default_avatar_for_role("qa") == "preset:qa"
    from sortie_deck.avatars import preset_src

    assert preset_src("preset:product") == "/avatars/product.webp"


def test_heuristic_consult_plan_for_eng_web():
    plan = _heuristic_plan(
        "eng_web",
        "eng_web",
        "build a snake game",
        {"product", "qa", "eng_web", "deploy"},
    )
    assert plan["need_consult"] is True
    assert len(plan["questions"]) >= 1
    targets = {q["to"] for q in plan["questions"]}
    assert "eng_web" not in targets
    assert targets <= {"product", "qa", "deploy"}
