"""
URL configuration for BINNA project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # مسار لوحة تحكم الإدارة الافتراضية لـ Django
    path('admin/', admin.site.urls),
    
    # مسار تطبيق تسجيل الدخول والتسجيل (binnaSign) - يغطي الصفحة الرئيسية
    path('', include('binnaSign.urls')),
    
    # مسار تطبيق لوحة تحكم الآدمن الخاص بالمنصة (binnaAdmin)
    path('binnaAdmin/', include('binnaAdmin.urls')),
    
    # مسار تطبيق لوحة تحكم العميل (binnaCustomer)
    path('binnaCustomer/', include('binnaCustomer.urls')),
    
    # مسار تطبيق لوحة تحكم مزود الخدمة/المقاول (binnaProvider)
    path('binnaProvider/', include('binnaProvider.urls')),
]

# دعم ملفات الميديا (الصور المرفوعة) والملفات الثابتة (CSS/JS) في بيئة التطوير
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)