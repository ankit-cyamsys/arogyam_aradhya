# Arogyam Aradhya — Backend & MLM PRD

> **Purpose:** the single source of truth for the backend + MLM logic.
> **How to use:** legend below marks what's built vs. what needs your input.
> Edit anything, add rules under the ❓ markers, and I'll implement to match.
>
> Legend: ✅ built & live · 🟡 built but simplified/assumed · ❓ needs your decision · 🔜 planned/not built

_Last updated: 2026-09-08 · Owner: Ankit (cyamsys)_

---

## 1. Product Overview

Two earning portals on one shared product catalog + one admin panel:

| Portal | Who | How they earn |
|---|---|---|
| **MLM Network** | Distributors in a binary tree | Binary matching (weekly), career-rank bonuses, ₹500 direct-referral |
| **Direct Selling (DSA)** | Standalone agents (no team) | Flat 40% commission on their own sales |

- Pricing base = **DP (distributor price)**. **MRP** = retail (display). **SP (Selling Points)** = business volume for MLM.
- Public storefront (Home, Products, Franchise, Documents, Pay, Gallery, About, Contact) + Cart.

---

## 2. Roles & Accounts

- **Member** — `segment = "mlm"` or `"direct"`. Login by member ID / phone / email.
- **Admin** — separate `admin_users` table. Single super admin (`admin`).
- Member IDs: `AA` + 8 digits (random). Founder/root is fixed `AA10000001`.
- Portal guard: a `direct` account cannot log into the MLM portal and vice-versa. ✅

---

## 3. Tech Stack & Architecture ✅

- **Backend:** FastAPI (Python 3.13), SQLAlchemy 2.0, PostgreSQL.
- **Frontend:** React (Vite) + Tailwind, served by FastAPI (single service).
- **Deploy:** Render (Docker, one web service + managed Postgres). GST/company info + all MLM rates are DB settings.
- **Tests:** pytest (31 tests) — auth, matching, ranks, weekly payout, GST, KYC, orders.

---

## 4. Data Model (key entities)

**Member** — `member_id, segment, name, email, phone, password_hash,`
`sponsor_id (referral), parent_id + position(L/R) (tree placement),`
`is_active (green flag), is_blocked, activated_at,`
`rank_level, rank_bonus_paid_level,`
`left_carry, right_carry (unmatched SP per leg),`
`total_left_sp, total_right_sp (lifetime, drives rank),`
`week_left_sp, week_right_sp (reset at weekly close),`
`self_purchase_sp, wallet_balance, total_earned, total_paid,`
`address/city/state/pincode, pan, aadhaar, bank_name/account/ifsc, nominee`

**Product** — `name, slug, category, mrp, price(DP), cost_price, sp, stock, image, is_active, is_offer`
**Category** — `name, slug`
**Order** / **OrderItem** — `order_no, member_id, subtotal(taxable), total(w/GST), total_sp, status(pending/paid/cancelled), payment_status(unpaid/paid)`
**SPLedger** — every SP event up a leg (L/R/S)
**CommissionLedger** — earnings: `kind ∈ {matching, rank, referral, dsa, level}`
**WeeklyPayout** — payout register row: `period, week_label, left_sp, right_sp, matching_sp, closing_sp, payout, cf_left, cf_right, status`
**PayoutRequest** — member withdrawal request: `amount, status(pending/approved/paid/rejected)`
**KycDocument** — `member_id, doc_type, filename, content_type, data(blob)` (5 slots)
**Setting** — key/value config (see §16)
**AdminUser** — `username, password_hash`

---

## 5. Authentication & Security ✅

- Passwords: bcrypt. JWT (HS256), 1-day expiry, `SECRET_KEY` from env.
- Signup: password ≥ 6 chars, phone normalized to 10 digits (+91/spaces stripped), email format-validated, **phone unique** across both portals.
- Rate limiting per IP: login 15/5min, signup 10/10min, admin 6/5min.
- Self-service change password; admin can reset a member's password.
- Blocked accounts cannot log in.

---

## 6. Member Lifecycle & GREENING ❓ **(needs your rules)**

**Currently built (🟡 simplified):**
- A member joins under a sponsor (placement L/R). Starts **inactive (red)**.
- On a self-purchase reaching **≥ 50 SP** (`activation_sp`), the member flips to **`is_active = True` (green)**, `activated_at` is set, and the sponsor is paid the **₹500 direct-referral** bonus (once).
- Greening currently happens when the order is **confirmed by admin**.

**❓ Please specify the real greening rules — I likely missed these:**
1. Is the greening threshold exactly **50 SP** in ONE order, or cumulative self-purchase? First order only or any time?
2. Is there a **time window** to green (e.g., must green within N days of joining, else ID lapses)?
3. **Green-to-green matching?** Do BOTH a left and a right downline need to be *green* for a matched pair to count/pay? (Many binary plans require this.)
4. **Re-greening / monthly repurchase** to stay green & keep earning? (`repurchase_sp` exists but unused.) What SP, what period, what happens if missed (red = no matching)?
5. Does greening affect **"Active Members"** counts on My Team? (Currently `is_active` drives it.)
6. Any **franchise/ID activation fee** or joining package (25/50/100 SP packages) tied to greening?
7. Red vs Green — any partial states (e.g., "SP done but KYC pending")?

_→ Fill in the exact rules here and I'll rewrite the greening engine + tests._

---

## 7. Binary Tree & Placement ✅

- Each member has a **sponsor** (who referred them → drives referral/level) and a **placement parent + position (L/R)**.
- New signup **spills over** down the chosen leg to the first open slot under the sponsor.
- `My Team`: left/right member counts, left/right **active** counts, parent, 3-level genealogy view.
- ❓ Confirm placement rule: always spillover to outermost open slot on chosen leg? Or sponsor picks exact position? Any auto-balancing?

---

## 8. Selling Points (SP) ✅ / ❓

- Each product has an **SP** value. An order's `total_sp` = Σ(product.sp × qty).
- On a **confirmed** order: buyer's `self_purchase_sp` increases; SP propagates up **every ancestor's** L or R leg (both `*_carry` for matching and lifetime `total_*_sp` for rank).
- 1 SP ≈ ₹10 for matching payout (see §9). ❓ Confirm SP→₹ for packages (100 SP pack = ₹12,000 in the plan sheet implies ₹120/SP business value — this is separate from the ₹10/SP matching rate).

---

## 9. Binary Matching & Weekly Payout ✅

- **Rate:** ₹10 per matched SP (`matching_per_sp`).
- **Blocks:** pays only in multiples of **50 SP** (`matching_block_sp`): 50→₹500, 100→₹1000, 150→₹1500…
- **Carry forward:** unmatched SP (and any sub-50 remainder) rolls to next period.
- **Weekly close** (admin-run, "Run Weekly Close"): for each member, `matched = min(left_carry,right_carry)`, `closing = floor(matched/50)*50`, `payout = closing×₹10`; writes a **payout-register row** (Week, L SP, R SP, Matching SP, Closing SP, Payout, CF L, CF R) and credits wallet.
- ❓ Capping? (`daily_capping`=0 = none) — is there a weekly/rank matching cap?
- ❓ Min payout to withdraw is 50 SP (₹500) — confirm.
- ❓ Should close be **automatic** on a fixed weekday (cron), not just manual?
- ❓ Green-to-green requirement (see §6.3) — currently matching counts all SP regardless of downline green status.

---

## 10. Career Ranks & Rewards ✅ / ❓

- 12 ranks by cumulative SP on **both** legs (weaker leg governs):

| Lvl | Rank | SP each leg | One-time bonus (₹) | Reward |
|---|---|---|---|---|
|1|Winner|200|4,000|Bag|
|2|Achiever|500|10,000|Smart Watch|
|3|Warrior|1,000|20,000|Tablet|
|4|Champion|2,000|40,000|Jim Corbett|
|5|Master|4,000|80,000|₹15k Mobile + Agra|
|6|Commander|8,000|80,000|₹30k Bike + Shimla|
|7|Royal Executive|16,000|2,50,000|₹1.5L Laptop + Gangtok|
|8|Imperial Leader|32,500|4,00,000|₹2L Gold + Goa|
|9|Diamond|65,000|6,00,000|₹3L Car + Bangkok|
|10|Crown|1,25,000|10,00,000|₹5L Car + Indonesia|
|11|King|2,50,000|15,00,000|₹7.5L Car + Switzerland|
|12|Global Icon|5,00,000|25,00,000|₹20L + Dubai|

- Rank auto-detected for display; the **one-time cash bonus is paid manually by admin** ("Pay Rank Bonus"), mirroring the reference.
- ❓ Confirm: is rank purely from cumulative total SP each leg, or matched SP, or does admin approve rank? (Reference stored a `level` field — admin-set?)
- ❓ Are the "+₹15k Mobile / Bike / Car / Gold" amounts **cash funds** too, or physical gifts fulfilled offline? (Currently only the first number is cash; rest is recognition text.)
- ❓ Rank maintenance/repurchase to keep a rank?

---

## 11. Direct Referral & Other Bonuses ✅ / ❓

- **Direct referral:** ₹500 to the sponsor when a directly-sponsored member greens (one-time). ❓ Is it ₹500 per direct, only first, or per-leg (the old sheet showed "Direct Ref 1/2 ₹500")?
- **Unilevel "level bonus":** built but **disabled** (`level_bonus_percent = []`) — not in your plan. ❓ Keep off?
- ❓ Any **repurchase/retail** income, **pool/turnover** bonus, or **leadership override** beyond matching + rank + referral?

---

## 12. Direct-Selling (DSA) Portal ✅

- Standalone agent (optional referral code, no tree). Greens on first purchase.
- Earns **40%** (`dsa_percent`) of the **taxable value (DP)** on their own confirmed orders → wallet.
- Dashboard: total sales, earnings, wallet, orders. Own orders + GST invoices.
- ❓ Confirm 40% flat, no downline/override for direct sellers.

---

## 13. Products & Catalog ✅

- 28 products (SP/MRP/DP from your list) + 4 offer packages (₹5k/12.5k/25k/50k). Categories: Immunity, Digestive, Skin Care, Wellness, Personal Care, Home Care, Offers.
- Admin CRUD (name, category, MRP, DP, cost, SP, stock, image, active, offer).
- ❓ Offer-package SP values are **estimates** (40/100/200/400) — give real values.

---

## 14. Orders & Payment (Admin-Confirm) ✅

- Member places order → **status `pending` / `unpaid`**. No SP/commissions yet.
- Member pays via **UPI/bank** (manual) per the Pay page.
- Admin **Confirms Payment** → SP propagation, greening, referral, DSA commission all run (once). Or **Cancels** (only if unpaid).
- No online gateway (your choice). ❓ Any payment-reference field the member should submit for the admin to match?

---

## 15. GST Invoicing ✅

- GST **18%**, **exclusive** (added on top of DP at checkout). GSTIN **09EJFPP4671A1Z5**, UP (state code 09), HSN default 30049011.
- Tax invoice per order: CGST+SGST (intra-state) or IGST (inter-state), amount-in-words, printable.
- Commissions computed on **taxable value**, not GST-inclusive total.
- ❓ Per-product HSN/GST rate (currently one default rate + HSN for all)?

---

## 16. KYC ✅

- 5 upload slots: profile photo, Aadhaar front/back, PAN front/back. Stored in DB (≤5MB, JPG/PNG/WEBP/PDF). Member uploads/replaces + previews; admin views. **No verification workflow** (per your instruction).
- ❓ Should greening/withdrawal require KYC uploaded/verified?

---

## 17. Wallet & Withdrawals ✅ / ❓

- Earnings (matching + rank + referral + DSA) credit `wallet_balance`.
- Member requests withdrawal (min ₹500 `payout_min`); admin approves → pays → rejects (refunds).
- Settings exist for `admin_charge_percent` (5%) and `tds_percent` (5%) but ❓ **not yet applied** to withdrawals — confirm the deduction rules (TDS %, admin charge %, on what).

---

## 18. Admin Panel ✅

Overview (members, active, pending orders, confirmed revenue, pending payouts) · Orders (confirm/cancel) · Products (CRUD) · Members (block, rank bonus, KYC, reset password) · Payouts (weekly close + withdrawal requests) · MLM Settings (all rates) · Weekly Close.
- ❓ Multiple admin roles/permissions needed, or single admin fine?

---

## 19. Configurable Settings (current defaults)

| Key | Value | Meaning |
|---|---|---|
| matching_per_sp | 10 | ₹ per matched SP |
| matching_block_sp | 50 | matching block size |
| daily_capping | 0 | matching cap (0=none) |
| direct_referral_bonus | 500 | ₹ per direct referral |
| dsa_percent | 40 | direct-seller commission % |
| activation_sp | 50 | SP to green an ID |
| repurchase_sp | 25 | (unused) monthly repurchase SP |
| gst_rate | 18 | GST % |
| price_gst_inclusive | false | DP is GST-exclusive |
| gstin | 09EJFPP4671A1Z5 | company GSTIN |
| payout_min | 500 | min withdrawal ₹ |
| admin_charge_percent | 5 | (not yet applied) |
| tds_percent | 5 | (not yet applied) |
| level_bonus_percent | [] | unilevel bonus (off) |

Ranks live in code (`app/services/ranks.py`) — ❓ move to editable settings?

---

## 20. API Reference (current)

**Auth:** `POST /api/auth/signup`, `/auth/direct/signup`, `/auth/login`, `/auth/admin/login`, `/auth/token`
**Member:** `GET/PUT /api/member/me`, `/member/dashboard`, `/member/direct/dashboard`, `/member/tree`, `/member/team`, `/member/level-bonus`, `/member/bonus`, `/member/payout-register`, `POST /member/change-password`, `GET/POST /member/kyc[/type][/file]`
**Catalog:** `GET /api/catalog/products`, `/catalog/categories`, `/catalog/products/{slug}`
**Orders:** `GET/POST /api/orders`, `GET /orders/{id}/invoice`
**MLM:** `GET /api/mlm/commissions`, `/mlm/payouts`, `POST /mlm/payouts`, `GET /mlm/idcard`
**Admin:** `/api/admin/overview`, `/members[...]`, `/members/{id}/{block,pay-rank-bonus,reset-password,kyc}`, `/orders[...]`, `/orders/{id}/{confirm,cancel}`, `/products[...]`, `/payouts`, `/payouts/close`, `/ranks`, `/settings`
**Site:** `GET /api/site/settings`, `GET /api/health`

---

## 21. Open Items / TODO

1. ❓ **Greening process** — full rules (§6) — TOP PRIORITY.
2. ❓ Green-to-green matching requirement (§9).
3. ❓ Repurchase/maintenance rules (§6.4, §10).
4. ❓ TDS + admin charge on withdrawals (§17).
5. ❓ Automatic weekly close (cron) vs manual.
6. ❓ Real offer-package SP values (§13).
7. 🔜 Offers / target-promotions section (deferred by you).
8. ❓ Direct-referral exact rule (§11).
9. ❓ Any other income types (pool/turnover/leadership) not covered.

---

_When you've filled the ❓ items, I'll update the engine + tests to match, then we finalize the backend._
