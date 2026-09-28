# skills

[![ci](https://github.com/Atituiset/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/Atituiset/skills/actions/workflows/ci.yml)
[![release](https://img.shields.io/github/v/release/Atituiset/skills)](https://github.com/Atituiset/skills/releases)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**[中文文档](README.zh-CN.md)** · English

Agent skills that turn real production experience into repeatable workflows. Plain Markdown + CLI scripts, composable, agent-agnostic — they run on Kimi Code, Claude Code, OpenCode, Codex, or anything that can read a file and run a shell.

The current focus is **bilingual (zh+en) video production with HyperFrames** — born from shipping real explainer videos, not from theorizing about them.

## Installation (30-second setup)

**Any agent** (via the [skills CLI](https://github.com/vercel-labs/skills)):

```bash
npx skills add Atituiset/skills
```

Pick the skills you want and which agents to install them on. To grab one directly:

```bash
npx skills add Atituiset/skills --skill bilingual-tech-explainer
```

**Claude Code plugin**:

```
/plugin marketplace add Atituiset/skills
/plugin install atituiset-skills
```

**Manual** (you own the files, nothing updates behind your back):

```bash
cp -r skills/video/bilingual-video ~/.agents/skills/          # Kimi Code / generic
cp -r skills/video/bilingual-video ~/.claude/skills/          # Claude Code
cp -r skills/video/bilingual-video ~/.config/opencode/skills/ # OpenCode
```

## Demo

[![Four stages, one line — a bilingual explainer produced end-to-end by these skills](docs/assets/demo-cover-en.png)](https://www.youtube.com/watch?v=K8Yn8pRAOAM)

**[From one neuron (1943) to the inference race (2026)](https://www.youtube.com/watch?v=K8Yn8pRAOAM)** — a 14-frame bilingual explainer (en 3m49s / zh 3m51s) produced end-to-end by an agent running `bilingual-tech-explainer`: human-scenario opening, wall→fix narrative spine, phrase-level captions with no background pill. Chinese cut on Bilibili: **[从 1943 年的一个神经元，到 2026 年的推理效率竞赛](https://www.bilibili.com/video/BV1HLhR6zESm/)**.

## Why these skills exist

Producing a video with an agent is easy to start and painful to finish. These are the failure modes that kept recurring, and the skills that encode their fixes:

**#1: The two languages fight each other.** One timeline parameterized for zh+en looks efficient — until Chinese narration runs 15% longer and every reveal is mistimed in one language. The fix is boring and decisive: **two independent projects**, each timed to its own native TTS word boundaries. No Whisper alignment, no uniform rescaling.

**#2: The video feels like a rushed slideshow.** Every frame opens on a blank canvas while the official 0.5s transition lands on its head, and nothing connects scene to scene. The fix is a **continuity kit**: a persistent evolution rail across the whole film, a stage skeleton visible within the first 0.45s of every frame, and wall cards that visualize the narrative setup.

**#3: Iteration costs a full rebuild.** Changing one line of script meant regenerating everything. The fix is a **single-line loop**: re-record only that line, re-sync durations, re-time only that frame, rebuild only its captions. Minutes, not an evening.

These fixes were extracted from a shipped production — *"From One LLM Call to a Full Harness"*, a 17-frame bilingual explainer (zh 3m33s / en 3m10s) — and condensed into 42 hard-won rules covering arrow geometry, CJK font subsetting, WCAG ghost text, seek-safety and the publishing close-out.

## Skills

### [video](skills/video/)

| Skill | What it does |
|---|---|
| [bilingual-video](skills/video/bilingual-video/) | The general layer for **any** bilingual HyperFrames video — dual projects, narration + word-boundary captions, iteration loop, generated publishing pack, 42 universal pitfalls. |
| [bilingual-tech-explainer](skills/video/bilingual-tech-explainer/) | Turns a technical article into a bilingual explainer for programmers — wall→fix narrative spine, continuity kit, teaching blueprints. Depends on `bilingual-video` plus the official [`faceless-explainer`](https://github.com/heygen-com/hyperframes) workflow. |

More domains are coming; the layout and its growth rules live in [skills/README.md](skills/README.md).

## Usage

Tell your agent:

> Read the bilingual-tech-explainer skill and turn this article (path/URL) into a bilingual explainer video for Bilibili and YouTube. Working directory: videos/<project>.

The agent runs the official faceless-explainer pipeline (scaffold → design preset → storyboard & script → narration → per-frame builders → assembly → checks → render); the skills supply the delta layer.

## Repository conventions

- **Layout**: `skills/<category>/<skill>/`, governed by [ADR-0001](.agents/adr/0001-skill-directory-layout.md). Categories grow when real skills need them — no empty scaffolding.
- **Lifecycle**: incubating skills live in `skills/in-progress/`; retired skills move to `skills/deprecated/`, never deleted.
- **Project layout produced by the video skills**:

  ```
  videos/<name>-zh/   # Chinese project (build first, full pipeline)
  videos/<name>-en/   # English project (copy zh frames → translate → re-time to word boundaries)
  ```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Decisions that change conventions are recorded as ADRs in [.agents/adr/](.agents/adr/).

## License

MIT (see [LICENSE](LICENSE)). Third-party font files under `skills/video/bilingual-tech-explainer/examples/assets/fonts/` keep their original licenses (EB Garamond / Inter / JetBrains Mono / Noto Sans SC — all OFL).
