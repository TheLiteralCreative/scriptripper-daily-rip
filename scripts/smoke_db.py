"""Quick DB connectivity smoke test for the LIVE app path (asyncpg -> Neon).

Proves the running app — not just Alembic — can reach the database and see the
schema. Run from the repo root with the venv active:

    python scripts/smoke_db.py
"""
import asyncio
import sys
from pathlib import Path

# Put the project root (parent of scripts/) on the import path so `app` resolves
# regardless of where this script is launched from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from app.database import engine


async def main() -> None:
    async with engine.connect() as conn:
        n_tables = (
            await conn.execute(
                text(
                    "select count(*) from information_schema.tables "
                    "where table_schema = 'public'"
                )
            )
        ).scalar()
        n_users = (await conn.execute(text("select count(*) from users"))).scalar()
    await engine.dispose()
    print(
        f"OK - app connected to Neon over asyncpg. "
        f"public tables={n_tables}, users={n_users}"
    )


if __name__ == "__main__":
    asyncio.run(main())
