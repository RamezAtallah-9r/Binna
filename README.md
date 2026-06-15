# BINNA | بناء &nbsp;🏗️

<div align="center">

![BINNA Banner](https://img.shields.io/badge/BINNA-Smart%20Construction%20Platform-b0dc00?style=for-the-badge&labelColor=1A1A1A)
&nbsp;
![Status](https://img.shields.io/badge/Status-MVP%20%2F%20In%20Development-FF6B00?style=for-the-badge&labelColor=1A1A1A)
&nbsp;
![Made in Palestine](https://img.shields.io/badge/Made%20in-Palestine%20🇵🇸-009736?style=for-the-badge&labelColor=1A1A1A)

**A Palestinian AI-powered construction marketplace — connecting builders, suppliers, and smart tools in one platform.**

[Features](#-features) · [Tech Stack](#-tech-stack) · [Getting Started](#-getting-started) · [API](#-api-endpoints) · [Screenshots](#-screenshots) · [Team](#-team)

</div>

---

```
██████╗ ██╗███╗   ██╗███╗   ██╗ █████╗
██╔══██╗██║████╗  ██║████╗  ██║██╔══██╗
██████╔╝██║██╔██╗ ██║██╔██╗ ██║███████║
██╔══██╗██║██║╚██╗██║██║╚██╗██║██╔══██║
██████╔╝██║██║ ╚████║██║ ╚████║██║  ██║
╚═════╝ ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚═╝  ╚═╝
```

> *"From blueprint to build — all in one platform."*

---

## 🟡🖤🟡🖤🟡🖤 &nbsp; What is BINNA?

BINNA (بناء) is a smart construction marketplace built for the Palestinian market. It combines an **AI-powered blueprint analyzer** with a **multi-supplier materials marketplace**, letting customers upload engineering plans and instantly receive quantity estimates, budget breakdowns, and supplier comparisons.

The platform serves three user types:

| Role | What they do |
|------|-------------|
| 🏠 **Customer / Contractor** | Upload blueprints, browse materials, compare prices, place orders |
| 🏭 **Supplier** | List products, manage inventory, fulfill orders |
| ⚙️ **Admin** | Manage users, suppliers, categories, and platform content |

---

## ✦ Features

### 🤖 AI Construction Estimator
- Upload blueprint images (PNG, JPG, WEBP, HEIC)
- Powered by **Gemini 2.5 Flash** vision model
- Extracts material types, quantities, and specifications
- Returns structured BOQ (Bill of Quantities) with line items
- Auto-retries on API overload (503 handling with backoff)
- Results stored per blueprint — no re-analysis needed on revisit

### 🏪 Construction Materials Marketplace
- 150+ Palestinian suppliers (West Bank coverage)
- Product catalog with categories, specs, and pricing
- Real-time price comparison across suppliers
- City-based filtering

### 📦 Order Management
- Full order lifecycle: pending → confirmed → in delivery → received
- WhatsApp notification dispatch via Meta Cloud API
- Customer order history and tracking dashboard

### 📊 Dashboards
- **Customer dashboard** — active orders, saved projects, price alerts, AI estimates
- **Supplier dashboard** — inventory, orders, sales analytics
- **Admin panel** — user management, supplier approvals, category management

### 💬 Messaging
- Direct supplier-customer chat
- Dispute resolution system

---

## 🛠 Tech Stack

```
🖥  Backend          Python 3.x · Django 5.x · Django REST Framework
🗄  Database         PostgreSQL
🤖  AI Engine        Google Gemini 2.5 Flash (vision)
🎨  Frontend         HTML · Tailwind CSS · Vanilla JavaScript
☁️  Storage          Google Cloud Storage (blueprint images)
🔐  Auth             Django session auth · JWT (API)
📲  Notifications    Meta WhatsApp Cloud API
🌐  Deployment       (in progress)
```

### Directory Structure:

```
binna/
├── binnaCustomer/          # Customer-facing app
│   ├── models.py           # Blueprint, Order, Project models
│   ├── views.py            # Upload, AI analysis, result pages
│   └── templates/
│       └── binnaCustomer/
│           ├── ai_assistans.html   # Blueprint upload page
│           └── result.html         # AI analysis results
├── binnaSupplier/          # Supplier dashboard app
├── binnaAdmin/             # Admin panel app
├── binnaAccounts/          # Auth: login, register, profile
├── static/
│   ├── img/                # Logo and brand assets
│   └── css/                # Custom styles (minimal — Tailwind CDN)
├── templates/              # Shared base templates
├── manage.py
├── requirements.txt
└── .env.example
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- A Google Cloud project with Gemini API enabled
- pip

### 1. Clone the repo

```bash
git clone https://github.com/your-username/binna.git
cd binna
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in:

```env
# Django
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=binna_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Google Gemini AI
GOOGLE_API_KEY=your-gemini-api-key

# Google Cloud Storage (optional for local dev)
GCS_BUCKET_NAME=your-bucket-name

# WhatsApp (optional for local dev)
WHATSAPP_TOKEN=your-meta-token
WHATSAPP_PHONE_ID=your-phone-id
```

### 5. Set up the database

```bash
createdb binna_db                 # or use pgAdmin
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` — the platform is running.

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/accounts/login/` | Login with username + password |
| `POST` | `/accounts/register/` | Create new account |
| `POST` | `/accounts/logout/` | Logout current session |

### AI Blueprint Analyzer
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/customer/upload/` | Upload blueprint image, trigger Gemini analysis (background thread) |
| `GET`  | `/customer/result/<id>/` | View result page (renders once analysis is complete) |
| `GET`  | `/api/analyze/<id>/` | **AJAX polling endpoint** — returns `pending` / `success` / `error` JSON |

#### AJAX polling response format
```json
// Still processing
{ "status": "pending" }

// Done
{
  "status": "success",
  "material_rows": [
    { "type": "طوب", "name": "Exterior block 40x20x20 cm", "qty": "1966", "unit": "block" }
  ],
  "sections": [
    { "heading": "Dimensions & Areas", "steps": ["Total length: 13.7 m", "..."] }
  ]
}

// Failed
{ "status": "error", "message": "503 UNAVAILABLE — model overloaded" }
```

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/customer/orders/` | List customer orders |
| `POST` | `/customer/orders/create/` | Place a new order |
| `GET`  | `/supplier/orders/` | List supplier's incoming orders |
| `POST` | `/supplier/orders/<id>/confirm/` | Confirm an order |

---

## 📸 Screenshots

> Screenshots will be added here as the UI is finalized.

```
[ Customer Dashboard ]   [ AI Blueprint Upload ]   [ Analysis Results ]
[ Supplier Dashboard ]   [ Admin Panel ]            [ Login Page ]
```

To add screenshots: place images in `/docs/screenshots/` and update this section.

---

## 🗺 Roadmap

- [x] Customer dashboard
- [x] Supplier dashboard
- [x] Admin panel
- [x] AI blueprint analyzer (Gemini 2.5 Flash)
- [x] Blueprint upload → instant redirect → AJAX result polling
- [x] Login / Register pages
- [ ] WhatsApp order notifications
- [ ] Mobile-responsive polish pass
- [ ] Payment gateway integration
- [ ] Mobile app (iOS + Android)
- [ ] Regional expansion (Jordan, Egypt)
- [ ] Government permit integration

---

## 🤝 Contributing

BINNA is currently in active MVP development. Contributions, issues, and feature requests are welcome.

```bash
# Fork → Clone → Create your feature branch
git checkout -b feature/your-feature-name

# Commit your changes
git commit -m "feat: add your feature"

# Push and open a Pull Request
git push origin feature/your-feature-name
```

Please keep PRs focused — one feature or fix per PR.

---

## 👥 Team

| Name | Role |
|------|------|
| **Murad Shaheen** | Co-Founder |
| **Ramez Ataallah** | Co-Founder & Developer |
| **Abdullah Awwad** | Co-Founder |

Special thanks to **Al-Mansour Construction Materials Store** for their industry expertise and support throughout development.

---

## 📄 License

This project is currently **proprietary** — all rights reserved by the BINNA team.
Contact us before using any part of this codebase.

---

<div align="center">

**BINNA | بناء**
*Smart Construction Platform · West Bank, Palestine 🇵🇸*

![](https://img.shields.io/badge/Built%20with-Django-092E20?style=flat-square&logo=django)
&nbsp;
![](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-4285F4?style=flat-square&logo=google)
&nbsp;
![](https://img.shields.io/badge/Styled%20with-Tailwind%20CSS-06B6D4?style=flat-square&logo=tailwindcss)
&nbsp;
![](https://img.shields.io/badge/DB-PostgreSQL-4169E1?style=flat-square&logo=postgresql)

</div>
