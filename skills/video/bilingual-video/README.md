# bilingual-video

The **general layer for bilingual (zh+en) video production** with HyperFrames — independent of video type. Dual independent projects, edge-tts (Chinese) / Kokoro (English) narration with native word-boundary captions, the single-line iteration loop, the generated publishing pack (cover / chapters / platform copy), and 42 universal pitfalls. Route to a concrete workflow via `/hyperframes` first; this layer applies to all of them.

任何 HyperFrames 视频的中英双语生产通用层——与视频类型无关：双语独立工程、edge-tts（中文）/Kokoro（英文）配音与原生词边界字幕、单行重录迭代闭环、自动生成的发布物料包（封面/章节/平台文案）、42 条通用踩坑清单。

## Install / 安装

```bash
npx skills add Atituiset/skills --skill bilingual-video
```

## Contents / 内容

| Path | What / 用途 |
|---|---|
| `SKILL.md` | The skill itself / 技能本体 |
| `scripts/gen-voice.py` | edge-tts narration with native word boundaries / edge-tts 原生词边界配音 |
| `scripts/gen-publish-pack.mjs` | generates PUBLISHING.md: render + chapters + cover + seam probe + platform copy / 一键生成发布物料（成片/章节/封面/转场探针/平台文案） |
| `references/pitfalls.md` | 42 universal pitfalls / 42 条通用踩坑清单 |

## Related / 相关

- `bilingual-tech-explainer`（同仓库）：技术科普视频特化层，依赖本技能。
