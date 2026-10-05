---
name: tldraw-video-assets
description: Wiring tldraw-exported SVG artwork into a deterministic video pipeline. The export is a document, not an image — labels are live HTML inside `<foreignObject>`, every label inlines a computed-style dump, declared boxes are padded far past the ink, and path data must be walked rather than paired two-by-two. Covers inline-don't-`<img>`, measuring ink, filtering the style dump out of hygiene scans, the decode failure that renders empty cream with no error, re-placing artwork on a new canvas as a beat stack, and verification by pixels. Pairs with the sibling `visual-storytelling`, which owns the design layer. Use when tldraw or hand-drawn diagram SVGs meet a seek-safe render: labels vanish, artwork measures absurd, a project scans as contaminated, or a composition renders blank or cropped. 把 tldraw 导出的手绘 SVG 接进确定性视频管线：导出物是文档不是图片，标签是 foreignObject 里的活 HTML，路径要真走不能两两配对，量墨不量盒子，验证靠像素。
---

# tldraw video assets (export → deterministic pipeline)

**Status: incubating** — see [skills/in-progress/](../README.md). Every number below was measured on the worked asset set in [`../visual-storytelling/examples/agent-article-beats/`](../visual-storytelling/examples/agent-article-beats/) (18 beat deltas + `final-frame.svg`) and on the composition code that consumes it.

## The boundary

| | owner |
|---|---|
| what a diagram should say, and in what order | [`../visual-storytelling`](../visual-storytelling/) — primitive grammar, beat sheet, progressive disclosure, the reveal contract, the family palette, arrow curvature, and the rule that no drawing tool's own animation may leak into an asset |
| what tldraw's exporter physically emits, and every trap downstream of that | **this skill** |

This skill owns the **integration** layer. It starts where that one hands off: an export on disk, a composition that must consume it, and a render that has to be provably right. Nothing here can be learned from the grammar, because none of it is about the grammar — a beat's *meaning* tells you nothing about the fact that its label is a live HTML subtree carrying 274 inlined longhand properties.

## The one law: read the export as source

tldraw's exporter emits a **document**, not a picture: HTML labels, an inlined computed-style dump, transform stacks, and the exporter's own opinions about how big a thing is. Every trap below is what happens when you skip that read. Act on it in this order:

1. **Inline it.** Never `<img>` — the label HTML and its `foreignObject` styling do not survive the reference; only inlining does.
2. **Measure ink, not boxes.**
3. **Scan properties, not text.**
4. **Verify by pixels.**
5. **Re-viewBox, never re-draw.**

## 1. The export is a document, not an image

Root element, verbatim from every file in the set:

```html
<svg xmlns="http://www.w3.org/2000/svg" direction="ltr" width="1280" height="720"
     viewBox="0 0 1280 720" stroke-linecap="round" stroke-linejoin="round"
     data-color-mode="light" class="tl-container tl-theme__force-sRGB tl-theme__light"
     style="background-color: transparent;">
```

Then a `<style>@import url("fonts.css");</style>`, then a flat run of `<g transform="matrix(1, 0, 0, 1, X, Y)" opacity="1" data-beat="N">` — one per shape, each a world translate and nothing else. Shape-local geometry sits in that group's own coordinates.

**A beat is not typeless.** Every label is live HTML in a camel-case `foreignObject`:

```html
<foreignObject x="-6" y="-6" width="202" height="36"
  class="tl-export-embed-styles tl-rich-text tl-rich-text-svg tl-text__outline">
  <div xmlns="http://www.w3.org/1999/xhtml" style="…274 longhands…">
    <div style="…274 longhands…">
      <p dir="auto" style="color: rgb(68, 101, 233); margin-block: 18px; …">Context · 办公桌</p>
```

Three consequences, all load-bearing:

- **The label carries the language of the drawing.** This set's 38 labels are Chinese (`邮件`, `数据库`, `只答不做`) or untranslated Latin product names (`LLM`, `CRM`, `MCP`, `Computer Use`, `Human-in-the-loop`). A bilingual project inherits exactly that set until it regenerates them.
- **A type floor you set applies to the art, not only to HTML you author.** The label type is inside the export, so it scales with the art and can fall under your floor. The working build scales the art's own `font-size` back up to hold a 24 px floor and *asserts* the lift never exceeds 1.90 — see `references/replacing-on-a-new-canvas.md`.
- **The case is `foreignObject`, which matters for any regex you write over the export.** Once that markup round-trips through an HTML parser the tag arrives lowercased, and a camelCase comparison silently skips every label — taking all the diagram's names out of the measured box and out of the plate.

Full element-by-element walkthrough: `references/export-anatomy.md`.

## 2. Inline it, and keep it deterministic

A `<foreignObject>` label inside an `<img>` silently disappears — no error, no empty box, just a diagram with no names. Inline the SVG into the composition. Inline it as **base64**, and assert an `<svg>` came back out:

```js
art.innerHTML = unb64(b[3]);               // b[3] is the beat's markup, base64
var svg = art.querySelector("svg");
if (!svg) throw new Error("band " + bi + " decoded to " + art.innerHTML.length
  + " chars and carries no <svg> — the base64 channel is corrupt");
```

Determinism is the other half. The export carries no animation, and none may be added: no tldraw shape or camera animation, no SMIL, no CSS keyframes, nothing wall-clock. Every reveal is the composition's job, driven by `hf-seek` time. (The *why* — that bilingual re-timing needs every reveal retimed per language, so anything baked into an asset fights it — is stated once in [`../visual-storytelling/SKILL.md`](../visual-storytelling/SKILL.md) § "The timing contract".)

Because every beat travels as markup through a string channel, watch the escaping. These exports contain `clip-path: url(&quot;#_export_8_r_2l__shape_mcp-arrow_clip&quot;)` inside a `style` attribute — real `&quot;` entities. Let one survive into a JSON payload and a *second* decode pass turns it into a raw `"` inside a JSON string; the composition then renders as **empty cream**, with no error anywhere. A composition can render "successfully" and be blank. Same lesson as the unstyled-template bug in [`../longform-series/references/render-pitfalls.md`](../longform-series/references/render-pitfalls.md): *the renderer exiting 0 is not evidence that anything was drawn.*

Base64 the channel, and keep the assert.

## 3. Measure ink, not boxes

Two traps, both of which produce a confident wrong number.

**The padding trap.** A `foreignObject` sized `width="202"` holds a short label, and `x`/`y` are offset by `-6` (or `-8`/`-8` at the other padding tier). The extreme case is in `beat-01.svg`: the label `用户` — two glyphs — declares `width="1413"`, and its real ink measures **36 × 24 px**. The declared box overstates its ink by ~39×. A bbox read off the export describes the box, not the ink, so estimate label ink from the text and its `font-size`, never from the box.

**The path-data trap.** Path `d` numbers must not be paired two-by-two. That is wrong for any path using `H`/`V` or implicit coordinate pairs, and catastrophic for a tldraw arrow whose shaft is authored in absolute coordinates while its head is a separate subpath — the first bbox pass reported a **1413 px "wide" arrow for a connector that is really 300 px long**, and every conclusion about whether the artwork fit its band rested on that number. The 1413 was a label box: in this asset set, `compositions/frames/02-wall-answer.html` holds both a `M 0 0 L 310 9` connector and two `width="1413"` label boxes in one document. Measured end to end on the worked set, the naive measure of `final-frame.svg` reads **2512 px wide**; the honest geometry is **1326 px**.

**The invisible-rect trap.** Every rough-stroked shape also carries a `<rect x="-100" y="-100" … opacity="0"/>` inside its clip group, sized to the shape's padded export box. One per rough-stroked shape, one `clipPath` alongside it — measured 38 of each across the set. They are never painted and they dominate a naive box: beat 5 reads **734 × 577** world units with them and **579 × 455** without.

The fix that worked is a real path-data walk that tracks the current point through `M/L/H/V/C/S/Q/T/A/Z` and their relative forms, returning control points too, plus a transform stack (`matrix`, `translate`, `scale`, `rotate`, `skewX`, `skewY`) for world coordinates. **Bias the error too large on purpose**: an over-estimate costs padding, an under-estimate silently crops. A working implementation, whose docstring is itself the incident report, is `/home/atituiset/Projects/skills/videos/ai-agent-primer-zh/scripts/svggeom.py` — pure stdlib, copy it anywhere.

Per-beat measurements for the worked set, and the full algorithm: `references/measurement-and-verification.md`.

## 4. Scan properties, not text — and never the dump

Every `foreignObject` child inlines a **full computed-style dump** through the `tl-export-embed-styles` class: **274 longhand properties** per dumped `<div>`, two dumped divs per label, ~6 KB of `style` attribute each, `will-change: auto` among them. One `will-change` per label, so a project carries **~300 literal `will-change: auto`** from a single artwork set.

So any scan for `will-change`, for CSS transitions, or for animation catches the dump and reports the project as contaminated. Measured: a naive scan returned **309 hits; all 309 were the inert default.** Two filters, both required:

- **Filter on the value.** `auto` is `will-change`'s *initial* value, so only a non-default value is authored.
- **Scan `<style>` blocks, not inline `style=""`.** Authored CSS lives in `<style>`; the dumps are excluded by construction.

The calibration lesson and the "a scan that cries wolf is worse than no scan" entry live in [`../longform-series/references/render-pitfalls.md`](../longform-series/references/render-pitfalls.md) — read it for the calibration discipline, not for the tldraw cause. [`../longform-series/scripts/check-hygiene.py`](../longform-series/scripts/check-hygiene.py) already implements both filters.

## 5. Verify by pixels

"Rendered without error" is **no evidence at all**. Three checks, in order, each run before anything downstream trusts the assets:

**Pixel equivalence** — stack the beats in `data-beat` order, composite, compare against `final-frame.svg`. Run on the worked set, this is exact: 18 beats stacked into one 1280×720 world rasterize to a **byte-identical** image to `final-frame.svg` — same MD5, **0 differing pixels of 921,600**, max channel delta 0. This is how the asset set was proven before any composition consumed it, and it is the only check that proves the deltas *compose*.

**Dark-pixel bbox** — decode the frame, mask every pixel whose distance from the known ground colour exceeds a tolerance, and take that mask's bounding box. On the worked set the painted ink measures **1222 × 663 px** inside its 1280×720 canvas. This is the check that catches a composition which rendered without error and is still wrong: edge-column ink, a collapsed plate, a band that never got its artwork.

Geometry and pixels are **separate gates, and they disagree in both directions**. The same world's ink-only geometry box is 1210 × 660 — over the raster on three edges (the control-point bias, working) and **10 px under it on the right**, which is one label's text-width estimate under-running on a mixed CJK/ASCII string. Only the raster finds that, and it is why measuring and verifying are two steps rather than one.

**Blank-frame check** — assert the channel decoded to markup containing an `<svg>` (§ 2), before rendering. Cheap, and it is the difference between finding the blank in a second and finding it in a delivery render.

## 6. Re-placing artwork on a new canvas: the beat stack

When a diagram that grows rightward has to grow **downward** — a 16:9 world cut to 9:16 — do not crop and do not scale the picture down. Stack the **delta** beats top to bottom in `data-beat` order, each re-`viewBox`'d to its own measured ink:

```js
svg.setAttribute("width", String(bw));     // bw, bh = this beat's ink × the band scale
svg.setAttribute("height", String(bh));
art.style.left = Math.round((968 - bw) / 2) + "px";   // centre it in the band
```

Four rules that only bite at this step:

- **Clip each band.** `[class~="bandart"] { overflow: hidden }` — a delta is a delta: arrowheads and label boxes reach past the shape they belong to, and letting them paint outside the band viewBox puts ink in the canvas edge columns. That is the clipping defect.
- **Namespace the ids.** tldraw's clipPath ids are beat-scoped (`_export_8_r_2l__shape_mcp-arrow_clip`), so two beats on one page can collide. Rewrite both `id="…"` and `url(#…)` per band.
- **Choose which beats the moment needs.** Several beats are meaningless in isolation — a delta is designed to be stacked *over* what is already there — so pick the beats that stand alone, and say which ones you left out.
- **Record every drop**, with the reason. A drop is a design decision, not an omission.

Working method, the per-beat lift arithmetic, and real dropped-artwork entries with their reasons: `references/replacing-on-a-new-canvas.md`.

## Pointers

| Read | When |
|---|---|
| `references/export-anatomy.md` | You have the file open and need to know what a part *is*: the root `<g>` shape wrapper, the fill/stroke pair per shape, the arrow's shaft-plus-separate-head, the `opacity="0"` clip rect, the `clipPath` id scheme, the two nested style dumps, the label box padding tiers, `fonts.css`. |
| `references/measurement-and-verification.md` | You are about to trust a number about this artwork: the path-data walk, the transform stack, the over-estimate bias, the `foreignObject` ink estimate, dropping invisible rects, the per-beat measurement table for the worked set, pixel equivalence, the dark-pixel bbox, the blank-frame check. |
| `references/replacing-on-a-new-canvas.md` | The canvas changes shape or size: the beat stack, per-beat `viewBox`, the type-lift arithmetic against a floor, choosing which beats a moment needs, recording what was dropped. |
| [`../visual-storytelling/SKILL.md`](../visual-storytelling/SKILL.md) | You need to know *what* to draw and in what order — before any of this applies. |
| [`../visual-storytelling/references/visual-grammar.md`](../visual-storytelling/references/visual-grammar.md) | You are casting concepts into primitives. |
| [`../longform-series/references/render-pitfalls.md`](../longform-series/references/render-pitfalls.md) | A render came out wrong with no error: blank frames, unstyled templates, the noise scan. |
| `/home/atituiset/Projects/skills/videos/ai-agent-primer-zh/scripts/svggeom.py` | Copy it. Pure-stdlib path walk + world bbox; its docstring is the incident report behind § 3. |

## Verification checklist

Run before a composition consumes the assets, and again after any re-placement. Each line is a gate: it passes or it is not done.

- [ ] Every beat inlines as **markup** (base64 or a file the build inlines). No `<img>`, no `<image href>` pointing at an SVG.
- [ ] Every band decodes to markup containing an `<svg>` — asserted at runtime, not assumed.
- [ ] Every `foreignObject` label **renders**, with its text in the language the composition needs. Read the rendered pixels; a present-but-empty `<foreignObject>` is the failure.
- [ ] Stacking beats 1..N in `data-beat` order is **pixel-identical** to `final-frame.svg` (0 differing pixels).
- [ ] Every reported size is **ink**, measured by walking path data and the transform stack, with `opacity="0"` rects dropped and label ink estimated from text + `font-size` — never from a declared box.
- [ ] Every measured box is **over** the truth — over on curves, over on label ink. Where it is not (the one under-run this pipeline's text estimate has), the dark-pixel check caught it.
- [ ] The hygiene scan **filters the dump**: `will-change` on value, and `<style>` blocks rather than inline `style=""`. A count above the project's known inert baseline is a finding.
- [ ] The render carries **no** motion of its own: no SMIL, no CSS keyframes, no wall-clock, no drawing-tool animation. All reveals are driven by `hf-seek` time.
- [ ] The dark-pixel bbox of the rendered frame sits inside the canvas with its intended margin, and the edge columns carry no ink.
- [ ] Re-placed bands: each has its own `viewBox` from its own ink, `overflow: hidden`, namespaced ids, and a label at or above the type floor.
- [ ] Every beat a moment did **not** use is recorded with its reason.