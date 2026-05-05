# GlowCare (Frontend‑Only Beauty eCommerce)

Vanilla HTML/CSS/JS multi‑page storefront. No backend. No database. Everything runs on a static server (VS Code Live Server) using `localStorage`.

## Run
- Open the folder in VS Code
- Right‑click `index.html` → **Open with Live Server**

## Demo Accounts
- User: `demo@glowcare.example` / `demo123`
- Admin: `admin@glowcare.example` / `admin123`

## Admin Mode (Keyboard‑Only)
- Enable admin mode: `Ctrl + Shift + A` (admin account required)
- Exit admin mode: `Ctrl + Shift + U` or `Esc`

## Routes
- `index.html` (home)
- `shop.html` (filters + sort + URL sync)
- `product.html?id=...` (variants + gallery + related)
- `wishlist.html`
- `cart.html`
- `checkout.html` (shipping only, guarded)
- `payment.html` (payment simulation, guarded)
- `success.html` (last order, guarded)
- `login.html`, `signup.html`, `forgot.html`
- `account.html` (logout shown here)
- `admin.html` (guarded + requires admin mode; logout shown here)
- `about.html`, `contact.html`, `info.html`

## Data Model (localStorage)
- Catalog: `glowcare_catalog_v1`
- Cart: `glowcare_cart_v1`
- Wishlist: `glowcare_wishlist_v1`
- Users: `glowcare_users_v1`
- Session: `glowcare_session_v1`
- Checkout draft: `glowcare_checkout_draft_v1`
- Orders: `glowcare_orders_v1`
- Last order: `glowcare_last_order_v1`
- Funnel: `glowcare_funnel_v1`

## Reset (Fresh Start)
- In browser DevTools → Application → Local Storage → clear site data (or clear all the keys above)

## Architecture
See `FLOW.md` for Mermaid diagrams.

## QA
Use `FRONTEND_QA_CHECKLIST.md` (2‑minute checklist).

