from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from .models import *
import random
import bcrypt

# ── استيراد الموديلات من التطبيقات المختلفة لربط البوابة المركزية ──
from binnaCustomer.models import Customer 
from binnaAdmin.models import ProjectAdmin
# ملاحظة: عندما تفتح تطبيق الموردين وتنشئ الموديل الخاص بهم، قم بفك التعليق عن السطر التالي:
# from binnaSupplyer.models import Supplier 

# ── دوال العرض (Rendering Only) ──────────────────────────

def index(request):
    return render(request, 'signhtml/index.html')

def login(request):
    return render(request, 'signhtml/login.html')

def register(request):
    return render(request, 'signhtml/signup.html')

def confirm_page(request):
    """عرض صفحة إدخال رمز التحقق (confirm.html)"""
    if 'verification_code' not in request.session:
        messages.error(request, "يرجى تسجيل حسابك أولاً لإرسال رمز التحقق.")
        return redirect('binnaSign:register')
    return render(request, 'signhtml/confirm.html')


# ── دوال المعالجة والمنطق (Logic & Process Only) ──────────

def create_customer_process(request):
    """معالجة بيانات نموذج التسجيل وتوليد رمز التحقق وإرساله عبر SendGrid"""
    if request.method == "POST":
        # 1. التحقق من البيانات باستخدام الـ Validator
        errors = Customer.objects.registration_validator(request.POST)
        if errors:
            for key, val in errors.items(): 
                messages.error(request, val)
            return redirect('binnaSign:register')
        
        # 2. توليد كود عشوائي من 6 أرقام وتخزينه في الـ Session
        code = str(random.randint(100000, 999999))
        request.session['verification_code'] = code
        request.session['temp_customer_data'] = request.POST.dict() 
        
        # 3. إرسال البريد الإلكتروني عبر قوالب SendGrid الديناميكية
        try:
            mail = EmailMultiAlternatives(
                subject='رمز التحقق الخاص بمنصة بناء - BINNA',
                body=' ', 
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[request.POST['email']]
            )
            
            mail.content_subtype = 'html'
            mail.template_id = 'd-098966f179df44e9b03c16c451870978' 
            
            mail.dynamic_template_data = {
                'code': code,
                'Sender_Name': 'بِنَاءْ',
                'Sender_Address': 'فلسطين',
                'Sender_City': 'نابلس',
                'Sender_State': 'الضفة الغربية',
                'Sender_Zip': '00970'
            }
            
            mail.send(fail_silently=False)
            return redirect('binnaSign:confirm_email')
            
        except Exception as e:
            print("================ SENDGRID ERROR ================")
            print(str(e))
            print("================================================")
            messages.error(request, "حدث خطأ أثناء إرسال كود التحقق، يرجى المحاولة لاحقاً.")
            return redirect('binnaSign:register')
            
    return redirect('binnaSign:register')


def verify_code(request):
    """التحقق من الكود المدخل وإنشاء الحساب الفعلي في قاعدة البيانات"""
    if request.method == "POST":
        user_code = request.POST.get('code')
        session_code = request.session.get('verification_code')
        temp_data = request.session.get('temp_customer_data')
        
        if user_code == session_code and temp_data:
            try:
                cleaned_data = {
                    'first_name': temp_data.get('first_name'),
                    'last_name': temp_data.get('last_name'),
                    'city': temp_data.get('city'),
                    'email': temp_data.get('email'),
                    'phone': temp_data.get('phone'),
                    'password': temp_data.get('password'),
                }

                Customer.objects.create_customer(cleaned_data)
                
                del request.session['verification_code']
                del request.session['temp_customer_data']
                
                messages.success(request, "تم تفعيل حسابك بنجاح! يرجى تسجيل الدخول للولوج إلى لوحة تحكم بناء.")
                return redirect('binnaSign:login')
                
            except Exception as e:
                print("================ DATABASE ERROR ================")
                print(str(e))
                print("================================================")
                messages.error(request, "حدث خطأ أثناء إنشاء الحساب، يرجى إعادة المحاولة.")
                return redirect('binnaSign:register')
        else:
            messages.error(request, "رمز التحقق غير صحيح، يرجى التأكد وإعادة المحاولة.")
            return redirect('binnaSign:confirm_email')
            
    return redirect('binnaSign:register')


def login_process(request):
    """🚀 التحديث: بوابة الدخول الموحدة لتوجيه المستخدمين برمجياً حسب نوع الحساب"""
    if request.method == "POST":
        email_input = request.POST.get('email')
        password_input = request.POST.get('password')

        # ── 🛡️ الفحص الأول: هل الحساب مخصّص للمسؤولين (ProjectAdmin)؟ ──
        admin_user = ProjectAdmin.objects.filter(email=email_input).first()
        if admin_user and bcrypt.checkpw(password_input.encode(), admin_user.password.encode()):
            request.session.flush()  # تصفير أي جلسات سابقة لضمان أمان الصلاحيات
            request.session['admin_id'] = admin_user.id
            request.session['user_role'] = 'admin'
            messages.success(request, f"مرحباً بك يا مهندس {admin_user.full_name} في غرفة التحكم.")
            return redirect('binnaAdmin:admin_dashboard')

        # ── 👷 الفحص الثاني: هل الحساب مخصّص للعملاء (Customer)؟ ──
        customer_user = Customer.objects.filter(email=email_input).first()
        if customer_user and bcrypt.checkpw(password_input.encode(), customer_user.password.encode()):
            request.session.flush()
            request.session['customer_id'] = customer_user.id
            request.session['user_role'] = 'customer'
            messages.success(request, f"أهلاً بك مجدداً، {customer_user.first_name}!")
            return redirect('binnaCustomer:customer_dashboard')

        # ── 🚛 الفحص الثالث: هل الحساب مخصّص للموردين (Supplier)؟ ──
        # ملاحظة: بمجرد تجهيز تطبيق وموديل الموردين، قم بفك التعليق لتفعيله تلقائياً:
        """
        supplier_user = Supplier.objects.filter(email=email_input).first()
        if supplier_user and bcrypt.checkpw(password_input.encode(), supplier_user.password.encode()):
            request.session.flush()
            request.session['supplier_id'] = supplier_user.id
            request.session['user_role'] = 'supplier'
            messages.success(request, f"مرحباً بك شريكنا المورد، {supplier_user.company_name}!")
            return redirect('binnaSupplyer:supplier_dashboard')
        """

        # ── ❌ الفحص الرابع: المدخلات لم تطابق أي حساب ──
        messages.error(request, "البريد الإلكتروني أو كلمة المرور غير صحيحة.")
        return redirect('binnaSign:login')
        
    return redirect('binnaSign:login')