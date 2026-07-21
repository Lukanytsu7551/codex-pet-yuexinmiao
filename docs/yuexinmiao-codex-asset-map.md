# 月薪喵 Codex 桌宠资产映射表

## 素材源

本映射表按用户要求，全部采用 `myunwang/LLMPET` 仓库里的月薪喵图片。

- 本地素材目录：`/Users/yangxuan/Desktop/实习/codex pet/assets/yuexinmiao`
- 原仓库目录：`https://github.com/myunwang/LLMPET/tree/main/assets/cat`
- 署名文件：`CREDITS.md`
- 使用建议：个人本机使用；公开分发或商用前需确认原作者授权。

## Codex 高层状态映射

| Codex 状态 | 使用素材 |
|---|---|
| Running | `cat-working.gif`, `cat-working-2.gif`, `cat-working-3.gif`, `cat-working-4.gif`, `cat-thinking.gif`, `cat-thinking-2.gif`, `cat-talking.gif`, `cat-juggling.gif`, `cat-sweeping.gif` |
| Needs input | `cat-waiting.gif`, `cat-needsinput.gif` |
| Ready | `cat-happy.gif`, `cat-attention.gif`, `cat-greet.gif` |
| Blocked | `cat-error.gif`, `cat-sad.gif` |
| Idle/Low activity | `cat-idle.gif`, `cat-loafing.gif`, `cat-loafing-2.gif`, `cat-loafing-3.gif`, `cat-roam.gif`, `cat-sleeping.gif`, `cat-sleeping-2.gif` |

## Codex V2 Atlas 行映射

| Atlas 行 | Codex 动作 | 首选素材 | 备用/轮换素材 | 处理方式 |
|---|---|---|---|---|
| 0 | idle | `cat-idle.gif` | - | 抽帧后循环成 6 帧 |
| 1 | running-right | `cat-roam.gif` | `cat-working.gif` | 从行走/奔跑感素材抽帧，必要时水平偏移 |
| 2 | running-left | `cat-roam.gif` | `cat-working.gif` | 由 row 1 镜像生成，仍来自原素材 |
| 3 | waving | `cat-greet.gif` | - | 打招呼 |
| 4 | jumping | `cat-happy.gif` | `cat-attention.gif` | 完成后的短暂开心 |
| 5 | failed | `cat-error.gif` | - | 出错或阻塞 |
| 6 | waiting | `cat-waiting.gif` | - | 等授权；needsinput 只能折叠到该行 |
| 7 | running | `cat-working.gif`, `cat-working-2.gif`, `cat-working-3.gif`, `cat-working-4.gif` | `cat-talking.gif`, `cat-juggling.gif`, `cat-sweeping.gif` | 按 Running 语义采样轮换 |
| 8 | review | `cat-thinking.gif`, `cat-thinking-2.gif` | `cat-talking.gif` | 思考/审阅；talking 只能折叠到该行 |
| 9 | look directions 0-157.5 | `cat-idle.gif`, `cat-attention.gif`, `cat-needsinput.gif`, `cat-thinking.gif` | `cat-roam.gif` | 只能近似填充，不是真实方向素材 |
| 10 | look directions 180-337.5 | `cat-idle.gif`, `cat-loafing.gif`, `cat-sleeping.gif`, `cat-sad.gif` | `cat-roam.gif` | 只能近似填充，不是真实方向素材 |

## 全量素材清单

| 文件 | 原始语义 | Codex 用途 |
|---|---|---|
| `cat-working.gif` | 干活 | Running / atlas row 7 |
| `cat-working-2.gif` | 干活 | Running / atlas row 7 |
| `cat-working-3.gif` | 干活 | Running / atlas row 7 |
| `cat-working-4.gif` | 干活 | Running / atlas row 7 |
| `cat-thinking.gif` | 思考 | Review / atlas row 8 |
| `cat-thinking-2.gif` | 思考 | Review / atlas row 8 |
| `cat-talking.gif` | 输出回复 | Running 备用 / atlas row 7 or 8 |
| `cat-juggling.gif` | 并行子任务 | Running 备用 / atlas row 7 |
| `cat-sweeping.gif` | 清理上下文 | Running 备用 / atlas row 7 |
| `cat-waiting.gif` | 等授权 | Needs input / atlas row 6 |
| `cat-needsinput.gif` | 等回复 | Needs input / atlas row 6 |
| `cat-attention.gif` | 看一眼 | Ready / atlas row 3 or 4 |
| `cat-happy.gif` | 完成庆祝 | Ready / atlas row 4 |
| `cat-greet.gif` | 新会话打招呼 | Ready / atlas row 3 |
| `cat-error.gif` | 出错 | Blocked / atlas row 5 |
| `cat-sad.gif` | 伤心 | Blocked 备用 / atlas row 5 |
| `cat-idle.gif` | 待命 | Idle / atlas row 0 |
| `cat-loafing.gif` | 摸鱼 | Idle 备用 / atlas row 0 |
| `cat-loafing-2.gif` | 摸鱼 | Idle 备用 / atlas row 0 |
| `cat-loafing-3.gif` | 摸鱼 | Idle 备用 / atlas row 0 |
| `cat-roam.gif` | 闲逛 | Drag rows / atlas row 1-2 |
| `cat-sleeping.gif` | 睡觉 | Low activity / look row filler |
| `cat-sleeping-2.gif` | 睡觉 | Low activity / look row filler |

## 转换原则

1. 不新增角色图片，不调用图像生成重画月薪喵。
2. 允许从 GIF 中抽帧、裁剪、缩放、居中、镜像和补透明边。
3. 允许把同一个 GIF 的帧循环或采样到 8 帧。
4. `running-left` 可以由 `running-right` 镜像得到，因为仍然来自原始 GIF。
5. 第 9-10 行只能近似填充，因为原仓库没有 16 方向看向素材。
