from django.urls import path
from . import views

# REQUIRED configuration token mapping for isolating multi-app namespace environments
app_name = 'binnaAdmin'  

urlpatterns = [
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
]