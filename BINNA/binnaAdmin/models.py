from django.db import models
import bcrypt
import re

class AdminManager(models.Manager):
    def admin_login_validator(self, postData):
        """التحقق من صحة صيغة المدخلات أثناء عملية تسجيل الدخول"""
        errors = {}
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        
        if not EMAIL_REGEX.match(postData.get('email', '')):
            errors['email'] = "يرجى إدخال بريد إلكتروني بصيغة صحيحة."
            
        if len(postData.get('password', '')) < 8:
            errors['password'] = "كلمة المرور يجب أن لا تقل عن 8 خانات."
            
        return errors

    def create_admin(self, cleaned_data):
        """تشفير كلمة المرور تلقائياً وحفظ حساب الأدمن الجديد يدويًا في قاعدة البيانات"""
        # 🔒 تشفير كلمة المرور الصافية باستخدام bcrypt وتحويلها لسلسلة نصية
        hashed_pw = bcrypt.hashpw(cleaned_data['password'].encode(), bcrypt.gensalt()).decode()
        
        return self.create(
            full_name=cleaned_data['full_name'],
            email=cleaned_data['email'],
            password=hashed_pw,
            role=cleaned_data.get('role', 'SuperAdmin') # القيمة الافتراضية هي مدير خارق
        )

class ProjectAdmin(models.Model):
    """الموديل المسؤول عن تخزين بيانات مدراء ومسؤولي منصة بِنَاءْ"""
    full_name = models.CharField(max_length=150) # 👈 تم التعديل هنا
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # 👈 تم التعديل هنا
    role = models.CharField(max_length=50, default="SuperAdmin") # 👈 تم التعديل هنا لتفادي سطر 36
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AdminManager()

    def __str__(self):
        return f"{self.full_name} ({self.role})"