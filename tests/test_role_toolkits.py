from __future__ import annotations

import asyncio

from sortie_deck.agents import AgentCatalog, CreateAgentRequest
from sortie_deck.models import CreateInitiativeRequest
from sortie_deck.orchestrator import Orchestrator, bind_catalogs
from sortie_deck.settings import Settings
from sortie_deck.toolkit import CreateToolkitRequest, ToolkitStore


def test_mission_role_toolkits_override_agent_defaults(tmp_path):
    cfg = Settings(data_dir=tmp_path / "data", deploy_executor="mock")
    toolkit = ToolkitStore(tmp_path / "toolkit.json")
    t1 = toolkit.create(
        CreateToolkitRequest(kind="tool", name="gh-cli", summary="GitHub CLI", endpoint="gh"),
        author_id="u1",
        author_name="Ada",
    )
    t2 = toolkit.create(
        CreateToolkitRequest(kind="skill", name="review-skill", summary="Review", body="# Review"),
        author_id="u1",
        author_name="Ada",
    )
    catalog = AgentCatalog(tmp_path / "agents.json")
    agent = catalog.create(
        CreateAgentRequest(
            title="Default Eng",
            slot="eng",
            summary="ships code",
            persona="You are eng.",
            toolkit_ids=[t1.id],
        ),
        author_id="u1",
        author_name="Ada",
    )
    bind_catalogs(agents=catalog, toolkit=toolkit)
    orch = Orchestrator(cfg)

    async def _run():
        await orch.startup()
        try:
            # Inherit agent default when role_toolkits omitted
            ini = await orch.create_initiative(
                CreateInitiativeRequest(
                    title="Inherit tools",
                    brief="Use default eng toolkit",
                    role_agents={"eng": agent.id},
                    creator_name="Ada",
                )
            )
            eng = next(r for r in ini.roles if r.role.value == "eng")
            assert eng.toolkit_ids == [t1.id]
            assert "Toolkit loadout" in (ini.meta.get("toolkit_brief") or "")

            # Explicit mission override wins
            ini2 = await orch.create_initiative(
                CreateInitiativeRequest(
                    title="Override tools",
                    brief="Mission picks skill instead",
                    role_agents={"eng": agent.id},
                    role_toolkits={"eng": [t2.id]},
                    creator_name="Ada",
                )
            )
            eng2 = next(r for r in ini2.roles if r.role.value == "eng")
            assert eng2.toolkit_ids == [t2.id]
            loadout = orch._pipeline_loadout(ini2)
            assert loadout["role_toolkits"]["eng"] == [t2.id]
            assert "role:eng" in loadout["toolkit_briefs"]
            assert orch.resolve_stage_toolkits(ini2, "eng_implement", "eng") == [t2.id]
        finally:
            await orch.shutdown()

    asyncio.run(_run())
