# Replacing artwork on a new canvas

The artwork is built for one world — 1280×720, growing rightward. Now put it in a portrait film, or on a wider card, or at twice the size, or in a scene that shares its canvas with something else. Do not crop, and do not scale the picture down until it fits: both throw away the composition's own decisions.

The move is the **beat stack**: re-`viewBox` each delta to its own measured ink and place the bands one under another, so the world grows downward the way it grew rightward.

Rule: [`../SKILL.md`](../SKILL.md) § 6. The numbers this uses come from the measurement work in [`measurement-and-verification.md`](measurement-and-verification.md).

## Why stacking and not cropping

A world that grows rightward is a wide, short object. A 9:16 frame is tall and narrow. Every way of reconciling those other than stacking throws something away:

- **Crop to the band** cuts connectors and labels that leave the frame, and the surviving half-drawings read as errors.
- **Lay out against declared boxes.** Measured in the working build: a band sized from beat 5's declared box held **449 × 333 px** of ink in a **798 × 628 px** box — 53% of the space reserved — and the scale that followed was **1.7× smaller** than the ink-correct one. That is 24 px of label type instead of 14 px. This is the [`measurement-and-verification.md`](measurement-and-verification.md) § 3 mistake wearing a layout costume.
- **Re-draw at the new aspect** throws away the beat sheet's fixed grammar and every label placement already reviewed.

Stacking spends nothing. Each band is the exporter's own markup with a new `viewBox`, so the hand-drawn wobble, the palette, the arrow curvature and the labels all arrive intact.

## The band

Per band, one beat delta:

```js
var by = num(b[5], 0), bw = num(b[6], 968), bh = num(b[7], 0);
wrap.style.top = by + "px";                       // y comes precomputed from the stack
wrap.style.width = "968px";
wrap.style.height = (bh + 14 + 40) + "px";        // art + label gap + label height

art.innerHTML = unb64(b[3]);                      // inline, never <img>
var svg = art.querySelector("svg");
if (!svg) throw new Error("band " + bi + " decoded to " + art.innerHTML.length
  + " chars and carries no <svg> — the base64 channel is corrupt");
svg.setAttribute("width", String(bw));
svg.setAttribute("height", String(bh));
svg.removeAttribute("style");
art.style.left = Math.round((968 - bw) / 2) + "px";   // centre it in the band
```

And the `viewBox` the composition receives is the band's own ink, written by the planner:

```python
art = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.2f} {y0:.2f} '
       f'{x1 - x0:.2f} {y1 - y0:.2f}" stroke-linecap="round" stroke-linejoin="round">'
       f'{svg_body}</svg>')
```

A real one, from the working plan: `viewBox="496.00 285.00 142.32 45.26"` — beat 2's ink, to the cent.

### The numbers, from the working portrait build

1080 × 1920 portrait, cream ground. Zones, all in canvas px:

```
CLAIM_TOP, CLAIM_BOTTOM   110,  430        the headline block
DIAG_TOP,  DIAG_BOTTOM    470, 1300        the beat stack
DIAG_X,    DIAG_W          56, 968         the band column
CAP_CY                   1530             the caption row
```

Band furniture: label type 30 px, label gap 14 px, label height 40 px, band gap 44 px, reveal 0.42 s, type floor 24 px, max lift 1.90. The diagram zone ends at 1300 rather than the earlier draft's 1345 because the caption band moved down to 1530 — and that is recorded in the plan as a `why`, not left as a number nobody questions.

## Three rules that only bite at this step

**Clip each band.**

```css
[class~="bandart"] { position: absolute; top: 0; display: block; overflow: hidden; }
```

A delta is a delta: arrowheads and label boxes reach past the shape they belong to. Left unclipped, that ink lands in the canvas edge columns — and edge-column ink is the defect the render audit is built to catch.

**Namespace the ids, both halves.** tldraw's clipPath ids are beat-scoped, so two bands are fine and one beat used twice is not. Rewrite `id="…"` *and* `url(#…)` together:

```python
def namespace_ids(markup: str, tag: str) -> str:
    out = _ID_RE.sub(lambda m: f'id="{tag}__{m.group(1)}"', markup)
    return _URL_RE.sub(lambda m: f"url(#{tag}__{m.group(1)})", out)
```

**Re-assert the font.** The labels are HTML inside the export, and the composition's stylesheet will not have reached them:

```css
[class~="bandart"] foreignobject div,
[class~="bandart"] foreignobject p {
  font-family: tldraw_draw, "Noto Sans SC", "Inter", sans-serif !important;
}
```

Lowercase tag selectors — see [`export-anatomy.md`](export-anatomy.md) § "Round-tripping the markup".

## The type floor is the art's floor too

The band scale is shared across all bands in a frame, because bands of different scale read as different art:

```python
budget = (DIAG_BOTTOM - DIAG_TOP) - n * (BAND_LABEL_GAP + BAND_LABEL_H) - (n - 1) * BAND_GAP
maxw = max(prims[b["beat"]]["w"] for b in d["bands"])
sumh = sum(prims[b["beat"]]["h"] for b in d["bands"])
s = min(DIAG_W / maxw, budget / sumh)
```

But the label type lives inside the export, so it scales with the art and can fall under a floor your HTML respects. So the type is lifted back, per band, to hold it:

```python
lab = label_px(svg_body)                       # the plate's own smallest font-size
k = 1.0 if lab <= 0 else max(1.0, FLOOR_PX / (lab * s))
if k > MAX_LIFT + 1e-6:
    raise SystemExit(f"{cid} band {i} (beat {b['beat']}) needs lift {k:.2f} > "
                     f"{MAX_LIFT} to hold {FLOOR_PX}px — re-design the stack")
svg_body = lift_type(svg_body, k)
```

`lift_type` scales every `font-size` / `line-height` / margin / padding / border length inside each `foreignobject`, and grows the `foreignObject` box to match — **about its centre when the label is centred, from its top-left when it is `text-align: start`**. Getting that backwards is a silent translation, not a visible error.

**Assert the lift, do not negotiate it.** Past some multiplier the band is no longer this film's art — it is a different drawing. Measured across the 29 frames of the working portrait film: lifts run **1.0 to 1.749** against an asserted cap of **1.90**. And the cap earns its keep: the same beat pair `[1, 10]` needed a lift of **1.528** in the portrait film and **2.09** in the smaller hook layout, which is over the cap — so the hook plan *dropped beat 10 from that frame* rather than hold the floor.

## Choosing which beats a moment needs

A delta is designed to be stacked **over** what is already there, so several beats are meaningless in isolation: an arrow whose shaft is clipped to reach off-frame, a `mutate` that only reads against the wall it flips, a second row of a workflow whose first row is missing. The sandbox fence is the plain case — `beat-16` is four dashed lines and a label, 784 × 598 world units, and alone it encloses nothing and says nothing. A plate that cannot stand alone cannot be a band.

So choose, per moment, and carry continuity deliberately:

- **Standalone beats.** A box, a card, a labelled cluster — anything that reads as a complete object.
- **Carry.** The previous frame's closing beat goes on top of this frame's first band, so the cut reads as continuation. In the working film this is the continuity device that pairs with the claim line.
- **One to three bands.** Measured distribution across 29 portrait frames: 26 frames carry 2 bands, 2 carry 1, 1 carries 3. A zone that grows a band per reveal is a zone that stops growing — see the drops below.
- **Fill, and report it.** The zone's used fraction came out at **0.854 – 0.958** across the 29 frames. A frame at 0.5 has room and should take more beats.

## Record every drop

A drop is a design decision, not an omission. Every frame carries a `dropped` field, and it is `null` when nothing was dropped — the field's existence is what makes "nothing dropped" a claim rather than an absence. Real entries, with the reason:

> the landscape frame's own RAG construction (8 layers: qarrow / kb / magnifier / arc / strike / doc1 / doc2). Those are beat 5 drawn at scene scale; beat 5 from 12-enclose is the same drawing re-clustered into one primitive with its labels, and a portrait band needs the primitive, not the layer set.

> the seven materials that land on the desk one by one in the landscape cut (问题/聊天/PDF/Excel/网页/工具结果/Skill 说明). Seven bands is the one stack the portrait zone cannot hold above the type floor — each band would be ~100 px of art — and they are named in the narration, one per spoken item, which is what the burned-in caption is for.

> beat 10 (Agent · 数字员工). Named compromise: DROP THE BEAT from this frame rather than hold the floor — [1,10] needs a type lift of 2.09 to keep 24 px, and the beat belongs to frame 12. Nothing is lost: the claim line still carries 从顾问到数字员工, and beat 10 gets a full band two frames later.

Note what the last two do. Each states *what is lost* and *where it lives instead* — the caption track, the narration, a later frame. A drop without a destination is a deletion.

The same discipline applies to a smaller edit: dropping a shape's echo subpath, thinning a double stroke, or hiding an annotation at small size is a decision to write down, not a cleanup to perform quietly.

## What to check afterwards

- [ ] Every band's `viewBox` equals its own measured ink box (invisible rects dropped, labels estimated) — not a slice of the world.
- [ ] Every band's ink sits inside its `overflow: hidden` box with no edge-column ink on the canvas.
- [ ] No `id` and no `url(#…)` is shared between two bands on the page.
- [ ] Every label renders, in the right language, at or above the floor — read the pixels.
- [ ] The zone's fill fraction is inside its intended band; anything far below means beats were dropped that did not need dropping.
- [ ] Every frame's `dropped` is either `null` or a stated reason with a destination.
- [ ] The dark-pixel bbox of the rendered frame sits inside the canvas with its intended margin.
- [ ] Beats 1..N stacked still reproduce the landscape world — pixel-equivalence, unchanged by the re-placement.