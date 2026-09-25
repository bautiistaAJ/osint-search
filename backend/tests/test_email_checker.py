"""Plain-assert tests for services/email_checker.py — run: python3 tests/test_email_checker.py"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from services.email_checker import (
    evaluate_condition,
    evaluate_match,
    _interpolate,
    _get_path,
    merge_results,
    load_sites,
    canary_fresh,
    _canary_state,
    CANARY_TTL,
)


def test_evaluate_condition_status():
    assert evaluate_condition({"status": [422]}, 422, "x", None) is True
    assert evaluate_condition({"status": [422]}, 200, "x", None) is False


def test_evaluate_condition_body():
    assert evaluate_condition({"body_contains": ["Hello World"]}, 200, "say hello world!", None) is True
    assert evaluate_condition({"body_contains": ["nope"]}, 200, "hello", None) is False
    assert evaluate_condition({"body_not_contains": ["nope"]}, 200, "hello", None) is True
    assert evaluate_condition({"body_not_contains": ["hello"]}, 200, "hello there", None) is False


def test_evaluate_condition_regex():
    assert evaluate_condition({"regex": ["^false$"]}, 200, "false", None) is True
    assert evaluate_condition({"regex": ["^false$"]}, 200, "FALSE", None) is True  # IGNORECASE
    assert evaluate_condition({"regex": ["^false$"]}, 200, "not false", None) is False


def test_evaluate_condition_json():
    j = {"taken": True, "status": 20, "body": {"email_verified": False}, "users": [{"id": 1}]}
    assert evaluate_condition({"json": {"key": "taken", "value": True}}, 200, "", j) is True
    assert evaluate_condition({"json": {"key": "taken", "value": False}}, 200, "", j) is False
    assert evaluate_condition({"json": {"key": "status", "value": 20}}, 200, "", j) is True
    assert evaluate_condition({"json": {"key": "body.email_verified", "value": False}}, 200, "", j) is True
    assert evaluate_condition({"json": {"key": "missing.key", "value": 1}}, 200, "", j) is False
    assert evaluate_condition({"json": {"key": "taken", "value": True}}, 200, "", None) is False


def test_evaluate_condition_json_truthy_falsy():
    j = {"users": [{"id": 1}], "empty": [], "flag": False}
    assert evaluate_condition({"json_truthy": {"key": "users"}}, 200, "", j) is True
    assert evaluate_condition({"json_truthy": {"key": "empty"}}, 200, "", j) is False
    assert evaluate_condition({"json_falsy": {"key": "empty"}}, 200, "", j) is True
    assert evaluate_condition({"json_falsy": {"key": "flag"}}, 200, "", j) is True
    assert evaluate_condition({"json_truthy": {"key": "users"}}, 200, "", None) is False


def test_evaluate_match_verdicts():
    m = {"exists": [{"status": [422]}], "not_exists": [{"status": [200]}]}
    assert evaluate_match(m, 422, "", None) == "exists"
    assert evaluate_match(m, 200, "", None) == "not_exists"
    assert evaluate_match(m, 500, "", None) == "no_match"
    m2 = {"exists": [{"status": [200]}], "not_exists": [{"body_contains": ["ok"]}]}
    assert evaluate_match(m2, 200, "ok", None) == "ambiguous"


def test_evaluate_match_any_of():
    m = {"exists": [{"status": [409]}, {"body_contains": ["taken"]}], "not_exists": []}
    assert evaluate_match(m, 409, "", None) == "exists"
    assert evaluate_match(m, 200, "already TAKEN", None) == "exists"
    assert evaluate_match(m, 200, "free", None) == "no_match"


def test_interpolate():
    ctx = {"email": "a@b.com", "token": "tok123"}
    assert _interpolate("x{email}y", ctx) == "xa@b.comy"
    assert _interpolate({"a": ["{token}"]}, ctx) == {"a": ["tok123"]}
    assert _interpolate("{unknown}", ctx) == "{unknown}"
    assert _interpolate(42, ctx) == 42


def test_get_path():
    d = {"a": {"b": {"c": 5}}}
    assert _get_path(d, "a.b.c") == 5
    assert _get_path(d, "a.x.c") is None
    assert _get_path(d, "top") is None


def test_merge_results():
    native = [
        {"site": "github.com", "url": "https://github.com", "found": True, "method": "native", "confidence": "medium"},
        {"site": "nike.com", "url": "https://nike.com", "found": True, "method": "native", "confidence": "low"},
    ]
    holehe = [
        {"site": "github.com", "url": "https://github.com", "found": True},
        {"site": "spotify.com", "url": "https://spotify.com", "found": True},
    ]
    merged = {r["site"]: r for r in merge_results(native, holehe)}
    assert len(merged) == 3
    assert merged["github.com"]["method"] == "both"
    assert merged["github.com"]["confidence"] == "high"
    assert merged["spotify.com"]["method"] == "holehe"
    assert merged["spotify.com"]["confidence"] == "medium"
    assert merged["nike.com"]["method"] == "native"
    assert merged["nike.com"]["confidence"] == "low"  # canary downgrade survives merge
    assert merge_results([], []) == []
    assert merge_results(None, None) == []


def test_merge_does_not_upgrade_low():
    native = [{"site": "x.com", "url": "https://x.com", "found": True, "method": "native", "confidence": "low"}]
    holehe = [{"site": "x.com", "url": "https://x.com", "found": True}]
    merged = merge_results(native, holehe)
    assert merged[0]["confidence"] == "low"
    assert merged[0]["method"] == "both"


def test_load_sites_registry():
    sites = load_sites()
    assert len(sites) >= 40, f"registry too small: {len(sites)}"
    domains = set()
    for s in sites:
        assert "name" in s and "domain" in s and "match" in s, f"missing keys: {s.get('domain')}"
        assert s["domain"] not in domains, f"duplicate: {s['domain']}"
        domains.add(s["domain"])
        assert "exists" in s["match"] or "not_exists" in s["match"]
        assert isinstance(s.get("enabled", True), bool)


def test_canary_freshness():
    assert _canary_state["ts"] == 0.0
    assert canary_fresh() is False
    _canary_state["ts"] = 1.0
    _canary_state["unreliable"] = {"bad.example"}
    assert canary_fresh() is False  # ts=1.0 is ancient
    import time
    _canary_state["ts"] = time.time()
    assert canary_fresh() is True
    _canary_state["ts"] = time.time() - CANARY_TTL - 10
    assert canary_fresh() is False
    _canary_state["ts"] = 0.0
    _canary_state["unreliable"] = set()


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(list(globals().items())):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except AssertionError as e:
                failures += 1
                print(f"  FAIL  {name}: {e}")
            except Exception as e:
                failures += 1
                print(f"  ERROR {name}: {e}")
    total = len([n for n, f in globals().items() if n.startswith("test_") and callable(f)])
    print(f"\n{total - failures}/{total} passed")
    sys.exit(1 if failures else 0)
