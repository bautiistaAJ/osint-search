# 📚 Documentación de OSINT Search ES

Última actualización: Septiembre 2026

---

## 🏗️ Arquitectura

OSINT Search ES está dividida en dos aplicaciones independientes que se comunican mediante REST:

### Backend (FastAPI — Puerto 8000)
- **Main**: `backend/main.py` — Servidor FastAPI que expone 9 endpoints de búsqueda más historial y favoritos
- **Base de datos**: SQLite (`osint_search.db` en el directorio `backend/`)
- **Modelos**: `backend/models/database.py` — Gestiona tablas de historial y favoritos
- **Servicios**: `backend/services/osint_services.py` — Llama herramientas CLI externas (maigret, holehe, GHunt, etc.) y consultas DNS/GitHub
- **Flujo**: El frontend hace una petición HTTP → FastAPI ejecuta el comando CLI apropiado → Devuelve JSON

### Frontend (Vue 3 + Vite — Puerto 5173)
- **Entry**: `frontend/src/main.js` — Configura Vue Router con rutas `/`, `/history`, `/favorites`
- **Interfaz**: `frontend/src/App.vue` — Panel de búsqueda, tarjetas de resultados, grafo de entidades, navegación inferior
- **Grafo**: `frontend/src/components/GraphView.vue` — Visualización de red con vis-network
- **Proxy**: `frontend/vite.config.js` — Proxyea `/api/*` a `http://localhost:8000` en modo desarrollo

### Comunicación
```
Frontend (5173)  →  /api/search/...  →  Vite Proxy  →  Backend (8000)
```

---

## 🚀 Instalación

### Opción 1: Script de instalación (Kali Linux)
```bash
chmod +x install_kali.sh
./install_kali.sh
```
> **Nota**: En Kali moderno (PEP 668), el script crea un entorno virtual (`venv`) para evitar el error. El repositorio es `https://github.com/bautiistaAJ/osint-search.git`.

### Opción 2: Docker Compose
```bash
docker-compose up --build
```
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs
- Base de datos persiste en el volumen `osint_data`

### Opción 3: Instalación manual
```bash
# Terminal 1 — Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev
```

> **Requisito**: Instalar primero las herramientas del sistema con `install_kali.sh` (apt, python3-venv, nodejs). El entorno virtual (venv) evita el error PEP 668 de Kali moderno.

---

## 🔍 Guía de búsqueda por tipo

### 👤 1. Usuario / Handle
**Endpoint**: `GET /api/search/username?q=johndoe99`

**Herramientas**: `maigret` (3000+ sitios) + `whatsmyname` (270+ sitios)

**Entrada**: Cualquier nombre de usuario o handle (sin @)

**Salida esperada**:
```json
{
  "query": "johndoe99",
  "results": [
    {"site": "GitHub", "url": "https://github.com/johndoe99", "found": true},
    {"site": "Twitter", "url": "https://twitter.com/johndoe99", "found": true}
  ],
  "total": 2
}
```

**En la interfaz**: Aparecen como tarjetas con enlace directo. Se muestra el grafo de entidades si hay resultados.

---

### 📧 2. Email
**Endpoint**: `GET /api/search/email?q=john@example.com`

**Herramientas**: `holehe` (120+ plataformas) + `HaveIBeenPwned` (brechas de seguridad)

**Entrada**: Dirección de email completa

**Salida esperada**:
```json
{
  "query": "john@example.com",
  "accounts": [
    {"site": "GitHub", "found": true},
    {"site": "Instagram", "found": true}
  ],
  "breach": {
    "breaches": [
      {"Title": "Example Breach", "BreachDate": "2021-03-15"}
    ],
    "found": true
  },
  "total": 3
}
```

**En la interfaz**: Muestra las cuentas encontradas como tarjetas + una sección adicional de "🔒 BRECHAS" con las filtraciones de seguridad.

---

### 🌐 3. Dominio (WHOIS)
**Endpoint**: `GET /api/search/domain?q=example.com`

**Herramienta**: `python-whois`

**Entrada**: Dominio sin protocolo (`example.com`, no `http://example.com`)

**Salida esperada**:
```json
{
  "query": "example.com",
  "results": {
    "raw": "Domain Name: EXAMPLE.COM\nRegistrar: ...",
    "found": true
  }
}
```

**En la interfaz**: Muestra el resultado WHOIS completo como texto preformateado.

---

### 📱 4. Teléfono
**Endpoint**: `GET /api/search/phone?q=+1234567890`

**Herramienta**: `phoneinfoga`

**Entrada**: Número de teléfono con código de país (`+1234567890`, `+34600123456`)

**Salida esperada**:
```json
{
  "query": "+1234567890",
  "results": {
    "raw": "Carrier: AT&T\nCountry: United States\nType: Mobile",
    "found": true
  }
}
```

**En la interfaz**: Muestra el resultado crudo de PhoneInfoga en un bloque `<pre>`.

---

### 🔍 5. Google Account
**Endpoint**: `GET /api/search/google?q=john@example.com`

**Herramienta**: `ghunt`

**Entrada**: Email asociado a una cuenta Google

**Salida esperada**:
```json
{
  "query": "john@example.com",
  "results": {
    "raw": "Perfil: John Doe\nFotos: 45\nYouTube: ...",
    "found": true
  }
}
```

**En la interfaz**: Muestra el resultado crudo de GHunt en un bloque `<pre>`.

---

### 🕸️ 6. Subdominios
**Endpoint**: `GET /api/search/subdomains?q=example.com`

**Herramienta**: `sublist3r`

**Entrada**: Dominio principal (`example.com`)

**Salida esperada**:
```json
{
  "query": "example.com",
  "results": {
    "raw": "www.example.com\nmail.example.com\napi.example.com",
    "found": true
  }
}
```

**En la interfaz**: Muestra la lista de subdominios en un bloque `<pre>`.

---

### 🎯 7. Recolección de Emails
**Endpoint**: `GET /api/search/harvest?q=example.com`

**Herramienta**: `theHarvester`

**Entrada**: Dominio para buscar emails (`example.com`)

**Salida esperada**:
```json
{
  "query": "example.com",
  "results": {
    "raw": "admin@example.com\nsupport@example.com\ninfo@example.com",
    "found": true
  }
}
```

**En la interfaz**: Muestra los emails recolectados en un bloque `<pre>`.

---

### 📋 8. Registros DNS
**Endpoint**: `GET /api/search/dns?q=example.com`

**Herramienta**: `dnspython`

**Entrada**: Dominio (`example.com`)

**Salida esperada**:
```json
{
  "query": "example.com",
  "results": {
    "A": ["93.184.216.34"],
    "AAAA": ["2606:2800:0220:0001:0248:1893:25c8:1946"],
    "MX": ["mail.example.com"],
    "TXT": ["v=spf1 include:_spf.example.com ~all"],
    "NS": ["a.iana-servers.net"],
    "CNAME": [],
    "CAA": [],
    "SOA": ["ns1.example.com"]
  },
  "found": true
}
```

**En la interfaz**: Muestra cada tipo de registro como una tarjeta con lista de valores.

---

### 🐙 9. GitHub
**Endpoint**: `GET /api/search/github?q=torvalds`

**Herramienta**: GitHub API (`api.github.com/users/{username}`)

**Entrada**: Username de GitHub (`torvalds`, no `@torvalds`)

**Salida esperada**:
```json
{
  "query": "torvalds",
  "results": {
    "login": "torvalds",
    "name": "Linus Torvalds",
    "bio": "...",
    "public_repos": 12,
    "followers": 200000,
    "following": 0,
    "html_url": "https://github.com/torvalds",
    "company": "Linux Foundation",
    "location": "Portland, OR",
    "email": null,
    "twitter_username": null,
    "found": true
  }
}
```

**En la interfaz**: Muestra una tarjeta especial de GitHub con foto, bio, repos, followers, ubicación y enlace.

---

## 🕸️ Visualización de Grafo de Entidades

El grafo se activa automáticamente cuando hay resultados. Usa `vis-network` para renderizar las conexiones.

**Cómo funciona**:
1. `App.vue` recibe los resultados del backend
2. Si `results.length > 0`, se activa `GraphView.vue`
3. `GraphView.vue` convierte los resultados en nodos y aristas
4. Se renderiza un grafo interactivo con zoom y drag

**Interacción**:
- Zoom con scroll
- Arrastrar nodos
- Hover para ver detalles

---

## 📜 Historial

**Ruta**: `/history`

El historial se almacena en SQLite (`backend/osint_search.db`). Cada búsqueda se registra con:
- Tipo de consulta (username, email, etc.)
- Valor de la consulta
- Resultados JSON
- Fecha/hora

**Endpoints**:
- `GET /api/history?limit=50` — Obtener las últimas 50 búsquedas

**Características**:
- Se guarda automáticamente con cada búsqueda
- Se puede acceder desde la barra de navegación inferior
- No se puede editar ni eliminar individualmente

---

## ⭐ Favoritos

**Ruta**: `/favorites`

**Endpoints**:
- `GET /api/favorites` — Listar todos los favoritos
- `POST /api/favorites` — Agregar un favorito (parámetros: `query_type`, `query_value`, `label`)
- `DELETE /api/favorites/{id}` — Eliminar un favorito por ID

**Características**:
- Permite marcar búsquedas como favoritas con una etiqueta personalizada
- Se accede desde la barra de navegación inferior
- Persiste en la base de datos SQLite

---

## 📋 Referencia completa de la API

Todos los endpoints excepto `/api/favorites` son **GET**. CORS habilitado para todos los orígenes.

### Búsquedas

| Endpoint | Método | Descripción | Parámetro |
|----------|--------|-------------|----------|
| `/api/search/username` | GET | Búsqueda de usuario | `q` |
| `/api/search/email` | GET | Búsqueda de email | `q` |
| `/api/search/phone` | GET | Búsqueda de teléfono | `q` |
| `/api/search/google` | GET | Búsqueda Google Account | `q` |
| `/api/search/subdomains` | GET | Enumeración de subdominios | `q` |
| `/api/search/harvest` | GET | Recolección de emails | `q` |
| `/api/search/dns` | GET | Registros DNS | `q` |
| `/api/search/github` | GET | Información de GitHub | `q` |
| `/api/search/domain` | GET | Información WHOIS | `q` |

### Utilidades

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/history` | GET | Historial de búsquedas (`limit` opcional) |
| `/api/favorites` | GET | Listar favoritos |
| `/api/favorites` | POST | Agregar favorito (`query_type`, `query_value`, `label`) |
| `/api/favorites/{fav_id}` | DELETE | Eliminar favorito |

### Ejemplos de petición

```bash
# Buscar un usuario
curl "http://localhost:8000/api/search/username?q=torvalds"

# Buscar un email
curl "http://localhost:8000/api/search/email?q=john@example.com"

# Buscar DNS
curl "http://localhost:8000/api/search/dns?q=example.com"

# Agregar a favoritos
curl -X POST "http://localhost:8000/api/favorites?query_type=username&query_value=torvalds&label=Linux"

# Ver favoritos
curl "http://localhost:8000/api/favorites"

# Eliminar favorito
curl -X DELETE "http://localhost:8000/api/favorites/1"
```

### Ejemplo con axios (frontend)
```javascript
const res = await axios.get("/api/search/username?q=torvalds");
console.log(res.data.results); // Array de resultados
```

---

## 🔧 Solución de problemas

### Error: externally-managed-environment / PEP 668
**Causa**: Kali moderno bloquea `pip install` sin un entorno virtual
**Solución**: Usar `python3 -m venv venv` y `source venv/bin/activate`. El script `install_kali.sh` lo hace automáticamente.

### Error: Comando no encontrado (maigret, holehe, etc.)
**Causa**: Las herramientas CLI no están instaladas o no están en el PATH
**Solución**:
```bash
source venv/bin/activate
pip install maigret holehe phoneinfoga ghunt sublist3r theharvester dnspython python-whois
which maigret  # Verificar que está en el PATH
```

### Error: Backend no responde
**Causa**: El servidor FastAPI no está corriendo
**Solución**:
```bash
cd backend
python3 main.py
# Verificar en http://localhost:8000/docs
```

### Error: Vite proxy no funciona
**Causa**: El frontend no puede alcanzar el backend
**Solución**: Verificar que el backend está corriendo en `localhost:8000`. El proxy en `vite.config.js` solo funciona con el servidor de desarrollo de Vite (`npm run dev`), no con `npm run build`.

### Error: Home.vue no encontrado
**Causa**: El archivo `frontend/src/views/Home.vue` puede estar faltando
**Solución**: Verificar que el archivo existe en `frontend/src/views/Home.vue`. Si no existe, el enrutamiento fallará.

### Error: Base de datos no se crea
**Causa**: El backend no tiene permisos de escritura en el directorio
**Solución**: Verificar que `backend/osint_search.db` puede crearse en el directorio `backend/`

### Los resultados vienen vacíos
**Causa**: La herramienta CLI externa no encontró nada o falló el timeout (120 segundos)
**Solución**: Verificar que la herramienta funciona directamente desde la terminal:
```bash
maigret torvalds
holehe john@example.com
```

---

## 🐳 Despliegue con Docker

```bash
docker-compose up --build
```

**Puertos**:
- Frontend: 5173
- Backend API: 8000
- Swagger Docs: http://localhost:8000/docs

**Volúmenes**:
- `./backend:/app` — Código del backend montado
- `./frontend:/app` — Código del frontend montado (excluye `/app/node_modules`)
- `osint_data` — Persistencia de la base de datos SQLite

> **Nota**: En Docker, el proxy de Vite no aplica. El frontend debe comunicarse directamente con `http://localhost:8000`.

---

## 📂 Estructura del proyecto

```
osint-search/
├── backend/
│   ├── main.py              # API FastAPI v2.0
│   ├── models/
│   │   ├── __init__.py      # Exporta funciones de database
│   │   └── database.py      # SQLite (historial + favoritos)
│   ├── services/
│   │   ├── __init__.py
│   │   └── osint_services.py # PhoneInfoga, GHunt, sublist3r, theHarvester, DNS, GitHub
│   ├── requirements.txt     # Dependencias Python
│   ├── osint_search.db      # Base de datos SQLite (se crea al ejecutar)
│   ├── venv/                # Entorno virtual Python
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.vue          # Interfaz principal
│   │   ├── components/
│   │   │   └── GraphView.vue # Visualización de grafo
│   │   ├── main.js          # Router
│   │   └── views/
│   │       ├── Home.vue      # Búsqueda + resultados + grafo (⚠️ puede faltar)
│   │       ├── History.vue   # Historial
│   │       └── Favorites.vue # Favoritos
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js       # Proxy /api → localhost:8000
│   └── Dockerfile
├── docker-compose.yml
├── install_kali.sh          # Script de instalacion para Kali
├── README.md
├── DOCS.md                  # Este archivo
└── AGENTS.md                # Instrucciones para OpenCode
```

---

## 🛠️ Herramientas integradas

| Herramienta | Tipo | Cobertura | Instalación |
|-------------|------|-----------|-------------|
| Maigret | Username | 3000+ sitios | `pip install maigret` |
| WhatsMyName | Username | 270+ sitios | `pip install whatsmyname` |
| holehe | Email | 120+ plataformas | `pip install holehe` |
| PhoneInfoga | Teléfono | Carrier, geoloc | `pip install phoneinfoga` |
| GHunt | Google Account | Perfil, fotos | `pip install ghunt` |
| sublist3r | Subdominios | DNS enumeration | `pip install sublist3r` |
| theHarvester | Email recon | Múltiples fuentes | `pip install theharvester` |
| python-whois | WHOIS | Dominios | `pip install python-whois` |
| dnspython | DNS Records | A/AAAA/MX/TXT | `pip install dnspython` |
| HaveIBeenPwned | Breach | Breach records | API gratuita |
| GitHub API | Perfil | Usuarios públicos | API gratuita |

---

## 📖 Recursos adicionales

- **Swagger UI**: http://localhost:8000/docs
- **Repositorio**: https://github.com/bautiistaAJ/osint-search
- **Licencia**: MIT

---

## 🆕 Próximos pasos

- [ ] Shodan + VirusTotal + Censys (infraestructura)
- [ ] IP geolocalización (IP2Location, AbuseIPDB)
- [ ] AI Assistant (sugerencias de próximos pasos)
- [ ] Reporte PDF/HTML
- [ ] Proxy support
- [ ] Reverse image search
- [ ] Wayback Machine

---

*Documentación generada para OSINT Search ES v1.0.0*