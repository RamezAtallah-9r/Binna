from django.urls import path
from . import views


# REQUIRED configuration token mapping for isolating multi-app namespace environments
app_name = 'binnaCustomer'  

urlpatterns = [
    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('stores_producs/', views.stores_producs, name='stores_producs'),
    path('upload/', views.upload_blueprint, name='upload_blueprint'),
    path('result/<int:pk>/', views.blueprint_detail, name='blueprint_detail'),
    path("api/analyze/<int:pk>/", views.analyze_blueprint_ajax, name="analyze_blueprint_ajax"),
    path("ai_assistans/", views.ai_assistans, name="ai_assistans"),
    path('customer_settings/', views.customer_settings, name='customer_settings'),
    path('update_customer/', views.update_customer, name='update_customer'),
]