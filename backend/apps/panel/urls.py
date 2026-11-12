"""URL configuration for panel app — working views."""

from django.urls import path
from .views import (
    # Gestor
    GestorHomeView,
    GestorClientListView, GestorClientCreateView,
    GestorClientDetailView, GestorClientEditView,
    GestorProcessListView, GestorProcessCreateView,
    GestorProcessDetailView, GestorProcessEditView,
    GestorProcessAddStepView, GestorProcessUpdateStepView,
    GestorProcessDeleteStepView, GestorProcessStepsUpdateView,
    GestorProcessDeleteView,
    GestorDocumentListView, GestorDocumentUploadView,
    GestorDocumentDeleteView, GestorDocumentGenerationView,
    # Templates
    GestorTemplateListView, GestorTemplateCreateView,
    GestorTemplateDetailView, GestorTemplateEditView,
    GestorTemplateAddStepView, GestorTemplateDeleteStepView,
    # Operator
    OperatorHomeView, OperatorTaskDetailView,
    OperatorDocumentUploadView,
    # Client
    ClientHomeView, ClientProcessDetailView, ClientProfileView,
)

app_name = 'panel'

urlpatterns = [
    # --- Gestor / Admin ---
    path('', GestorHomeView.as_view(), name='home'),

    # Clients
    path('clientes/', GestorClientListView.as_view(), name='gestor_clients'),
    path('clientes/nuevo/', GestorClientCreateView.as_view(), name='gestor_client_create'),
    path('clientes/<int:pk>/', GestorClientDetailView.as_view(), name='gestor_client_detail'),
    path('clientes/<int:pk>/editar/', GestorClientEditView.as_view(), name='gestor_client_edit'),

    # Processes
    path('procesos/', GestorProcessListView.as_view(), name='gestor_processes'),
    path('procesos/nuevo/', GestorProcessCreateView.as_view(), name='gestor_process_create'),
    path('procesos/<int:pk>/', GestorProcessDetailView.as_view(), name='gestor_process_detail'),
    path('procesos/<int:pk>/editar/', GestorProcessEditView.as_view(), name='gestor_process_edit'),
    path('procesos/<int:pk>/pasos/nuevo/', GestorProcessAddStepView.as_view(), name='gestor_process_add_step'),
    path('procesos/<int:process_pk>/pasos/<int:step_pk>/actualizar/', GestorProcessUpdateStepView.as_view(), name='gestor_process_update_step'),
    path('procesos/<int:process_pk>/pasos/<int:step_pk>/eliminar/', GestorProcessDeleteStepView.as_view(), name='gestor_process_delete_step'),
    path('procesos/<int:pk>/pasos/actualizar/', GestorProcessStepsUpdateView.as_view(), name='gestor_process_steps_update'),
    path('procesos/<int:pk>/eliminar/', GestorProcessDeleteView.as_view(), name='gestor_process_delete'),

    # Documents (accessed from process detail, not sidebar)
    path('documentos/', GestorDocumentListView.as_view(), name='gestor_documents'),
    path('documentos/subir/', GestorDocumentUploadView.as_view(), name='gestor_document_upload'),
    path('documentos/<int:pk>/eliminar/', GestorDocumentDeleteView.as_view(), name='gestor_document_delete'),

    # Document generation (contracts, letters, etc.)
    path('documentos/generar/', GestorDocumentGenerationView.as_view(), name='gestor_document_generation'),

    # Process Templates
    path('plantillas/', GestorTemplateListView.as_view(), name='gestor_templates'),
    path('plantillas/nueva/', GestorTemplateCreateView.as_view(), name='gestor_template_create'),
    path('plantillas/<int:pk>/', GestorTemplateDetailView.as_view(), name='gestor_template_detail'),
    path('plantillas/<int:pk>/editar/', GestorTemplateEditView.as_view(), name='gestor_template_edit'),
    path('plantillas/<int:pk>/pasos/nuevo/', GestorTemplateAddStepView.as_view(), name='gestor_template_add_step'),
    path('plantillas/<int:template_pk>/pasos/<int:step_pk>/eliminar/', GestorTemplateDeleteStepView.as_view(), name='gestor_template_delete_step'),

    # --- Operator ---
    path('operador/', OperatorHomeView.as_view(), name='operator_home'),
    path('operador/tareas/<int:pk>/', OperatorTaskDetailView.as_view(), name='operator_task_detail'),
    path('operador/tareas/<int:pk>/actualizar/', OperatorTaskDetailView.as_view(), name='operator_task_update'),
    path('operador/documentos/subir/', OperatorDocumentUploadView.as_view(), name='operator_document_upload'),

    # --- Client ---
    path('mis-procesos/', ClientHomeView.as_view(), name='client_home'),
    path('mis-procesos/<int:pk>/', ClientProcessDetailView.as_view(), name='client_process_detail'),
    path('mi-perfil/', ClientProfileView.as_view(), name='client_profile'),
]
