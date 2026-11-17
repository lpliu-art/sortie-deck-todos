from __future__ import annotations

import base64
import io
import zipfile
from pathlib import Path

from sortie_deck.orchestrator import Orchestrator, bind_catalogs
from sortie_deck.settings import Settings
from sortie_deck.toolkit import (
    CreateToolkitRequest,
    ImportToolkitRequest,
    ToolkitStore,
    UpdateToolkitRequest,
    parse_mcp_config,
    parse_skill_markdown,
    parse_skill_package_files,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_parse_mcp_and_skill_import(tmp_path):
    store = ToolkitStore(tmp_path / "toolkit.json")
    mcp_json = """
    {
      "mcpServers": {
        "github": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-github"],
          "env": {"GITHUB_TOKEN": "x"}
        },
        "remote": {"url": "http://127.0.0.1:9000/sse", "transport": "sse"}
      }
    }
    """
    mcps = parse_mcp_config(mcp_json)
    assert len(mcps) == 2
    assert mcps[0].args

    skill = parse_skill_markdown(
        "---\nname: demo-skill\ndescription: hello\n---\n\n# Demo\nDo the thing.\n",
        name_hint="fallback",
    )
    assert skill.name == "demo-skill"
    assert "Do the thing" in skill.body

    pkg = parse_skill_package_files(
        {
            "my-skill/SKILL.md": "---\nname: my-skill\ndescription: pack\n---\nBody\n",
            "my-skill/scripts/run.py": "print('hi')\n",
        }
    )
    assert pkg.name == "my-skill"
    assert pkg.scripts and pkg.scripts[0].path.endswith("run.py")

    imported = store.import_payload(
        ImportToolkitRequest(kind="mcp", content=mcp_json, overwrite=True),
        author_id="u1",
        author_name="Ada",
    )
    assert len(imported) == 2

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(
            "zip-skill/SKILL.md",
            "---\nname: zip-skill\ndescription: from zip\n---\nZip body\n",
        )
        zf.writestr("zip-skill/scripts/hello.sh", "#!/bin/sh\necho hi\n")
    zipped = store.import_payload(
        ImportToolkitRequest(
            kind="skill",
            zip_base64=base64.b64encode(buf.getvalue()).decode(),
            filename="zip-skill.zip",
            overwrite=True,
        ),
        author_id="u1",
        author_name="Ada",
    )
    assert zipped[0].name == "zip-skill"
    assert any(s.path.endswith("hello.sh") for s in zipped[0].scripts)

    # scripts via create/update
    created = store.create(
        CreateToolkitRequest(
            kind="skill",
            name="with-script",
            body="# x",
            scripts=[{"path": "scripts/a.py", "content": "print(1)", "language": "py"}],
        ),
        author_id="u1",
        author_name="Ada",
    )
    assert created.scripts[0].language == "py"


def test_import_packages_examples(tmp_path):
    store = ToolkitStore(tmp_path / "toolkit.json")
    mcp_path = REPO_ROOT / "packages" / "examples" / "demo-mcp.json"
    imported = store.import_payload(
        ImportToolkitRequest(kind="mcp", content=mcp_path.read_text(encoding="utf-8"), overwrite=True),
        author_id="u1",
        author_name="Ada",
    )
    assert imported and imported[0].kind == "mcp"

    skill_md = (REPO_ROOT / "packages" / "examples" / "demo-skill" / "SKILL.md").read_text(encoding="utf-8")
    skill = store.import_payload(
        ImportToolkitRequest(kind="skill", content=skill_md, overwrite=True),
        author_id="u1",
        author_name="Ada",
    )
    assert skill[0].name == "sortie-demo-skill"


def test_disabled_toolkit_omitted_from_persona_brief(tmp_path):
    store = ToolkitStore(tmp_path / "toolkit.json")
    on = store.create(
        CreateToolkitRequest(kind="tool", name="enabled-tool", summary="active", endpoint="curl"),
        author_id="u1",
        author_name="Ada",
    )
    off = store.create(
        CreateToolkitRequest(kind="tool", name="disabled-tool", summary="hidden", endpoint="curl"),
        author_id="u1",
        author_name="Ada",
    )
    store.update(off.id, UpdateToolkitRequest(enabled=False))
    bind_catalogs(toolkit=store)
    orch = Orchestrator(Settings(data_dir=tmp_path / "data", deploy_executor="mock"))
    brief = orch._toolkit_brief([on.id, off.id])
    assert "enabled-tool" in brief
    assert "disabled-tool" not in brief
