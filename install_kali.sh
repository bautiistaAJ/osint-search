#!/bin/bash
# Instalación OSINT Search ES para Kali Linux
set -e

echo "🔧 Instalando dependencias del sistema..."
sudo apt update -qq
sudo apt install -y python3-pip python3-full python3-venv nodejs npm docker.io docker-compose curl git

echo "🐍 Instalando herramientas Python..."
python3 -m pip install --break-system-packages maigret holehe python-whois whatsmyname httpx aiosqlite fastapi uvicorn python-multipart

echo "📁 Clonando proyecto..."
if [ ! -d "osint-search-es" ]; then
    git clone https://github.com/tu-usuario/osint-search-es.git
fi
cd osint-search-es

echo "📦 Instalando dependencias del backend..."
cd backend
python3 -m pip install --break-system-packages -r requirements.txt
cd ..

echo "📦 Instalando dependencias del frontend..."
cd frontend
npm install
cd ..

echo "✅ Instalación completa!"
echo ""
echo "Para ejecutar:"
echo "  Terminal 1: cd osint-search-es/backend && python3 main.py"
echo "  Terminal 2: cd osint-search-es/frontend && npm run dev"
echo ""
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
