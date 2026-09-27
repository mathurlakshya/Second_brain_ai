import json


def test_device_token_protection_round_trip():
    import session

    payload = session._protect_secret("launch-test-token")
    assert session._unprotect_secret(payload) == "launch-test-token"


def test_legacy_device_token_migrates(tmp_path, monkeypatch):
    import session

    token_path = tmp_path / "device_token.json"
    token_path.write_text(
        json.dumps({"user_id": 7, "token": "legacy-token"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(session, "TOKEN_FILE", str(token_path))

    loaded = session.load_trusted_device()
    assert loaded == {"user_id": 7, "token": "legacy-token"}

    migrated = json.loads(token_path.read_text(encoding="utf-8"))
    assert "token" not in migrated
    assert migrated["credential"]["format"] in {"dpapi", "plain"}
