# Export anatomy

What a tldraw SVG export physically contains, element by element, and what each part obliges you to do. Every snippet below is verbatim from the worked asset set at [`../../visual-storytelling/examples/agent-article-beats/`](../../visual-storytelling/examples/agent-article-beats/) — 18 `beat-NN.svg` deltas plus `final-frame.svg` and `fonts.css`.

Read this with the file open. The rules are in [`../SKILL.md`](../SKILL.md); this is the map of the markup those rules are about.

## What the set is made of

```
beat-01.svg … beat-18.svg   one delta per beat, all on one shared 1280x720 world
final-frame.svg             the whole world in one export (315 KB)
fonts.css                   205 KB, one @font-face: tldraw_draw as a base64 woff2
```

Element census across the set plus `final-frame.svg`: 19 `<svg>`, 474 `<g>`, 384 `<path>`, 76 `<foreignObject>`, 152 `<div>`, 76 `<p>`, 72 `<defs>`, 72 `<clipPath>`, 72 `<rect>`. Path commands used: `M`, `L`, `C`, `Q`, `Z` — **absolute only**. No `H`/`V`, no relative forms, no arcs.

That last fact matters for honesty: this exporter emits only `M/L/C/Q/Z`. A walker still needs the `H`/`V`/relative/`A` branches, because a composition merges hand-authored marks and re-exported shapes into the same file, and because the failure those branches prevent is silent either way — but on *these* files the walker's value is control points, the transform stack, and the ink/box distinction, not `H`/`V`.

## The root

```html
<svg xmlns="http://www.w3.org/2000/svg" direction="ltr" width="1280" height="720"
     viewBox="0 0 1280 720" stroke-linecap="round" stroke-linejoin="round"
     data-color-mode="light" class="tl-container tl-theme__force-sRGB tl-theme__light"
     style="background-color: transparent;">
<style>@import url("fonts.css");</style>
```

`stroke-linecap`/`stroke-linejoin="round"` are set on the root and inherited by every stroke — the round join is what makes a hand-drawn wobble read as one continuous line.

`style="background-color: transparent"` is appended by the export. Strip it when you inline into a composition that owns its own ground; it is the only thing on the root that can fight a stage background.

**`fonts.css`.** Every export embeds a ~200 KB base64 `@font-face`; it was extracted once into the shared file and each `<defs>` replaced with `@import url("fonts.css")`. When the SVG is *inlined into a composition*, that `@import` resolves against the **document**, not the SVG — so `fonts.css` must sit beside the composition, or its contents must be pasted into the composition's `<style>`. The label type is `font-family: tldraw_draw, sans-serif` and nothing else resolves it.

## The shape wrapper

```html
<g transform="matrix(1, 0, 0, 1, 747, 472)" opacity="1" data-beat="8">
```

One per shape. `transform` is a pure world translate — `matrix(a,b,c,d,e,f)` with `a=d=1`, `b=c=0`, and `e,f` the shape's position in the 1280×720 world. `data-beat` is the stamp that makes a delta stackable. `opacity="1"` is constant.

Shape-local geometry sits in that group's own coordinates, so measuring anything means composing the transform stack down to the root.

## A geo shape: fill path, then outline path

```html
<path fill="#fcfffe" d="M 4 0 L 60 0 Q 64 0 64 4 L 64 36 Q 64 40 60 40 L 4 40 Q 0 40 0 36 L 0 4 Q 0 0 4 0"/>
<path stroke-width="2" d="M 3.9238 -0.3227 L 59.6877 0.3269 Q 63.6877 0.3269 63.6877 4.3269 L 64.1823 36.4432 …"
      fill="none" stroke="#099268"/>
```

Two paths, not one: an exact fill (sharp `Q` corners) and a separate wobbly outline stroke. This is what makes the draw-on reveal possible — a single filled blob could not be stroked on, which is the design-layer requirement stated in [`../../visual-storytelling/references/visual-grammar.md`](../../visual-storytelling/references/visual-grammar.md) ("fills as separate elements") showing up here as markup.

Note the second path is **two subpaths in one `d`**: the outer contour, then an echo of it a fraction of a unit inside.

```html
d="M 3.9238 -0.3227 … 3.9238 -0.3227  M 3.7969 -0.069 L 59.7156 -0.2517 … 3.7969 -0.069"
```

This is the **double-stroke wobble**, and it is the drawing's character, not noise. In `beat-03.svg` the same shape reads `L 275.7999 0.352` on the straight top edge and `L 280.4469 235.5948` on the right edge — a 4.65-unit difference between where the straight edge stops and where the rounded corner bulges, on a 281-unit shape. A walker that tracks only `L` endpoints misses that bulge; one that tracks `Q` control points too gets a genuine over-estimate.

**Recolour with tokens; do not re-draw.** The echo sits sub-unit inside the outer contour — measured on `beat-03.svg`: 13 vertices each, nearest-point offsets **0.06 to 1.11 units, mean 0.38**. So two lines land roughly one canvas pixel apart at target size, and a one-pixel smudge at 1920 is mud at 320. One stroke is the shape. If you drop the echo, record it as a decision ([`replacing-on-a-new-canvas.md`](replacing-on-a-new-canvas.md)).

## Arrows: shaft and head are separate paths

```html
<g transform="scale(1)">
  <defs>
    <clipPath id="_export_8_r_2l__shape_mcp-arrow_clip">
      <path d="M -100 -100 L 119 -100 L 119 142 L -100 142 Z"/>
    </clipPath>
  </defs>
  <g fill="none" stroke="#099268" stroke-width="2" stroke-linejoin="round"
     stroke-linecap="round" pointer-events="none">
    <g style="clip-path: url(&quot;#_export_8_r_2l__shape_mcp-arrow_clip&quot;);">
      <rect x="-100" y="-100" width="219" height="242" opacity="0"/>
      <path stroke-width="2" d="M 0 0 L 19 42"/>
    </g>
    <path d="M 19.591636693003856 36.02924074982993 L 19 42 L 14.124989155973722 38.50224796896261"/>
  </g>
</g>
```

Four things to read off this:

1. **The shaft is clipped.** `M 0 0 L 19 42` runs past the shape's bounds and the clip trims it. The clipPath is a padded rectangle at `(-100,-100)`.
2. **The head is a sibling of the clipped group, not part of it.** Three absolute points, written near the shaft's end but in the same local coordinates. A bbox that walks only the first `d`, or that pairs numbers across both, gets the arrow wrong in opposite directions.
3. **`&quot;` is real text in the file.** `style="clip-path: url(&quot;#…&quot;);"` — see the escaping hazard in [`../SKILL.md`](../SKILL.md) § 2.
4. **`pointer-events="none"`** on the stroke group. Inert; carried through verbatim.

**The invisible rect.** `<rect … opacity="0"/>` sits inside the clipped group, at `(-100,-100)`, sized to the shape's padded export box. One per rough-stroked shape, and exactly one `clipPath` beside it — 38 of each across the set. It is never painted, and it dominates any box computed without dropping it: `beat-05` measures **734 × 577** world units with these rects and **579 × 455** without.

Arrow curvature is authored as a real curve, not a `bend`:

```html
<path stroke-width="2" d="M 0 0 C 40.0931 -22.3915 74.3508 -53.9086 100 -92"
      stroke-dasharray="0.020166889095154503 4.134823382358042" stroke-dashoffset="0"/>
```

## The line shape

The `eval` clipboard's three rules and the sandbox fence are line shapes — the same clip machinery, with no head:

```html
<g stroke-width="3.5" fill="none" stroke="#1d1d1d">
  <path d="M 0 0 L 784 0" stroke-dasharray="0.0350015625 7.028061486486488" stroke-dashoffset="0.0175"/>
  <path d="M 784 0 L 784 578" stroke-dasharray="0.03524603658536586 7.10055339506173" stroke-dashoffset="0.0175"/>
  …
</g>
```

Note this one is **not** clipped and carries **no** `opacity="0"` rect — a plain rough stroke is authored whole. Four beats have zero invisible rects (`02`, `03`, `04`, `16`) and their boxes are unchanged by the filter; `beat-16` is the largest of them at **784 × 598**, and it is a plain dashed rule, so its strokes are authored whole.

**The dash numbers are the draw style.** A 0.035-unit dash against a ~7.03-unit gap is a dot; at `stroke-linecap="round"` each dot paints a `stroke-width`-diameter mark. Read as "the exporter renders the hand-drawn dash style", not as an animation hint.

## The label

```html
<foreignObject x="-6" y="-6" width="202" height="36"
  class="tl-export-embed-styles tl-rich-text tl-rich-text-svg tl-text__outline">
  <div xmlns="http://www.w3.org/1999/xhtml" style="…274 longhands, ~6 KB…">
    <div style="…274 longhands, ~6 KB…">
      <p dir="auto" style="color: rgb(68, 101, 233); interactivity: inert;
         margin-block: 18px; margin-bottom: 18px; margin-top: 18px;
         row-rule-color: rgb(68, 101, 233);">Context · 办公桌</p>
    </div>
  </div>
</foreignObject>
```

The four classes are the exporter's contract: `tl-export-embed-styles` (the dump), `tl-rich-text` + `tl-rich-text-svg` (a rich-text shape rendered into SVG), `tl-text__outline` (outline-mode text). `interactivity: inert` on the `<p>` is the exporter declaring the label non-interactive.

**Two dumped divs per label**, not one — 548 longhand declarations, ~12 KB of `style` attribute, and **one `will-change: auto` per label**. `fonts.css` contains zero `will-change`, `transition`, `animation`, or `@keyframes`; every one of them is in these dumps.

### Padding tiers

Two tiers, and neither describes the ink:

| Tier | Attributes | `height` | `font-size` | Labels |
|---|---|---|---|---|
| auto-width | `x="-6" y="-6"` | 36 | 18 | 35 of 38 — every diagram name |
| fixed-width | `x="-8" y="-8"` | 48 | 24 | 3 — `🧠`, `✓` ×2, and the closing `Claude Code · Codex · WorkBuddy` card |

The `36` is not arbitrary: the `<p>` carries `margin-block: 18px`, so 18 + 18 = 36 — the box height is two vertical margins. The `48` tier is the same shape at 24 px type.

### The widths are not the text

Measured per label, declared box vs estimated ink:

| `width` | label | ink | overstates by |
|---|---|---|---|
| `1417` | `🧠`, `✓` | 12.7 × 32.4 | **111×** |
| `1413` | `LLM`, `RAG`, `SOP`, `CRM`, `MCP` (3 Latin glyphs) | 33.5 × 24.3 | **42×** |
| `1413` | `用户` (two CJK glyphs) | 36.0 × 24.3 | **39×** |
| `1413` | `Memory · 笔记本` | 133.6 × 24.3 | 10.6× |
| `1413` | `Eval · 给 AI 做考试` | 165.6 × 24.3 | 8.5× |
| `148` | `✗ 只答不做` | 86.9 × 24.3 | 1.7× |
| `212` | `Agent · 数字员工` | 142.0 × 24.3 | 1.5× |
| `202` | `Context · 办公桌` | 143.1 × 24.3 | 1.4× |
| `222` | `Permission · Sandbox` | 186.1 × 24.3 | 1.2× |

**20 of the 38 labels declare `width="1413"`** and 3 declare `width="1417"`. That is the exporter's padded extent for a text shape whose width was never set in the editor: the same number for a two-glyph word and for a nineteen-character line. The overstatement runs from 1.2× to 111×, and it is *largest exactly where labels are shortest* — so a layout that trusts declared widths is wrong by most on the labels that carry least, which is how it survives review.

The fitted widths (`76`, `92`, `98`, `102`, `148`, `152`, `202`, `212`, `222`) are text shapes that *were* resized in the editor. Still padded, just less absurdly.

**The one place the ink estimate under-runs.** `Eval · 给 AI 做考试` estimates 165.6 px of advance width; the rasterised label reaches ~175.6. That is the `text_width` heuristic's own error — it is an estimate by design (CJK 1.0 em, Latin ~0.52, space 0.30, `·—…` 0.55) and mixed CJK/ASCII strings are where it slips. It is the one measurement in the chain that reports **under** the truth, and it is why geometry and pixels are separate gates ([`measurement-and-verification.md`](measurement-and-verification.md)).

### The language is the drawing's

All 38 labels in the set:

```
用户  🧠  LLM                          ✗ 只答不做              Context · 办公桌
✗ 桌上没有这份文件                     公司知识库  RAG  按意思搜索  ✓
Memory · 笔记本                         Tools · 手
MCP  邮件  CRM  数据库                  Skill · SOP 手册  SOP
Agent · 数字员工  ✓
观察  思考  行动  检查  工作循环
读取发票  识别金额  校验日期  检查制度  输出结果  Workflow · 提前写死
Multi-Agent · AI 团队                  Computer Use
人确认  Human-in-the-loop              Permission · Sandbox
Eval · 给 AI 做考试                     Claude Code · Codex · WorkBuddy
```

Bilingual or otherwise: a project inherits **one** language's labels. Regenerating them is a draw-side decision; here it means re-exporting, not editing the pipeline.

## The id scheme

```html
id="_export_8_r_2l__shape_mcp-arrow_clip"
id="_export_14_r_31__shape_cu-arrow_clip"
id="_export_17_r_37__shape_eval-line-1_clip"
```

`_export_<beat>_<shape>__<shape-name>_clip`. **Beat-scoped, not globally unique.** Two beats inlined on one page are fine; the same beat inlined twice — two panels, a repeated card, a cover that reuses a beat — collides, and `url(#…)` resolves to whichever came first. Namespace `id="…"` *and* `url(#…)` per placement before inlining.

## Round-tripping the markup

Two parser facts, both silent:

- **HTML lowercases tag names.** Once the markup goes through an HTML parser, `foreignObject` arrives as `foreignobject` — a camelCase tag comparison skips every label, taking all the diagram's names out of the measured box and out of the plate. CSS selectors have to be written lowercase too.
- **XML re-serialisation invents prefixes.** `ElementTree.tostring` emits `<html:div>` once the namespace declaration is stripped, and an undeclared prefix is not HTML — the label is dropped. Register the `html` prefix **and** leave `""` for SVG, because `register_namespace` keeps one prefix→URI map and claiming the empty prefix twice silently unregisters SVG so everything comes back as `ns0:`.

## The measurements to take before you trust anything

Full method in [`measurement-and-verification.md`](measurement-and-verification.md). The two that decide most arguments:

| | value |
|---|---|
| `final-frame.svg`, declared boxes and all | **1326 × 744** world units |
| `final-frame.svg`, invisible rects dropped | **1210 × 660** |
| the same frame, rasterised, ink measured from pixels | **1222 × 663** |
| `final-frame.svg` measured by pairing `d` numbers two-by-two | **2512 px wide** |

The middle row is the number to plan against. The last row is the number you get for free if you skip the walk — and it is not an error, it is a plausible-looking wrong answer.