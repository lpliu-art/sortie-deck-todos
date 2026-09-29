from __future__ import annotations

import pytest

from sortie_deck.auth import (
    AuthStore,
    CreateUserRequest,
    hash_password,
    verify_password,
)
from sortie_deck.settings import Settings


def test_password_hash_roundtrip():
    stored = hash_password("s3cret")
    assert verify_password("s3cret", stored)
    assert not verify_password("wrong", stored)


def test_auth_login_and_roles(tmp_path):
    store = AuthStore(tmp_path / "users.json", token_secret="test-secret")
    admin = store.login("admin", "admin123")
    assert admin.user.role == "admin"
    assert "." in admin.token
    member = store.login("operator", "operator123")
    assert member.user.role == "member"
    assert store.resolve(admin.token).username == "admin"
    created = store.create_user(
        CreateUserRequest(username="bob", password="bob123", display_name="Bob", role="member")
    )
    assert created.username == "bob"
    assert any(u.username == "bob" for u in store.list_users())


def test_bad_login_and_forged_token(tmp_path):
    store = AuthStore(tmp_path / "users.json", token_secret="test-secret")
    with pytest.raises(PermissionError):
        store.login("admin", "nope")
    assert store.resolve("not-a-token") is None
    assert store.resolve("raw.deadbeef") is None
    good = store.login("admin", "admin123")
    raw, _sig = good.token.rsplit(".", 1)
    assert store.resolve(f"{raw}.{'0' * 32}") is None
    forged = AuthStore(tmp_path / "users.json", token_secret="other-secret")
    assert forged.resolve(good.token) is None


def test_admin_gate_via_api(tmp_path):
    store = AuthStore(tmp_path / "users.json", token_secret="api-test-secret")
    member = store.login("operator", "operator123")
    admin = store.login("admin", "admin123")
    assert store.resolve(member.token).role == "member"
    assert store.resolve(admin.token).role == "admin"


def test_production_refuses_default_secret():
    s = Settings(env="production", token_secret="tdt-dev-secret")
    with pytest.raises(RuntimeError, match="TDT_TOKEN_SECRET"):
        s.resolved_token_secret()
    ok = Settings(env="production", token_secret="prod-strong-secret")
    assert ok.resolved_token_secret() == "prod-strong-secret"


def test_empty_token_secret_rejected(tmp_path):
    with pytest.raises(ValueError):
        AuthStore(tmp_path / "users.json", token_secret="  ")
