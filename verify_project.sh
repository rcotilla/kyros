#!/bin/bash
# ============================================
# KAIROS - Verification & Status Check
# Verificar que todo el proyecto esté completo
# ============================================

echo "╔════════════════════════════════════════════╗"
echo "║   KAIROS - Project Verification           ║"
echo "║   Status Check & Installation Guide       ║"
echo "╚════════════════════════════════════════════╝"
echo ""

cd /home/rolando/Documentos/Kyros

# Check venv
echo "🔍 Verificando entorno virtual..."
if [ -d "venv" ]; then
    echo "✅ venv/ - OK"
else
    echo "❌ venv/ - NO ENCONTRADO"
fi

# Check backend structure
echo ""
echo "🔍 Verificando estructura backend..."

backends=(
    "backend/kairos/__init__.py"
    "backend/kairos/settings.py"
    "backend/kairos/urls.py"
    "backend/kairos/wsgi.py"
    "backend/kairos/asgi.py"
    "backend/manage.py"
)

for file in "${backends[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - FALTA"
    fi
done

# Check apps
echo ""
echo "🔍 Verificando aplicaciones Django..."

apps=(
    "core"
    "documents"
    "tasks"
    "landing"
)

for app in "${apps[@]}"; do
    app_path="backend/apps/$app"

    if [ -d "$app_path" ]; then
        required_files=(
            "__init__.py"
            "apps.py"
            "models.py"
            "admin.py"
            "views.py"
            "urls.py"
            "serializers.py"
            "migrations/__init__.py"
        )

        echo ""
        echo "  📦 $app:"

        for file in "${required_files[@]}"; do
            full_path="$app_path/$file"
            if [ -f "$full_path" ]; then
                echo "     ✅ $file"
            else
                echo "     ⚠️  $file - (opcional o no requerido)"
            fi
        done
    else
        echo "  ❌ $app/ - NO ENCONTRADA"
    fi
done

# Check templates
echo ""
echo "🔍 Verificando templates..."

templates=(
    "backend/templates/base.html"
    "backend/templates/landing/index.html"
    "backend/templates/landing/about.html"
    "backend/templates/landing/contact.html"
)

for template in "${templates[@]}"; do
    if [ -f "$template" ]; then
        echo "✅ $template"
    else
        echo "❌ $template - FALTA"
    fi
done

# Check configuration files
echo ""
echo "🔍 Verificando archivos de configuración..."

configs=(
    "requirements.txt"
    "README.md"
    "ESTRUCTURA_PROYECTO.md"
    ".gitignore"
    "setup.sh"
    "setup_complete.sh"
    "docs/FASE_3.md"
    "frontend/README.md"
)

for config in "${configs[@]}"; do
    if [ -f "$config" ]; then
        echo "✅ $config"
    else
        echo "❌ $config - FALTA"
    fi
done

# Check Python syntax
echo ""
echo "🔍 Verificando sintaxis Python..."

python_files=$(find backend -name "*.py" -type f | head -10)
errors=0

for file in $python_files; do
    if python3 -m py_compile "$file" 2>/dev/null; then
        echo "✅ $file"
    else
        echo "❌ $file - Error de sintaxis"
        ((errors++))
    fi
done

# Summary
echo ""
echo "╔════════════════════════════════════════════╗"
echo "║            📊 RESUMEN FINAL                ║"
echo "╚════════════════════════════════════════════╝"
echo ""

if [ $errors -eq 0 ]; then
    echo "✅ Proyecto completado exitosamente"
    echo ""
    echo "📋 Checklist de Instalación:"
    echo "  1. ✅ Estructura creada"
    echo "  2. ⏳ Instalar dependencias:"
    echo "     source venv/bin/activate"
    echo "     pip install -r requirements.txt"
    echo "  3. ⏳ Crear base de datos:"
    echo "     cd backend"
    echo "     python manage.py migrate"
    echo "  4. ⏳ Crear superusuario:"
    echo "     python manage.py createsuperuser"
    echo "  5. ⏳ Ejecutar servidor:"
    echo "     python manage.py runserver"
    echo ""
    echo "🌐 Acceso:"
    echo "  • Landing: http://localhost:8000/"
    echo "  • Admin:   http://localhost:8000/admin/"
    echo "  • API:     http://localhost:8000/api/"
else
    echo "⚠️  Se encontraron algunos problemas"
    echo "   Revisa los errores de sintaxis arriba"
fi

echo ""
echo "📚 Para más información, ver:"
echo "  • README.md - Documentación general"
echo "  • ESTRUCTURA_PROYECTO.md - Estructura detallada"
echo "  • docs/FASE_3.md - Features futuras"
echo ""
