#!/bin/bash

###############################################################################
#
# KAIROS Frontend - Ejecutor de Aplicación Web
#
# Este script inicia la aplicación Flet como una aplicación web
# Accesible desde: http://localhost:8550 (puerto por defecto de Flet)
#
# Uso:
#   ./run_web.sh              # Ejecuta en puerto 8550 (default)
#   ./run_web.sh --port 3000  # Ejecuta en puerto 3000
#
###############################################################################

set -e

# Color para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Obtener el directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Configuración por defecto
PORT=8550
WEB_MODE="--web"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --desktop)
            WEB_MODE=""
            shift
            ;;
        --help)
            echo "Uso: $0 [OPCIONES]"
            echo ""
            echo "Opciones:"
            echo "  --port PORT      Puerto para la aplicación (default: 8550)"
            echo "  --desktop        Ejecutar como desktop en lugar de web"
            echo "  --help           Mostrar esta ayuda"
            exit 0
            ;;
        *)
            echo "Opción desconocida: $1"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                ║${NC}"
echo -e "${BLUE}║            KAIROS - Frontend Web (Flet)                        ║${NC}"
echo -e "${BLUE}║                                                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar que Flet está instalado
if ! python -m flet --version &>/dev/null; then
    echo -e "${YELLOW}⚠️  Flet no está instalado${NC}"
    echo ""
    echo "Instalando Flet..."
    if command -v uv &> /dev/null; then
        uv pip install flet>=0.86.5
    else
        pip install flet>=0.86.5
    fi
fi

# Mostrar información
echo -e "${GREEN}✓ Iniciando aplicación Flet${NC}"
echo ""

if [ -n "$WEB_MODE" ]; then
    echo -e "  ${BLUE}Modo:${NC} WEB"
    echo -e "  ${BLUE}Puerto:${NC} $PORT"
    echo -e "  ${BLUE}URL:${NC} http://localhost:$PORT"
    echo ""
    echo -e "${YELLOW}💡 La aplicación se abrirá en tu navegador automáticamente${NC}"
    echo ""
    echo -e "${YELLOW}📝 Controles:${NC}"
    echo "  • Click en '+ Nuevo Proceso' para incrementar el contador"
    echo "  • Recarga la página para resetear el estado"
    echo ""
    echo -e "${YELLOW}📊 API Backend (Django):${NC}"
    echo "  • Backend en: http://localhost:8000"
    echo "  • Docs: http://localhost:8000/docs"
    echo ""
    echo -e "${YELLOW}🛑 Para detener: Presiona Ctrl+C${NC}"
    echo ""
    echo "─────────────────────────────────────────────────────────────────"
    echo ""

    # Ejecutar como web
    if command -v flet &> /dev/null; then
        flet run --web --port $PORT
    else
        python -m flet run --web --port $PORT
    fi
else
    echo -e "  ${BLUE}Modo:${NC} DESKTOP"
    echo ""
    echo -e "${YELLOW}🛑 Para detener: Cierra la ventana de la aplicación${NC}"
    echo ""
    echo "─────────────────────────────────────────────────────────────────"
    echo ""

    # Ejecutar como desktop
    if command -v flet &> /dev/null; then
        flet run
    else
        python -m flet run
    fi
fi
