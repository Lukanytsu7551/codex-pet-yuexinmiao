# Yuexinmiao Codex Pet

Personal Codex pet materials based on the Yuexinmiao skin assets from `myunwang/LLMPET`.

## Contents

- `assets/yuexinmiao/` - Yuexinmiao GIF assets copied from `LLMPET/assets/cat`
- `docs/codex-pet-design-yuexinmiao.md` - Codex pet design notes
- `docs/yuexinmiao-codex-asset-map.md` - mapping from LLMPET GIF assets to Codex pet states and v2 atlas rows

## Source And Attribution

The Yuexinmiao GIF assets are from:

- Repository: https://github.com/myunwang/LLMPET
- Source directory: https://github.com/myunwang/LLMPET/tree/main/assets/cat
- Attribution file: `assets/yuexinmiao/CREDITS.md`

The original `LLMPET` attribution notes that the cat meme GIFs come from Douyin creator `@月薪喵`.

## Usage Scope

This repository is intended for personal/local experimentation with a Codex pet. Do not publish, redistribute, or commercialize the Yuexinmiao assets without confirming permission from the original rights holder.

## Codex Pet Conversion Notes

Codex v2 pets use an 8x11 sprite atlas. The LLMPET Yuexinmiao assets are individual GIFs, so the intended conversion flow is:

1. Extract frames from the GIFs.
2. Scale and center frames into 192x208 cells.
3. Compose rows for idle, drag, greeting, completion, failed, waiting, running, and review states.
4. Fill the look-direction rows with existing GIF-derived frames as a best-effort approximation.
5. Package the final sprite sheet with `spriteVersionNumber: 2`.

The original Yuexinmiao assets do not include true 16-direction look sprites, so rows 9-10 of a Codex v2 atlas will be approximate unless new art is created.

