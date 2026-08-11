"""
scripts/seed_course_index.py

Reads backend/assets/index.txt, extracts every URL that contains 192.168.10.3,
decodes the URL-encoded Chinese path segments, identifies the level-1 directories
(top-level course folders), and creates a CourseProduct record for each with a
random unit price if one does not already exist.

Run from the backend/ directory:
    PYTHONPATH=. python3 scripts/seed_course_index.py
"""
from __future__ import annotations

import asyncio
import random
from pathlib import Path
from urllib.parse import unquote

from db.session import init_models, session_scope
from models.academic import CourseProduct
from models.branch import Branch
from sqlalchemy import select

ASSET_PATH = Path(__file__).parent.parent / "assets" / "index.txt"
INDEX_BASE = "http://192.168.10.3:8000/"

random.seed(99)


def extract_level1_dirs() -> list[str]:
    """Return sorted list of unique decoded level-1 directory names."""
    dirs: set[str] = set()
    with ASSET_PATH.open(encoding="utf-8") as fh:
        for raw in fh:
            url = raw.strip()
            if not url or "192.168.10.3" not in url:
                continue
            if not url.startswith(INDEX_BASE):
                continue
            remainder = url[len(INDEX_BASE):]
            parts = remainder.strip("/").split("/")
            if parts and parts[0]:
                dirs.add(unquote(parts[0]))
    return sorted(dirs)


async def seed() -> None:
    await init_models()

    dirs = extract_level1_dirs()
    print(f"Found {len(dirs)} level-1 directories in index.txt:")
    for d in dirs:
        print(f"  {d}")

    async with session_scope() as db:
        branch = (await db.execute(select(Branch).limit(1))).scalar_one_or_none()
        if branch is None:
            print("\nNo branch found in database. Run scripts/seed.py first.")
            return

        existing_names: set[str] = set(
            (await db.execute(select(CourseProduct.name))).scalars().all()
        )

        created = 0
        for i, name in enumerate(dirs, start=1):
            if name in existing_names:
                print(f"  [skip] {name} (already exists)")
                continue
            price = round(random.uniform(1980.0, 9800.0), 2)
            product = CourseProduct(
                seq=i,
                name=name,
                product=name,
                difficulty=random.randint(2, 5),
                unit_price=price,
                duration_spec="45分钟/次",
                branch_id=branch.id,
                info=f"来自本地服务器课程目录：{name}",
                goal="",
            )
            db.add(product)
            created += 1
            print(f"  [create] {name}  ¥{price:,.2f}")

        await db.commit()
        print(f"\nDone. Created {created} new course product(s).")


if __name__ == "__main__":
    asyncio.run(seed())
