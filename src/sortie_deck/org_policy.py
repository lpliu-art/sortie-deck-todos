from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class OrgPolicy(BaseModel):
    """Single-tenant org guardrails for tracks and toolkits."""

    default_track: str | None = None
    allowed_tracks: list[str] = Field(default_factory=list)
    allowed_toolkit_ids: list[str] = Field(default_factory=list)
    deny_toolkit_import: bool = False
    notes: str = ""


def load_org_policy(path: Path | None) -> OrgPolicy | None:
    if path is None:
        return None
    if not path.exists():
        return None
    raw = json.loads(path.read_text(encoding="utf-8") or "{}")
    return OrgPolicy.model_validate(raw)


def enforce_track(policy: OrgPolicy | None, track: str | None) -> str | None:
    if not policy or not track:
        return track
    allowed = policy.allowed_tracks
    if allowed and track not in allowed:
        raise PermissionError(f"track `{track}` not allowed by org policy")
    return track


def filter_toolkit_ids(policy: OrgPolicy | None, ids: list[str]) -> list[str]:
    if not policy or not policy.allowed_toolkit_ids:
        return list(ids)
    allow = set(policy.allowed_toolkit_ids)
    return [i for i in ids if i in allow]


def assert_toolkit_allowed(policy: OrgPolicy | None, toolkit_id: str) -> None:
    if not policy or not policy.allowed_toolkit_ids:
        return
    if toolkit_id not in policy.allowed_toolkit_ids:
        raise PermissionError(f"toolkit `{toolkit_id}` not allowed by org policy")


def assert_import_allowed(policy: OrgPolicy | None) -> None:
    if policy and policy.deny_toolkit_import:
        raise PermissionError("toolkit import denied by org policy")


def apply_defaults(policy: OrgPolicy | None, meta: dict[str, Any]) -> dict[str, Any]:
    if not policy:
        return meta
    out = dict(meta)
    if policy.default_track and not out.get("pipeline_track"):
        out["pipeline_track"] = policy.default_track
    return out
