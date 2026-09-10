-- Arogyam Aradhya — migration to the final MLM rules.
-- Idempotent & non-destructive. Safe to run multiple times on the live Render DB.
-- (Already applied by the maintainer on 2026-09-10; re-running is harmless.)
-- Note: on a brand-new empty DB you don't need this — the app's startup
--       (`python -m app.seed`) creates all tables and seeds products/admin/founder.

BEGIN;

-- 1) New columns -------------------------------------------------------------
ALTER TABLE members         ADD COLUMN IF NOT EXISTS capping_limit    numeric(14,2) DEFAULT 0;
ALTER TABLE members         ADD COLUMN IF NOT EXISTS total_matched_sp numeric(14,2) DEFAULT 0;
ALTER TABLE payout_requests ADD COLUMN IF NOT EXISTS tds              numeric(12,2) DEFAULT 0;
ALTER TABLE payout_requests ADD COLUMN IF NOT EXISTS net              numeric(12,2) DEFAULT 0;

-- 2) Backfill weekly capping for already-green members by first-purchase tier -
UPDATE members SET capping_limit = 200000
  WHERE is_active AND self_purchase_sp >= 100 AND capping_limit = 0;
UPDATE members SET capping_limit = 100000
  WHERE is_active AND self_purchase_sp >= 50  AND self_purchase_sp < 100 AND capping_limit = 0;
UPDATE members SET capping_limit = 50000
  WHERE is_active AND self_purchase_sp >= 25  AND self_purchase_sp < 50  AND capping_limit = 0;

-- 3) Settings: set/confirm the final values ----------------------------------
INSERT INTO settings (key, value, label, "group", created_at, updated_at) VALUES
  ('gst_rate',        '5.0',    'GST rate % on products',                       'gst',         now(), now()),
  ('activation_sp',   '25.0',   'Self-purchase SP (cumulative) to green an ID', 'eligibility', now(), now()),
  ('capping_25sp',    '50000.0','Weekly cap (first purchase >=25 SP)',          'matching',    now(), now()),
  ('capping_50sp',    '100000.0','Weekly cap (first purchase >=50 SP)',         'matching',    now(), now()),
  ('capping_100sp',   '200000.0','Weekly cap (first purchase >=100 SP)',        'matching',    now(), now()),
  ('payout_day',      'Tuesday','Weekly payout closing day',                    'payout',      now(), now()),
  ('whatsapp_number', '919839227978', 'Company WhatsApp number (orders)',       'site',        now(), now()),
  ('whatsapp_message','Welcome to Arogyam Aradhya! Here is my order detail and invoice. Please guide me for payment to the Admin account so I get all benefits.', 'WhatsApp order intro message', 'site', now(), now())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

-- 4) Remove settings no longer used -----------------------------------------
DELETE FROM settings WHERE key IN (
  'direct_referral_bonus', 'admin_charge_percent', 'daily_capping',
  'mgmt_percent', 'company_profit_percent', 'product_cost_percent',
  'payout_min_percent', 'payout_max_percent', 'repurchase_sp', 'level_bonus_percent'
);

COMMIT;
