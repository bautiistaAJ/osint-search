import asyncio
import hashlib
import json
import re
import secrets
import time
from pathlib import Path

import httpx

SITES_FILE = Path(__file__).with_name("email_sites.json")

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
SITE_TIMEOUT = 8.0
TOTAL_BUDGET = 60.0
CONCURRENCY = 15
CANARY_TTL = 24 * 3600

_canary_state = {"ts": 0.0, "unreliable": set()}
_canary_lock = asyncio.Lock()


def load_sites() -> list:
    try:
        return json.loads(SITES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def canary_fresh() -> bool:
    return _canary_state["ts"] > 0 and (time.time() - _canary_state["ts"]) < CANARY_TTL


def _interpolate(value, ctx):
    if isinstance(value, str):
        for k, v in ctx.items():
            value = value.replace("{" + k + "}", v)
        return value
    if isinstance(value, dict):
        return {k: _interpolate(v, ctx) for k, v in value.items()}
    if isinstance(value, list):
        return [_interpolate(v, ctx) for v in value]
    return value


def _get_path(data, path):
    cur = data
    for part in str(path).split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def evaluate_condition(cond, status, text, json_data) -> bool:
    if "status" in cond:
        return status in cond["status"]
    if "body_contains" in cond:
        low = text.lower()
        return any(str(s).lower() in low for s in cond["body_contains"])
    if "body_not_contains" in cond:
        low = text.lower()
        return not any(str(s).lower() in low for s in cond["body_not_contains"])
    if "regex" in cond:
        return any(re.search(p, text, re.IGNORECASE | re.DOTALL) for p in cond["regex"])
    if "json" in cond:
        if json_data is None:
            return False
        spec = cond["json"]
        return _get_path(json_data, spec["key"]) == spec.get("value")
    if "json_truthy" in cond:
        if json_data is None:
            return False
        return bool(_get_path(json_data, cond["json_truthy"]["key"]))
    if "json_falsy" in cond:
        if json_data is None:
            return False
        return not bool(_get_path(json_data, cond["json_falsy"]["key"]))
    return False


def evaluate_match(match, status, text, json_data) -> str:
    exists = any(evaluate_condition(c, status, text, json_data) for c in match.get("exists", []))
    not_exists = any(evaluate_condition(c, status, text, json_data) for c in match.get("not_exists", []))
    if exists and not_exists:
        return "ambiguous"
    if exists:
        return "exists"
    if not_exists:
        return "not_exists"
    return "no_match"


def _build_steps(site) -> list:
    if "steps" in site:
        steps = site["steps"]
    else:
        steps = [{k: site[k] for k in ("method", "url", "headers", "params", "json", "form", "capture") if k in site}]
    top_headers = site.get("headers", {})
    merged = []
    for st in steps:
        st = dict(st)
        st["headers"] = {**top_headers, **st.get("headers", {})}
        merged.append(st)
    return merged


async def _request(step, ctx, client) -> httpx.Response:
    method = step.get("method", "GET").upper()
    url = _interpolate(step["url"], ctx)
    kwargs = {"headers": step.get("headers") or None}
    if "params" in step:
        kwargs["params"] = _interpolate(step["params"], ctx)
    if "json" in step:
        kwargs["json"] = _interpolate(step["json"], ctx)
    if "form" in step:
        kwargs["data"] = _interpolate(step["form"], ctx)
    return await client.request(method, url, **kwargs)


async def check_site(site, email, client) -> str:
    """Returns 'exists' | 'not_exists' | None (error/no_match/ambiguous skipped)."""
    ctx = {
        "email": email,
        "md5_email": hashlib.md5(email.strip().lower().encode()).hexdigest(),
    }
    resp = None
    try:
        for step in _build_steps(site):
            resp = await _request(step, ctx, client)
            for cap in step.get("capture", []):
                var = cap.get("var", "cap")
                if "cookie" in cap:
                    val = resp.cookies.get(cap["cookie"])
                else:
                    m = re.search(cap["regex"], resp.text, re.DOTALL)
                    if not m:
                        continue
                    group = cap.get("group", 1)
                    try:
                        val = m.group(group) if m.groups() else m.group(0)
                    except IndexError:
                        val = m.group(0)
                if val:
                    ctx[var] = val
    except Exception:
        return None
    if resp is None:
        return None
    try:
        json_data = resp.json()
    except Exception:
        json_data = None
    verdict = evaluate_match(site["match"], resp.status_code, resp.text, json_data)
    if verdict in ("exists", "not_exists"):
        return verdict
    return None


async def _run_canary(sites, client, sem) -> set:
    canary_email = f"canary-{secrets.token_hex(12)}@gmail.com"

    async def run(site):
        async with sem:
            return await check_site(site, canary_email, client)

    verdicts = await asyncio.gather(*[run(s) for s in sites])
    unreliable = {s["domain"] for s, v in zip(sites, verdicts) if v == "exists"}
    _canary_state["ts"] = time.time()
    _canary_state["unreliable"] = unreliable
    return unreliable


async def _cached_or_run_canary(sites, client, sem) -> set:
    if canary_fresh():
        return set(_canary_state["unreliable"])
    async with _canary_lock:
        if canary_fresh():
            return set(_canary_state["unreliable"])
        return await _run_canary(sites, client, sem)


async def check_email_native(email: str) -> list:
    sites = [s for s in load_sites() if s.get("enabled", True)]
    if not sites:
        return []
    try:
        return await asyncio.wait_for(_native_inner(sites, email), TOTAL_BUDGET)
    except (asyncio.TimeoutError, Exception):
        return []


async def _native_inner(sites, email) -> list:
    sem = asyncio.Semaphore(CONCURRENCY)
    headers = {"User-Agent": DEFAULT_UA, "Accept": "*/*"}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=SITE_TIMEOUT) as client:
        async def run(site):
            async with sem:
                return await check_site(site, email, client)

        unreliable, verdicts = await asyncio.gather(
            _cached_or_run_canary(sites, client, sem),
            asyncio.gather(*[run(s) for s in sites]),
        )

    results = []
    for site, verdict in zip(sites, verdicts):
        if verdict != "exists":
            continue
        domain = site["domain"]
        results.append({
            "site": domain,
            "url": f"https://{domain}",
            "found": True,
            "method": "native",
            "confidence": "low" if domain in unreliable else "medium",
        })
    return results


def merge_results(native: list, holehe: list) -> list:
    merged = {}
    for r in native or []:
        if r.get("found") and r.get("site"):
            merged[r["site"]] = dict(r)
    for h in holehe or []:
        domain = h.get("site")
        if not domain:
            continue
        if domain in merged:
            merged[domain]["method"] = "both"
            if merged[domain].get("confidence") == "medium":
                merged[domain]["confidence"] = "high"
        else:
            merged[domain] = {
                "site": domain,
                "url": h.get("url") or f"https://{domain}",
                "found": True,
                "method": "holehe",
                "confidence": "medium",
            }
    return list(merged.values())
