# bilingual-tech-explainer

Turn a technical article or research notes into a **bilingual (zh+en) explainer video for programmers**. A delta layer on top of HyperFrames' official `faceless-explainer` workflow: dual independent projects, edge-tts/Kokoro narration with native word-boundary captions, a continuity kit (evolution rail, 0.45s stage scaffolding, wall cards), the publishing pack close-out, and 42 production-tested pitfalls.

把技术文章/调研文档做成**中英双语程序员科普视频**。基于 HyperFrames 官方 `faceless-explainer` 工作流的差异层：双语独立工程、edge-tts/Kokoro 配音 + 原生词边界字幕、连贯性三件套（演化 rail / 开场舞台骨架 / 边界卡片）、发布物料包收尾、42 条实战踩坑清单。

## Install / 安装

```bash
npx skills add Atituiset/skills --skill bilingual-tech-explainer
```

## Contents / 内容

| Path | What / 用途 |
|---|---|
| `SKILL.md` | The skill itself / 技能本体 |
| `scripts/gen-voice.py` | edge-tts narration with native word boundaries / edge-tts 原生词边界配音 |
| `recipes/agent-harness-explainer/` | Frozen recipe: design preset + storyboard skeleton / 冻结配方 |
| `examples/` | Reference case-frame implementation + OFL fonts / 案例帧参考实现 |
| `references/pitfalls.md` | 42 hard-won rules — read before dispatching agents / 42 条踩坑清单 |

## Proven in production / 实战案例

*"From One LLM Call to a Full Harness"* — 17-frame bilingual explainer (zh 3m33s / en 3m10s): LLM → context → ReAct → tool calling → memory → Harness, eight real harnesses compared, nine-way positioning map.

《从一次 LLM 调用到完整 Harness》双语科普视频：17 帧，zh 3m33s / en 3m10s。
