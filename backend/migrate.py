"""
Supabase Migration Runner
=========================
Reads all SQL files from supabase/migrations/ in order and executes them
against your Supabase PostgreSQL database in a single command.

Usage:
    python migrate.py

Requires DATABASE_URL in backend/.env (found in Supabase Dashboard -> Settings -> Database -> Connection string -> URI)
"""

import os
import sys
import glob
import json
import urllib.request
import urllib.error

MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "supabase", "migrations")

# ---------------------------------------------------------------------------
# .env loader (zero dependencies)
# ---------------------------------------------------------------------------
def load_env_file(filepath=".env"):
    """Load key-value pairs from a .env file into os.environ."""
    paths = [
        filepath,
        os.path.join(os.path.dirname(__file__), filepath),
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, val = line.split("=", 1)
                            key = key.strip()
                            val = val.strip().strip('"').strip("'")
                            if key and key not in os.environ:
                                os.environ[key] = val
                return
            except Exception:
                pass

load_env_file()

# ---------------------------------------------------------------------------
# Collect migration files in sorted order
# ---------------------------------------------------------------------------
def get_migration_files():
    """Return a sorted list of .sql files in the migrations directory."""
    if not os.path.isdir(MIGRATIONS_DIR):
        print(f"[!] Migrations directory not found: {MIGRATIONS_DIR}")
        sys.exit(1)

    files = sorted(glob.glob(os.path.join(MIGRATIONS_DIR, "*.sql")))
    if not files:
        print("[!] No .sql migration files found.")
        sys.exit(1)

    return files

# ---------------------------------------------------------------------------
# Strategy 1: psycopg2 (direct PostgreSQL connection via DATABASE_URL)
# ---------------------------------------------------------------------------
def run_with_psycopg2(database_url, files):
    """Execute migrations using psycopg2 and a direct database connection."""
    import psycopg2

    print(f"[*] Connecting to database...")
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cur = conn.cursor()

    for filepath in files:
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            sql = f.read()
        try:
            print(f"  [+] Running: {filename} ...", end=" ")
            cur.execute(sql)
            print("OK")
        except Exception as e:
            print(f"FAILED\n      Error: {e}")

    cur.close()
    conn.close()
    print("\n[✓] All migrations completed successfully!")

# ---------------------------------------------------------------------------
# Strategy 2: Supabase Management API (uses SUPABASE_URL + service_role key)
# ---------------------------------------------------------------------------
def run_with_supabase_api(supabase_url, supabase_key, files):
    """
    Execute migrations via Supabase's /pg/query endpoint (requires service_role key).
    Falls back to printing manual instructions if the endpoint isn't available.
    """
    combined_sql = ""
    for filepath in files:
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            sql = f.read()
        combined_sql += f"\n-- ======= {filename} =======\n{sql}\n"

    # Try the /pg/query endpoint (available on some Supabase versions)
    endpoint = f"{supabase_url}/pg/query"
    payload = json.dumps({"query": combined_sql}).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status in (200, 201):
                print("[✓] All migrations executed via Supabase API!")
                return True
    except Exception:
        pass

    return False

# ---------------------------------------------------------------------------
# Strategy 3: Generate combined SQL for manual execution
# ---------------------------------------------------------------------------
def generate_combined_sql(files):
    """Combine all migration files into one SQL script for manual pasting."""
    output_path = os.path.join(os.path.dirname(__file__), "supabase", "combined_migration.sql")
    with open(output_path, "w", encoding="utf-8") as out:
        out.write("-- ============================================\n")
        out.write("-- COMBINED MIGRATION (auto-generated)\n")
        out.write("-- Paste this into Supabase SQL Editor and Run\n")
        out.write("-- ============================================\n\n")
        for filepath in files:
            filename = os.path.basename(filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                sql = f.read()
            out.write(f"-- ======= {filename} =======\n")
            out.write(sql)
            out.write("\n\n")
    return output_path

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    files = get_migration_files()

    print("=" * 55)
    print("  Supabase Migration Runner")
    print("=" * 55)
    print(f"\n  Found {len(files)} migration file(s):")
    for f in files:
        print(f"    - {os.path.basename(f)}")
    print()

    database_url = os.environ.get("DATABASE_URL", "").strip()
    supabase_url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip() or os.environ.get("SUPABASE_KEY", "").strip()

    # Strategy 1: Direct PostgreSQL via DATABASE_URL
    if database_url:
        try:
            import psycopg2  # noqa: F401
            run_with_psycopg2(database_url, files)
            return
        except ImportError:
            print("[!] DATABASE_URL is set but 'psycopg2' is not installed.")
            print("    Install it with: pip install psycopg2-binary")
            print("    Trying alternative methods...\n")

    # Strategy 2: Supabase Management API
    if supabase_url and supabase_key:
        print("[*] Attempting Supabase API method...")
        if run_with_supabase_api(supabase_url, supabase_key, files):
            return
        print("[!] API method not available. Generating combined SQL file...\n")

    # Strategy 3: Generate a combined .sql file for manual use
    output = generate_combined_sql(files)
    print("[✓] Combined migration file created:")
    print(f"    {output}\n")
    print("  How to apply it:")
    print("  1. Open your Supabase Dashboard -> SQL Editor -> New Query")
    print("  2. Paste the contents of the combined file above")
    print("  3. Click 'Run'\n")

    if not database_url:
        print("  TIP: For one-command migrations, add DATABASE_URL to backend/.env:")
        print("       DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres")
        print("       Then: pip install psycopg2-binary && python migrate.py\n")

if __name__ == "__main__":
    main()
