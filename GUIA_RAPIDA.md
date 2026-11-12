# 🚀 KAIROS - Guía Rápida de Ejecución

## 📊 Estado Actual del Proyecto

```
Kyros/
├── backend/          ✅ Django API lista (Puerto 8000)
├── frontend/         ✅ Flet web app lista (Puerto 8550)
└── docs/             📋 Documentación completa
```

---

## 🎯 Ejecutar la Plataforma Completa

### 1️⃣ Iniciar Backend (Django API)

```bash
# Terminal 1: Backend
cd /home/rolando/Documentos/Kyros
source venv/bin/activate
cd backend
python manage.py runserver
```

✅ Backend disponible en: `http://localhost:8000`

### 2️⃣ Iniciar Frontend (Flet Web)

```bash
# Terminal 2: Frontend
cd /home/rolando/Documentos/Kyros/frontend
./run_web.sh
```

✅ Frontend disponible en: `http://localhost:8550`

---

## 🛠️ Métodos para Ejecutar el Frontend

### Método 1: Script Bash (MÁS SIMPLE)
```bash
cd /home/rolando/Documentos/Kyros/frontend
./run_web.sh
```

### Método 2: Script Python
```bash
cd /home/rolando/Documentos/Kyros/frontend
python run_web.py
```

### Método 3: Comando Flet Directo
```bash
cd /home/rolando/Documentos/Kyros/frontend
flet run --web
```

### Método 4: Con UV
```bash
cd /home/rolando/Documentos/Kyros/frontend
uv run flet run --web
```

---

## 🌐 URLs de Acceso

| Componente | URL | Descripción |
|-----------|-----|-------------|
| **Frontend (Flet Web)** | http://localhost:8550 | Aplicación web interactiva |
| **Backend (Django)** | http://localhost:8000 | API REST |
| **Admin Django** | http://localhost:8000/admin | Panel administrativo |
| **Landing Page** | http://localhost:8000/ | Página de bienvenida |

---

## 📝 Ejemplo de Flujo Completo

### Terminal 1: Iniciar Backend
```bash
cd /home/rolando/Documentos/Kyros
source venv/bin/activate          # Activar venv
cd backend
python manage.py runserver        # Inicia en 8000
```

Espera hasta ver:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Terminal 2: Iniciar Frontend
```bash
cd /home/rolando/Documentos/Kyros/frontend
./run_web.sh                      # Inicia en 8550
```

Verás:
```
✓ Iniciando aplicación Flet

  • Modo: WEB
  • Puerto: 8550
  • URL: http://localhost:8550
```

### Abrir en Navegador
- Frontend: `http://localhost:8550` (Se abre automáticamente)
- Backend: `http://localhost:8000` (Para ver landing)
- Admin: `http://localhost:8000/admin` (Gestionar datos)

---

## 🎮 Usar la Aplicación

### En el Frontend (http://localhost:8550)
1. Ver el contador en 0
2. Click en "+ Nuevo Proceso"
3. El contador incrementa
4. Recarga (F5) para resetear

### En el Backend Admin (http://localhost:8000/admin)
- Usuario: `admin`
- Contraseña: (la que creaste en setup)
- Crear roles, usuarios, clientes, procesos

---

## ⚙️ Puertos Personalizados

Si 8550 está en uso:
```bash
./run_web.sh --port 3000          # Frontend en puerto 3000
```

---

## 🛑 Detener las Aplicaciones

### Frontend (Web)
En Terminal 2: `Ctrl+C`

### Backend (Django)
En Terminal 1: `Ctrl+C`

---

## 📊 Estructura de Carpetas

```
/home/rolando/Documentos/Kyros/
│
├── venv/                          ← Entorno Python (3.14)
│
├── backend/
│   ├── kairos/                    ← Configuración Django
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── core/                  ← Autenticación
│   │   ├── clients/               ← Gestión de clientes
│   │   ├── processes/             ← Gestión de procesos
│   │   └── landing/               ← Página web pública
│   ├── templates/
│   │   └── landing/               ← HTML público
│   ├── manage.py
│   └── db.sqlite3                 ← Base de datos
│
├── frontend/
│   ├── src/
│   │   ├── main.py                ← App Flet
│   │   └── assets/
│   ├── run_web.sh                 ← Ejecutor Bash
│   ├── run_web.py                 ← Ejecutor Python
│   ├── pyproject.toml
│   └── README.md
│
└── docs/
    └── [documentación]
```

---

## 🔗 Integración Backend ↔ Frontend

### Frontend (Flet) → Backend (Django)

El frontend está preparado para conectarse con estos endpoints:

```
POST   /api/token/           ← Autenticación (obtener JWT)
GET    /api/user/profile/    ← Perfil del usuario actual
GET    /api/clients/         ← Listar clientes
POST   /api/clients/         ← Crear cliente
GET    /api/processes/       ← Listar procesos
POST   /api/processes/       ← Crear proceso
GET    /api/process-types/   ← Tipos de procesos
```

Próximas fases: Integrar llamadas HTTP reales en `frontend/src/main.py`

---

## 📚 Archivos Importantes

### Backend
- `backend/kairos/settings.py` - Configuración general
- `backend/kairos/urls.py` - Rutas de la API
- `backend/apps/core/models.py` - Modelos (Role, UserProfile, Audit)
- `backend/apps/clients/models.py` - Modelo Client (próxima creación)
- `backend/apps/processes/models.py` - Modelo Process (próxima creación)

### Frontend
- `frontend/src/main.py` - Aplicación Flet principal
- `frontend/run_web.sh` - Script para ejecutar como web
- `frontend/pyproject.toml` - Dependencias

### Documentación
- `README.md` - Descripción general
- `INICIO.md` - Guía de instalación y primeros pasos
- `ESTRUCTURA_PROYECTO.md` - Detalles técnicos
- `ACTUALIZACIONES_REALIZADAS.md` - Cambios recientes

---

## 🐛 Troubleshooting

### El frontend no se abre automáticamente
```bash
# Abre manualmente en el navegador:
http://localhost:8550
```

### Puerto 8550 en uso
```bash
./run_web.sh --port 3000      # Usar otro puerto
```

### Flet no encontrado
```bash
pip install flet>=0.86.5
# o
uv pip install flet>=0.86.5
```

### Backend no responde desde frontend
- Verifica que Django corre en http://localhost:8000
- Comprueba que CORS está habilitado en settings.py
- Revisa la consola del navegador (F12 → Network)

---

## 📞 Recursos

- **Documentación Django**: https://docs.djangoproject.com
- **Documentación Flet**: https://flet.dev/docs
- **API REST**: https://www.django-rest-framework.org
- **JWT Authentication**: https://django-rest-framework-simplejwt.readthedocs.io

---

## ✅ Checklist para Empezar

- [ ] Leer esta guía
- [ ] Abrir 2 terminales
- [ ] Terminal 1: `cd Kyros && source venv/bin/activate && cd backend && python manage.py runserver`
- [ ] Terminal 2: `cd Kyros/frontend && ./run_web.sh`
- [ ] Abrir http://localhost:8550 en navegador
- [ ] ¡Disfrutar! 🎉

---

## 🎯 Próximas Fases

**Fase 1 (Actual)**: MVP de gestoría
- ✅ Backend API (Django)
- ✅ Frontend web (Flet)
- ⏳ Integración real de APIs

**Fase 2**: Funcionalidades completas
- [ ] Autenticación JWT en frontend
- [ ] Gestión real de clientes
- [ ] Gestión real de procesos
- [ ] Dashboard y reportes

**Fase 3**: Producción
- [ ] Deploy en servidor
- [ ] Database PostgreSQL
- [ ] Monitoreo y logs
- [ ] Optimización

---

**KAIROS - Plataforma de Gestión de Procesos de Gestoría**
*Última actualización: 2026-08-13*
*Versión: 0.1.0*
