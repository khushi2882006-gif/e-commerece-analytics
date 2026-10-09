# E-Commerce Sales Analytics Dashboard

A full-stack web application for visualizing e-commerce sales analytics across 6 modules: Sales, Customers, Products, Inventory, Marketing, and Fulfillment.

---

## Prerequisites

| Tool | Version | Download |
|------|---------|----------|
| Python | **3.12** | https://www.python.org/downloads/ |
| Node.js | 18+ | https://nodejs.org/ |
| Git | any | https://git-scm.com/ |

> ⚠️ **Python 3.12 is required.** Python 3.13+ has binary wheel compatibility issues with several dependencies on Windows.

---

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/khushi2882006-gif/ecommerce-analytics.git
cd ecommerce-analytics
```

### 2. Set up the Backend

```bash
cd backend

# Create virtual environment with Python 3.12
py -3.12 -m venv venv          # Windows
# python3.12 -m venv venv      # macOS / Linux

# Activate
.\venv\Scripts\Activate.ps1    # Windows PowerShell
# source venv/bin/activate     # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment (copy and edit)
copy .env.example .env         # Windows
# cp .env.example .env         # macOS / Linux
```

Edit `.env` to set a strong `SECRET_KEY`:
```
SECRET_KEY=your-long-random-secret-here
```
Generate one with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Set up the Frontend

```bash
cd ../frontend
npm install
```

---

## Running the Application

Open **two terminal windows** and run each simultaneously.

### Terminal 1 — Backend (FastAPI)

```bash
cd ecommerce-analytics/backend

# Windows — activate venv first
.\venv\Scripts\Activate.ps1

python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The backend will automatically:
- Create `analytics.db` (SQLite)
- Seed 200 customers, 50 products, 1 200 orders with realistic mock data

### Terminal 2 — Frontend (React + Vite)

```bash
cd ecommerce-analytics/frontend
npm run dev
```

---

## Accessing the Application

| URL | Description |
|-----|-------------|
| http://localhost:5173 | Frontend Dashboard |
| http://localhost:8000/docs | Swagger API Documentation |
| http://localhost:8000/redoc | ReDoc API Documentation |
| http://localhost:8000/health | Health Check |

---

## Default Credentials

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `admin123` |

---

## Re-seeding Data

To clear and regenerate all mock data:

```bash
cd backend
python seed.py
```

---

## Project Structure

```
ecommerce-analytics/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLAlchemy + SQLite setup
│   ├── auth.py              # JWT authentication
│   ├── seed.py              # Mock data seeder
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Environment variable template
│   ├── models/
│   │   ├── customer.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── inventory.py
│   │   ├── shipment.py
│   │   └── marketing.py
│   └── routers/
│       ├── auth.py
│       ├── sales.py
│       ├── customers.py
│       ├── products.py
│       ├── inventory.py
│       ├── marketing.py
│       └── fulfillment.py
└── frontend/
    ├── src/
    │   ├── App.tsx
    │   ├── main.tsx
    │   ├── api/             # Axios API clients
    │   ├── components/      # Shared UI components
    │   ├── context/         # Auth, Theme, DateRange contexts
    │   └── pages/           # One page per dashboard module
    ├── package.json
    └── vite.config.ts
```

---

## Dashboard Modules

| Module | Route | Description |
|--------|-------|-------------|
| Sales Overview | /sales | Revenue trends, KPIs, channel breakdown |
| Customer Analytics | /customers | Acquisition, tiers, geography, cohort retention |
| Product Performance | /products | Top sellers, categories, slow-moving items |
| Inventory | /inventory | Stock levels, turnover, restock events |
| Marketing | /marketing | Spend vs revenue, promo impact, conversion |
| Fulfillment | /fulfillment | Delivery times, carrier comparison, failed orders |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12 + FastAPI |
| Database | SQLite (via SQLAlchemy) |
| Auth | JWT (python-jose + passlib) |
| Frontend | React 18 + TypeScript |
| Build Tool | Vite |
| Styling | TailwindCSS |
| Charts | Recharts |
| HTTP Client | Axios |
| Routing | react-router-dom v6 |
| Icons | lucide-react |

---

## Troubleshooting

### `WinError 10013` — port already in use
```bash
# Find what's using port 8000
netstat -ano | findstr ":8000"
# Kill it (replace 12345 with actual PID)
taskkill /PID 12345 /F
# Or just use a different port
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

### `.pyd` DLL blocked by Windows AppControl
```powershell
Get-ChildItem -Recurse -Path .\venv\Lib\site-packages -Include "*.pyd","*.dll" |
  ForEach-Object { Unblock-File $_.FullName }
```

### `pandas` build error on Windows
Ensure you are using Python 3.12 and install with binary wheels only:
```bash
pip install -r requirements.txt --only-binary=:all:
```
