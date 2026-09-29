from __future__ import annotations

from pathlib import Path

import pytest

from sortie_deck.org_policy import (
    OrgPolicy,
    assert_import_allowed,
    enforce_track,
    filter_toolkit_ids,
    load_org_policy,
)


def test_load_default_policy():
    path = Path("packages/policies/default.json")
    policy = load_org_policy(path)
    assert policy is not None
    assert "express" in policy.allowed_tracks


def test_enforce_track_and_filter():
    policy = OrgPolicy(allowed_tracks=["express"], allowed_toolkit_ids=["tk_a"])
    enforce_track(policy, "express")
    with pytest.raises(PermissionError):
        enforce_track(policy, "default")
    assert filter_toolkit_ids(policy, ["tk_a", "tk_b"]) == ["tk_a"]


def test_deny_import():
    policy = OrgPolicy(deny_toolkit_import=True)
    with pytest.raises(PermissionError):
        assert_import_allowed(policy)
