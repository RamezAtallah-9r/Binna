import re
import time
import threading
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Blueprint

from google import genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# ── Gemini settings ────────────────────────────────────────────────────────
GEMINI_MODEL       = "gemini-2.5-flash"
GEMINI_MAX_RETRIES = 4    # attempts total before giving up
GEMINI_RETRY_DELAY = 6    # seconds between retries on 503

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
    Parse raw Gemini text into structured data.
    Returns (material_rows, sections) — both lists of dicts.
    """
    # ── Material rows ──────────────────────────────────────────────────
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

    # ── Calculation sections ───────────────────────────────────────────
    # Strip the summary block so we only parse the calculations
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
    Run Gemini in a background thread with retry logic.
    Always saves something to blueprint.analysis_result so the AJAX
    endpoint can detect completion:
      - Normal result  → saved as-is
      - Error          → saved with "ERROR:" prefix so AJAX can detect it
    """
    def _save_error(msg):
        blueprint.analysis_result = f"ERROR:{msg}"
        blueprint.save()

    try:
        pil_image = Image.open(blueprint.image.path)
        client    = genai.Client()
    except Exception as e:
        _save_error(str(e))
        return

    for attempt in range(1, GEMINI_MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[pil_image, GEMINI_PROMPT]
            )
            blueprint.analysis_result = response.text or "لم يتم إرجاع نتيجة."
            blueprint.save()
            return   # success

        except Exception as e:
            error_str = str(e)
            is_503    = "503" in error_str or "UNAVAILABLE" in error_str

            if is_503 and attempt < GEMINI_MAX_RETRIES:
                time.sleep(GEMINI_RETRY_DELAY)
                continue

            _save_error(error_str)
            return

    _save_error("فشلت جميع المحاولات.")


# ── Views ──────────────────────────────────────────────────────────────────

def index(request):
    """AI assistant upload page."""
    return render(request, "binnaCustomer/ai_assistans.html")


def upload_blueprint(request):
    """
    POST: Validate + save image → redirect to result page immediately.
    No Gemini call here — the result page fetches analysis via AJAX.
    """
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
            uploaded_file.seek(0)   # verify() exhausts the stream
        except Exception as e:
            return render(
                request,
                "binnaCustomer/ai_assistans.html",
                {"error": f"صورة غير صالحة: {e}"}
            )

        blueprint = Blueprint.objects.create(image=uploaded_file)

        # Kick off Gemini in a background thread so the redirect is instant.
        # The AJAX endpoint checks blueprint.analysis_result to report status.
        thread = threading.Thread(target=_run_gemini, args=(blueprint,), daemon=True)
        thread.start()

        # Redirect immediately — result page will poll for the analysis
        return redirect("binnaCustomer:blueprint_detail", pk=blueprint.id)

    return render(request, "binnaCustomer/ai_assistans.html")


def blueprint_detail(request, pk):
    """
    Render the result page shell instantly.
    The page JS polls analyze_blueprint_ajax for the actual analysis.
    """
    blueprint = get_object_or_404(Blueprint, pk=pk)
    return render(
        request,
        "binnaCustomer/result.html",
        {"blueprint": blueprint}
    )


@require_GET
def analyze_blueprint_ajax(request, pk):
    """
    AJAX polling endpoint — called repeatedly by result.html until done.

    Returns JSON with one of three statuses:
      "pending"  — Gemini is still running (background thread not done)
      "success"  — analysis done, returns parsed data
      "error"    — something went wrong
    """
    blueprint = get_object_or_404(Blueprint, pk=pk)

    # Still waiting for the background thread
    if not blueprint.analysis_result:
        return JsonResponse({"status": "pending"})

    # Check for a stored error marker (we prefix errors with "ERROR:")
    if blueprint.analysis_result.startswith("ERROR:"):
        return JsonResponse({
            "status":  "error",
            "message": blueprint.analysis_result[6:].strip(),
        })

    # Parse and return structured data
    material_rows, sections = _parse_result(blueprint.analysis_result)

    return JsonResponse({
        "status":        "success",
        "material_rows": material_rows,
        "sections":      sections,
        "image_url":     blueprint.image.url if blueprint.image else None,
    })