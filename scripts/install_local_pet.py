#!/usr/bin/env python3
"""Install the generated Yuexinmiao Codex pet into ~/.codex/pets."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "dist" / "yuexinmiao-codex-pet"
TARGET_DIR = Path.home() / ".codex" / "pets" / "yuexinmiao-codex-pet"


def main() -> None:
    required = ["pet.json", "spritesheet.webp"]
    missing = [name for name in required if not (PACKAGE_DIR / name).exists()]
    if missing:
        raise SystemExit(f"Missing generated files: {', '.join(missing)}. Run scripts/build_pet_atlas.py first.")

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    for name in required:
        shutil.copy2(PACKAGE_DIR / name, TARGET_DIR / name)

    print(f"Installed Codex pet to {TARGET_DIR}")
    print("Restart Codex or open the pet picker if the app does not refresh automatically.")


if __name__ == "__main__":
    main()

