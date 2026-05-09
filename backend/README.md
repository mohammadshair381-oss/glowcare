## GlowCare CMS (Django + PostgreSQL)

This backend turns the existing premium frontend into a **real CMS-driven ecommerce site**.

### Features
- Django authentication (staff-only dashboard)
- Custom premium dashboard (`/dashboard/`) with live preview links
- Visual homepage editor (`/dashboard/homepage/editor/`) with split preview + drag/drop sections
- Real database models for products, variants, media, homepage (hero slides, ribbons, sections order/toggles, theme, menus, testimonials, logos)
- REST API for frontend to load dynamic homepage + product catalog
- Media uploads stored under `media/`

### Quick start (local)
1) Create venv + install deps:
   - `python -m venv .venv`
   - Windows: `.venv\\Scripts\\activate`
   - `pip install -r backend/requirements.txt`

2) Run PostgreSQL (preferred)
   - Option A (recommended): Docker
     - `docker compose -f backend/docker-compose.yml up -d`
   - Option B: use your local Postgres and set env vars below

3) Create `backend/.env` (copy from `backend/.env.example`)

4) Migrate + create admin user:
   - `python backend/manage.py migrate`
   - `python backend/manage.py createsuperuser`

5) Run server:
   - `python backend/manage.py runserver`

6) Open:
  - Frontend: `http://127.0.0.1:8000/`
  - Dashboard: `http://127.0.0.1:8000/dashboard/`
  - Visual Editor: `http://127.0.0.1:8000/dashboard/homepage/editor/`

### API endpoints
- `GET /api/v1/homepage/` — homepage JSON (hero, sections, theme, nav/footer)
- `GET /api/v1/products/` — product catalog list
- `GET /api/v1/products/<id>/` — product detail

### Notes
- Frontend JS is updated to call the API first, with local fallback.
- Use the dashboard to edit content; changes reflect instantly on refresh.
