---
name: visual-storytelling
description: Turn an article or topic into a growing hand-drawn cartoon diagram world for explainer videos — progressive visual disclosure (one world that grows beat by beat, never per-scene redraws), a fixed visual grammar of primitives (Actor / Container / Tool / Flow / Gate …), and a narration-anchored beat sheet that renders to static SVG scene assets. Timing is never baked into assets — HyperFrames owns the timeline, so bilingual (zh+en) re-timing stays independent. Pairs with this repo's bilingual-video and bilingual-tech-explainer skills (in this repo under skills/video/). Use when an explainer video or deck needs cartoon / hand-drawn diagrams that build up step by step to teach abstract concepts (LLM, RAG, Agent, system architecture, processes). 把抽象知识变成逐步生长的手绘卡通图解。
---

# Visual storytelling (narrative → growing diagram world)

**Status: incubating.** Distilled from design discussion plus one worked example (`examples/agent-article-beats.md`), which has since been rendered end-to-end — 18 per-beat delta SVGs + a final frame, stacked and pixel-verified — and the rules below were revised from that run (family palette, delta export, draw-on handoff, label/geometry mechanics). No video has shipped with it yet; when a rule breaks in production, fix the rule here in the same commit.

**Dependencies**: none required to produce assets; to turn assets into a film, pair with this repo's `bilingual-video` (dual-project timing, captions) and `bilingual-tech-explainer` (wall→fix narrative spine, continuity kit).

Bundled material (`<SKILL_DIR>` = this skill's directory):
- `references/visual-grammar.md` — the primitive catalog: every primitive's meaning and canonical composition, plus fixed diagram syntaxes for recurring concept patterns (RAG, Skill, Workflow, MCP, agent loop, multi-agent, human-in-the-loop, eval) and the composition style rules (family palette, arrow curvature, label mechanics, draw-on readiness)
- `examples/agent-article-beats.md` — a complete beat sheet for a real article (LLM/RAG/Agent/Skill explainer), the thing to copy for format and granularity
- `examples/agent-article-beats/` — that beat sheet rendered: 18 delta SVGs (`beat-01.svg` … `beat-18.svg`), `final-frame.svg` (whole world), and the shared `fonts.css`

## The one law: progressive visual disclosure

Build **one world that grows**, never a stack of independently drawn scenes. The viewer watches a chatbot grow into an Agent; they are never shown the finished architecture diagram and walked through it.

Concretely:

- Objects, once revealed, **persist**. Later beats add to them, connect them, transform them in place, or enclose them — they do not get redrawn in a new style or position without a narrative reason.
- Each beat carries **one narrative event**: one arrival on stage plus whatever that arrival causes. A bridge landing *and* the wall it crossed flipping ✗→✓ is one event (one beat); two unrelated arrivals are two beats — split them.
- The finished diagram is the last beat, never the first. A complete architecture chart narrated top-to-bottom is the anti-pattern this skill exists to prevent.

This is the diagram-layer expression of the continuity kit in `bilingual-tech-explainer`: the same principle (evolution rail, persistent stage) applied to the diagram's content, not just its chrome.

## The timing contract: assets carry none

The diagram layer owns **what is drawn**; the video layer owns **when it appears**. This is a hard contract, not a style choice:

- Every beat renders to a **static, seek-safe asset** (SVG, or SVG + a scene manifest naming its groups). No embedded animation, no SMIL, no CSS keyframes, no wall-clock anything inside the asset.
- Every "animation" the viewer sees (draw-on, fade, grow, camera move) is produced at composition time by HyperFrames revealing or transforming pre-drawn elements, driven by `hf-seek` time.
- Never let a drawing tool's own animation features (tldraw shape/camera animation, `setTimeout` draw-on effects) into the pipeline. Bilingual production re-times every reveal to each language's TTS word boundaries (zh runs ~15% longer than en); any timing baked into an asset fights that and loses.

When rendering, group each beat's newly revealed elements under an SVG `id`/`data-beat` attribute so the composition can target exactly that group.

Default reveal handed downstream (so assets must be built for it): per `data-beat` group, **draw strokes on** (stroke-dashoffset along each path/arrow/rule) and **fade fills and labels in**. That requires every primitive to be stroke-able vector paths in the hand-drawn dash style with fills as separate elements — an asset flattened into one filled blob cannot be drawn on.

## Workflow

### Step 1: Teaching spine

Extract the narrative order before any drawing. If the source is a technical article, apply the wall→fix spine from `bilingual-tech-explainer` (each concept enters because the previous layer hit a wall). The spine for the worked example: chatbot answers but can't act → it doesn't know your company's data → it forgets you → it has no hands → it needs an SOP → … → digital employee.

**Done when**: you can state, in one sentence per concept, *why it appears now* — as a limitation of what is already on screen.

### Step 2: Cast concepts into primitives

Map every concept in the spine to the fixed vocabulary in `references/visual-grammar.md`. Prefer the catalog's canonical composition over inventing a new drawing; invent only when no primitive fits, and add the new primitive to the catalog in the same commit. Fixed grammar is what makes the second video look like it belongs to the same series as the first — free-form drawing per scene is the failure mode.

**Done when**: every concept in the spine has a primitive (or a declared new one), and no primitive in the beat sheet appears only once without a narrative reason.

### Step 3: Beat sheet

Write the beat sheet (format below), one beat per narration-driven reveal, anchored to script lines. Granularity: 12–18 beats for a 3–5 minute explainer; if beats outnumber script paragraphs, merge them.

**Done when**: reading only the beat sheet's `reveal`/`action` lines in order reproduces the teaching spine from Step 1, and the final beat equals the article's summary diagram.

### Step 4: Render assets

Render each beat's **delta** as SVG — only the shapes that beat adds, all in one shared 1280×720 world coordinate system so the composition can stack them in beat order — plus one `final-frame` export of the whole world for the closing shot. Toolchain, in order of preference:

1. **Hand-authored SVG** — best control, zero dependencies; most primitive diagrams are rectangles, arrows, and labels.
2. **rough.js** — when the hand-drawn wobble should be generated rather than drawn; pure SVG output, no DOM needed.
3. **tldraw SDK** — for dense multi-beat worlds where arrow bend, rotation, rich text, and programmatic export earn the setup (the worked example used this). Its SVG export needs a browser environment (DOM measurement), so it runs in a headless page, not a plain Node script. Do not adopt it for the wobble alone — rough.js covers that.

Production notes from the worked example (tldraw path):

- Export per beat with `editor.getSvgString(ids, { bounds: new Box(0, 0, 1280, 720), background: false, padding: 0 })`, `ids` = that beat's shapes only; then verify export order against creation order and stamp each root `<g>` with `data-beat` before writing the file.
- Text exports as `<foreignObject>` → compositions must **inline** the SVG; an `<img>` reference silently drops all text.
- Every export embeds a ~200 KB base64 `@font-face`. Extract it once into `fonts.css`, replace each file's `<defs>` with `@import url("fonts.css")` — assets shrink ~70% and still open standalone while the css sits beside them. When SVGs are inlined into a composition, that `@import` resolves against the *document*, not the SVG: copy `fonts.css` next to the composition or paste its contents into the composition's `<style>`.
- Geo shapes with an inline label impose a minimum height (the label grows the box) — small labelled boxes get a fixed-width overlay text shape instead, or a wall card grows and starts reading as a different object.
- Arrow `bend` is an absolute sagitta in px. Arrows that ride a ring must bow *outward* with it — the bend sign flips with direction, so check the rendered curve against the ring every time.

Verify each SVG opens standalone (`fonts.css` beside it), exposes `data-beat` groups, and contains no script/SMIL/animation; stacking beats 1..N must reproduce the world's state at beat N.

**Done when**: every beat has a delta asset plus there is a final-frame asset, stacked previews match the frames you reviewed, and the final frame visually matches the article's own summary diagram if it has one.

### Step 5: Hand off to the video pipeline

Hand assets + beat sheet to the video skill (`bilingual-video` / `bilingual-tech-explainer`), which composes reveals onto narration word boundaries per language. Inline the SVGs (never `<img>` — foreignObject text vanishes), stack the deltas in beat order on one canvas, ship `fonts.css` beside the composition, and reveal each `data-beat` group with the default draw-on recipe from the timing contract — re-timed per language. The beat sheet's `at` anchors are narration *lines*, not timestamps — timestamps are derived downstream, per language.

## Beat sheet format

Deliberately minimal — a beat sheet, not a scene IR. Do not add fields "for future renderers"; a field earns its place only when a real render needs it.

```yaml
scene: <kebab-case-id>
objects:
  - id: llm
    primitive: actor        # a vocabulary entry from references/visual-grammar.md
    label: LLM
    metaphor: brain         # the cartoon rendering hint
    position: center
beats:
  - at: "最早我们使用 AI，就是你问一句、它答一句"
    reveal: llm
  - at: "但是它不知道你们公司的差旅制度"
    reveal: rag
    connect: llm -> rag
  - at: "把这些组合起来，它就不再是顾问，而是员工"
    action:
      type: enclose         # draw a container around existing objects
      targets: [llm, rag]
      label: Agent
```

Action vocabulary: `reveal` (object appears), `connect` (flow arrow between existing objects), `mutate` (object changes state in place — e.g. barrier card flips ✗→✓), `enclose` (container wraps targets, object becomes a system), `annotate` (label/callout on existing objects), `exit` (object leaves, rare — prefer mutation). A beat carries `reveal`/`connect` plus one `action`; when a single narrative event needs several — a bridge reveal plus the wall flip it causes, an enclose plus the mutation that lands with it — use `actions:` (a list) instead.

## Style baseline

Hand-drawn cartoon: slightly wobbly strokes (draw dash style), rounded corners, flat fills. Color encodes the **concept family** and stays fixed for the whole series — never re-colored per scene: blue = knowledge & context (desk, kb, RAG, docs), green = hands & verification (tools, MCP, systems, computer use, eval, ✓), orange = methods (skill, workflow), violet = the agent itself (enclosure, loop, team, products), yellow = human & memory (user, gate, notebook), red = walls, grey = annotations, ink = structure lines. Text in diagrams is minimal — the narration carries the explanation; labels carry only identity. See each primitive's canonical composition in `references/visual-grammar.md` before styling anything new.
