# KAIROS - Plataforma de Gestión de Procesos de Gestoría

Plataforma profesional para la gestión integral de procesos de gestoría: extranjería, marcas, constituciones y otros trámites. Construida con **Python Full-Stack**.

## 🎯 Objetivo

Facilitar la gestión de expedientes y procesos de gestoría a través de una plataforma modular y escalable, con roles diferenciados (Cliente, Gestor, Administrativo) y seguimiento integral de trámites.

## 🏗️ Estructura del Proyecto

```
Kyros/
├── venv/                    # Entorno virtual Python
├── backend/                 # Proyecto Django
│   ├── kairos/             # Configuración del proyecto
│   ├── apps/               # Aplicaciones Django
│   │   ├── core/           # Autenticación y usuarios
│   │   ├── documents/      # Gestión de documentos
│   │   ├── tasks/          # Gestión de tareas
│   │   └── landing/        # Landing page
│   ├── templates/          # Templates HTML
│   ├── static/             # Archivos estáticos (CSS, JS, imágenes)
│   ├── media/              # Archivos subidos por usuarios
│   ├── logs/               # Logs de la aplicación
│   ├── manage.py           # Utilidad de gestión de Django
│   └── db.sqlite3          # Base de datos (desarrollo)
├── frontend/               # App Flet (Fase 2)
├── docs/                   # Documentación del proyecto
├── requirements.txt        # Dependencias Python
├── setup.sh               # Script de inicialización
├── .gitignore             # Archivos a ignorar en git
└── hoja_de_ruta.txt       # Especificación del proyecto
```

## 📋 Fase de Desarrollo

### Fase 1: MVP - Gestión de Procesos (✅ ACTIVA)
- [x] Estructura Django inicial
- [x] Modelos: User, Role, UserProfile, Audit
- [x] Modelos: Client, Process, ProcessType
- [x] Landing page con Bootstrap
- [x] Django Admin configurado
- [ ] API REST para procesos
- [ ] Autenticación JWT
- [ ] Vistas por rol: Cliente, Gestor, Administrativo

#### Fases Futuras (Documentadas, no activas en Fase 1)
- **Fase 2**: Portal web interactivo + Notificaciones
- **Fase 3**: Automatización avanzada, PDFs, almacenamiento cloud

*Nota: Las Fases 2 y 3 se implementarán de forma incremental. Por ahora, enfoque en Fase 1.*

## 🚀 Instalación y Setup

### Prerrequisitos
- Python 3.10+
- pip
- git

### Pasos de Instalación

#### 1. Clonar/Descargar el proyecto
```bash
cd /home/rolando/Documentos/Kyros
```

#### 2. Activar el entorno virtual
```bash
source venv/bin/activate
```

#### 3. Instalar dependencias (cuando haya conexión a internet)
```bash
pip install -r requirements.txt
```

#### 4. Realizar migraciones de base de datos
```bash
cd backend
python manage.py migrate
```

#### 5. Crear superusuario (admin)
```bash
python manage.py createsuperuser
```

Sigue los pasos y proporciona:
- Username: (ej: admin)
- Email: (ej: admin@kairos.local)
- Password: (ej: secreto123)

#### 6. Inicializar datos de Fase 1
```bash
python manage.py loaddata initial_roles
```

#### 7. Ejecutar servidor de desarrollo
```bash
python manage.py runserver
```

El servidor estará disponible en: http://localhost:8000

## 📚 Acceso a la Aplicación

### Landing Page
- **URL**: http://localhost:8000/
- **Descripción**: Página pública de bienvenida

### Django Admin (Panel de Administración)
- **URL**: http://localhost:8000/admin/
- **Usuario**: admin
- **Contraseña**: (la que configuraste en createsuperuser)

### API REST (Fase 1)
- **Base URL**: http://localhost:8000/api/
- **Endpoints**:
  - `POST /api/token/` - Obtener token JWT con credenciales
  - `GET /api/user/profile/` - Perfil del usuario actual
  - `GET /api/roles/` - Listar roles disponibles
  - `GET /api/clients/` - Listar clientes (según permisos)
  - `POST /api/clients/` - Crear nuevo cliente
  - `GET /api/processes/` - Listar procesos/expedientes
  - `POST /api/processes/` - Crear nuevo proceso
  - `GET /api/process-types/` - Tipos de procesos (Extranjería, Marcas, etc)

## 🔧 Configuración

### Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:

```env
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Email (para Fase 3)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña

# AWS S3 (para Fase 3)
USE_S3=False
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
```

## 📝 Roles y Permisos (Fase 1)

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **Cliente** | Solicitante de trámites | Ver propios procesos, contactar gestor, descargar documentos |
| **Gestor** | Gestor profesional | Ver todos los procesos, gestionar clientes, crear expedientes, asignar tareas |
| **Administrativo** | Soporte administrativo | Datos de clientes, documentación, reportes, soporte general |
| **Admin** | Administrador del sistema | Acceso total a Django Admin, configuración, usuarios |

## 🛠️ Desarrollo

### Crear una nueva aplicación Django
```bash
cd backend
python manage.py startapp nombre_app
```

### Crear migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### Limpiar caché y archivos temporales
```bash
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

## 🧪 Testing (Fase 2)

```bash
pytest backend/
pytest backend/apps/core/tests.py -v
```

## 📦 Dependencias Principales (Fase 1)

- **Django 5.1** - Framework web
- **djangorestframework** - API REST
- **django-cors-headers** - CORS support
- **djangorestframework-simplejwt** - Autenticación JWT
- **psycopg2-binary** - Driver PostgreSQL
- **django-environ** - Gestión de variables de entorno

Ver `requirements.txt` para la lista completa.

## 🚢 Deployment (Producción)

### Usando Gunicorn + Nginx

1. Configurar variables de entorno en producción
2. Ejecutar migraciones
3. Recopilar archivos estáticos: `python manage.py collectstatic`
4. Iniciar Gunicorn: `gunicorn kairos.wsgi:application --bind 0.0.0.0:8000`
5. Configurar Nginx como proxy inverso

## 📖 Documentación Adicional

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Flet Documentation](https://flet.dev/) (para Fase 2)

## 🤝 Contribución

Este es un proyecto en desarrollo. Las contribuciones son bienvenidas.

## 📄 Licencia

Proyecto privado - KAIROS 2024

## 👥 Contacto

- Email: info@kairos.local
- Teléfono: +54 (11) 0000-0000

---

**Estado Actual**: Fase 1 en progreso - Estructura base completa, pendiente instalación de dependencias y pruebas.
