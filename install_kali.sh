#!/bin/bash
# Instalación OSINT Search ES para Kali Linux
set -e

echo "🔧 Instalando dependencias del sistema..."
sudo apt update -qq
sudo apt install -y python3-pip python3-full python3-venv nodejs npm docker.io docker-compose curl git

echo "📁 Preparando el proyecto..."
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    if [ ! -d "osint-search" ]; then
        git clone https://github.com/bautiistaAJ/osint-search.git
        cd osint-search
    fi
else
    echo "Proyecto ya existe en el directorio actual."
fi

echo "🐍 Creando entorno virtual Python..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

echo "🐍 Instalando dependencias del backend..."
cd backend
pip install -r requirements.txt 2>/dev/null || echo "⚠️ Algunos paquetes fallaron, continuando..."
pip install maigret holehe python-whois ghunt sublist3r theharvester dnspython python-dotenv 2>/dev/null || true
pip install git+https://github.com/sherlock-project/whatsmyname.git 2>/dev/null || echo "⚠️ whatsmyname no disponible, omitiendo..."
cd ..

echo "📦 Instalando dependencias del frontend..."
cd frontend
npm install
cd ..

echo "✅ Instalación completa!"
echo ""
echo "Para ejecutar:"
echo "  Terminal 1:"
echo "    cd backend && source ../venv/bin/activate && python3 main.py"
echo "  Terminal 2:"
echo "    cd frontend && npm run dev"
echo ""
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Para activar el entorno virtual manualmente:"
echo "  source venv/bin/activate"
