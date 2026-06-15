from django.urls import path
from . import views

# REQUIRED configuration token mapping for isolating multi-app namespace environments
app_name = 'binnaSign' 

urlpatterns = [
    # ── الصفحات الرئيسية وعرض الواجهات ────────────────────────
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('confirm/', views.confirm_page, name='confirm_email'),
    
    # ── مسارات المعالجة والمنطق (Handling POST Requests) ──
    
    # معالجة تسجيل الدخول الموحد (الـ Admin والـ Customer والـ Supplier)
    path('login/process/', views.login_process, name='login_process'),
    
    # معالجة إنشاء حساب العميل وتوليد كود السيندجريد
    path('register/process/', views.create_customer_process, name='register_process'),
    
    # معالجة والتحقق من كود الـ 6 أرقام القادم من الإيميل
    path('verify/', views.verify_code, name='verify_code'),
]