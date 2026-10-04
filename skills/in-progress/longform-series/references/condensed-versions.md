# Condensed versions (8–10 minute and 3–5 minute cuts)

A long film usually ships beside two shorter versions of itself: one that fits a long-form slot, one that fits a feed. Both were produced on this project, in both languages, and the first approach failed in a way worth recording — because it looked reasonable.

## The law: a condensed version is written for its runtime, not cut from the master

A condensed version built by **cutting existing segments** loses content, and it loses it in a specific way: to hit a duration ceiling you trim *inside* scenes, and truncating a scene mid-passage drops the **point** of the passage, not just its tail.

What the first pass lost, by version:

| Version | Gone from it |
|---|---|
| 8–10 minute | the whole Context Window passage — the 128K / 200K / 1M material and the idea that a bigger desk holds more material; the seven-material list; nine named tools with three worked examples; the phrase "Tool Use" itself |
| 3–5 minute | exactly one mention of *hands* anywhere in it — the word "Tools", sitting inside a list |

None of it came back by re-cutting. The surviving passes had nothing to give, because what was missing was not time; it was sentences.

The fix is **purpose-written narration for the runtime**: same points, fewer words. A condensed line is *written*, so its scene never needs truncating. After the rewrite both versions landed in range — 9:25 and 4:58 — with every lost item back in.

Think in **points**, not scenes. Enumerate what the long form establishes, then write the shortest narration that still establishes each one. A scene is not a unit of content; a point is, and a scene may hold several.

## Ceilings are ceilings, not aspirations

A named runtime range is a **ceiling**: "8–10 minutes" means 480–600 s, "3–5 minutes" means 180–300 s. Measure the delivered file and report the **margin** against each ceiling. Two seconds of headroom is a finding — the next line pushes it over — not a pass.

## The time warp

A frame composition's cues are **absolute frame-local times**. New narration therefore means new cue times *everywhere in that frame*: every card reveal, every caption group, every state change. Nothing in the frame survives by offset.

The working approach is a **piecewise-linear warp**, never a constant scale, built from two sources:

1. **Alignment.** An LCS alignment between the master line's word timings (`audio_meta.json`, frame-local) and the new line's yields a statistical old-time → new-time map. Most of the frame comes from this.
2. **Anchors.** The cue times where the picture must land on a specific word, authored by hand, overriding the map. These are what make the warp trustworthy where it matters.

Piecewise, not uniform: a uniform scale is simpler and it reads rushed, because it compresses every beat by the same factor. A piecewise curve **holds** on the beats that carry a point and **compresses** on enumeration — the one place where words per second can rise without anything being lost.

Record which warp each frame used. A frame whose cues were never warped back drifts silently, and nothing downstream detects the drift.

## Derived artifacts need their own narration

The first pass opened and closed the condensed versions on cards that no existing line fit, and shipped them **silent** — 4.8 s of silence at the front, 4.8 s at the back. Silence on an opening or closing card reads as a broken export, not as a style: the viewer has no way to tell the difference.

The cards belong to the condensed version, so the condensed version's script answers them.

## A condensed cut obeys the self-containment law

The same law as an episode split (`references/episode-self-containment.md`), applied to a version: no included beat may open on a back-reference to something the cut dropped.

The first 3–5 minute version explained Agent without ever saying what Agent does **not** know, because the frame that paid that off was 98 s away and did not fit. Nothing was wrong with either frame; the cut separated a limitation from its consequence. Include the limitation or drop the consequence — never keep the consequence and lose its setup.

## Record every trim and every warp

Every trimmed passage and every warped frame is a **recorded cost**, in the version's manifest and in its publishing copy. A trim nobody wrote down reads as an oversight to the next person, who then re-litigates the cut. Per version, per language, the manifest carries: the dropped passages with their reason, the warp each frame used, and the measured duration with its margin against the ceiling.

## Each version is its own artifact

Its own cover, its own publishing copy, its own chapters — **indexed** from the main document rather than reproduced there, so a title changes in one place. The class-level rule behind this (enumerate the artifact classes, and treat cover + copy as part of each one's definition of done) is in `references/render-pitfalls.md`.