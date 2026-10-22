"""Pre-launch data reset for the live production database.

Run this YOURSELF, from your own machine — never paste your production
DATABASE_URL into a chat with anyone, including an AI assistant. This script
reads the connection string from an environment variable or interactive
prompt so it never has to appear in a command's argv (which could otherwise
leak into shell history).

What it does — same as docs/go_live_reset.sql:
  1. Deletes all orders, order items, SP ledger, commission ledger, payout
     requests, weekly payouts, and KYC documents (all pre-launch test data).
  2. Deletes every member except the founder root (AA10000001), and resets
     the founder's wallet/SP/rank stats to zero.
  3. Deletes all products and categories so the next app boot's `app.seed`
     (which the Docker CMD runs automatically on every restart) repopulates
     the fresh product catalog.
  4. Upserts the current contact/GST/WhatsApp settings.

Usage:
    cd backend
    .venv/bin/python scripts/go_live_reset.py

It will prompt for the DATABASE_URL (input hidden, not echoed) and then
require you to type RESET to confirm before touching anything. Safe to run
only ONCE right before go-live — re-running it after real signups begin
would also wipe real data.
"""
from __future__ import annotations

import getpass
import os
import sys

import psycopg

STATEMENTS = [
    "DELETE FROM order_items",
    # sp_ledger.order_id references orders, so it must go before orders.
    "DELETE FROM sp_ledger",
    "DELETE FROM orders",
    "DELETE FROM commission_ledger",
    "DELETE FROM payout_requests",
    "DELETE FROM weekly_payouts",
    "DELETE FROM kyc_documents",
    "DELETE FROM members WHERE member_id <> 'AA10000001'",
    """
    UPDATE members SET
      wallet_balance = 0, total_earned = 0, total_paid = 0,
      left_carry = 0, right_carry = 0,
      total_left_sp = 0, total_right_sp = 0, total_matched_sp = 0,
      self_purchase_sp = 0, week_left_sp = 0, week_right_sp = 0,
      capping_limit = 0, rank_level = 0, rank_bonus_paid_level = 0,
      is_blocked = false
    WHERE member_id = 'AA10000001'
    """,
    "DELETE FROM products",
    "DELETE FROM categories",
]

SETTINGS = [
    ("support_phone", "+91 95328 21223", "Support phone", "site"),
    ("support_email", "adminarogyamaradhya@gmail.com", "Support email", "site"),
    ("address", "Aradhya Bhavan, Jakhania, Gobind, Ghazipur, Uttar Pradesh", "Company address", "site"),
    ("whatsapp_number", "919532821223", "Company WhatsApp number (orders)", "site"),
    ("company_address", "Aradhya Bhavan, Jakhania, Gobind, Ghazipur, Uttar Pradesh", "Company address on invoice", "gst"),
    ("price_gst_inclusive", "true", "Are DP/MRP prices GST-inclusive?", "gst"),
]

SETTINGS_UPSERT = """
    INSERT INTO settings (key, value, label, "group", created_at, updated_at)
    VALUES (%s, %s, %s, %s, now(), now())
    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
"""


def main() -> None:
    dsn = os.environ.get("DATABASE_URL") or getpass.getpass(
        "Production DATABASE_URL (input hidden, paste and press Enter): "
    ).strip()
    if not dsn:
        print("No connection string given. Aborting.")
        sys.exit(1)

    confirm = input(
        "\nThis will PERMANENTLY delete all orders, commissions, payouts, KYC docs,\n"
        "every member except the founder root, and the full product catalog.\n"
        "Type RESET to continue: "
    )
    if confirm.strip() != "RESET":
        print("Not confirmed. Aborting — nothing was changed.")
        sys.exit(1)

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            for stmt in STATEMENTS:
                cur.execute(stmt)
                label = stmt.strip().splitlines()[0][:60]
                print(f"  {label} -> {cur.rowcount} row(s)")
            for key, value, label, group in SETTINGS:
                cur.execute(SETTINGS_UPSERT, (key, value, label, group))
                print(f"  setting '{key}' upserted")
        conn.commit()

    print("\nDone. Now trigger a Manual Deploy / Restart on Render so `python -m "
          "app.seed` repopulates categories + the new product catalog.")


if __name__ == "__main__":
    main()
