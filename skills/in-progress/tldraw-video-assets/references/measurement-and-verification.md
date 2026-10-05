# Measurement and verification

Two instruments, two jobs. **Geometry** walks the markup and gives you a number you can lay out against. **Pixels** decode a rendered frame and tell you what actually landed. Neither substitutes for the other, and the failure mode is always the same: a confident wrong number that every later decision inherits.

Rules: [`../SKILL.md`](../SKILL.md) § 3 and § 5. Markup being measured: [`export-anatomy.md`](export-anatomy.md).

## 1. The path-data walk

Path `d` numbers must not be paired two-by-two. Pairing is wrong for any path using `H`/`V` or implicit coordinate pairs, and catastrophic for a tldraw arrow whose shaft is authored in absolute coordinates while its head is a separate subpath. The first bbox pass in the working project reported a **1413 px "wide" arrow for a connector that is really 300 px long**, and every conclusion about whether a beat fit a portrait band rested on that number.

The 1413 was a *label box*: `compositions/frames/02-wall-answer.html` holds both a `M 0 0 L 310 9` connector and two `width="1413"` label boxes in one document. Reproduced end to end on the worked set, the paired-numbers measure of `final-frame.svg` reads **2512 px wide** where the honest geometry is **1326** and the painted ink is **1222**.

A walk that works — pure stdlib, no project imports, copy it anywhere:

```python
_ARGC = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}

def parse_path(d):
    """Return every point the pen visits, in path coordinates."""
    toks = [(c, None) if c else (None, float(v))
            for c, v in _TOKEN.findall(d or "")]
    pts, i, cmd, cur, start = [], 0, None, (0.0, 0.0), (0.0, 0.0)
    while i < len(toks):
        c, v = toks[i]
        if c is not None:
            cmd = c; i += 1
            if cmd in "Zz":
                cur = start; continue
            if i >= len(toks):
                break
        if cmd is None:
            i += 1; continue
        need = _ARGC.get(cmd.upper(), 0)
        if need == 0:
            i += 1; continue
        vals = []
        while len(vals) < need and i < len(toks) and toks[i][0] is None:
            vals.append(toks[i][1]); i += 1
        if len(vals) < need:
            break
        up, rel, x, y = cmd.upper(), cmd.islower(), cur[0], cur[1]
        if up in ("M", "L", "T"):
            nx, ny = vals[0], vals[1]
            cur = (x + nx, y + ny) if rel else (nx, ny)
            pts.append(cur)
            if up == "M":
                start = cur
                cmd = "l" if rel else "L"      # implicit lineto after moveto
        elif up == "H":
            cur = (x + vals[0], y) if rel else (vals[0], y); pts.append(cur)
        elif up == "V":
            cur = (x, y + vals[0]) if rel else (x, vals[0]); pts.append(cur)
        elif up in ("C", "S", "Q"):
            # every control point is emitted too: the bbox must over-estimate, never
            # under-estimate, or a curve gets silently cropped out of the plate.
            seg = [(x + vals[k], y + vals[k + 1]) if rel else (vals[k], vals[k + 1])
                   for k in range(0, need - 1, 2)]
            pts.extend(seg)
            cur = seg[-1]
        elif up == "A":
            cur = (x + vals[5], y + vals[6]) if rel else (vals[5], vals[6])
            pts.append(cur)
        else:
            break
    return pts
```

Three details that are not stylistic:

- **Emit control points.** A `Q` corner that bulges past its endpoints is exactly the `beat-03` case (`L 275.7999 0.352` on the straight top edge, `L 280.4469 235.5948` on the right edge — a 4.65-unit corner bulge on a 281-unit shape). Endpoints-only under-report the drawing's character.
- **Honour the implicit lineto after `moveto`.** `M x y z z` is a lineto, not a moveto. Getting that wrong teleports the pen and the box with it.
- **Lowercase the tag before comparing.** `shape_points()` receives `foreignobject`, not `foreignObject`, the moment the markup has been through an HTML parser.

## 2. The transform stack

Shape-local coordinates mean nothing alone. Compose the whole chain to the root:

```python
IDENT = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

def parse_transform(s):
    out = IDENT
    for name, args in re.findall(r"(matrix|translate|scale|rotate|skewX|skewY)\s*\(([^)]*)\)", s):
        n = [float(x) for x in re.findall(NUM, args)]
        if name == "matrix" and len(n) >= 6:      m = tuple(n[:6])
        elif name == "translate" and n:            m = (1, 0, 0, 1, n[0], n[1] if len(n) > 1 else 0)
        elif name == "scale" and n:
            sx = n[0]; sy = n[1] if len(n) > 1 else sx;  m = (sx, 0, 0, sy, 0, 0)
        elif name == "rotate" and n:
            a = math.radians(n[0]); cx, cy = (n[1], n[2]) if len(n) > 2 else (0.0, 0.0)
            rot = (math.cos(a), math.sin(a), -math.sin(a), math.cos(a), 0, 0)
            m = mat_mul((1, 0, 0, 1, cx, cy), mat_mul(rot, (1, 0, 0, 1, -cx, -cy)))
        elif name == "skewX" and n:  m = (1, 0, math.tan(math.radians(n[0])), 1, 0, 0)
        elif name == "skewY" and n:  m = (1, math.tan(math.radians(n[0])), 0, 1, 0, 0)
        else: continue
        out = mat_mul(out, m)          # order matters: parent ∘ child
    return out
```

Skip these tags entirely, or their padded geometry lands in your box: `defs`, `clipPath`, `style`, `title`, `desc`, `metadata`, `symbol`, `mask`, `pattern`, `filter`, `linearGradient`, `radialGradient`, `marker`.

`rotate` about a centre is the one that bites: three numbers, not one, and the translation has to sandwich the rotation.

## 3. Ink, not boxes

Three separate corrections, applied in this order.

**Drop the invisible rects.** Every rough-stroked shape carries a `<rect … opacity="0"/>` at `(-100,-100)`, sized to the shape's padded export box — 38 across the set, exactly one per `clipPath`. It is never painted.

```python
for parent in root.iter():
    for child in list(parent):
        if child.attrib.get("opacity") == "0":
            parent.remove(child)
```

**Estimate label ink from text and `font-size`,** never from the declared box. Read the string out of the subtree, take the largest `font-size` in any descendant's `style`, and advance per character: CJK 1.0 em, space 0.30, `·—…` 0.55, digit 0.56, uppercase 0.62, other Latin 0.53, times 1.35 for line height. It is an estimate and must say so.

**Bias the error too large, on purpose.** An over-estimate costs a little padding. An under-estimate silently crops. Returning control points, keeping the `opacity="0"` rects out, and rounding the text estimate up are all the same decision.

### What that costs on the worked set

Every beat measured twice: declared boxes and invisible rects in, then ink only.

| beat | with rects | ink only | | beat | with rects | ink only |
|---|---|---|---|---|---|---|
| 01 | 510 × 212 | 411 × 156 | | 10 | 720 × 534 | 720 × 534 |
| 02 | 142 × 45 | 142 × 45 | | 11 | 430 × 307 | 234 × 119 |
| 03 | 284 × 278 | 284 × 278 | | 12 | 408 × 273 | 294 × 144 |
| 04 | 216 × 46 | 216 × 46 | | 13 | 399 × 308 | 235 × 247 |
| 05 | **734 × 577** | **579 × 455** | | 14 | 310 × 201 | 210 × 61 |
| 06 | 472 × 240 | 317 × 89 | | 15 | 352 × 355 | 198 × 202 |
| 07 | 412 × 247 | 284 × 90 | | 16 | 784 × 598 | 784 × 598 |
| 08 | 319 × 344 | 213 × 164 | | 17 | 368 × 360 | 238 × 192 |
| 09 | 216 × 225 | 145 × 125 | | 18 | 478 × 248 | 478 × 108 |

World units, 1280×720 world. Beats 02/03/04/10/16 are unaffected: 02/03/04/16 carry no invisible rect at all, and beat 10's single rect sits inside its other ink. The worst case is beat 6: **472 × 240 declared, 317 × 89 painted** — a 2.7× phantom height, on a beat whose art is two short boxes and a connector.

In the working project the same correction moved the layout by a factor, not a percentage: the band drawn from beat 5's declared box held 449 × 333 px of ink in a 798 × 628 px box — 53% of the space reserved — and the resulting scale was **1.7× smaller** than the ink-correct one. The gap between those two scales is 24 px of label type versus 14 px.

## 4. Verification

**Geometry and pixels disagree in both directions, and each disagreement means something.** Measured on the worked set's whole world:

| | box |
|---|---|
| declared boxes, invisible rects included | 1326 × 744 |
| geometry, ink only, control points included | **1210 × 660** |
| rasterised, ink measured from pixels | **1222 × 663** |

Read it as: geometry sits 1 px outside the raster on the left, top and bottom — the control-point bias, working. And geometry sits **10 px inside the raster on the right**, which is the `Eval · 给 AI 做考试` text estimate under-running on a mixed CJK/ASCII string. So the walker over-estimates curves and under-estimates that one label. Only the raster catches the second, which is why the pixel check is not a confirmation of the geometry check.

### Pixel equivalence

Stack the beats in `data-beat` order, composite into one world, compare against `final-frame.svg`. Run on the worked set it is exact:

```
pixel-equivalence: differing px 0 of 921600 | max channel delta 0
```

This is how the asset set was proven before any composition consumed it. It is the only check that proves the deltas *compose* — that beat 5's shapes and beat 8's do not collide, and that no delta quietly repaints an earlier one.

To rasterise without a renderer dependency, a headless browser on a page with the world's markup and a cream ground does it:

```bash
chrome-headless-shell --no-sandbox --disable-gpu --hide-scrollbars \
  --window-size=1280,720 --screenshot=out.png page.html
```

**Set `html,body{margin:0}` first.** The default 8 px body margin offsets the raster by exactly 8 px in both axes, which is invisible in a comparison against itself and fatal against a geometry box — the first run of this check put the ink at y 43–705 against a geometry box of y 36–696.

### Dark-pixel bbox

Decode the frame, mask every pixel whose distance from the known ground colour exceeds a tolerance, take the mask's bounding box.

```python
CREAM = np.array([0xFD, 0xFA, 0xE7])   # the ground the composition declares
INK_TOL = 26                            # per-channel; sum > 3 * INK_TOL to mask
EDGE_COLS = 4
m = np.abs(frame - CREAM).sum(2) > 3 * INK_TOL
```

Three things this catches that "rendered without error" does not:

- **Edge-column ink.** Any ink in the outermost 4 columns is clipped content. A band's art is allowed to reach its own box edge; the canvas edge is not.
- **A plate that never got its artwork.** An empty band is a box of ground, so it reads as a clean region, not an error.
- **A band that collapsed.** The filled fraction of the diagram zone is a real number from pixels; the geometric fill the planner computed is an upper bound from boxes. Report both side by side and a plan that overstates itself becomes visible.

Measure against a **known-good reference**, not an absolute constant: the same composition before and after a change, or a shipped frame. An absolute expectation goes stale the moment the ground colour or tolerance moves, and then it is decoration.

### The blank-frame check

A composition can render successfully and be blank. Two independent guards:

**At the channel.** Base64 the markup and assert an `<svg>` came out, with the decoded length in the message so a truncated payload is distinguishable from an empty one.

**At the pixels.** Ink coverage near zero is the symptom; assert a floor on the masked pixel count per frame, not just a bbox.

The escaping route to a blank frame is in [`../SKILL.md`](../SKILL.md) § 2. The general lesson — *the renderer exiting 0 is not evidence that anything was drawn* — is shared with the unstyled-template bug in [`../../longform-series/references/render-pitfalls.md`](../../longform-series/references/render-pitfalls.md).

## 5. The hygiene scan

Full rule and calibration discipline: [`../../longform-series/references/render-pitfalls.md`](../../longform-series/references/render-pitfalls.md) § "A scan that cries wolf is worse than no scan". The export-side facts, which are this skill's:

- One `will-change: auto` **per label**, inside the dump. The worked set has 38 labels and 38 `will-change` occurrences across its 18 beats; `final-frame.svg` carries 38 more.
- The dump is **274 longhands per dumped `<div>`**, two dumped divs per label, ~6 KB of `style` each. `will-change: auto` sits alphabetically between `width: auto` and `window-drag: none`, in a run of properties that are all at their initial values.
- `fonts.css` contains **zero** `will-change`, `transition`, `animation`, or `@keyframes`. Every hit is in the dumps.
- Measured on one project: a naive scan returned **309 hits, all 309 the inert default**.

```python
# authored if the value is not the initial `auto`
RE_WILL_CHANGE_AUTHORED = re.compile(r"will-change\s*:\s*(?!auto\b)[a-zA-Z-]+")
# and only inside <style> blocks: the dumps are inline style="" and excluded by construction
RE_WILL_CHANGE_CSS = re.compile(r"will-change\s*:\s*(?!auto\b)[a-zA-Z-]+")
```

Know the expected inert-hit count for the project and treat a count above it as the finding. Once one run's output is mostly inert, every later run gets skipped unread — including the one real defect.

## Reference implementation

`/home/atituiset/Projects/skills/videos/ai-agent-primer-zh/scripts/svggeom.py` — 262 lines, pure stdlib, no project imports. `parse_path`, `parse_transform`, `shape_points`, `bbox_svg`, `text_width`. Its module docstring is the incident report behind § 1; copy it rather than re-deriving it.