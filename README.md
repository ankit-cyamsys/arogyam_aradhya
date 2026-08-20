# Arogyam Aradhya

An Ayurvedic e-commerce platform with **two earning portals** on one shared catalog:

- **MLM Network** (`/dashboard`) — binary genealogy tree, SP-based matching bonus,
  level bonus, and ₹500 per direct referral.
- **Direct Selling** (`/seller`) — standalone agents earning a flat **40%** on their
  own sales (no team).

Plus a public storefront and an admin panel with a fully **configurable** compensation
plan. Pricing uses **DP** (distributor/discount price) as the base; **1 SP = ₹10**.

Portal chooser lives at `/join`. Each portal has its own login and rejects cross-portal
sign-in.

**Stack:** FastAPI · PostgreSQL (SQLite for dev) · React (Vite) · Tailwind CSS

```
backend/    FastAPI app, SQLAlchemy models, MLM commission engine
frontend/   React SPA (storefront + member dashboard + admin)
PRODUCT/    Original product images (source assets)
```

## Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate           # Windows;  source .venv/bin/activate on mac/linux
pip install -r requirements.txt
cp .env.example .env             # then edit DATABASE_URL
python -m app.seed               # create tables + demo data
python -m uvicorn app.main:app --reload --port 8000
```

> **Important:** the backend must run on **port 8000** — the frontend proxies API
> calls there. Running it on any other port makes login/data silently fail.
> Easiest: from the project root run **`./start.ps1`** (starts both servers correctly).

- API docs: http://127.0.0.1:8000/docs
- **Admin:** `admin` / `admin123`
- A demo network member is printed by the seed script (password `demo123`).

### Switching to PostgreSQL
Create the DB and point `DATABASE_URL` at it:
```
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/arogyam
```
Then re-run `python -m app.seed`.

## Frontend

```bash
cd frontend
npm install
npm run dev                      # http://localhost:5173  (proxies /api to :8010)
```

## The MLM engine

- **Binary tree:** every member has a `sponsor` (referral, drives level bonus) and a
  `parent`/`position` placement (drives binary matching). New signups spill over down
  the chosen leg.
- **Selling Points (SP):** each order's SP flows up every ancestor's left/right leg.
- **Binary matching:** `min(left_carry, right_carry)` is matched each cycle, paid at
  `matching_percent`, capped by `daily_capping`; the remainder carries forward.
- **Level bonus:** a % of order value paid up the sponsor line, level by level.
- **All rates are admin-editable** under *Admin → MLM Settings* (placeholder defaults;
  replace with your real plan before launch).
