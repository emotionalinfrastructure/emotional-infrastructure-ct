# tests/test_smoke.py
def test_sanity():
    """Basic smoke test to verify test runner works."""
    assert True


def test_ctp_module_import():
    """Check that main Consent Token Protocol files are importable."""
    import importlib

    modules = [
        "app",
        "issuer",
        "server",
    ]

    for module in modules:
        mod = importlib.import_module(module)
        assert mod is not None, f"Failed to import {module}"
