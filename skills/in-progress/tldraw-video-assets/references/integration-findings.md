# Integration findings from a second tldraw artwork set

The worked example in `../visual-storytelling/examples/agent-article-beats/` taught the SKILL's
§1–§6. This file is the second set's findings — a **GPU-scheduling** world rendered with
tldraw 3.15.6, built into a bilingual 19-frame HyperFrames film, shipped to
`hyperframes check` with 0 errors and 186/186 WCAG AA text checks. Every number here was
measured on that run; the assets live in
`/home/atituiset/Projects/skills/videos/chunked-prefill-zh/assets/beats/` and the tooling in
that project's `scripts/` (`render-beats.py`, `stile-labels.py`, `theme-check.py`,
`measure-beats.py`) — copy them, don't re-derive them.

Two of these findings are about the **toolchain version**, and they change what the SKILL's
earlier sections say:

| Earlier claim | What tldraw 3.15.6 actually did |
|---|---|
| §3 "the padding trap": a `foreignObject` declares `width="1413"` for two glyphs | the declared box is the **shape's own plate** — 400 px for a 400 px GPU card. The trap inverts: the box **under**-reports, and what it hides is text that overflows its plate. |
| §4 "~300 literal `will-change: auto` from a single artwork set" | 296 label dumps / **657** `will-change` in the *stripped* set — 2 dumped `<div>`s per label × 148 labels. Both §4 filters still hold: a naive scan reported every one of them, `check-hygiene.py` reported the project clean. |

## 7. Re-theme, don't re-draw — and assert the theme is complete

tldraw's light palette is authored against a near-white canvas. On this film's warm cream
(`#FAF9F5`), measured, four of the seven family colours are under WCAG 4.5:1:

| family | tldraw light | on cream | themed | on cream | on tile |
|---|---|---|---|---|---|
| blue knowledge | `#4465e9` | 4.65 | `#3550cc` | 6.29 | 5.48 |
| violet system | `#ae3ec9` | 4.60 | `#8f2fa8` | 6.35 | 5.54 |
| green output | `#099268` | **3.74** | `#067353` | 5.56 | 4.85 |
| orange methods | `#e16919` | **3.20** | `#96500f` | 5.78 | 5.04 |
| red walls | `#e03131` | **4.28** | `#b8232a` | 6.02 | 5.25 |
| grey annotation | `#9fa8b2` | **2.29** | `#5f6a78` | 5.22 | 4.55 |
| ink structure | `#1d1d1d` | 16.00 | — | — | — |

Artwork that looks fine fails `check`'s contrast audit. Two different mechanisms carry the
fix, and they need different CSS:

- **Labels** carry `color` in an **inline style** → only `!important` wins:
  `.art foreignObject [style*="color: rgb(9, 146, 104)"] { color: #067353 !important; }`
  Match on the literal rgb string — the colours are not classes.
- **Shapes** carry `fill` / `stroke` as **presentation attributes** → a plain attribute
  selector beats them with no `!important`:
  `.art [stroke="#e03131"] { stroke: #b8232a; }`

**The ground is a decision, and the theme sheet is where it gets recorded.** This section was
originally written around a warm cream ground (`#FAF9F5`) and read as though that were the
subject's natural colour — which is how a machinery/infra film shipped on cream and was told,
at delivery, that it should have been a dark technical theme. The authoring direction is
`../visual-storytelling` Step 0 ("Ask for the palette direction — never assume the ground");
it must be answered **before** the first beat, and the answer written into this sheet.

What the theme layer must therefore carry, so that a palette is one edit rather than a re-draw:

- `--t-ground` and one `--t-plate` (the elevated surface step) as named values — the gate and
  the frame both read them, so a re-theme never has to hunt for a hardcoded ground.
- every family re-picked for **the chosen ground**, and asserted, not eyeballed. Dark fails in
  the opposite direction from light: a mid-value hue comfortable on cream can vanish on
  near-black, so the same gate has to run with the dark pair.
- the **label knockout stroke = the ground**. Arrow labels carry a stroke painted under their
  fill; hardcoded to a light value it gives every glyph a bright halo the moment the ground
  goes dark (§13.2 deletes the halo node, but a dark theme still needs *some* knockout value).
- a note of which families are **shape-only** (no text), because a family that cannot clear
  4.5:1 is still usable as a fill.

Then **assert the theme is complete**, because the failure mode is silent: an un-themed
colour is artwork that looks fine and fails a delivery render. `scripts/theme-check.py`
enumerates every colour in the export, requires a rule for each, and requires every text
colour to clear 4.5:1 on the ground *and* on the plate step. It reads colours off `<p>` only — the
div-level dump repeats `rgb(255,255,255)` on every label, and scanning the whole file reports
a white that is never painted.

The export embeds only its own mono face (`font-family: tldraw_mono, monospace`). CJK labels
fall back to whatever the page names, so the theme names one:
`.art foreignObject div { font-family: tldraw_mono, "Noto Sans SC", sans-serif !important; }`

## 8. The style dump will crash the renderer, and stripping it is provable

Every label inlines **two** dumped `<div>`s of 274 longhands — ~6 KB each. On this run:
296 dumps, ~180,000 inline property declarations once 19 frames inline them.

The failure is not lint, not a wrong frame, and not an out-of-memory message:

```
check_runtime_failure: Protocol error (Runtime.callFunctionOn): Target closed
```

`hyperframes check` died on `index.html` at `t=0s` with 12 GB free and nothing to point at.
`lint` was clean the whole time. **An assembly that dies at t=0 with no error is an assembly
that is too heavy**, and the fix is to make the assets smaller *before* assembling.

`scripts/stile-labels.py` keeps the properties a label actually reads — placement, box
sizing, the font triple, colour, alignment, wrapping — and drops the rest:

```
19 svg · 296 label dumps rewritten
before 1069 KB → after 229 KB (78% smaller)
```

**And proves it**, because a size win is not evidence: rasterise the stack before and after
and diff. `0 differing pixels of 921,600, max channel delta 0`.

Two traps in that proof, both paid for:

- **Never invent a value while stripping.** A first pass "tidied" `inline-size: auto` into
  `100%`, `box-sizing: content-box` into `border-box`, `tab-size: 8` into `2`, and added
  `display: flex` to the inner div. The stack moved by two pixels on *every* label — 89,578
  differing pixels, max delta 220. Every kept value has to be copied verbatim from the dump,
  and the two dumped divs are told apart by **order**, not by content.
- **Strip after the fonts, not before**, or the extracted `@font-face` changes size too: a
  strip-first pass reported 78%, a strip-last pass 78% on a smaller base. Order the pipeline
  once and write it down.

## 9. The arrow-label halo: invisible on a light ground, and 1.01:1 text

tldraw paints an arrow label **twice** at the same coordinates: a halo pass
(`<text stroke="#f9fafb" stroke-width="3" fill="#f9fafb">`) and then the glyphs
(`fill="#1d1d1d"`). It is a legibility trick for dark grounds.

On a light ground it is not redundant, it is **invisible** — and it is still measured. The
contrast audit read it as `1.01:1` in every frame that contains the arrow.

Three things that do *not* work, in order of trying them:

- `aria-hidden="true"` — the audit does not honour it.
- `data-layout-allow-overlap` — it is not a layout defect; it is a text-contrast defect.
- A layout suppression on the art svg — hides the real collisions along with it.

What works is to **drop the element and prove the drop**: the themed stack with the halo and
the themed stack without it are `0 differing pixels` apart, because there was nothing on
screen to remove. Remember the whole-world export needs the same pass as the deltas — for one
run the halos survived in `final-frame.svg` and the stack-vs-final pixel gate caught it.

## 10. The layout audit cannot see a delta stack, so compute the buried labels

`check`'s layout audit compares **rendered text boxes**. A delta stack's whole mechanism is
painting a new plate over an old one — so a `mutate` that repaints a card reports as
`content_overlap` between the label it buried and the label it painted. On this run that was
**80 findings, all of them correct behaviour and none of them defects**.

Do not blanket-mark the art (that hides real collisions) and do not ignore the audit. Compute
it: walk each beat's filled shapes and each label's ink box through one transform-stack pass,
and mark the labels whose centre falls inside a **later** beat's painted area. That found 8,
and all 8 are `mutate` labels:

```
beat  3  'Prefill · 独占 2 秒'          → repainted by beat 4's phase plates
beat  3  '✗ 五十个人全部卡死'            → repainted by beat 7's flip
beat  4  'Prefill · 一次性算完所有输入'   → repainted by beat 7's schedule
beat  4  'Decode · 逐字'                → repainted by beat 7's schedule
beat  5  '✗ 互斥：算力和带宽只能二选一'   → repainted by beat 13's flip
beat  9  '✗ 切碎了会不会丢信息'          → repainted by beat 10's flip
beat 15  '✗ 服务崩溃' / '一张卡崩了 → TP 通信死锁'  → repainted by beat 17's flip
```

Two details that cost a run each:

- **The marker has to reach the text leaf.** Putting it on the `<foreignObject>` changed
  nothing — the audit measures the `<p>`. Both.
- **An SVG is XML.** `data-layout-allow-overlap` without a value is a parse error, and
  ElementTree fails 4 KB into the file with "junk after document element". Write
  `data-layout-allow-overlap="covered"`.

The compare table that survived this pass was a real defect, not a false positive: the two
columns' label boxes were 4 px apart, and the export's own `-6 px` padding closes that. Rows
now sit 24 px apart with a 30 px gap, which is what the label line boxes (24.3 px) need.

## 11. Placement arithmetic, measured

The world is 1280×720; the film is 1920×1080. What the run learned about putting one on the
other:

| decision | measured |
|---|---|
| art scale | **1.05** → 1344×756. At 1.24 (1587×893) the world's top edge lands *inside* the head band and every chrome row collides with the diagram's own labels. |
| art band | bottom `6.5cqh`; head band above (rail 4.6 + kicker/title 8.4), caption band below (4.2). Three bands, never overlapping. |
| label size on screen | an 18 px `size: s` label → **19 px**, below the frame's 27 px type floor. The world wants authoring at the film's canvas size; see `../visual-storytelling/references/visual-grammar.md` § "The diagram layer and the frame layer". |
| dark-pixel bbox | ink measures 1222 × 661 px inside the 1280×720 world (margins 38 left / 38 top / 20 right / 26 bottom); the geometry-only box over-runs the raster on the top edge and **under**-runs it by 2–3 px on the other three — the same control-point/text-estimate split the SKILL already documents, in the other direction. |

## 12. What this run's tooling looks like

```
scripts/render-beats.py     # headless tldraw page → one delta SVG per beat + final-frame
                            #   + fonts.css, then: halo drop, data-beat stamp
scripts/stile-labels.py     # strip the computed-style dump, prove it by pixel diff
scripts/theme-check.py      # every colour themed; every text colour ≥4.5:1 on cream + tile
scripts/measure-beats.py    # per-beat INK boxes (walks path data, drops opacity-0 rects,
                            #   estimates label ink from text + font-size), vs the naive width
```

The render needs a browser with DOM measurement (tldraw measures text), so it is a headless
page driven by Playwright/Chromium — a plain Node script cannot do it. Drive it from a page
that exposes `window.__renderAll()` and have Playwright collect the strings; assert that the
export order matches creation order, since `getSvgString(ids)` honours the array order and a
reordered array silently changes the paint order of a stack.
## 13. Making the artwork *choreographable* (the run that turned this from a slideshow into a film)

### 13.1 A batch export gives you nothing to animate

`editor.getSvgString([id, id, id], opts)` emits **anonymous `<g>` roots**. A downstream
composition can then only stagger a reveal by *index*, which is exactly the "one gesture
replayed 18 times" failure. Export **one shape at a time** and stamp each result with the
shape's own name:

```ts
const one = async (id: string) => {
  const svg = (await editor.getSvgString([id], opts)).svg
  const close = svg.lastIndexOf('</svg>')          // keep the <defs>/<style> strip_fonts needs
  const inner = svg.slice(svg.indexOf('>') + 1, close)
  const k = inner.indexOf('<g '), e = inner.indexOf('>', k)
  return inner.slice(0, k) + inner.slice(k, e) + ` data-tl="${id.replace(/^shape:/, '')}"` + inner.slice(e)
}
```

Two traps: each single-shape export is its **own `<svg>` document**, so re-wrap the joined
delta as a valid standalone SVG on disk (one consumer rasterises the files as-is, another
inlines them into one world); and name the attribute off tldraw's shape id, which already
carries the name you gave the shape in the spec.

**Name shapes for their ROLE, not their look.** `b07-wall-freeze-strike` survives a colour
change; `red-bar-3` becomes a lie the first time the wall is struck through and repainted
green. Every choreography then addresses `q('[data-tl="b07-wall-freeze-strike"]')` and a
re-layout cannot silently re-point it.

### 13.2 tldraw's arrow-label halo fails every contrast audit

tldraw paints some labels **twice at identical coordinates**: a plate-coloured `<text>` with
a thick stroke, then the dark glyphs. That knockout is white text on a light ground, so
every WCAG audit reads it at ~1.01:1 and fails — and an SVG `<text>` cannot be marked
decorative in any way an auditor honours (`aria-hidden` is ignored; the value of
`data-layout-allow-overlap` is matched by `hasAttribute`, so it only ever applies to the
*layout* audit, not the contrast one).

Fix: **delete the halo node and keep its job on the real glyphs.** Identify the halo by its
plate-coloured `fill` (`#f9fafb` / `#fcfffe` / …), not by any attribute of yours, then add
`paint-order="stroke"` so the stroke paints *under* the fill. One text node, one fill,
identical pixels, and the contrast audit only ever sees dark-on-cream. Apply the same
treatment to `final-frame.svg` or the deltas can never re-equal it.

### 13.3 A malformed "mark this overlap as intentional" is worse than no mark

Two separate off-by-one bugs, both producing *plausible-looking* output:

- `out[:at] + ins + out[at+1:]` where `at` is the tag's **insert point** — eats the tag
  name's first letter and leaves `oreignObject` dangling.
- Inserting at `at + 1` (just past `<`) — HTML reads an empty tag name, and
  `data-layout-allow-overlap="covered"foreignObject` becomes one malformed attribute.

Only `out[:at] + ins + out[at:]` at `at = start + 1 + len(tagName)` is correct.

The failure mode is nasty in both directions: the malformed version made `check` report
**zero** layout errors (it could not measure a tag it could not parse) and the render was
missing 26 of 108 shapes. **A green check is not evidence the art is on screen** — rasterise
one frame and count `[data-tl]` nodes with a non-zero bounding box. `w:0 h:0` is the tell.

### 13.4 Paint the cover plate BETWEEN the beats, not after them

`inner = beats1..N` then `inner += plate + beatN` repaints the band's owner **twice**, and
the two copies of its own label overlap each other. Order it `beats1..N-1 + plate + beatN`.

## 14. The audio is a separate deliverable from the script

`SCRIPT.md` and `audio_meta.json` are independent inputs to `build-project.py`. Rewriting the
narration and rebuilding produces a film whose **captions say one thing and whose voice says
another**, with the duration unchanged enough that nothing looks wrong in a spot-check —
`build-project.py` reported the *same* 274.34 s before and after a full rewrite of every line.

Rule: **`SCRIPT.md` changed ⇒ re-run the TTS ⇒ re-derive `audio_meta.json` before rendering.**
`gen-voice.py --project .` regenerates all lines from the script, so there is no excuse.

## 15. Porting the same art to a second engine (Remotion) — two more silent-total failures

The master's beats were re-emitted per frame in Remotion by string surgery on `data-beat` spans.
Both bugs below produced a film that **type-checked, rendered, and showed almost nothing**, with
no error, no warning, and no visible symptom other than a missing picture.

### 15.1 A wrapper `<g>` needs TWO closings

Animating a shape means inserting a wrapper inside its group:

```ts
return group.slice(0, openEnd) + wrap + group.slice(openEnd, close) + '</g></g>';
//                                                              ^^^^^^^^^^^ TWO
```

`group.slice(openEnd, close)` consumes the group's own `</g>`, so emitting a single `</g>`
closes the **wrapper** and leaves the group open. The document is then unbalanced by one tag
per animated shape. Remotion injects the SVG through `dangerouslySetInnerHTML` on an `<svg>`
element, so it is parsed by the **HTML** parser, which auto-closes the unclosed group at the
first subsequent `</g>` and silently discards everything after it — 8 unbalanced groups cost
this project 26 of 108 shapes, with the world rendering as just the handful of shapes before
the first animated token.

Assert the invariant instead of trusting the eye:

```js
const opens = (out.match(/<g\b/g) || []).length, closes = (out.match(/<\/g>/g) || []).length;
```

Do this in the generator, not in a test: the same string can be printed and counted in one line,
and a failed render costs minutes. It is also the cheapest possible pre-render gate — it caught
this in seconds where a still render took ninety and a full render takes fifteen minutes.

### 15.2 Baking a theme: resolve `var()`, or every shape goes black

Copying palette rules out of `theme.css` into markup needs the variables **resolved**. Two
failures in one:

- Keyed by attribute name (`{'fill': hex}`) instead of `fill:#4465e9` — every rule overwrote the
  last, so 18 of 20 colours silently kept their raw tldraw hex.
- Reading each rule's right-hand side as a literal hex — but they are ALL `var(--t-blue)`, so only
  the two hand-written rules matched and the theme "applied" to nothing.

The failure is invisible: `fill="var(--t-blue)"` is not a colour, the browser falls back to
black, and the film renders as a black-on-black diagram that still type-checks. A resolver that
matches `var\(\s*(--[\w-]+)\s*\)` against the `:root` block is the whole fix.

**The tell in both cases: a colour census, not a screenshot.** Counting distinct pixel values in
one frame is a two-line check that separates "the film is black" from "the film is empty" — the
two failures look identical on screen and have opposite fixes.

## 16. Rebuilding the film as per-frame compositions (where the tldraw world stopped being affordable)

The 18-beat cumulative world was retired in favour of one independent composition per frame.
The diagnosis, from `measure.json` on the last build before the change:

| beat | ink w × h | share of the 1280×720 world |
|---|---|---|
| 03 | 1200 × 522 | 68.0% |
| 07 | 1182 × 475 | 60.9% |
| 15 | 831 × 526 | 47.5% |
| 04 | 411 × 101 | 4.5% |
| 08 | 215 × 24 | **0.6%** |
| 16 | 196 × 5 | **0.1%** |
| 18 | 318 × 187 | 6.5% |

Three beats fill the frame; **twelve of eighteen occupy under 10%**, and one is a single 5-pixel
line. That is not a layout bug — it is what a single shared canvas does. Every beat is drawn in
the leftovers of the ones before it, so nothing can be re-composed, nothing can leave, and the
type has nowhere to go: labels authored at 18 px inside the world reached the screen at ~22 px,
below the frame's own 27 px floor.

Per-frame composition fixes all three at once, and **deletes the entire asset pipeline** —
`render-beats` → `stile-labels` → `measure` → theme bake → `verify_stack` — along with every bug
those stages produced.

### 16.1 `interpolatePaths` is not a shape-morph primitive

Two failures, and the dangerous one is the second.

**It throws on mismatched structures.** One rounded-rect path → four of them is refused:
`Cannot interpolate SVG paths with different subpath structures`, and the scene renders nothing.
Four ADJACENT slices (tiling the plate exactly, so it still reads as one bar) each morphing into
one block is legal — and a better picture, because the audience watches the bar get *cut*.

**With matching structures it can still emit garbage.** The four-slice version passed a still at
the midpoint and produced nonsense at the film's closing frame: a slice whose x range should have
been 200…500 came out −130…206. `interpolatePaths` was never wrong about *what* it does — it
interpolates path *strings*, and rounded-corner `Q` chains are exactly where that assumption is
easiest to make and hardest to see.

The gate that caught it is one line, and it belongs in the generator rather than a test:

```js
const xs = [...path.matchAll(/[-\d.]+/g)].map(Number);
if (Math.min(...xs) < 0 || Math.max(...xs) > worldW) throw new Error('morph escaped the world');
```

For anything with known corners, **interpolate four numbers and let `<rect>` do the rounding.**
Path morphing is worth it for genuinely free-form geometry, and for nothing else.

### 16.2 HTML inside `<svg>` is dropped silently

`Station` was written as a `<div>` with a border and a flex row — the obvious way to write a box,
and the obvious thing to drop inside a JSX `<svg>`. It rendered **nothing, with no error**: a
`<div>` inside `<svg>` is not a box, it is an unknown element the parser discards, so the scene
looked merely empty and the frame appeared to have no content. Same class as §8 and §13.3: *the
renderer exiting 0 is not evidence that anything was drawn.* Anything drawn inside an `<svg>` must
be an SVG element — or a `<foreignObject>`, deliberately.

### 16.3 One `<g>` is one coordinate space, and derived layout must be derived

Four stations sharing one `<g>` all drew at the origin, stacked. Then the arrows between them were
hardcoded `x` values, so moving a station desynchronised the diagram from its own connectors.

Both are the same mistake: a layout that exists in two places. Declare the row once —

```ts
const STATIONS = [{name: '分词', x: 0, w: 160}, {name: 'Prefill', x: 230, w: 210}, …]
```

— and derive the arrows, the loop-back arc and the measurement brackets from it. `transform`
must also be applied *inside* any per-item scale, so an item grows from its own left edge rather
than from the row's origin.

### 16.4 What retiring elements actually buys

The instruction was "讲完的元素要及时退场，只保留当前帧核心讲解元素，这样元素大小和字体大小都能变大". The mechanism is trivial once each frame is its own component: **retiring is not rendering.** There is no exit animation to design, because there is no prior frame to animate away from.

The corollary is the thing worth remembering: the earlier engine needed an exit *gesture* — shrink the departing beat toward its own centre while it faded — and that gesture cost real complexity in a system where a departure was a `data-beat` group that had to be found, rewritten and kept in sync. In a per-frame model the question never arises.

### 16.5 Captions drift when the walk indexes the wrong coordinate system

Delivered once with "语音和字幕有点不同步", and the cause was not timing at all — it was a walk
that indexed **two different things with one variable**:

```js
const concat = words.map((w) => w.text).join('');   // a STRING: concat[i] is a CHARACTER
if (concat[wi] !== ch) { … wi = concat.find(ch, wi) … }   // find() returns a CHARACTER index
cur_words.push(words[wi]); wi += 1;                       // …but wi is used as a WORD index
```

Every group over-ran or lagged, and all **242 caption pages** carried the wrong half-second. No
error, no warning: the times were well-formed numbers attached to the wrong words. This shape was
inherited from the diagram engine's `group_captions`, which had never been checked.

Two things had to be fixed, and only the second was the real one:

1. `gen-voice.py` joins wrapped script lines **with a space**; the caption script joined them
   without. Two parsers of one script with different joining rules is a desync waiting to happen.
   Worth fixing on its own — but it was not why the captions were wrong.
2. The coordinate system. Correct shape: walk **characters**, record the character position of
   each narration character, then map positions back to words through an index built while
   joining: `words.forEach((w, j) => { for (k of w.text) charToWord.push(j) })`.

**Assert the invariant, every build, for the price of three lines:**

```js
const want = page.text.replace(/[\s\u3000-\u303f\uff00-\uffef]/g, '');
const got = page.words.map((w) => w.text).join('').replace(SAME, '');
if (want !== got) { console.error(`F${n} p${i}: ${want} != ${got}`); process.exit(1); }
```

plus a coverage check — every page must begin exactly on a real word boundary, in order, with no
gaps or repeats. Both are silent failures otherwise, and the second one catches a walk that is
correct on page 1 and wrong from page 2 on.

Generalise: **whenever a generator aligns a script with measured timings, the alignment itself
needs a gate.** A caption generator that produces plausible-looking times is the most dangerous
kind of wrong, because every downstream check passes.
