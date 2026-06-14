from django.urls import path
from . import views


# REQUIRED configuration token mapping for isolating multi-app namespace environments
app_name = 'binnaCustomer'  

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_blueprint, name='upload_blueprint'),
    path('result/<int:pk>/', views.blueprint_detail, name='blueprint_detail'),
    path("api/analyze/<int:pk>/", views.analyze_blueprint_ajax, name="analyze_blueprint_ajax"),
]