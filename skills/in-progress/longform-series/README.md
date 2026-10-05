# longform-series

**Incubating** — see [skills/in-progress/](../README.md) for what that means.

Splits a finished long-form bilingual explainer into a self-contained episode series. The law: **the master renders once, everything downstream is ffmpeg** — one master per language, then every episode cut and publishing package comes off those pixels at ffmpeg speed. Carries the split design law (each episode poses its own question; deictic lines break self-containment), the condensation law (a shorter version is written for its runtime, not cut from the master), the render-economics flags that decide which edits cost a re-render, and the per-frame-seek traps that cost 20–35 minute renders.

Pairs with [bilingual-video](../../video/bilingual-video/) and [bilingual-tech-explainer](../../video/bilingual-tech-explainer/), which own the film, and the sibling [visual-storytelling](../visual-storytelling/), which owns the growing-diagram layer inside it.

## Layout

- `SKILL.md` — the law, what each change costs, the render fast-path flags, the workflow with completion criteria, and the reference map
- `references/render-pitfalls.md` — the trap catalog as symptom → cause → fix, grouped: motion/judder, identifiers and template transport, caption runtime, seams, tooling and delivery
- `references/episode-self-containment.md` — the split-design law: lead-ins, lead-outs, the deictic-line list, narration-anchored splitting, the cold-open decision, the banned-pattern scan
- `references/condensed-versions.md` — the condensation law: why cutting segments loses points, purpose-written narration for a runtime, the piecewise cue-time warp, the trim ledger, duration ceilings as ceilings
- `references/bilingual-dual-project.md` — why zh and en carry separate timelines, the word-boundary reveal clock, the seam-holding card, episode-relative split offsets
- `references/vertical-shortform.md` — the 9:16 re-composition law: layout before crop, the hook a vertical film must not be, the attempts and what each one measured, muted viewing, tokens that do not survive the aspect change
- `scripts/check-hygiene.py` — the pre-render gate. Hard-fails authored `will-change`, CSS `transition`/`animation` and `@keyframes`; warns on tweened `filter` with its duration, since the judder boundary is the hold. Calibrated against inert hits and phantom findings, so its output can be trusted. Exits 1 on a hard failure.

## Status

Distilled from one end-to-end run of the whole pipeline — see the status line in `SKILL.md` for what that run covered and which rules it revised. Every trap in `references/render-pitfalls.md` actually happened there.

The vertical branch was attempted and abandoned: repeated crop-based re-layouts of a landscape composition never reached publishable quality, and the one approach that cleared a readable type floor turned out to be a layout decision rather than a crop decision. The branch is kept as `references/vertical-shortform.md` because the failure is the lesson — a 9:16 deliverable is a re-composition — and the attempts, their measurements and the abandoned state are recorded rather than lost. The graduation test is a second series built with this skill, after which the rules get revised from what broke.