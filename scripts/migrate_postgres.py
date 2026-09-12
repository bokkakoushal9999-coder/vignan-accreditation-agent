"""
PostgreSQL Cloud Migration & Validation Script for VFSTR AI Accreditation Agent.
Allows one-command setup, migration, and verification of the accreditation database
on PostgreSQL (Supabase, Neon, AWS RDS, GCP Cloud SQL, or local Postgres).

Usage:
    python scripts/migrate_postgres.py [--url postgresql://user:pass@host:5432/dbname] [--seed]
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import create_engine, inspect, text
from core.models import Base
from core.database import (
    get_engine, get_session_factory, get_db_session, database_health_check,
    ACCREDITATION_DB_PATH
)
from core.seed_database import _perform_seed


def migrate_to_postgres(postgres_url: str, seed: bool = True):
    """
    Initializes tables on PostgreSQL and optionally migrates or seeds data.
    """
    print(f"[*] Initializing PostgreSQL Cloud Database...")
    if postgres_url.startswith("postgres://"):
        postgres_url = postgres_url.replace("postgres://", "postgresql://", 1)

    # 1. Create Engine with connection pool
    try:
        pg_engine = create_engine(
            postgres_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300
        )
        with pg_engine.connect() as conn:
            res = conn.execute(text("SELECT version();")).scalar()
            print(f"[+] Successfully connected to PostgreSQL server:")
            print(f"    {res}")
    except Exception as e:
        print(f"[-] Failed to connect to PostgreSQL: {e}")
        return False

    # 2. Create Schema / Tables
    print(f"[*] Creating 15 relational tables via SQLAlchemy metadata...")
    Base.metadata.create_all(bind=pg_engine)
    inspector = inspect(pg_engine)
    created_tables = inspector.get_table_names()
    print(f"[+] Successfully verified {len(created_tables)} tables in PostgreSQL:")
    for t in sorted(created_tables):
        print(f"    - {t}")

    # 3. Seed initial multi-framework data
    if seed:
        print(f"[*] Seeding multi-framework accreditation dataset (NAAC, NBA, NIRF, 45 evidence records)...")
        from sqlalchemy.orm import sessionmaker
        SessionMaker = sessionmaker(bind=pg_engine)
        session = SessionMaker()
        try:
            _perform_seed(session)
            session.commit()
            print(f"[+] Seeding complete! Database is fully initialized for cloud operation.")
        except Exception as e:
            session.rollback()
            print(f"[-] Error while seeding: {e}")
        finally:
            session.close()

    # 4. Final Diagnostics
    print(f"\n[*] Table Record Counts on PostgreSQL:")
    with pg_engine.connect() as conn:
        for t in sorted(created_tables):
            cnt = conn.execute(text(f"SELECT COUNT(*) FROM {t};")).scalar()
            print(f"    {t:28} : {cnt} rows")

    print(f"\n[✓] Cloud migration complete! Set DATABASE_URL={postgres_url} in your cloud environment.")
    return True


if __name__ == "__main__":
    # Ensure fresh .env variables are loaded
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and v:
                            os.environ[k] = v
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="VFSTR Accreditation PostgreSQL Migration Tool")
    parser.add_argument("--url", help="PostgreSQL connection string (e.g. postgresql://user:pass@host:5432/db)")
    parser.add_argument("--seed", dest="seed", action="store_true", default=True, help="Seed baseline criteria and evidence data (default: True)")
    parser.add_argument("--no-seed", dest="seed", action="store_false", help="Skip data seeding")

    args = parser.parse_args()
    target_url = args.url or os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")

    if not target_url:
        print("[-] Error: No PostgreSQL URL provided.")
        print("    --> If you edited the .env file, please make sure to SAVE it (press Ctrl + S in your editor).")
        print("    --> Or pass the URL directly: python scripts/migrate_postgres.py --url \"postgresql://user:pass@host:5432/db\" --seed")
        sys.exit(1)

    if "<username>" in target_url or "<password>" in target_url or "<database_name>" in target_url:
        print(f"[-] Error: Target URL contains placeholder brackets: {target_url}")
        print("    --> Please replace <username>, <password>, and <database_name> with your real credentials.")
        sys.exit(1)

    migrate_to_postgres(target_url, seed=args.seed)
