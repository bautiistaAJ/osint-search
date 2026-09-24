# AGENTS.md

## Project Overview

OSINT Search ES - a cyberpunk-styled OSINT tool with a FastAPI backend (Python 3.11+) and Vue 3 + Vite frontend (Node.js 20+). Two independent apps that communicate via REST; frontend proxies /api to localhost:8000.

## Architecture

- Backend (backend/): FastAPI app on port 8000. Entry point is main.py. Uses subprocess to call external CLI tools (maigret, whatsmyname, holehe, phoneinfoga, ghunt, sublist3r, theHarvester). Database is SQLite (osint_search.db in the backend/ dir). Models in models/, services in services/.

- Frontend (frontend/): Vue 3 + Vue Router + Vite on port 5173. vite.config.js proxies /api to http://localhost:8000. Uses vis-network for entity graph visualization.

- Docker Compose: docker-compose up --build runs both services. Backend volume-mounts ./backend:/app; frontend volume-mounts ./frontend:/app with /app/node_modules excluded.

## Running the App

Option 1 - Direct (Kali/recommended):
cd backend && source venv/bin/activate && python3 main.py
cd frontend && npm run dev

Option 2 - Docker:
docker-compose up --build

Option 3 - Install script (Kali):
chmod +x install_kali.sh && ./install_kali.sh

## Key Gotchas

- Run python3 main.py from inside backend/ with venv activated - imports use from models.database import ... and from services.osint_services import ..., which only work when the backend directory is the working directory or on sys.path. Use `python3 -m venv venv` and `source venv/bin/activate` first.
- External tools are installed via pip in the venv - requirements.txt includes maigret, whatsmyname, holehe, phoneinfoga, ghunt, sublist3r, theHarvester, dnspython, python-whois. pip install -r requirements.txt handles all CLI tools.
- Vite proxy: Frontend API calls to /api/... are proxied to http://localhost:8000 only when the dev server is running. In production (Docker), the proxy config does not apply.
- No test, lint, typecheck, or formatter scripts are configured. package.json only has dev, build, preview. No pytest, ruff, or eslint setup exists.
- No CI workflows, pre-commit hooks, or existing instruction files.
- install_kali.sh clones from https://github.com/bautiistaAJ/osint-search.git
- Database file: osint_search.db is created in the backend/ directory at runtime. When using Docker, it persists in the osint_data volume.
- Kali moderno (PEP 668) requires a virtual environment. The venv is created at project root level (venv/) and must be activated before running the backend.

## Frontend Structure

- src/App.vue - layout shell with RouterView, header, **global bottom nav (only place it's defined — views must NOT render their own nav)**
- src/style.css - design tokens (CSS variables) + global styles including `.bottom-nav` (do not duplicate `.bottom-nav a` in scoped styles — it overrides `router-link-active` and makes active link invisible)
- src/main.js - Vue app + router setup (routes: /, /history, /favorites); imports style.css
- src/views/ - Home.vue, History.vue, Favorites.vue (no nav inside; App.vue provides it)
- src/components/ - GraphView.vue, TerminalView.vue, UsernameResults.vue, EmailResults.vue, DnsResults.vue, SubdomainResults.vue, PhoneDossier.vue, GithubDossier.vue, ScanConsole.vue
- src/assets/tokens.css - legacy (superseded by src/style.css)

## Known Gotchas (Frontend)

- vis-network 10.x: no top-level `levels` option (use `layout.hierarchical` instead). `hoverNode` event params use `params.node` (singular), NOT `params.nodes`.
- Vue `<script setup>`: `defineProps`/`defineEmits` are compiler macros — do NOT import them. `ref`/`computed` MUST be imported.
- Backend `/api/history` and `/api/favorites` rows converted with `{k: r[k] for k in r.keys()}` (aiosqlite.Row), wrapped in try/except returning `[]`.

## API Reference

All endpoints are GET except /api/favorites (POST/DELETE):
- /api/search/username?q=, /api/search/email?q=, /api/search/phone?q=, /api/search/google?q=, /api/search/subdomains?q=, /api/search/harvest?q=, /api/search/dns?q=, /api/search/github?q=, /api/search/domain?q=
- /api/history, /api/favorites
- Swagger docs at http://localhost:8000/docs
