import re
import time
import threading
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib import messages  
from .models import *
from django.db.models import Q
from google import genai
from PIL import Image
from dotenv import load_dotenv
from binnaProvider.models import Supplier, Inventory, SupplierCategory, InventoryCategory, City
import bcrypt

load_dotenv()

# ── Gemini settings ────────────────────────────────────────────────────────
# binnaCustomer/views.py في الأعلى تماماً
GEMINI_MODEL = "gemini-3.5-flash"
GEMINI_MAX_RETRIES = 6                 # زيادة المحاولات لمنع قيود 503 اللحظية
GEMINI_RETRY_DELAY = 8                 # وقت الانتظار بالثواني بين المحاولات

GEMINI_PROMPT = """
You are a Senior Civil Engineer based in Palestine.

Analyze this building blueprint and estimate all construction materials.

Rules:
- Use metric units.
- Ceiling height = 4.0 meters.
- Exterior blocks = 40×20×20 cm.
- Interior blocks = 40×20×10 cm.
- Structural concrete = B300.
- Apply local Palestinian assumptions.

Structure your response in two clear parts:

PART 1 — CALCULATIONS
Show each calculation step clearly under these headings (use these exact headings):
## الأبعاد والمساحات
## الطوب الخارجي
## الطوب الداخلي
## الخرسانة
## الأسمنت
## حديد التسليح

Under each heading, show: what you measured, the formula used, and the result.
Keep each step on its own line. Be concise — one line per step.

PART 2 — SUMMARY
At the END return EXACTLY this format (one line per material, no extra text):

Summary of Estimated Construction Materials:

* MaterialRow: [Type] || [Specification] || [Quantity] || [Unit]

Example:
* MaterialRow: طوب || طوب خارجي 40x20x20 سم || 3500 || طوبة
* MaterialRow: أسمنت || أسمنت B300 || 420 || كيس
* MaterialRow: حديد || حديد تسليح || 1260 || كغم
"""


# ── Helpers ────────────────────────────────────────────────────────────────

def _parse_result(analysis_text):
    """
    تحليل النص الخام القادم من Gemini وتحويله إلى بيانات مهيكلة لمصفوفات الواجهة.
    """
    material_rows = []
    for line in analysis_text.splitlines():
        if "MaterialRow:" in line and "||" in line:
            clean = re.sub(r'^[*\s\-]*MaterialRow:\s*', '', line, flags=re.IGNORECASE).strip()
            parts = [p.strip() for p in clean.split("||")]
            if len(parts) >= 4:
                material_rows.append({
                    "type": parts[0],
                    "name": parts[1],
                    "qty":  parts[2],
                    "unit": parts[3],
                })

    calc_text = re.split(r'Summary of Estimated', analysis_text, flags=re.IGNORECASE)[0].strip()

    sections = []
    pattern  = re.compile(r'##\s*(.+?)\n(.*?)(?=##|\Z)', re.DOTALL)
    for match in pattern.finditer(calc_text):
        heading = match.group(1).strip()
        steps   = [l.strip() for l in match.group(2).strip().splitlines() if l.strip()]
        if steps:
            sections.append({"heading": heading, "steps": steps})

    return material_rows, sections


def _run_gemini(blueprint):
    """
    تشغيل عملية التحليل في دالة منفصلة (Thread) بالخلفية لضمان استقرار استجابة السيرفر.
    """
    import os  

    def _save_error(msg):
        blueprint.analysis_result = f"ERROR:{msg}"
        blueprint.save()

    try:
        pil_image = Image.open(blueprint.image.path)
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("🚨 لم يتم العثور على GEMINI_API_KEY داخل ملف الـ .env")
            
        client = genai.Client(api_key=api_key)
        
    except Exception as e:
        print("================ GEMINI INIT ERROR ================")
        print(str(e))
        print("===================================================")
        _save_error(f"فشل تهيئة المحرك: {str(e)}")
        return

    for attempt in range(1, GEMINI_MAX_RETRIES + 1):
        try:
            print(f"🔄 محاولة جلب التحليل من Gemini (المحاولة {attempt} من {GEMINI_MAX_RETRIES})...")
            
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[pil_image, GEMINI_PROMPT]
            )
            
            if response.text:
                blueprint.analysis_result = response.text
                blueprint.save()
                print("✅ تم تحليل المخطط بنجاح واستلام البيانات من Gemini!")
                return   # خروج بنجاح عند استلام الحسابات الإنشائية
            else:
                raise ValueError("أرجع المحرك استجابة فارغة.")

        except Exception as e:
            error_str = str(e)
            print(f"⚠️ خطأ أثناء المحاولة {attempt}: {error_str}")
            
            is_503 = "503" in error_str or "UNAVAILABLE" in error_str or "ResourceExhausted" in error_str

            if is_503 and attempt < GEMINI_MAX_RETRIES:
                print(f"⏱️ السيرفر مشغول (503). جاري إيقاف الـ Thread مؤقتاً لـ {GEMINI_RETRY_DELAY} ثوانٍ...")
                time.sleep(GEMINI_RETRY_DELAY)
                continue

            print("================ GEMINI RUNTIME ERROR ================")
            print(error_str)
            print("======================================================")
            _save_error(error_str)
            return

    _save_error("فشلت جميع محاولات الاتصال بسبب انشغال خوادم قوقل.")


# ── Views ──────────────────────────────────────────────────────────────────

def customer_dashboard(request):
    """لوحة التحكم لعملاء منصة بناء"""
    if 'customer_id' not in request.session or request.session.get('user_role') != 'customer':
        messages.error(request, "منطقة محظورة! يرجى تسجيل الدخول كعميل أولاً.")
        return redirect('binnaSign:login')
    
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    context = {'customer': customer}
    return render(request, "binnaCustomer/customer_dashboard.html", context)


def ai_assistans(request):
    return render(request, "binnaCustomer/ai_assistans.html")


def upload_blueprint(request):
    """
    التحقق من صحة الصورة وحفظ المخطط الإنشائي ثم إطلاق خيط المعالجة بالخلفية
    """
    if 'customer_id' not in request.session or request.session.get('user_role') != 'customer':
        messages.error(request, "يرجى تسجيل الدخول للوصول إلى المساعد الذكي.")
        return redirect('binnaSign:login')

    if request.method == "POST":
        uploaded_file = request.FILES.get("blueprint_image")

        if not uploaded_file:
            return render(
                request,
                "binnaCustomer/ai_assistans.html",
                {"error": "الرجاء رفع صورة المخطط الهندسي أولاً."}
            )

        try:
            Image.open(uploaded_file).verify()
            uploaded_file.seek(0)  
        except Exception as e:
            return render(
                request,
                "binnaCustomer/ai_assistans.html",
                {"error": f"صورة غير صالحة أو امتداد غير مدعوم: {e}"}
            )

        blueprint = Blueprint.objects.create(image=uploaded_file)

        thread = threading.Thread(target=_run_gemini, args=(blueprint,), daemon=True)
        thread.start()

        return redirect("binnaCustomer:blueprint_detail", pk=blueprint.id)

    return render(request, "binnaCustomer/ai_assistans.html")


def blueprint_detail(request, pk):
    """عرض صفحة النتائج فوراً، بينما يتولى كود الـ JavaScript الاستعلام التكراري"""
    if 'customer_id' not in request.session or request.session.get('user_role') != 'customer':
        messages.error(request, "يرجى تسجيل الدخول أولاً لعرض نتائج المخطط.")
        return redirect('binnaSign:login')

    blueprint = get_object_or_404(Blueprint, pk=pk)
    return render(
        request,
        "binnaCustomer/result.html",
        {"blueprint": blueprint}
    )


@require_GET
def analyze_blueprint_ajax(request, pk):
    """
    نقطة استعلام الـ AJAX: تقوم الواجهة بالاتصال بها باستمرار حتى اكتمال التجهيز والتفكيك بنجاح
    """
    if 'customer_id' not in request.session or request.session.get('user_role') != 'customer':
        return JsonResponse({"status": "error", "message": "Unauthorized access"}, status=403)

    blueprint = get_object_or_404(Blueprint, pk=pk)

    if not blueprint.analysis_result:
        return JsonResponse({"status": "pending"})

    if blueprint.analysis_result.startswith("ERROR:"):
        return JsonResponse({
            "status":  "error",
            "message": blueprint.analysis_result[6:].strip(),
        })

    # دالة الـ Parser المضافة الآن ستقوم بفك النص دون أي NameError
    material_rows, sections = _parse_result(blueprint.analysis_result)

    return JsonResponse({
        "status":        "success",
        "material_rows": material_rows,
        "sections":      sections,
        "image_url":     blueprint.image.url if blueprint.image else None,
    })


def stores_producs(request):
    if 'customer_id' not in request.session or request.session.get('user_role') != 'customer':
        messages.error(request, "يرجى تسجيل الدخول كعميل أولاً.")
        return redirect('binnaSign:login')

    mode = request.GET.get('mode', 'suppliers')
    search_query = request.GET.get('q', '').strip()

    selected_city = request.GET.get('city', '')
    selected_supplier_category = request.GET.get('supplier_category', '')
    selected_inventory_category = request.GET.get('inventory_category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    suppliers = Supplier.objects.all().select_related('city', 'category')
    products = Inventory.objects.all().select_related('supplier', 'category', 'supplier__city')

    cities = City.objects.all()
    supplier_categories = SupplierCategory.objects.all()
    inventory_categories = InventoryCategory.objects.all()

    if search_query:
        suppliers = suppliers.filter(
            Q(store_name__icontains=search_query) |
            Q(owner_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(city__name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

        products = products.filter(
            Q(name__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(supplier__store_name__icontains=search_query) |
            Q(supplier__city__name__icontains=search_query)
        )

    if selected_city:
        suppliers = suppliers.filter(city_id=selected_city)
        products = products.filter(supplier__city_id=selected_city)

    if selected_supplier_category:
        suppliers = suppliers.filter(category_id=selected_supplier_category)

    if selected_inventory_category:
        products = products.filter(category_id=selected_inventory_category)

    if min_price:
        products = products.filter(sell_price__gte=min_price)

    if max_price:
        products = products.filter(sell_price__lte=max_price)

    context = {
        'suppliers': suppliers,
        'products': products,
        'cities': cities,
        'supplier_categories': supplier_categories,
        'inventory_categories': inventory_categories,
        'mode': mode,
        'search_query': search_query,
        'selected_city': selected_city,
        'selected_supplier_category': selected_supplier_category,
        'selected_inventory_category': selected_inventory_category,
        'min_price': min_price,
        'max_price': max_price,
    }

    return render(request, "binnaCustomer/stors-product.html", context)

def store_details(request, supplier_id):
    if 'customer_id' not in request.session or request.session.get('user_role') != 'customer':
        messages.error(request, "يرجى تسجيل الدخول كعميل أولاً.")
        return redirect('binnaSign:login')

    supplier = get_object_or_404(Supplier, id=supplier_id)
    inventory_items = Inventory.objects.filter(supplier=supplier).select_related('category')

    context = {
        'supplier': supplier,
        'inventory_items': inventory_items,
    }

    return render(request, "binnaCustomer/store_details.html", context)

def inventory_details(request, inventory_id):
    if 'customer_id' not in request.session or request.session.get('user_role') != 'customer':
        messages.error(request, "يرجى تسجيل الدخول كعميل أولاً.")
        return redirect('binnaSign:login')

    item = get_object_or_404(Inventory, id=inventory_id)

    context = {
        'item': item,
        'supplier': item.supplier,
    }

    return render(request, "binnaCustomer/inventory_details.html", context)

def customer_settings(request):
    # جلب بيانات العميل الحالي من الجلسة
    customer = get_object_or_404(Customer, id=request.session.get('customer_id'))
    return render(request, "binnaCustomer/customer_settings.html", {'customer': customer})

def update_customer(request):
    if request.method == 'POST':
        # جلب العميل باستخدام الـ Manager الذي قمت بإنشائه
        customer = Customer.objects.get(id=request.session.get('customer_id'))
        
        # استخدام الدالة التي عرفتها أنت في الموديل!
        customer.update_customer_info(request.POST)
        
        # معالجة كلمة المرور منفصلة لأنها تحتاج تشفير (bcrypt)
        new_password = request.POST.get('password')
        if new_password:
            # التحقق من القوة (اختياري، يمكنك استخدام الـ validator الموجود في الـ Manager)
            customer.password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode('utf-8')
            customer.save()
            
        messages.success(request, "تم تحديث بياناتك بنجاح!")
        return redirect('binnaCustomer:customer_settings')
    
    return redirect('binnaCustomer:customer_settings')
