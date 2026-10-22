-- Arogyam Aradhya — pre-launch data reset for the live Render Postgres DB.
-- Wipes all test members, orders, and transactional data while keeping the
-- founder root (AA10000001) and the admin login. Also clears products /
-- categories so the next app boot (`python -m app.seed`, which the Docker
-- CMD runs automatically on every restart) repopulates the fresh 36-item
-- catalog from the updated seed.py.
--
-- How to run (do this yourself — don't hand your DB credentials to anyone,
-- including an AI assistant, to run this for you):
--   1. Render dashboard → your Postgres (arogyam-db) → "Connect" → copy the
--      "PSQL Command" (or External Connection string) and run it in your
--      own terminal, or use Render's web Shell tab if offered.
--   2. Paste/run this whole file: \i docs/go_live_reset.sql
--   3. After it finishes, go to the web service → "Manual Deploy" →
--      "Deploy latest commit" (or "Restart Service") so the container reboots
--      and `python -m app.seed` repopulates categories + products.
--
-- Safe to run only ONCE right before go-live. Re-running it later would also
-- wipe real member/order data created after launch — don't re-run blindly.

BEGIN;

-- 1) Transactional / ledger data — delete everything (all pre-launch noise).
--    sp_ledger.order_id references orders, so it must go before orders.
DELETE FROM order_items;
DELETE FROM sp_ledger;
DELETE FROM orders;
DELETE FROM commission_ledger;
DELETE FROM payout_requests;
DELETE FROM weekly_payouts;
DELETE FROM kyc_documents;

-- 2) Members — delete everyone except the founder root.
DELETE FROM members WHERE member_id <> 'AA10000001';

-- 3) Reset the founder's own accumulated stats to a clean slate.
UPDATE members SET
  wallet_balance    = 0,
  total_earned      = 0,
  total_paid        = 0,
  left_carry        = 0,
  right_carry       = 0,
  total_left_sp     = 0,
  total_right_sp    = 0,
  total_matched_sp  = 0,
  self_purchase_sp  = 0,
  week_left_sp      = 0,
  week_right_sp     = 0,
  capping_limit     = 0,
  rank_level        = 0,
  rank_bonus_paid_level = 0,
  is_blocked        = false
WHERE member_id = 'AA10000001';

-- 4) Catalog — clear so the next boot's seed() repopulates the new 36-item
--    catalog with the correct MRP/DP/SP and photos.
DELETE FROM products;
DELETE FROM categories;

-- 5) Settings — bring contact info / GST / WhatsApp number up to date in case
--    this production DB already has stale rows from a previous deploy.
INSERT INTO settings (key, value, label, "group", created_at, updated_at) VALUES
  ('support_phone',       '+91 95328 21223',  'Support phone',   'site', now(), now()),
  ('support_email',       'adminarogyamaradhya@gmail.com', 'Support email', 'site', now(), now()),
  ('address',             'Aradhya Bhavan, Jakhania, Gobind, Ghazipur, Uttar Pradesh', 'Company address', 'site', now(), now()),
  ('whatsapp_number',     '919532821223',     'Company WhatsApp number (orders)', 'site', now(), now()),
  ('company_address',     'Aradhya Bhavan, Jakhania, Gobind, Ghazipur, Uttar Pradesh', 'Company address on invoice', 'gst', now(), now()),
  ('price_gst_inclusive', 'true',             'Are DP/MRP prices GST-inclusive?', 'gst', now(), now())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

COMMIT;
