from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = REPO_ROOT / "packages" / "templates"

_ALIASES = {
    "default": "default_pipeline.yaml",
    "default-office-iteration": "default_pipeline.yaml",
    "express": "express_pipeline.yaml",
    "standard": "standard_pipeline.yaml",
}


def load_pipeline_template(name: str = "default") -> dict[str, Any]:
    filename = _ALIASES.get(name)
    if not filename:
        filename = f"{name}_pipeline.yaml" if not name.endswith(".yaml") else name
        if not name.endswith("_pipeline.yaml") and not name.endswith(".yaml"):
            filename = f"{name}_pipeline.yaml"
    path = TEMPLATES_DIR / filename
    if not path.exists():
        # bare name.yaml fallback
        alt = TEMPLATES_DIR / f"{name}.yaml"
        path = alt if alt.exists() else TEMPLATES_DIR / "default_pipeline.yaml"
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_persona(role: str) -> str:
    path = TEMPLATES_DIR / "personas" / f"{role}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return f"You are the {role} role agent."
