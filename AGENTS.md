# AGENTS.md

## Project Overview

OSINT Search ES - a cyberpunk-styled OSINT tool with a FastAPI backend (Python 3.11+) and Vue 3 + Vite frontend (Node.js 20+). Two independent apps that communicate via REST; frontend proxies /api to localhost:8000.

## Architecture

- Backend (backend/): FastAPI app on port 8000. Entry point is main.py. Uses subprocess to call external CLI tools (maigret, whatsmyname, holehe, phoneinfoga, ghunt, sublist3r, theHarvester). Database is SQLite (osint_search.db in the backend/ dir). Models in models/, services in services/.

- Frontend (frontend/): Vue 3 + Vue Router + Vite on port 5173. vite.config.js proxies /api to http://localhost:8000. Uses vis-network for entity graph visualization.

- Docker Compose: docker-compose up --build runs both services. Backend volume-mounts ./backend:/app; frontend volume-mounts ./frontend:/app with /app/node_modules excluded.

## Running the App

Option 1 - Direct (Kali/recommended):
cd backend && python main.py
cd frontend && npm run dev

Option 2 - Docker:
docker-compose up --build

Option 3 - Install script (Kali):
chmod +x install_kali.sh && ./install_kali.sh

## Key Gotchas

- Run python main.py from inside backend/ - imports use from models.database import ... and from services.osint_services import ..., which only work when the backend directory is the working directory or on sys.path.
- External tools must be installed separately - the backend calls maigret, whatsmyname, holehe, phoneinfoga, ghunt, sublist3r, theHarvester, dnspython, python-whois as CLI commands. pip install -r requirements.txt installs Python packages but the CLI tools may need pip install of the specific package names.
- Vite proxy: Frontend API calls to /api/... are proxied to http://localhost:8000 only when the dev server is running. In production (Docker), the proxy config does not apply.
- No test, lint, typecheck, or formatter scripts are configured. package.json only has dev, build, preview. No pytest, ruff, or eslint setup exists.
- No CI workflows, pre-commit hooks, or existing instruction files.
- install_kali.sh clones from https://github.com/tu-usuario/osint-search-es.git - update the URL before use.
- Database file: osint_search.db is created in the backend/ directory at runtime. When using Docker, it persists in the osint_data volume.

## Frontend Structure

- src/App.vue - main component with search UI, graph view, and bottom nav
- src/main.js - Vue app + router setup (routes: /, /history, /favorites)
- src/views/ - History.vue, Favorites.vue
- src/components/GraphView.vue - vis-network entity graph
- src/views/Home.vue - referenced in main.js imports but may be missing from the views/ directory

## API Reference

All endpoints are GET except /api/favorites (POST/DELETE):
- /api/search/username?q=, /api/search/email?q=, /api/search/phone?q=, /api/search/google?q=, /api/search/subdomains?q=, /api/search/harvest?q=, /api/search/dns?q=, /api/search/github?q=, /api/search/domain?q=
- /api/history, /api/favorites
- Swagger docs at http://localhost:8000/docs
