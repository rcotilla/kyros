# 📋 Estructura del Proyecto KAIROS

## Arquitectura General

```
kyros/
├── backend/                          # Backend Django
│   ├── kairos/                       # Configuración del proyecto
│   │   ├── settings.py              # Configuración principal
│   │   ├── urls.py                  # URLs principales
│   │   └── wsgi.py                  # WSGI
│   │
│   ├── apps/                         # Aplicaciones Django
│   │   ├── landing/                  # Página pública y autenticación
│   │   │   ├── models.py           # ContactMessage
│   │   │   ├── views.py            # LandingView, ContactView, LoginView, LogoutView
│   │   │   └── urls.py            # /, /contacto, /login, /logout
│   │   │
│   │   ├── clients/                  # Gestión de clientes
│   │   │   ├── models.py           # Client (NIF, contacto, dirección)
│   │   │   ├── serializers.py      # API REST
│   │   │   ├── views.py            # API ViewSet
│   │   │   └── urls.py            # /api/v1/clients/
│   │   │
│   │   ├── processes/                # Gestión de procesos/expedientes
│   │   │   ├── models.py           # ProcessType, Process, ProcessStep
│   │   │   ├── serializers.py      # API REST
│   │   │   ├── views.py            # API ViewSet + PDF endpoint
│   │   │   └── urls.py            # /api/v1/processes/
│   │   │
│   │   ├── documents/                # Gestión documental
│   │   │   ├── models.py           # Document (vinculado a Client + Process)
│   │   │   ├── serializers.py      # API REST
│   │   │   ├── views.py            # API ViewSet
│   │   │   └── urls.py            # /api/v1/documents/
│   │   │
│   │   ├── tasks/                    # Gestión de tareas
│   │   │   ├── models.py           # Task, TaskComment
│   │   │   ├── serializers.py      # API REST
│   │   │   ├── views.py            # API ViewSet
│   │   │   └── urls.py            # /api/v1/tasks/
│   │   │
│   │   └── panel/                    # Vistas de trabajo por rol
│   │       ├── views.py            # GestorRequiredMixin + vistas por rol
│   │       ├── forms.py            # Formularios CRUD
│   │       └── urls.py            # /panel/*
│   │
│   ├── pdf_service/                  # Generación de PDFs
│   │   ├── __init__.py             # PDFGenerator class
│   │   └── templates/pdf/          # Templates WeasyPrint
│   │       ├── base.html           # Estilos base PDF
│   │       ├── process_summary.html
│   │       └── client_report.html
│   │
│   ├── templates/                    # Templates HTML
│   │   ├── base.html                # Base landing + modal login
│   │   ├── landing/
│   │   │   ├── home.html           # Landing page
│   │   │   └── contacto.html       # Formulario contacto
│   │   └── panel/
│   │       ├── base_panel.html     # Base para vistas de trabajo
│   │       ├── gestor/             # Vistas del gestor
│   │       │   ├── home.html       # Resumen con estadísticas
│   │       │   ├── client_list.html
│   │       │   ├── client_form.html
│   │       │   ├── client_detail.html
│   │       │   ├── process_list.html
│   │       │   ├── process_form.html
│   │       │   ├── process_detail.html
│   │       │   ├── document_list.html
│   │       │   └── document_upload.html
│   │       ├── operator/           # Vistas del operador
│   │       │   ├── home.html       # Lista de tareas
│   │       │   ├── task_detail.html
│   │       │   └── document_upload.html
│   │       └── client/             # Vistas del cliente
│   │           ├── home.html       # Sus procesos
│   │           ├── process_detail.html
│   │           └── profile.html
│   │
│   ├── static/                       # Archivos estáticos
│   │   └── css/
│   │       └── styles.css           # Estilos globales
│   │
│   └── manage.py
│
├── frontend/                         # Frontend React (opcional)
│   └── package.json
│
├── docs/                             # Documentación
│   ├── API_REFERENCE.md
│   ├── DEPLOYMENT.md
│   ├── FLUJOS_USUARIO.md
│   └── ESTRUCTURA_PROYECTO.md       # Este archivo
│
├── .env                             # Variables de entorno
├── requirements.txt                  # Dependencias Python
└── README.md
```

## Modelos Principales

### Client (clients/models.py)
- **Campos**: document_type, document_number, first_name, last_name, email, phone, address, city, province, status
- **Relaciones**: assigned_to (User), created_by (User)
- **Propiedades**: full_name, document_display

### Process (processes/models.py)
- **Campos**: file_number (auto: EXP-XXXXX), title, description, status, priority, start_date, due_date
- **Relaciones**: process_type (ProcessType), client (Client), gestor (User), operator (User)
- **Estados**: draft → pending → in_progress → review → waiting_client → submitted → approved → completed → closed
- **Prioridades**: low, medium, high, urgent

### ProcessType (processes/models.py)
- **Categorías**: extranjeria, marcas, constituciones, contabilidad, legal, otro
- **Ejemplos**: Extranjería, Marcas y Patentes, Constituciones, Contabilidad, Asesoría Legal

### ProcessStep (processes/models.py)
- **Campos**: name, description, order, status, assigned_to, due_date
- **Estados**: pending → in_progress → completed → skipped

### Document (documents/models.py)
- **Campos**: title, description, file, doc_type, is_public
- **Relaciones**: client (Client), process (Process), uploaded_by (User)
- **Tipos**: identification, contract, form, certificate, receipt, legal, other

## API REST

Todos los endpoints están bajo `/api/v1/`:

| Endpoint | Métodos | Descripción |
|----------|---------|-------------|
| `/api/v1/auth/` | POST | Login JWT |
| `/api/v1/clients/` | CRUD | Clientes |
| `/api/v1/processes/` | CRUD | Procesos + PDF |
| `/api/v1/documents/` | CRUD | Documentos |
| `/api/v1/tasks/` | CRUD | Tareas |

### PDFs
- `GET /api/v1/processes/{id}/pdf/` → Resumen del proceso
- `GET /api/v1/clients/{id}/pdf/` → Reporte del cliente

## Vistas de Trabajo (panel/)

### Gestor (/panel/)
- **Resumen**: estadísticas de clientes, procesos, documentos
- **Clientes**: CRUD completo con búsqueda
- **Procesos**: CRUD con filtros por estado/prioridad
- **Documentos**: lista y subida

### Operador (/panel/operador/)
- **Tareas**: lista pendientes/en progreso
- **Detalle tarea**: actualizar estado, subir documentos
- **Subir documento**: formulario directo

### Cliente (/panel/cliente/)
- **Mis procesos**: lista de procesos del cliente
- **Detalle proceso**: información, avance, documentos
- **Mi perfil**: datos del cliente

## Flujo de Autenticación

1. **Landing page** → Modal login → POST /login/
2. **Redirect por rol**:
   - admin/manager → /panel/
   - operator → /panel/operador/
   - client → /panel/cliente/
3. **Logout** → /logout/ → Landing page

## Configuración

- **Servidor**: `python manage.py runserver 0.0.0.0:8001`
- **Base de datos**: SQLite (kairos/db.sqlite3)
- **Variables de entorno**: .env (SECRET_KEY, DEBUG, ALLOWED_HOSTS)
- **PDFs**: WeasyPrint
- **Auth**: Session-based (web), JWT disponible (API/mobile)
