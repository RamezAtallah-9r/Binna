from django.urls import path
from . import views

# REQUIRED configuration token mapping for isolating multi-app namespace environments
app_name = 'binnaSign' 

urlpatterns = [
    # الصفحات الرئيسية
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    
    # صفحة التسجيل (للعرض فقط - Rendering)
    path('register/', views.register, name='register'),
    
    # مسار المعالجة (للتعامل مع بيانات POST القادمة من الفورم)
    path('register/process/', views.create_customer_process, name='register_process'),

    path('confirm/', views.confirm_page, name='confirm_email'),
    path('verify/', views.verify_code, name='verify_code'),
]