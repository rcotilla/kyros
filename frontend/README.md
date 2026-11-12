# KAIROS Frontend - Aplicación Web con Flet

Plataforma de Gestión de Procesos de Gestoría - Frontend construido con **Flet**.

## 🚀 Inicio Rápido

### Opción 1: Script Ejecutable (Recomendado)

#### En Linux/macOS:
```bash
cd /home/rolando/Documentos/Kyros/frontend
./run_web.sh
```

#### En Windows (Bash/Git Bash):
```bash
cd C:\ruta\a\Kyros\frontend
./run_web.sh
```

#### Con Python:
```bash
cd /home/rolando/Documentos/Kyros/frontend
python run_web.py
```

### Opción 2: Comandos Flet Directos

#### Ejecutar como Web (Aplicación Web interactiva)
```bash
cd frontend
flet run --web
```

**La aplicación se abrirá en:** `http://localhost:8550`

#### Ejecutar como Desktop (Aplicación de escritorio)
```bash
cd frontend
flet run
```

#### Con Puerto Personalizado
```bash
flet run --web --port 3000
# Accede a: http://localhost:3000
```

### Opción 3: Con UV (Recomendado)
```bash
# Ejecutar como web
uv run flet run --web

# Ejecutar como desktop
uv run flet run

# Con puerto personalizado
uv run flet run --web --port 3000
```

---

## 📋 Requisitos

- Python 3.10+
- Flet >= 0.86.5

### Instalar Dependencias

```bash
# Con pip
pip install flet>=0.86.5

# Con uv (recomendado)
uv pip install flet>=0.86.5

# O con pyproject.toml
uv sync
```

---

## 🎯 Descripción de la Aplicación

### Características Actuales
- ✅ Interfaz web moderna con Flet
- ✅ Contador de procesos interactivo
- ✅ Responsive y compatible con navegadores
- ✅ Tema claro/oscuro
- ✅ Integración lista para API backend (Django)

### Estructura
```
frontend/
├── src/
│   ├── main.py          # Aplicación principal
│   └── assets/          # Recursos (imágenes, iconos, etc)
├── tests/               # Tests
├── run_web.sh          # Script bash para ejecutar como web
├── run_web.py          # Script Python para ejecutar
├── pyproject.toml      # Configuración del proyecto
└── README.md           # Este archivo
```

---

## 🔧 Configuración

### Puertos Disponibles
- **8550**: Puerto por defecto de Flet
- **3000**: Alternativa (si 8550 está en uso)
- **5000**: Alternativa 2
- **Personalizado**: Puedes especificar cualquier puerto

### Variables de Entorno (Opcional)
```bash
# Para API backend
export API_URL=http://localhost:8000
export API_TOKEN=your-jwt-token

# Luego ejecutar
./run_web.sh
```

---

## 📱 Modos de Ejecución

### Modo Web (por defecto)
```bash
./run_web.sh                    # Puerto 8550
./run_web.sh --port 3000       # Puerto 3000
python run_web.py              # Puerto 8550
python run_web.py --port 3000  # Puerto 3000
```

**Ventajas:**
- ✅ Accesible desde cualquier navegador
- ✅ URL compartible
- ✅ Responsive en móviles
- ✅ Sin instalación de app

### Modo Desktop
```bash
./run_web.sh --desktop          # Bash script
python run_web.py --desktop     # Python script
flet run                         # Flet directo
```

**Ventajas:**
- ✅ Mejor rendimiento
- ✅ Acceso a características de sistema
- ✅ Interfaz nativa del SO

---

## 🔗 Integración con Backend (Django)

La aplicación está lista para conectarse con el backend Django en `http://localhost:8000`.

### Endpoints Disponibles
```
POST   /api/token/           # Obtener JWT
GET    /api/user/profile/    # Perfil del usuario
GET    /api/clients/         # Listar clientes
POST   /api/clients/         # Crear cliente
GET    /api/processes/       # Listar procesos
POST   /api/processes/       # Crear proceso
GET    /api/process-types/   # Tipos de procesos
```

### Conectar Frontend con Backend
En `src/main.py`, modifica la variable `API_URL`:

```python
API_URL = "http://localhost:8000/api"
JWT_TOKEN = "your-jwt-token-here"
```

---

## 🧪 Testing

### Ejecutar Tests
```bash
# Con pytest
pytest tests/

# Con flet
flet test

# Con uv
uv run pytest tests/
```

---

## 🏗️ Build/Empaquetación

### Build para Web (producción)
```bash
flet build web -v
```

Salida en: `build/web/`

### Build para Escritorio
```bash
# Windows
flet build windows -v

# macOS
flet build macos -v

# Linux
flet build linux -v
```

### Build para Móvil
```bash
# Android
flet build apk -v

# iOS
flet build ipa -v
```

Para más detalles: https://flet.dev/docs/publish/

---

## 📊 Estructura del Código

### main.py
```python
import flet as ft

def main(page: ft.Page):
    # Configuración de página
    page.title = "KAIROS"

    # Componentes UI
    counter = ft.Text("0", size=50)

    # Layout
    page.add(
        ft.Column([
            # Header
            # Content
            # Footer
        ])
    )

if __name__ == "__main__":
    ft.run(main)
```

### Agregar Nuevas Páginas
```python
# Crear nueva página
def home_page(page):
    page.add(ft.Text("Inicio"))

def clients_page(page):
    page.add(ft.Text("Gestión de Clientes"))

# Navegar
def navigate(page, page_name):
    page.clean()
    if page_name == "home":
        home_page(page)
    elif page_name == "clients":
        clients_page(page)
```

---

## 🐛 Troubleshooting

### "Flet no encontrado"
```bash
pip install flet>=0.86.5
```

### Puerto 8550 en uso
```bash
./run_web.sh --port 3000
```

### La aplicación no se abre automáticamente
Abre manualmente: `http://localhost:8550`

### Error de conexión con backend
- Verifica que Django está corriendo en `http://localhost:8000`
- Comprueba que CORS está habilitado
- Revisa la consola del navegador (F12 → Pestaña Network)

---

## 📚 Recursos

- **Documentación Flet**: https://flet.dev/docs
- **GitHub Flet**: https://github.com/flet-dev/flet
- **Ejemplos**: https://github.com/flet-dev/examples
- **Componentes**: https://flet.dev/docs/controls

---

## 🔄 Desarrollo

### Modo Watch (Recargar automáticamente)
```bash
flet run --web --debug
```

### Logs Detallados
```bash
python run_web.py --debug
```

---

## 📝 Próximas Fases

### Fase 2 (Frontend Mejorado)
- [ ] Integración real con API backend
- [ ] Sistema de autenticación (JWT)
- [ ] Gestión de clientes
- [ ] Gestión de procesos/expedientes
- [ ] Dashboard y reportes
- [ ] Notificaciones en tiempo real

### Fase 3 (Producción)
- [ ] Deploy en servidor
- [ ] CI/CD pipeline
- [ ] Monitoreo y logs
- [ ] Optimización de rendimiento
- [ ] Cache y offline mode

---

## 🚀 Ejecución Rápida

**La forma más simple:**

```bash
cd /home/rolando/Documentos/Kyros/frontend
./run_web.sh
```

¡Eso es todo! La aplicación se abrirá en `http://localhost:8550`

---

## 📞 Soporte

Para problemas con Flet, consulta:
- https://flet.dev/docs
- https://github.com/flet-dev/flet/issues
- https://discord.gg/hCwqxK33cn (Discord de Flet)

---

*Parte del proyecto KAIROS - Plataforma de Gestión de Procesos de Gestoría*
*Versión: 0.1.0 | Última actualización: 2026-08-13*
