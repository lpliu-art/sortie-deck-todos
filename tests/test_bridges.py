from __future__ import annotations

import hashlib
import hmac
import time

from sortie_deck.bridges import (
    BridgeMapping,
    BridgeStore,
    feishu_text_from_payload,
    slack_text_from_payload,
    verify_slack_signature,
)


def test_bridge_store_roundtrip(tmp_path):
    store = BridgeStore(tmp_path / "bridges.json")
    m = store.upsert(
        BridgeMapping(provider="slack", channel_id="C1", initiative_id="ini_1", label="main")
    )
    assert store.resolve("slack", "C1").initiative_id == "ini_1"
    assert m.label == "main"


def test_slack_signature_and_payload():
    secret = "sigsec"
    ts = str(int(time.time()))
    body = b"command=%2Fapprove&text=&channel_id=C9&user_name=alice"
    base = f"v0:{ts}:".encode() + body
    sig = "v0=" + hmac.new(secret.encode(), base, hashlib.sha256).hexdigest()
    assert verify_slack_signature(
        signing_secret=secret, timestamp=ts, body=body, signature=sig
    )
    channel, author, text = slack_text_from_payload(
        {"command": "/approve", "text": "", "channel_id": "C9", "user_name": "alice"}
    )
    assert channel == "C9"
    assert author == "alice"
    assert text.startswith("/approve")


def test_feishu_payload():
    payload = {
        "event": {
            "message": {
                "chat_id": "oc_1",
                "content": '{"text":"/start"}',
            },
            "sender": {"sender_id": {"open_id": "ou_x"}},
        }
    }
    channel, author, text = feishu_text_from_payload(payload)
    assert channel == "oc_1"
    assert author == "ou_x"
    assert text == "/start"
