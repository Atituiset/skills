# skills

[![ci](https://github.com/Atituiset/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/Atituiset/skills/actions/workflows/ci.yml)
[![release](https://img.shields.io/github/v/release/Atituiset/skills)](https://github.com/Atituiset/skills/releases)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**[English](README.md)** · 中文文档

把真实生产经验固化成可复用工作流的 agent skills 集合。纯 Markdown + CLI 脚本，可组合、跨 agent——Kimi Code、Claude Code、OpenCode、Codex 或任何能读文件跑 shell 的 agent 都能驱动。

当前重点是**用 HyperFrames 生产中英双语视频**——从真实交付的科普片里长出来的，不是纸上谈兵。

## 安装（30 秒）

**任意 agent**（通过 skills CLI）：

```bash
npx skills add Atituiset/skills
```

安装器会让你挑选要装的技能和目标 agent。直接装某一个：

```bash
npx skills add Atituiset/skills --skill bilingual-tech-explainer
```

**Claude Code 插件**：

```
/plugin marketplace add Atituiset/skills
/plugin install atituiset-skills
```

**手动复制**（文件归你所有，不会被静默更新）：

```bash
cp -r skills/video/bilingual-video ~/.agents/skills/          # Kimi Code / 通用
cp -r skills/video/bilingual-video ~/.claude/skills/          # Claude Code
cp -r skills/video/bilingual-video ~/.config/opencode/skills/ # OpenCode
```

## Demo

[![四个阶段，一条线——由本仓库技能端到端产出的双语科普视频](docs/assets/demo-cover-en.png)](https://www.youtube.com/watch?v=K8Yn8pRAOAM)

**[从 1943 年的一个神经元，到 2026 年的推理效率竞赛](https://www.youtube.com/watch?v=K8Yn8pRAOAM)**——14 帧双语科普片（en 3m49s / zh 3m51s），agent 运行 `bilingual-tech-explainer` 端到端产出：人话场景开场、撞墙→补墙叙事、无底版短语级字幕。中文版（B站）：**[从 1943 年的一个神经元，到 2026 年的推理效率竞赛](https://www.bilibili.com/video/BV1HLhR6zESm/)**。

## 为什么做这些技能

用 agent 做视频，开始容易收尾难。这些是反复出现的失败模式，以及固化进技能的修法：

**#1：两种语言互相打架。** 一条时间轴参数化中英双语看似高效——直到中文配音长出 15%，另一种语言的每个 reveal 全部错位。修法朴素但决定性：**两个独立工程**，各自按本语言 TTS 原生词边界定时。不走 Whisper 对齐，不做均匀缩放。

**#2：成片像赶场幻灯片。** 官方 0.5s 转场落在每帧开头，观众反复看到空白画布，场景之间毫无关联。修法是**连贯性三件套**：贯穿全片的演化 rail、每帧 0.45 秒内就位的舞台骨架、把叙事铺垫可视化的边界卡片。

**#3：迭代一次等于重来一遍。** 改一行文案就要全片重生成。修法是**单行闭环**：只重录该行 → 回写时长 → 只重定时该帧 → 只重建该帧字幕。几分钟，而不是一晚上。

这些修法提炼自真实交付的作品——《从一次 LLM 调用到完整 Harness》（17 帧双语科普，zh 3m33s / en 3m10s）——并沉淀为 42 条实战规则，覆盖箭头几何、CJK 字体子集化、WCAG ghost text、seek 安全、发布收尾等。

## 技能列表

### [video](skills/video/)

| 技能 | 用途 |
|---|---|
| [bilingual-video](skills/video/bilingual-video/) | **任何双语视频**的通用生产层——双工程、配音与词边界字幕、迭代闭环、自动生成的发布物料包、42 条通用踩坑清单。 |
| [bilingual-tech-explainer](skills/video/bilingual-tech-explainer/) | 把技术文章做成中英双语程序员科普视频——撞墙→补墙叙事骨架、连贯性三件套、教学蓝图。依赖 `bilingual-video` 和官方 [`faceless-explainer`](https://github.com/heygen-com/hyperframes) 工作流。 |

更多领域陆续加入；目录结构与生长规则见 [skills/README.md](skills/README.md)。

## 使用

对你的 agent 说：

> 读 bilingual-tech-explainer 技能，把这篇文章（附路径/链接）做成中英双语科普视频，发布到 B站和 YouTube。工作目录：videos/<工程名>。

agent 会走官方 faceless-explainer 流水线（脚手架 → 设计预设 → 分镜脚本 → 配音 → 子代理建帧 → 装配 → 校验 → 渲染），差异层由技能接管。

## 仓库约定

- **目录结构**：`skills/<类目>/<技能>/`，由 [ADR-0001](.agents/adr/0001-skill-directory-layout.md) 治理。类目随真实技能生长，不建空目录。
- **生命周期**：孵化中的技能进 `skills/in-progress/`；淘汰的移入 `skills/deprecated/`，不删除。
- **视频技能产出的工程布局**：

  ```
  videos/<name>-zh/   # 中文工程（先做，全流程）
  videos/<name>-en/   # 英文工程（复制 zh 帧 → 翻译 → 按词边界重定时）
  ```

## 参与贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。凡改变约定的决策都以 ADR 记录在 [.agents/adr/](.agents/adr/)。

## License

MIT（见 [LICENSE](LICENSE)）。第三方字体文件（`skills/video/bilingual-tech-explainer/examples/assets/fonts/`）保留各自原始许可证（EB Garamond / Inter / JetBrains Mono / Noto Sans SC 均为 OFL）。
