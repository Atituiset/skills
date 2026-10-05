---
name: longform-series
description: Split a finished long-form bilingual explainer into a self-contained episode series in HyperFrames — one master render per language, then every episode cut and publishing package is ffmpeg off those pixels. Laws: the master renders once; an episode works for a cold viewer (lead-in poses its own question, deictic lines break self-containment); a shorter version is written for its runtime, not cut from the master (cue times re-warped onto the same frames); a 9:16 deliverable is a re-composition, not a crop. Plus render-economics flags (`-c/--composition`, `--quality draft|delivery`, `--batch`, `-w/--workers`, `--resume`) that decide which edits cost a re-render. Use when cutting a long video into episodes, splitting on narration anchors, writing an 8–10 or 3–5 minute version, re-laying out landscape for vertical, or debugging judder, blank cards, doubled captions and render cost. 把长视频拆成可独立观看的双语分集、写短版（重写旁白而非截取）、横屏重排竖屏、排查渲染抖动与字幕重复。
---

# Longform series (one master render, then an episode series)

**Status: incubating.** Distilled from one end-to-end run: a ~28-minute bilingual (zh+en) technical explainer built from a source article, split into 25 self-contained episodes for separate publication, condensed into 8–10 and 3–5 minute versions per language, and then taken down a vertical branch that never reached publishable quality — kept as a record, not as a deliverable. Most of the traps below were bought with 20–35 minute renders and false-fix loops. When a rule breaks in production, fix the rule here in the same commit.

**Dependencies**: the film comes from this repo's `video/bilingual-video` (dual projects, TTS, caption generation, publishing pack) and `video/bilingual-tech-explainer` (wall→fix spine, continuity kit); the diagram layer from the sibling `visual-storytelling` (progressive visual disclosure, static seek-safe assets). This skill owns everything from the split onward. Every number here is measured on that run — treat each as the shape of the cost, then re-measure on yours.

## The one law: the master renders once

Everything downstream is ffmpeg. The master mp4 — one per language — is the only thing the composition renderer produces. Episode cuts, per-episode publishing packages and hook spans are derived from the master's pixels plus the master's timeline data, so they cost seconds and the renderer stays cold. A condensed version is the one downstream artifact that touches the renderer, and it renders **frames**, not the film — see the Step 7 cost row.

Corollary: most "I changed one line, why is it re-rendering everything" pain is a **granularity** mistake, not a renderer limitation. Pick the **render unit** deliberately — a frame is the finest unit, an episode boundary is the coarsest — and the build time of the next hour follows from that choice.

## What each change costs

| Change | Cost |
|---|---|
| A narration line | Re-record that line → sync durations → re-time its frame → render that one frame (`-c`) |
| Frame composition markup, a card's ids, a seam | Render that one frame (`-c`) |
| One composition serving N variants (per-episode re-timed copies) | N renders from one source of truth via `--batch`, instead of N hand-duplicated copies |
| Episode boundary, episode title, chapter text, description copy | No render — re-cut with ffmpeg |
| An episode's hook span | No render — a different in/out on the same master |
| A condensed version's narration | Re-record that version's lines → re-warp the cue times of every frame they touch (`-c` per frame) → ffmpeg its cuts. Never a master render |
| A condensed version's runtime | No master render — it is its own set of frames, and its cuts and chapters come off them with ffmpeg |

## Render economics: which flag unlocks which fast path

| Fast path | Flag | What it buys |
|---|---|---|
| Render one composition instead of `index.html` | `-c, --composition=<file>` | The single biggest lever: a frame edit renders a frame, not the film |
| Iterate | `--quality draft` | Iteration passes at a fraction of a delivery run |
| Final | `--quality delivery` | The master, and any frame it depends on |
| N variants from one composition | `--batch=<json>` with `--variables-file` / `--variables` | Replaces N hand-duplicated copies of the same markup — the duplication that produced the duplicated-id bug |
| Parallel Chrome processes | `-w, --workers` | More workers inside one render. Scale against **available** memory, not core count — each worker is a Chrome holding the whole composition. Run one render at a time; see `references/render-pitfalls.md` |
| Resume a segmented capture | `--resume`, with `HF_SEGMENTED_CAPTURE=true` | A long segmented capture survives an interruption |
| Survive a software-GPU long run | `--browser-timeout 600 --protocol-timeout 1800000 --player-ready-timeout 900000` | A 20-minute run has already failed when one of these three was left off; take all three together |

## The gate before a render

A scan costs seconds; discovering its finding in the output costs a delivery render. Run `scripts/check-hygiene.py <project>` before every render, and fold it into the project's own `verify` step so nobody has to remember.

It hard-fails authored `will-change`, CSS `transition`/`animation` and `@keyframes`; it warns on tweened `filter` with the tween's own duration, because the judder boundary is the **hold**, not the tween. Its findings are calibrated — inert hits filtered, argument bodies parsed — so a count above the project's baseline is a finding; see `references/render-pitfalls.md` (tooling group).

## Workflow

### Step 1 — Beat sheet from the article

Progressive visual disclosure via the sibling `visual-storytelling`: one world that grows, one narrative event per beat, assets carrying no timing. The beat sheet's `at` anchors are narration *lines*, never timestamps.

**Done when**: reading the beats' reveal/action lines in order reproduces the teaching spine, and the final beat is the article's own summary.

### Step 2 — Storyboard with timings

Turn beats into frames: each frame gets a start, a duration, a title and the narration lines it owns. Durations come from the recorded narration, per language.

**Done when**: every frame carries a title and a duration, and the frame durations sum to the narration length for that language.

### Step 3 — One HTML composition per frame

Each frame is its own composition and renders correctly at an arbitrary seek time — nothing depends on what ran before it. Any UI that repeats, within a frame or across frames, is instantiated from one template, and a frame's styles ride inside its `<template>`. Both transports, the one that fails silently, and the pixel-diff that catches it are in `references/render-pitfalls.md` (identifiers group). Determinism is the contract that makes the frame re-renderable; the scan for it is in `references/render-pitfalls.md` (tooling group).

**Done when**: every frame opens standalone at any seek time, and rendering it twice produces identical pixels.

### Step 4 — Captions, per language

Build captions from that language's TTS word boundaries, so caption timing and card word reveals share one clock. Caption group = a phrase or breath group, never a 2–4 word fragment. The reveal clock, the runtime shape, the CJK segmentation rules and the skin/font traps are in `references/bilingual-dual-project.md` and `references/render-pitfalls.md` (caption runtime group).

**Done when**: every spoken word is covered by exactly one caption group, and both languages' captions land inside their own narration.

### Step 5 — Render the master, once per language

Final quality, the whole `index.html`. After this the renderer is done with the film. Run the gate first.

**Done when**: `check-hygiene.py` exits 0, both language masters render clean, and each one's duration matches its narration total.

### Step 6 — Cut the episodes (the ffmpeg layer)

Splits are **narration-anchored**, not duration-anchored. Each episode needs its own lead-in and lead-out; the design law, the deictic-line list and the length-cap exception are in `references/episode-self-containment.md`.

**Done when**: every episode has an in/out on the master's timeline, a lead-in that poses its own question, and a lead-out; the episode list and its boundaries live in a split manifest.

### Step 7 — Condensed versions (written for their own runtime)

An 8–10 minute and a 3–5 minute version are **second narrations**, not shorter masters: the same points in fewer words, so no scene ever needs truncating. Their cue times are warped onto the same frames, their covers and copy are their own, and their durations are ceilings to report a margin against. The law, the warp, and the cost of the segment-cut approach that failed first are in `references/condensed-versions.md`.

**Done when**: each version's measured duration is inside its ceiling with the margin recorded, and every point the long form makes is either present in the condensed narration or listed in that version's manifest as a named trim.

### Step 8 — Publishing packages

One package per episode per language, plus one per condensed version, carrying the same slots the single-film pack carries, re-timed to episode-relative time. Then machine-scan every publishable string — titles, descriptions, chapters, tags and every card line — for cross-episode references, with per-language banned patterns.

Covers come out of the same renderer as the episodes, parameterised by the manifest rather than copied per artifact class, and their legibility is measured at thumbnail size. The field-not-prose rule, the thumbnail measures and the manifest-parameterised renderer are in `references/render-pitfalls.md` (tooling group).

**Done when**: the scan returns zero hits in both languages, every chapter timestamp in a package is episode-relative and starts at zero, and every artifact class has its cover as well as its copy.

### Step 9 — Hook spans for the vertical branch

A 9:16 deliverable is a re-composition, not a crop, and this project never got one to publishable quality — so the branch is **recorded, not produced**. What survives as useful work is metadata: every episode records a hook span with its reason, written next to its copy, so a later vertical pass starts from a cut list instead of a hunt. The layout law and the failed attempts are in `references/vertical-shortform.md`.

**Done when**: every episode has at least one recorded hook span naming the question and answer inside it, or an explicit note that it has none.

## Reference map

| Open | When you hit |
|---|---|
| `references/render-pitfalls.md` | Judder, shimmer, blank cards, an instance that mounted as unstyled inline text, wrong or doubled captions, a runtime crash, a white flash at a seam, an unexpected pile of lint warnings, a render that died partway, a scan whose hits are all noise or are not there at all, a cut that lands off its time, a cover that reads at full size and not as a thumbnail, derived art that disagrees with its description, a rebuild that overwrote the working set, a release shipped without its cover |
| `references/episode-self-containment.md` | You are splitting, or a cold viewer cannot follow an episode — lead-in/lead-out wording, deictic lines, the banned-pattern scan, the cold-open decision |
| `references/condensed-versions.md` | You are making an 8–10 or 3–5 minute version — why cutting segments loses points, purpose-written narration, the piecewise cue warp, the trim ledger |
| `references/bilingual-dual-project.md` | zh and en timelines, TTS word boundaries as the reveal clock, cross-language re-timing |
| `references/vertical-shortform.md` | You are planning 9:16 and have to choose between a crop and a re-layout — pick the **layout** first, then read the attempts and what each cost. The branch was abandoned; the record is kept |