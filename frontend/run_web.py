#!/usr/bin/env python3
"""
KAIROS Frontend - Ejecutor Web

Inicia la aplicación Flet como webapp en modo web.

Uso:
    python run_web.py              # Ejecuta en puerto 8550 (default)
    python run_web.py --port 3000  # Ejecuta en puerto 3000
    python run_web.py --desktop    # Ejecuta como desktop
    python run_web.py --help       # Muestra ayuda
"""

import sys
import subprocess
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="KAIROS Frontend - Ejecutor Web (Flet)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python run_web.py              # Ejecutar como web (puerto 8550)
  python run_web.py --port 3000  # Ejecutar en puerto específico
  python run_web.py --desktop    # Ejecutar como desktop
        """
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8550,
        help="Puerto para la aplicación web (default: 8550)"
    )

    parser.add_argument(
        "--desktop",
        action="store_true",
        help="Ejecutar como desktop en lugar de web"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Modo debug"
    )

    args = parser.parse_args()

    print("\n")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                                                                ║")
    print("║            KAIROS - Frontend Web (Flet)                        ║")
    print("║                                                                ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    # Cambiar al directorio del script
    script_dir = Path(__file__).parent

    # Mostrar información
    print("✓ Iniciando aplicación Flet")
    print()

    if args.desktop:
        print(f"  • Modo: DESKTOP")
        print()
        print("🛑 Para detener: Cierra la ventana de la aplicación")
        print()
        print("─" * 60)
        print()
        cmd = ["flet", "run"]
    else:
        print(f"  • Modo: WEB")
        print(f"  • Puerto: {args.port}")
        print(f"  • URL: http://localhost:{args.port}")
        print()
        print("💡 La aplicación se abrirá en tu navegador automáticamente")
        print()
        print("📝 Controles:")
        print("  • Click en '+ Nuevo Proceso' para incrementar el contador")
        print("  • Recarga la página para resetear el estado")
        print()
        print("📊 API Backend (Django):")
        print("  • Backend en: http://localhost:8000")
        print("  • Docs: http://localhost:8000/docs")
        print()
        print("🛑 Para detener: Presiona Ctrl+C")
        print()
        print("─" * 60)
        print()
        cmd = ["flet", "run", "--web", "--port", str(args.port)]

    if args.debug:
        cmd.append("--debug")

    try:
        subprocess.run(cmd, cwd=script_dir, check=True)
    except FileNotFoundError:
        print("\n❌ Error: 'flet' no encontrado")
        print("\nInstala Flet con:")
        print("  pip install flet>=0.86.5")
        print("  o")
        print("  uv pip install flet>=0.86.5")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Aplicación detenida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
