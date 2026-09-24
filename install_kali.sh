#!/bin/bash
# Instalación OSINT Search ES para Kali Linux
set -e

echo "🔧 Instalando dependencias del sistema..."
sudo apt update -qq
sudo apt install -y python3-pip python3-full python3-venv nodejs npm docker.io docker-compose curl git

echo "📁 Clonando el proyecto..."
if [ ! -d "osint-search-es" ]; then
    git clone https://github.com/tu-usuario/osint-search-es.git
fi
cd osint-search-es

echo "🐍 Creando entorno virtual Python..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

echo "🐍 Instalando dependencias del backend..."
cd backend
pip install -r requirements.txt
cd ..

echo "📦 Instalando dependencias del frontend..."
cd frontend
npm install
cd ..

echo "✅ Instalación completa!"
echo ""
echo "Para ejecutar:"
echo "  Terminal 1:"
echo "    cd osint-search-es/backend && source venv/bin/activate && python3 main.py"
echo "  Terminal 2:"
echo "    cd osint-search-es/frontend && npm run dev"
echo ""
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Para activar el entorno virtual manualmente:"
echo "  source osint-search-es/venv/bin/activate"
