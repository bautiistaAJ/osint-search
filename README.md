# OSINT Search ES 🔍

Buscador OSINT personalizado con interfaz cyberpunk en español.

## Características

### Busquedas
- 👤 **Username** — Maigret (3000+ sitios) + WhatsMyName (270+ sitios)
- 📧 **Email** — holehe (120+ plataformas) + HaveIBeenPwned (breaches)
- 🌐 **Dominio** — WHOIS completo
- 📱 **Teléfono** — PhoneInfoga (carrier, país, tipo de línea)
- 🔍 **Google Account** — GHunt (perfil, fotos, YouTube, G+)
- 🕸️ **Subdominios** — sublist3r
- 🎯 **Recolección de Emails** — theHarvester (múltiples fuentes)
- 📋 **Registros DNS** — A, AAAA, MX, TXT, NS, CNAME, CAA, SOA
- 🐙 **GitHub** — Perfil, repos, seguidores, bio, ubicación

### Visualización
- 🕸️ **Grafo de entidades** — Visualización de conexiones entre resultados
- 🎨 **Estilo Cyberpunk** — Neones cyan/magenta, glitch effects, grid animado
- 📊 **Dashboard de resultados** — Tarjetas con enlaces directos

### Utilidades
- 📜 Historial de búsquedas (SQLite)
- ⭐ Favoritos
- 📤 Exportar resultados (JSON)
- 🔒 API REST documentada (Swagger en `/docs`)

## Requisitos

- Python 3.11+
- Node.js 20+
- Docker + Docker Compose (opcional)
- Kali Linux recomendado

## Instalación rápida (Kali Linux)

```bash
# 1. Instalar dependencias del sistema
sudo apt install python3-pip nodejs npm docker.io docker-compose

# 2. Clonar el proyecto
git clone <repo> osint-search-es
cd osint-search-es

# 3. Ejecutar el script de instalación
chmod +x install_kali.sh
./install_kali.sh

# 4. Ejecutar el backend
cd backend && python main.py

# 5. Ejecutar el frontend (en otra terminal)
cd frontend && npm run dev
```

> **Nota**: Kali moderno usa PEP 668 (entornos externamente gestionados). El script `install_kali.sh` incluye `--break-system-packages` para `pip`. Si instalas manualmente, usa `pip install --break-system-packages <paquete>`.

## Con Docker Compose

```bash
docker-compose up --build
```

Luego abrir en el navegador:
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

## Uso

Seleccioná el tipo de búsqueda en el dropdown:

| Tipo | Qué buscá | Ejemplo |
|------|-----------|---------|
| 👤 Usuario | Handle/nombre de usuario | `johndoe99` |
| 📧 Email | Email y cuentas vinculadas | `john@example.com` |
| 🌐 Dominio | Información WHOIS | `example.com` |
| 📱 Teléfono | Carrier, país, línea | `+1234567890` |
| 🔍 Google Account | Perfil Google | `john@example.com` |
| 🕸️ Subdominios | Subdominios de un dominio | `example.com` |
| 🎯 Recolección Email | Emails de un dominio | `example.com` |
| 📋 DNS | Registros DNS | `example.com` |
| 🐙 GitHub | Perfil de GitHub | `torvalds` |

## API Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/search/username?q=` | GET | Búsqueda de usuario |
| `/api/search/email?q=` | GET | Búsqueda de email |
| `/api/search/phone?q=` | GET | Búsqueda de teléfono |
| `/api/search/google?q=` | GET | Búsqueda Google Account |
| `/api/search/subdomains?q=` | GET | Enumeración de subdominios |
| `/api/search/harvest?q=` | GET | Recolección de emails |
| `/api/search/dns?q=` | GET | Registros DNS |
| `/api/search/github?q=` | GET | Información de GitHub |
| `/api/search/domain?q=` | GET | Información WHOIS |
| `/api/history` | GET | Historial de búsquedas |
| `/api/favorites` | GET | Favoritos |
| `/api/favorites` | POST | Agregar favorito |
| `/api/favorites/:id` | DELETE | Eliminar favorito |

## Estructura del proyecto

```
osint-search-es/
├── backend/
│   ├── main.py              # API FastAPI v2.0
│   ├── models/
│   │   └── database.py      # SQLite (historial + favoritos)
│   ├── services/
│   │   └── osint_services.py # PhoneInfoga, GHunt, sublist3r, theHarvester, DNS, GitHub
│   ├── requirements.txt     # Todas las dependencias
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.vue          # Interfaz cyberpunk principal
│   │   ├── components/
│   │   │   └── GraphView.vue # Visualización de grafo de entidades
│   │   ├── main.js          # Router
│   │   └── views/
│   │       ├── Home.vue      # Búsqueda + resultados + grafo
│   │       ├── History.vue   # Historial
│   │       └── Favorites.vue # Favoritos
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
├── install_kali.sh
└── README.md
```

## Herramientas integradas

| Herramienta | Tipo | Cobertura | License |
|-------------|------|-----------|---------|
| Maigret | Username | 3000+ sitios | MIT |
| WhatsMyName | Username | 270+ sitios | MIT |
| holehe | Email | 120+ plataformas | MIT |
| PhoneInfoga | Teléfono | Carrier, geoloc | MIT |
| GHunt | Google Account | Perfil, fotos | MIT |
| sublist3r | Subdomains | DNS enumeration | MIT |
| theHarvester | Email recon | Múltiples fuentes | MIT |
| python-whois | WHOIS | Dominios | MIT |
| dnspython | DNS Records | A/AAAA/MX/TXT | MIT |
| HaveIBeenPwned | Breach | Breach records | Free API |
| GitHub API | Perfil | Usuarios públicos | Free |

## Próximos pasos

- [ ] Shodan + VirusTotal + Censys (infraestructura)
- [ ] IP geolocalización (IP2Location, AbuseIPDB)
- [ ] AI Assistant (sugerencias de próximos pasos)
- [ ] Reporte PDF/HTML
- [ ] Proxy support
- [ ] Reverse image search
- [ ] Wayback Machine

## Licencia

MIT
