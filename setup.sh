#!/bin/bash
# ============================================
# KAIROS Setup Script
# Instala todas las dependencias necesarias
# ============================================

set -e

echo "🚀 Inicializando proyecto KAIROS..."

# Activar venv
source venv/bin/activate

echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo "🔧 Ejecutando migraciones de Django..."
cd backend
python manage.py migrate

echo "👤 Creando superusuario (Django Admin)..."
echo "Ingresa credenciales para el admin:"
python manage.py createsuperuser

echo "✅ ¡Proyecto listo!"
echo ""
echo "Para iniciar el servidor de desarrollo:"
echo "  cd backend"
echo "  python manage.py runserver"
echo ""
echo "Acceder a:"
echo "  Admin: http://localhost:8000/admin/"
echo "  API: http://localhost:8000/api/"
