from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from sortie_deck.models import new_id, utc_now

DEV_TOKEN_SECRET = "tdt-dev-secret"


class UserRole(str):
    ADMIN = "admin"
    MEMBER = "member"


class User(BaseModel):
    id: str = Field(default_factory=lambda: new_id("usr_"))
    username: str
    display_name: str
    role: Literal["admin", "member"] = "member"
    password_hash: str
    created_at: str = Field(default_factory=lambda: utc_now().isoformat())


class PublicUser(BaseModel):
    id: str
    username: str
    display_name: str
    role: Literal["admin", "member"]


class LoginRequest(BaseModel):
    username: str
    password: str


class CreateUserRequest(BaseModel):
    username: str
    password: str
    display_name: str
    role: Literal["admin", "member"] = "member"


class TokenPayload(BaseModel):
    token: str
    user: PublicUser


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, _hex = stored.split("$", 1)
    except ValueError:
        return False
    return hmac.compare_digest(hash_password(password, salt), stored)


def _sign_token(raw: str, secret: str) -> str:
    sig = hmac.new(secret.encode(), raw.encode(), hashlib.sha256).hexdigest()[:32]
    return f"{raw}.{sig}"


def _unsign_token(token: str, secret: str) -> str | None:
    if "." not in token:
        return None
    raw, sig = token.rsplit(".", 1)
    expected = hmac.new(secret.encode(), raw.encode(), hashlib.sha256).hexdigest()[:32]
    if not hmac.compare_digest(sig, expected):
        return None
    return raw


class AuthStore:
    def __init__(self, path: Path, token_secret: str = DEV_TOKEN_SECRET) -> None:
        secret = (token_secret or "").strip()
        if not secret:
            raise ValueError("token_secret must not be empty")
        self.path = path
        self.token_secret = secret
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            admin = User(
                username="admin",
                display_name="Admin",
                role="admin",
                password_hash=hash_password("admin123"),
            )
            member = User(
                username="operator",
                display_name="Operator",
                role="member",
                password_hash=hash_password("operator123"),
            )
            self._save({"users": [admin.model_dump(), member.model_dump()], "tokens": {}})

    def _load(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8") or "{}")

    def _save(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def list_users(self) -> list[PublicUser]:
        data = self._load()
        return [
            PublicUser(
                id=u["id"],
                username=u["username"],
                display_name=u["display_name"],
                role=u["role"],
            )
            for u in data.get("users", [])
        ]

    def get_by_username(self, username: str) -> User | None:
        data = self._load()
        for raw in data.get("users", []):
            if raw["username"] == username:
                return User.model_validate(raw)
        return None

    def get_by_id(self, user_id: str) -> User | None:
        data = self._load()
        for raw in data.get("users", []):
            if raw["id"] == user_id:
                return User.model_validate(raw)
        return None

    def create_user(self, req: CreateUserRequest) -> PublicUser:
        if self.get_by_username(req.username):
            raise ValueError("username already exists")
        user = User(
            username=req.username,
            display_name=req.display_name,
            role=req.role,
            password_hash=hash_password(req.password),
        )
        data = self._load()
        data.setdefault("users", []).append(user.model_dump())
        self._save(data)
        return PublicUser(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            role=user.role,
        )

    def delete_user(self, user_id: str) -> None:
        data = self._load()
        users = data.get("users", [])
        target = next((u for u in users if u["id"] == user_id), None)
        if not target:
            raise KeyError(user_id)
        if target["role"] == "admin":
            admins = [u for u in users if u["role"] == "admin"]
            if len(admins) <= 1:
                raise ValueError("cannot delete the last admin")
        data["users"] = [u for u in users if u["id"] != user_id]
        self._save(data)

    def login(self, username: str, password: str) -> TokenPayload:
        user = self.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            raise PermissionError("invalid credentials")
        raw = secrets.token_urlsafe(24)
        data = self._load()
        data.setdefault("tokens", {})[raw] = {
            "user_id": user.id,
            "exp": time.time() + 60 * 60 * 24 * 7,
        }
        self._save(data)
        return TokenPayload(
            token=_sign_token(raw, self.token_secret),
            user=PublicUser(
                id=user.id,
                username=user.username,
                display_name=user.display_name,
                role=user.role,
            ),
        )

    def logout(self, token: str) -> None:
        raw = _unsign_token(token, self.token_secret)
        if not raw:
            return
        data = self._load()
        data.get("tokens", {}).pop(raw, None)
        self._save(data)

    def resolve(self, token: str | None) -> PublicUser | None:
        if not token:
            return None
        raw = _unsign_token(token, self.token_secret)
        if not raw:
            return None
        data = self._load()
        meta = data.get("tokens", {}).get(raw)
        if not meta:
            return None
        if meta.get("exp", 0) < time.time():
            data["tokens"].pop(raw, None)
            self._save(data)
            return None
        user = self.get_by_id(meta["user_id"])
        if not user:
            return None
        return PublicUser(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            role=user.role,
        )
