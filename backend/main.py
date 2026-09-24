from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import subprocess
import json
import asyncio
from pathlib import Path

from models.database import init_db, add_history, get_history, add_favorite, get_favorites, delete_favorite
from services.osint_services import (
    run_phoneinfoga, run_ghunt, run_sublist3r,
    run_theharvester, run_dns, run_github
)

app = FastAPI(title="OSINT Search ES", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent

def run_cmd(cmd: list) -> str:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""
    except Exception:
        return ""

def run_maigret(username: str) -> list:
    output = run_cmd(["maigret", username])
    results = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("Site") or line.startswith("Maigret"):
            continue
        parts = line.split(" - ")
        if len(parts) >= 2:
            results.append({"site": parts[0].strip(), "url": parts[1].strip(), "found": True})
    return results

def run_whatsmyname(username: str) -> list:
    output = run_cmd(["whatsmyname", username])
    results = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("Username") or line.startswith("WhatsMyName"):
            continue
        parts = line.split(" - ")
        if len(parts) >= 2:
            results.append({"site": parts[0].strip(), "url": parts[1].strip(), "found": True})
    return results

async def query_holehe(email: str) -> list:
    output = run_cmd(["holehe", email])
    results = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("Checking") or line.startswith("Holehe") or line.startswith("Usage"):
            continue
        if "❌" in line:
            continue
        site = line.split("→")[-1].strip() if "→" in line else line.split(" ")[0].strip()
        if site:
            results.append({"site": site, "found": True})
    return results

async def query_hibp(email: str) -> dict:
    import httpx
    try:
        url = f"https://haveibeenpwned.com/api/v2/breachedaccount/{email}"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=30)
            if r.status_code == 200:
                data = r.json()
                return {"breaches": data, "found": True}
            elif r.status_code == 404:
                return {"breaches": [], "found": False}
            else:
                return {"error": f"Status {r.status_code}", "found": False}
    except Exception as e:
        return {"error": str(e), "found": False}

async def query_whois(domain: str) -> dict:
    try:
        import whois as whois_lib
        result = whois_lib.whois(domain)
        if result:
            text = str(result)
            return {"raw": text, "found": bool(text.strip())}
        return {"raw": "", "found": False}
    except Exception as e:
        return {"error": str(e), "found": False}

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/api/search/username")
async def search_username(q: str):
    results_maigret = run_maigret(q)
    results_wn = run_whatsmyname(q)
    combined = []
    seen = set()
    for r in results_maigret:
        if r["url"] not in seen:
            seen.add(r["url"])
            combined.append(r)
    for r in results_wn:
        if r["url"] not in seen:
            seen.add(r["url"])
            combined.append(r)
    await add_history("username", q, json.dumps(combined))
    return {"query": q, "results": combined, "total": len(combined)}

@app.get("/api/search/email")
async def search_email(q: str):
    results = await query_holehe(q)
    breach_data = await query_hibp(q)
    combined = {
        "query": q,
        "accounts": results,
        "breach": breach_data,
        "total": len(results) + len(breach_data.get("breaches", []))
    }
    await add_history("email", q, json.dumps(combined))
    return combined

@app.get("/api/search/phone")
async def search_phone(q: str):
    data = run_phoneinfoga(q)
    await add_history("phone", q, json.dumps(data))
    return {"query": q, "results": data}

@app.get("/api/search/google")
async def search_google(q: str):
    data = run_ghunt(q)
    await add_history("google", q, json.dumps(data))
    return {"query": q, "results": data}

@app.get("/api/search/subdomains")
async def search_subdomains(q: str):
    data = run_sublist3r(q)
    await add_history("subdomains", q, json.dumps(data))
    return {"query": q, "results": data}

@app.get("/api/search/harvest")
async def search_harvest(q: str):
    data = run_theharvester(q)
    await add_history("harvest", q, json.dumps(data))
    return {"query": q, "results": data}

@app.get("/api/search/dns")
async def search_dns(q: str):
    results, success = run_dns(q)
    await add_history("dns", q, json.dumps(results))
    return {"query": q, "results": results, "found": success}

@app.get("/api/search/github")
async def search_github(q: str):
    data = run_github(q)
    await add_history("github", q, json.dumps(data))
    return {"query": q, "results": data}

@app.get("/api/search/domain")
async def search_domain(q: str):
    whois_data = await query_whois(q)
    await add_history("domain", q, json.dumps(whois_data))
    return {"query": q, "results": whois_data}

@app.get("/api/history")
async def history(limit: int = 50):
    return await get_history(limit)

@app.post("/api/favorites")
async def favorite(query_type: str, query_value: str, label: str):
    fav_id = await add_favorite(query_type, query_value, label)
    return {"id": fav_id, "status": "added"}

@app.get("/api/favorites")
async def favorites():
    return await get_favorites()

@app.delete("/api/favorites/{fav_id}")
async def remove_favorite(fav_id: int):
    await delete_favorite(fav_id)
    return {"status": "deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
