from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.urls import reverse
from .models import *
import random
from django.core.mail import send_mail

import bcrypt
# استيراد موديل Customer من التطبيق الآخر
from binnaCustomer.models import Customer 

# ── دوال العرض (Rendering Only) ──────────────────────────

def index(request):
    return render(request, 'signhtml/index.html')

def login(request):
    return render(request, 'signhtml/login.html')

def register(request):
    return render(request, 'signhtml/signup.html')

# ── دوال المعالجة (Logic & Process Only) ──────────────────

def create_customer_process(request):
    if request.method == "POST":
        # 1. التحقق من البيانات (نفس الكود السابق)
        errors = Customer.objects.registration_validator(request.POST)
        if errors:
            for key, val in errors.items(): messages.error(request, val)
            return redirect('binnaSign:register')
        
        # 2. توليد كود عشوائي وتخزينه في الـ Session
        code = str(random.randint(100000, 999999))
        request.session['verification_code'] = code
        request.session['temp_customer_data'] = request.POST # تخزين مؤقت للبيانات
        
        # 3. إرسال الإيميل (استخدم Email.js أو Django mail)
        # ملاحظة: إذا كنت تصر على Email.js (Frontend)، ستحتاج تمرير الكود للـ Template
        # لكن الأفضل إرساله من Django مباشرة:
        send_mail('رمز التحقق من بناء', f'كود التحقق الخاص بك هو: {code}', 
                  'your-email@binna.com', [request.POST['email']])
        
        return redirect('binnaSign:confirm_email')

def login_process(request):
    """معالجة بيانات تسجيل الدخول"""
    if request.method == "POST":
        customer = Customer.objects.filter(email=request.POST['email']).first()
        
        # التحقق من كلمة المرور
        if customer and bcrypt.checkpw(request.POST['password'].encode(), customer.password.encode()):
            request.session['customer_id'] = customer.id
            return redirect('binnaCustomer:index')
        
        messages.error(request, "Invalid Email or Password")
        return redirect('binnaSign:login')
        
    return redirect('binnaSign:login')

def verify_code(request):
    if request.method == "POST":
        user_code = request.POST.get('code')
        session_code = request.session.get('verification_code')
        
        if user_code == session_code:
            # البيانات صحيحة، الآن نقوم بإنشاء العميل فعلياً
            data = request.session.get('temp_customer_data')
            new_customer = Customer.objects.create_customer(data)
            
            # تنظيف الـ Session
            del request.session['verification_code']
            del request.session['temp_customer_data']
            
            request.session['customer_id'] = new_customer.id
            return redirect('binnaCustomer:dashboard') # المسار الصحيح للوحة التحكم
        else:
            messages.error(request, "الكود غير صحيح، حاول مجدداً")
            return redirect('binnaSign:confirm_email')