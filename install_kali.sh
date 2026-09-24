#!/bin/bash
# Instalación OSINT Search ES para Kali Linux
set -e

echo "🔧 Instalando dependencias del sistema..."
sudo apt update -qq
sudo apt install -y python3-pip python3-full python3-venv nodejs npm docker.io docker-compose curl git libjpeg-dev zlib1g-dev

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
pip install --only-binary :all: pillow

echo "🐍 Instalando dependencias del backend..."
cd backend
pip install --only-binary :all: -r requirements.txt
pip install maigret holehe python-whois ghunt sublist3r theharvester dnspython python-dotenv
pip install whats-my-name
cd ..

echo "📦 Instalando dependencias del frontend..."
cd frontend
npm install
chmod +x node_modules/.bin/vite
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
