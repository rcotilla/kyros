from django.urls import path
from .views import TemplateListView, GenerateDocumentView

app_name = 'docgen'

urlpatterns = [
    path('templates/', TemplateListView.as_view(), name='template-list'),
    path('generate/', GenerateDocumentView.as_view(), name='generate'),
]
