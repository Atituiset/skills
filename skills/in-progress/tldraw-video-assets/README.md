# tldraw-video-assets

**Incubating** — see [skills/in-progress/](../README.md) for what that means.

The integration layer for tldraw-exported SVG artwork in a deterministic video pipeline: what the exporter physically contains, what breaks downstream, how to measure it, how to verify it, how to re-place it on a different canvas.

Pairs with [visual-storytelling](../visual-storytelling/), which owns the design layer — the primitive grammar, the beat sheet, progressive disclosure, the reveal contract. What a diagram should say is that skill's; what tldraw's output *is* is this one. The worked asset set this skill was measured against is that skill's `examples/agent-article-beats/`.

## Layout

- `SKILL.md` — the law and six rules, each with its measured evidence, plus the verification checklist
- `references/export-anatomy.md` — element-by-element anatomy of an export: the shape wrapper, the fill/outline pair, the arrow's separate shaft and head, the invisible clip rects, the clipPath id scheme, the two style dumps, the label padding tiers
- `references/measurement-and-verification.md` — the path-data walk, the transform stack, the over-estimate bias, per-beat measurements, pixel equivalence, the dark-pixel bbox, the hygiene scan
- `references/replacing-on-a-new-canvas.md` — the beat stack, per-beat `viewBox`, the type-lift arithmetic against a floor, choosing which beats a moment needs, recording what was dropped

## Status

Every rule here was distilled from one real integration: 18 beat deltas plus a final frame, consumed by a rendered bilingual landscape film and then re-planned as a 29-frame portrait beat stack. The asset set is pixel-proven — stacking beats 1–18 reproduces the final frame with 0 differing pixels — and the portrait stack is the only part not yet put through a full render. The skill itself has not been exercised on a second project; the graduation test is one more artwork set taken through it from a clean checkout, then a revision from what broke.