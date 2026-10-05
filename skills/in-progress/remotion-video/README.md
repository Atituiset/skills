# remotion-video

**Incubating** — see [skills/in-progress/](../README.md) for what that means.

Produce or revise Remotion videos from an article, a script, or an existing project: story first, movement designed before styling, **quiet captions by default**, and a verified delivery that includes the video, its publication copy, a cover and a representative still. Deliberately narrow about claims — the copy describes the delivered cut, not the ambition.

Pairs with [bilingual-video](../../video/bilingual-video/) and [bilingual-tech-explainer](../../video/bilingual-tech-explainer/), which own the bilingual film pipeline; a Remotion cut is one renderer option inside that layer, not a replacement for it.

## Layout

- `SKILL.md` — the eight steps: from the actual request, through setup, story, movement, captions and verification, to the delivery package
- `references/production.md` — project setup, composition structure, props and assets
- `references/motion-direction.md` — designing movement before styling
- `references/narration-and-captions.md` — one caption owner per spoken phrase, CJK coverage, readability
- `references/publication-copy.md` — `PUBLISH.md`, plus the cover and the original-video still, per language
- `scripts/prepare-timeline.py`, `scripts/gen-voice.py` — timeline scaffolding and narration
- `scripts/verify-render.py` — the checks to run before delivery, and what each one catches
- `assets/QuietCaptions.tsx` — the default caption component

## Status

`references/publication-copy.md` now covers the full delivery package — copy, a publication cover and a representative still from the final video — rather than copy alone, extended during production of the long-form bilingual explainer. The rule it encodes: **check every requested language individually** — finishing one version does not close a missing one.