#!/bin/bash
# ============================================
# KAIROS - Installation & Setup Script
# Script para inicializar el proyecto Django
# ============================================

set -e

echo "╔════════════════════════════════════════════╗"
echo "║        KAIROS - Setup Script              ║"
echo "║   Plataforma de Gestión de Documentos     ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Determine the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ El entorno virtual no existe."
    echo "📝 Creando venv..."
    python3 -m venv venv
fi

# Activate venv
echo "🔌 Activando entorno virtual..."
source venv/bin/activate

# Install requirements
echo "📦 Instalando dependencias..."
echo "⚠️  Si tienes problemas de conexión, usa:"
echo "   pip install Django==5.1 --no-index"
echo ""

pip install -r requirements.txt --quiet || {
    echo "⚠️  Algunos paquetes no pudieron instalarse."
    echo "   Continuando con Django base..."
    pip install Django==5.1 --quiet || echo "❌ No se pudo instalar Django"
}

# Migrate database
echo "🗄️  Ejecutando migraciones de base de datos..."
cd backend
python manage.py migrate --noinput

# Create initial roles
echo "👥 Creando roles iniciales..."
python manage.py shell << END
from apps.core.models import Role

roles = [
    ('client', 'Cliente'),
    ('manager', 'Gestor'),
    ('operator', 'Operador'),
    ('admin', 'Administrador'),
]

for name, display_name in roles:
    Role.objects.get_or_create(
        name=name,
        defaults={'description': f'Rol: {display_name}'}
    )
    print(f"✅ Rol '{display_name}' creado/verificado")
END

# Create superuser
echo ""
echo "👤 Creando superusuario (admin)..."
echo "Por favor, ingresa los siguientes datos:"
python manage.py createsuperuser --noinput \
    --username admin \
    --email admin@kairos.local || {
    echo "ℹ️  Usando cuenta admin existente o ingresa manualmente:"
    python manage.py createsuperuser
}

# Set password for admin (optional)
python manage.py shell << END
from django.contrib.auth.models import User
from apps.core.models import Role, UserProfile

try:
    user = User.objects.get(username='admin')
    user.set_password('admin')
    user.save()
    print(f"✅ Contraseña de admin configurada a: 'admin'")

    # Create user profile
    role = Role.objects.get(name='admin')
    UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': role, 'status': 'active'}
    )
    print(f"✅ Perfil de usuario creado")
except Exception as e:
    print(f"⚠️  Error al configurar admin: {e}")
END

# Collect static files
echo ""
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║          ✅ SETUP COMPLETADO              ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "🚀 Para iniciar el servidor de desarrollo:"
echo ""
echo "   1. Activar venv:"
echo "      source venv/bin/activate"
echo ""
echo "   2. Entrar en backend:"
echo "      cd backend"
echo ""
echo "   3. Ejecutar servidor:"
echo "      python manage.py runserver"
echo ""
echo "📍 Acceso:"
echo "   • Landing: http://localhost:8000/"
echo "   • Admin:   http://localhost:8000/admin/"
echo "   • API:     http://localhost:8000/api/"
echo ""
echo "🔑 Credenciales por defecto:"
echo "   • Usuario: admin"
echo "   • Contraseña: admin"
echo ""
echo "⚠️  ¡Cambia la contraseña en producción!"
echo ""
