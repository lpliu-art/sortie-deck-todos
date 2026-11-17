from __future__ import annotations

from sortie_deck.artifacts import ArtifactStore
from sortie_deck.graph import build_graph_from_template
from sortie_deck.pipeline import (
    catalog_by_id,
    materialize_template,
    normalize_specs,
)
from sortie_deck.plugins.factory import build_default_registry


def test_custom_template_with_hitl_after_wires_interrupt_nodes(tmp_path) -> None:
    catalog = catalog_by_id()
    specs = normalize_specs(
        [
            catalog["intake"],
            {**catalog["product_prd"], "hitl_after": True},
            catalog["eng_implement"],
            catalog["done"],
        ]
    )
    tpl = materialize_template(specs, name="hitl-test")
    assert any(s.get("hitl_after") for s in tpl["stages"])

    registry = build_default_registry(repo_root=tmp_path, worktrees_root=tmp_path / "wt")
    artifacts = ArtifactStore(tmp_path / "artifacts")
    graph = build_graph_from_template(tpl, registry, artifacts)

    assert "product_prd" in graph.nodes
    assert "hitl__product_prd" in graph.nodes
    assert "done" in graph.nodes
