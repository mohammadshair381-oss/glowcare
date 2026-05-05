# GlowCare 2‑Minute Frontend QA Checklist

## 1) Load + layout
- Open `index.html` → navbar + footer render (injected)
- Resize to mobile width → hamburger menu opens/closes, no layout breaks

## 2) Shop
- Open `shop.html`
- Search keyword (e.g. `serum`) → results update
- Toggle brand + concern filters → URL updates and refresh keeps filters
- Sort by price low/high → grid updates

## 3) Product page
- Open a product from shop → lands on `product.html?id=...`
- Switch shade/size (if available) → stock message updates
- Add to cart with qty 2–3 → cart badge increments
- Wishlist toggle → wishlist badge increments

## 4) Cart
- Open `cart.html`
- Qty +/− works, remove works, clear cart works
- Apply coupon `GLOW10` → total decreases

## 5) Auth guard
- Logout (from `account.html`) then try `checkout.html` → redirected to `login.html?next=checkout.html`

## 6) Checkout → Payment → Success
- Login demo user
- `checkout.html` → submit shipping → goes to `payment.html`
- Try invalid UPI/Card → shows toast validation
- Pay until success → lands on `success.html`
- `account.html` → order appears in orders list

## 7) Admin
- Login admin user
- Press `Ctrl+Shift+A` → opens `admin.html`
- Add product (name/brand/price) → shows in products table and appears in `shop.html`
- Press `Esc` or `Ctrl+Shift+U` → admin mode off → returns to `account.html`

