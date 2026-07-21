# 为什么不能按 LLMPET 状态直接显示每个 GIF

Codex 原生 pet 和 LLMPET 的状态机制不同。

LLMPET 是一个独立 Electron 桌宠，它可以自己监听 hook 事件，然后按 `working`、`thinking`、`talking`、`juggling`、`sweeping`、`loafing`、`sleeping` 等自定义状态直接切换 GIF。

Codex 原生 pet 不是这种任意状态 GIF 播放器。它读取的是一个固定 v2 sprite atlas：

- 8 列 × 11 行
- 每格 192×208
- 总尺寸 1536×2288
- `spriteVersionNumber: 2`

Codex v2 atlas 的标准行是固定的：

| 行 | Codex 原生含义 |
|---|---|
| 0 | idle |
| 1 | running-right |
| 2 | running-left |
| 3 | waving |
| 4 | jumping |
| 5 | failed |
| 6 | waiting |
| 7 | running |
| 8 | review |
| 9 | look directions 000-157.5 |
| 10 | look directions 180-337.5 |

所以，图片里的月薪喵状态需要折叠映射：

| LLMPET 状态 | Codex 原生近似行 |
|---|---|
| working | running |
| thinking | review |
| talking | review |
| juggling | running |
| sweeping | running |
| waiting | waiting |
| needsinput | waiting |
| attention | waving / jumping |
| happy | jumping |
| greet | waving |
| error | failed |
| loafing | 无原生行，仅保留在完整状态表或近似填充 look 行 |
| idle | idle |
| roam | running-right / running-left |
| sleeping | 无原生行，仅保留在完整状态表或近似填充 look 行 |

本项目现在同时产出两套结果：

1. `dist/yuexinmiao-codex-pet/spritesheet.webp`：Codex 原生可安装的 v2 pet。
2. `dist/yuexinmiao-codex-pet/llmpet-state-map.json` 和 `qa/state-gallery.html`：完整 LLMPET 月薪喵状态到 GIF 的一一对应表。

如果未来要做到真正的 `talking/juggling/sweeping/loafing` 独立状态切换，就不能只靠 Codex 原生 pet，需要做一个 LLMPET 风格的独立桌宠应用或等待 Codex 暴露自定义状态切换接口。

