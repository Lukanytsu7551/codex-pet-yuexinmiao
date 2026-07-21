#!/usr/bin/env python3
"""Build a Codex v2 pet atlas from LLMPET Yuexinmiao GIF assets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageSequence


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "yuexinmiao"
OUT_DIR = ROOT / "dist" / "yuexinmiao-codex-pet"
QA_DIR = OUT_DIR / "qa"

CELL_W = 192
CELL_H = 208
COLS = 8
ROWS = 11
ATLAS_W = CELL_W * COLS
ATLAS_H = CELL_H * ROWS


ROW_SPECS = [
    {"row": 0, "state": "idle", "used": 6, "sources": ["cat-idle.gif", "cat-loafing.gif"]},
    {"row": 1, "state": "running-right", "used": 8, "sources": ["cat-roam.gif"]},
    {"row": 2, "state": "running-left", "used": 8, "sources": ["cat-roam.gif"], "mirror": True},
    {"row": 3, "state": "waving", "used": 4, "sources": ["cat-greet.gif", "cat-attention.gif"]},
    {"row": 4, "state": "jumping", "used": 5, "sources": ["cat-happy.gif"]},
    {"row": 5, "state": "failed", "used": 8, "sources": ["cat-error.gif", "cat-sad.gif"]},
    {"row": 6, "state": "waiting", "used": 6, "sources": ["cat-waiting.gif", "cat-needsinput.gif"]},
    {
        "row": 7,
        "state": "running",
        "used": 6,
        "sources": ["cat-working.gif", "cat-working-2.gif", "cat-working-3.gif", "cat-working-4.gif"],
    },
    {"row": 8, "state": "review", "used": 6, "sources": ["cat-thinking.gif", "cat-thinking-2.gif", "cat-talking.gif"]},
    {
        "row": 9,
        "state": "look-directions-a",
        "used": 8,
        "sources": ["cat-thinking.gif", "cat-needsinput.gif", "cat-attention.gif", "cat-roam.gif"],
        "approximate": True,
    },
    {
        "row": 10,
        "state": "look-directions-b",
        "used": 8,
        "sources": ["cat-idle.gif", "cat-loafing.gif", "cat-sleeping.gif", "cat-sad.gif"],
        "approximate": True,
    },
]


def iter_gif_frames(path: Path) -> list[Image.Image]:
    with Image.open(path) as im:
        frames = []
        for frame in ImageSequence.Iterator(im):
            frames.append(frame.convert("RGBA"))
    if not frames:
        raise ValueError(f"No frames found in {path}")
    return frames


def flatten_sources(files: Iterable[str]) -> list[tuple[str, Image.Image]]:
    frames: list[tuple[str, Image.Image]] = []
    for name in files:
        path = ASSET_DIR / name
        if not path.exists():
            raise FileNotFoundError(path)
        source_frames = iter_gif_frames(path)
        for frame in source_frames:
            frames.append((name, frame))
    return frames


def sample_frames(frames: list[tuple[str, Image.Image]], count: int) -> list[tuple[str, Image.Image]]:
    if count <= 0:
        return []
    if len(frames) == 1:
        return frames * count
    if len(frames) >= count:
        indexes = [round(i * (len(frames) - 1) / max(count - 1, 1)) for i in range(count)]
        return [frames[i] for i in indexes]
    sampled = []
    for i in range(count):
        sampled.append(frames[i % len(frames)])
    return sampled


def fit_cell(frame: Image.Image, mirror: bool = False) -> Image.Image:
    image = frame.convert("RGBA")
    if mirror:
        image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    bbox = image.getbbox()
    if bbox:
        image = image.crop(bbox)

    max_w = 168
    max_h = 176
    scale = min(max_w / image.width, max_h / image.height, 1.0 if max(image.size) >= 180 else 1.35)
    new_size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
    image = image.resize(new_size, Image.Resampling.LANCZOS)

    cell = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    x = (CELL_W - image.width) // 2
    y = (CELL_H - image.height) // 2
    cell.alpha_composite(image, (x, y))
    return cell


def make_contact_sheet(atlas: Image.Image, path: Path) -> None:
    label_h = 28
    sheet = Image.new("RGBA", (ATLAS_W, ATLAS_H + ROWS * label_h), (245, 245, 245, 255))
    for row in range(ROWS):
        src_box = (0, row * CELL_H, ATLAS_W, (row + 1) * CELL_H)
        dst_y = row * (CELL_H + label_h) + label_h
        sheet.alpha_composite(atlas.crop(src_box), (0, dst_y))
    sheet.save(path)


def make_row_previews(atlas: Image.Image, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for spec in ROW_SPECS[:9]:
        frames = []
        for col in range(spec["used"]):
            frame = atlas.crop((col * CELL_W, spec["row"] * CELL_H, (col + 1) * CELL_W, (spec["row"] + 1) * CELL_H))
            frames.append(frame)
        if not frames:
            continue
        frames[0].save(
            output_dir / f"row-{spec['row']:02d}-{spec['state']}.gif",
            save_all=True,
            append_images=frames[1:],
            duration=160,
            loop=0,
            disposal=2,
        )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)

    atlas = Image.new("RGBA", (ATLAS_W, ATLAS_H), (0, 0, 0, 0))
    build_manifest = {
        "cell": {"width": CELL_W, "height": CELL_H},
        "atlas": {"width": ATLAS_W, "height": ATLAS_H, "columns": COLS, "rows": ROWS},
        "rows": [],
        "notes": [
            "Rows 9-10 are best-effort fillers because the source GIFs do not include true 16-direction look sprites.",
            "All imagery is derived from assets/yuexinmiao GIF files.",
        ],
    }

    for spec in ROW_SPECS:
        source_frames = flatten_sources(spec["sources"])
        sampled = sample_frames(source_frames, spec["used"])
        for col, (source, frame) in enumerate(sampled):
            cell = fit_cell(frame, mirror=bool(spec.get("mirror")))
            atlas.alpha_composite(cell, (col * CELL_W, spec["row"] * CELL_H))

        build_manifest["rows"].append(
            {
                "row": spec["row"],
                "state": spec["state"],
                "used_columns": list(range(spec["used"])),
                "sources": spec["sources"],
                "mirrored": bool(spec.get("mirror")),
                "approximate": bool(spec.get("approximate")),
            }
        )

    spritesheet_png = OUT_DIR / "spritesheet.png"
    spritesheet_webp = OUT_DIR / "spritesheet.webp"
    atlas.save(spritesheet_png)
    atlas.save(spritesheet_webp, "WEBP", lossless=True, quality=100, method=6)

    pet_manifest = {
        "id": "yuexinmiao-codex-pet",
        "displayName": "月薪喵 Codex Pet",
        "description": "A personal Codex pet assembled from LLMPET Yuexinmiao GIF assets.",
        "spriteVersionNumber": 2,
        "spritesheetPath": "spritesheet.webp",
    }
    (OUT_DIR / "pet.json").write_text(json.dumps(pet_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "build-manifest.json").write_text(
        json.dumps(build_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    make_contact_sheet(atlas, QA_DIR / "contact-sheet.png")
    make_row_previews(atlas, QA_DIR / "previews")

    print(f"Wrote {spritesheet_webp}")
    print(f"Wrote {OUT_DIR / 'pet.json'}")
    print(f"Wrote {QA_DIR / 'contact-sheet.png'}")
    print(f"Wrote {QA_DIR / 'previews'}")


if __name__ == "__main__":
    main()
