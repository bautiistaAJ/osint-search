import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

def run_cmd(cmd: list, timeout: int = 120) -> str:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""
    except Exception:
        return ""

def run_phoneinfoga(phone: str) -> dict:
    output = run_cmd(["phoneinfoga", "-n", phone])
    if not output:
        output = run_cmd(["phoneinfoga", phone])
    return {"raw": output, "found": bool(output.strip())}

def run_ghunt(email: str) -> dict:
    output = run_cmd(["ghunt", "email", email])
    if not output:
        output = run_cmd(["ghunt", email])
    return {"raw": output, "found": bool(output.strip())}

def run_sublist3r(domain: str) -> dict:
    output = run_cmd(["sublist3r", "-d", domain])
    return {"raw": output, "found": bool(output.strip())}

def run_theharvester(domain: str) -> dict:
    output = run_cmd(["theHarvester", "-d", domain, "-b", "all"])
    if not output:
        output = run_cmd(["theharvester", "-d", domain, "-b", "all"])
    if not output:
        output = run_cmd(["theHarvester", "-d", domain])
    return {"raw": output, "found": bool(output.strip())}

def run_dns(domain: str) -> dict:
    try:
        import dns.resolver
        results = {}
        record_types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME', 'CAA', 'SOA']
        for rt in record_types:
            try:
                answers = dns.resolver.resolve(domain, rt)
                results[rt] = [str(a) for a in answers]
            except Exception:
                results[rt] = []
        return results, True
    except Exception as e:
        return {"error": str(e)}, False

async def run_github(username: str) -> dict:
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://api.github.com/users/{username}"
            r = await client.get(url, timeout=30)
            if r.status_code == 200:
                data = r.json()
                return {
                    "login": data.get("login"),
                    "name": data.get("name"),
                    "bio": data.get("bio"),
                    "public_repos": data.get("public_repos"),
                    "followers": data.get("followers"),
                    "following": data.get("following"),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "html_url": data.get("html_url"),
                    "company": data.get("company"),
                    "location": data.get("location"),
                    "email": data.get("email"),
                    "twitter_username": data.get("twitter_username"),
                    "found": True
                }
            return {"found": False, "status": r.status_code}
    except Exception as e:
        return {"error": str(e), "found": False}
