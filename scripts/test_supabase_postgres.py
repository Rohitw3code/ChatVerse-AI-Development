"""
Simple script to test a connection to your Supabase Postgres database.

It reads credentials from environment variables (preferably via your .env):
- PSQL_USERNAME
- PSQL_PASSWORD
- PSQL_HOST
- PSQL_PORT (default: 5432)
- PSQL_DATABASE
- PSQL_SSLMODE (default: require)

Usage:
  python scripts/test_supabase_postgres.py

Exit codes:
  0 on success, 1 on failure.
"""
from __future__ import annotations

import os
import sys
from typing import Tuple

try:
    # Load .env if present (python-dotenv is in requirements)
    from dotenv import load_dotenv
    load_dotenv()  # looks for .env in current working directory
except Exception:
    # dotenv is optional for environments where vars are already exported
    pass

try:
    import psycopg  # psycopg v3
except Exception as e:
    print("[ERROR] psycopg is not installed. Ensure 'psycopg-binary' is in requirements.")
    print(f"Details: {e}")
    sys.exit(1)


def read_config() -> Tuple[dict, list]:
    """Read DB connection config from environment and return (params, missing_keys)."""
    required_keys = [
        "PSQL_USERNAME",
        "PSQL_PASSWORD",
        "PSQL_HOST",
        "PSQL_DATABASE",
    ]
    optional_defaults = {
        "PSQL_PORT": "5432",
        "PSQL_SSLMODE": "require",
    }

    missing = [k for k in required_keys if not os.getenv(k)]

    params = {
        "user": os.getenv("PSQL_USERNAME"),
        "password": os.getenv("PSQL_PASSWORD"),
        "host": os.getenv("PSQL_HOST"),
        "port": int(os.getenv("PSQL_PORT", optional_defaults["PSQL_PORT"])),
        "dbname": os.getenv("PSQL_DATABASE"),
        "sslmode": os.getenv("PSQL_SSLMODE", optional_defaults["PSQL_SSLMODE"]),
        "connect_timeout": 10,
    }
    return params, missing


def test_connection() -> bool:
    params, missing = read_config()
    if missing:
        print("[ERROR] Missing required environment variables:", ", ".join(missing))
        print("Hint: create/update your .env file or export vars before running.")
        return False

    print("Attempting to connect to Postgres...")
    for k, v in params.items():
        # Avoid printing the password
        if k == "password":
            display = "<redacted>"
        else:
            display = v
        print(f"  {k}: {display}")

    try:
        with psycopg.connect(**params) as conn:
            with conn.cursor() as cur:
                # Basic sanity checks
                cur.execute("SELECT 1")
                one = cur.fetchone()

                cur.execute("SELECT version(), current_database(), now()")
                version, dbname, now_ts = cur.fetchone()

        print("\n[OK] Connected successfully!")
        print(f"  SELECT 1 => {one}")
        print(f"  version => {version}")
        print(f"  database => {dbname}")
        print(f"  now() => {now_ts}")
        return True
    except Exception as e:
        print("\n[ERROR] Failed to connect or run queries:")
        print(f"  {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    ok = test_connection()
    sys.exit(0 if ok else 1)
