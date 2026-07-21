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
    {"row": 0, "state": "idle", "used": 6, "sources": ["cat-idle.gif"]},
    {"row": 1, "state": "running-right", "used": 8, "sources": ["cat-roam.gif"]},
    {"row": 2, "state": "running-left", "used": 8, "sources": ["cat-roam.gif"], "mirror": True},
    {"row": 3, "state": "waving", "used": 4, "sources": ["cat-greet.gif"]},
    {"row": 4, "state": "jumping", "used": 5, "sources": ["cat-happy.gif"]},
    {"row": 5, "state": "failed", "used": 8, "sources": ["cat-error.gif"]},
    {"row": 6, "state": "waiting", "used": 6, "sources": ["cat-waiting.gif"]},
    {
        "row": 7,
        "state": "running",
        "used": 6,
        "sources": ["cat-working.gif", "cat-working-2.gif", "cat-working-3.gif", "cat-working-4.gif"],
    },
    {"row": 8, "state": "review", "used": 6, "sources": ["cat-thinking.gif", "cat-thinking-2.gif"]},
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


LLMPET_STATE_SPECS = [
    {
        "state": "working",
        "label": "working 干活",
        "when": "正在调用工具 / 改文件",
        "sources": ["cat-working.gif", "cat-working-2.gif", "cat-working-3.gif", "cat-working-4.gif"],
        "codex_rows": [7],
    },
    {
        "state": "thinking",
        "label": "thinking 思考",
        "when": "提交提问后 / 工具间隙的长推理",
        "sources": ["cat-thinking.gif", "cat-thinking-2.gif"],
        "codex_rows": [8],
    },
    {
        "state": "talking",
        "label": "talking 回应中",
        "when": "模型正在输出回复文本",
        "sources": ["cat-talking.gif"],
        "codex_rows": [8],
        "codex_note": "Codex 原生 pet 没有 talking 行，归入 review/thinking 行。",
    },
    {
        "state": "juggling",
        "label": "juggling 并行子任务",
        "when": "召唤 subagent 多线开工",
        "sources": ["cat-juggling.gif"],
        "codex_rows": [7],
        "codex_note": "Codex 原生 pet 没有 juggling 行，归入 running/working 行。",
    },
    {
        "state": "sweeping",
        "label": "sweeping 清理",
        "when": "压缩 / 清理上下文",
        "sources": ["cat-sweeping.gif"],
        "codex_rows": [7],
        "codex_note": "Codex 原生 pet 没有 sweeping 行，归入 running/working 行。",
    },
    {
        "state": "waiting",
        "label": "waiting 等你授权",
        "when": "需要你点允许 / 拒绝",
        "sources": ["cat-waiting.gif"],
        "codex_rows": [6],
    },
    {
        "state": "needsinput",
        "label": "needsinput 等你回复",
        "when": "需要你选择 / 输入",
        "sources": ["cat-needsinput.gif"],
        "codex_rows": [6],
        "codex_note": "Codex 原生 pet 没有独立 needsinput 行，归入 waiting 行。",
    },
    {
        "state": "attention",
        "label": "attention 看一眼",
        "when": "任务刚结束提醒你",
        "sources": ["cat-attention.gif"],
        "codex_rows": [3, 4],
        "codex_note": "Codex 原生 pet 没有 attention 行，归入 waving/jumping。",
    },
    {
        "state": "happy",
        "label": "happy 完成庆祝",
        "when": "一轮任务干完",
        "sources": ["cat-happy.gif"],
        "codex_rows": [4],
    },
    {
        "state": "greet",
        "label": "greet 打招呼",
        "when": "新会话开始",
        "sources": ["cat-greet.gif"],
        "codex_rows": [3],
    },
    {
        "state": "error",
        "label": "error 出错",
        "when": "执行失败 / API 报错",
        "sources": ["cat-error.gif"],
        "codex_rows": [5],
    },
    {
        "state": "loafing",
        "label": "loafing 摸鱼",
        "when": "上一步干完、下一步还没来的间隙",
        "sources": ["cat-loafing.gif", "cat-loafing-2.gif", "cat-loafing-3.gif"],
        "codex_rows": [9, 10],
        "codex_note": "Codex 原生 pet 没有 loafing 行，只能保留在完整状态表或近似填入 look 行。",
    },
    {
        "state": "idle",
        "label": "idle 待命",
        "when": "没有任务",
        "sources": ["cat-idle.gif"],
        "codex_rows": [0],
    },
    {
        "state": "roam",
        "label": "roam 闲逛",
        "when": "长时间空闲",
        "sources": ["cat-roam.gif"],
        "codex_rows": [1, 2],
        "codex_note": "Codex 原生 pet 用 running-left/right 表示拖动移动，闲逛语义只能近似映射。",
    },
    {
        "state": "sleeping",
        "label": "sleeping 睡觉",
        "when": "会话结束 / 久无活动",
        "sources": ["cat-sleeping.gif", "cat-sleeping-2.gif"],
        "codex_rows": [10],
        "codex_note": "Codex 原生 pet 没有 sleeping 行，只能保留在完整状态表或近似填入 look 行。",
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


def write_state_map(output_dir: Path) -> None:
    state_map = {
        "source": "myunwang/LLMPET assets/cat",
        "native_codex_limitation": (
            "Codex native pets use fixed v2 atlas rows, not arbitrary LLMPET state names. "
            "The full LLMPET Yuexinmiao states are preserved here for documentation and previews; "
            "only the closest supported rows can be rendered by Codex itself."
        ),
        "states": LLMPET_STATE_SPECS,
    }
    (output_dir / "llmpet-state-map.json").write_text(
        json.dumps(state_map, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_state_gallery(path: Path) -> None:
    rows = []
    for spec in LLMPET_STATE_SPECS:
        imgs = "\n".join(
            f'<img src="../../../assets/yuexinmiao/{source}" alt="{source}" title="{source}">' for source in spec["sources"]
        )
        codex_rows = ", ".join(str(row) for row in spec["codex_rows"])
        note = spec.get("codex_note", "")
        rows.append(
            f"""
      <tr>
        <td class="images">{imgs}</td>
        <td><strong>{spec["label"]}</strong><br><span>{spec["state"]}</span></td>
        <td>{spec["when"]}</td>
        <td>Codex row {codex_rows}<br><span>{note}</span></td>
      </tr>"""
        )
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>月薪喵状态映射</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #20242a; }}
    h1 {{ font-size: 28px; margin-bottom: 8px; }}
    p {{ color: #59616c; line-height: 1.6; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 24px; }}
    th, td {{ border: 1px solid #d8dee6; padding: 14px; vertical-align: middle; text-align: left; }}
    th {{ background: #f6f8fa; }}
    img {{ width: 72px; height: 72px; object-fit: contain; margin-right: 8px; }}
    .images {{ min-width: 240px; }}
    span {{ color: #6b7280; font-size: 13px; }}
  </style>
</head>
<body>
  <h1>月薪喵皮肤 × 状态</h1>
  <p>这里是一一对应的 LLMPET 月薪喵 GIF 状态表。Codex 原生宠物只能播放固定 v2 atlas 行，所以部分 LLMPET 状态会折叠到最接近的 Codex 行。</p>
  <table>
    <thead>
      <tr><th>表情</th><th>状态</th><th>什么时候出现</th><th>Codex 原生映射</th></tr>
    </thead>
    <tbody>
      {"".join(rows)}
    </tbody>
  </table>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


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
    write_state_map(OUT_DIR)
    make_contact_sheet(atlas, QA_DIR / "contact-sheet.png")
    make_row_previews(atlas, QA_DIR / "previews")
    write_state_gallery(QA_DIR / "state-gallery.html")

    print(f"Wrote {spritesheet_webp}")
    print(f"Wrote {OUT_DIR / 'pet.json'}")
    print(f"Wrote {OUT_DIR / 'llmpet-state-map.json'}")
    print(f"Wrote {QA_DIR / 'contact-sheet.png'}")
    print(f"Wrote {QA_DIR / 'state-gallery.html'}")
    print(f"Wrote {QA_DIR / 'previews'}")


if __name__ == "__main__":
    main()
