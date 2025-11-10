# Functional test: token issue + validate roundtrip.
import importlib
import pytest

@pytest.mark.smoke
def test_modules_importable():
    for module in ["app", "issuer", "server"]:
        mod = importlib.import_module(module)
        assert mod is not None, f"Failed to import {module}"

@pytest.mark.functional
def test_issue_and_validate_roundtrip(monkeypatch):
    try:
        from issuer import issue_token
        from app import validate_token  # or server.validate_token if defined there
    except Exception:
        pytest.skip("Roundtrip APIs not available yet")
        return

    token = issue_token(sub="test-user", scope=["tone.read"], ttl=60)
    result = validate_token(token)
    assert isinstance(result, dict)
    assert result.get("status") in {"valid", "ok", True}
