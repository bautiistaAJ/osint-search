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

- vis-network 10.x: no top-level `levels` option (use `layout.hierarchical` instead). `hoverNode` event params use `params.node` (singular), NOT `params.nodes`. Never open URLs on `hoverNode` — only on `click`.
- vis-network node color keys: only `background`/`border`/`highlight`/`hover` are read — `color: {...}` and `highlightBorder` are IGNORED. Use `color: { background, highlight: { background, border }, border }`. For icons use `shape:'icon'` + `icon: { face: "'FontAwesome'", code }` (FontAwesome 4.7 CSS linked in index.html).
- vis-network `Popup.setText` uses `innerText` for strings — HTML tooltips must be HTMLElement. Use `makeTitle(html)` helper (`div.innerHTML = html`) in GraphView.vue.
- Graph incremental render: initial `TOP_K = 24` nodes, `loadMore()` appends next batch via `addRange(from, to)` on the same DataSet (no full rebuild). Never rebuild the whole graph on legend/find actions — use `network.selectNodes` + `fit`.
- Graph node URL open: click → detail panel (`selected` ref) with explicit ABRIR/COPIAR buttons; never `window.open` from hover or auto-click.
- `submittedQuery` ref snapshot in Home.vue: bound as `:queryValue` so per-keystroke edits don't trigger GraphView rebuild. Graph rebuilds only on `props.results` watch.
- Vue `<script setup>`: `defineProps`/`defineEmits` are compiler macros — do NOT import them. `ref`/`computed` MUST be imported.
- Backend `/api/history` and `/api/favorites` rows converted with `{k: r[k] for k in r.keys()}` (aiosqliteRow), wrapped in try/except returning `[]`.
- Graph render rule: `showGraph` is ONLY set for GRAPH_TYPES (`username`, `email`) with array results — dict-shaped types (dns, github, phone, google, domain, subdomains, harvest) must render their own components. Backend dicts get wrapped into 1-element arrays in `processResponse`, so never gate the graph on `results.length > 0` alone.
- Home.vue results chain: one wrapper `v-if="searched && !loading && !error"` contains a single `v-if/v-else-if` chain (graph → raw → dns → github → email → empty). Keep ScanConsole and the error banner as separate `v-if`s BEFORE the wrapper; do not insert siblings between chain branches (Vue attaches `v-else-if` to the nearest preceding `v-if` sibling).
- GRAPH/LIST toggle: `viewMode` ref in Home.vue; GraphView stays mounted via `v-show` so the network is not rebuilt on toggle. Reset `viewMode='graph'` on each new search and type change (`onTypeChange`).
- Google Fonts: single `<link>` in `index.html` — do NOT add `@import url(...)` in component `<style>` blocks (there were 11 duplicates, all removed).
- `.status-badge` and `@keyframes pulse` live in `src/style.css` (not in dead `tokens.css`). Graph CSS lives only in GraphView.vue scoped styles — do not duplicate in style.css.

## API Reference

All endpoints are GET except /api/favorites (POST/DELETE):
- /api/search/username?q=, /api/search/email?q=, /api/search/phone?q=, /api/search/google?q=, /api/search/subdomains?q=, /api/search/harvest?q=, /api/search/dns?q=, /api/search/github?q=, /api/search/domain?q=
- /api/history, /api/favorites
- Swagger docs at http://localhost:8000/docs
