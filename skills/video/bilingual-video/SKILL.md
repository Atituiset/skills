---
name: bilingual-video
description: The general layer for producing ANY bilingual (zh+en) video with HyperFrames, independent of video type — dual independent projects, edge-tts (Chinese) / Kokoro (English) narration with native word-boundary captions, the single-line re-record iteration loop, the generated publishing pack (cover / chapters / platform copy), and a 42-rule universal pitfalls checklist. Every route (explainer / promo / recut / motion-graphics …) passes through this layer first. Use when producing any bilingual (zh+en) video with HyperFrames, regardless of video type. 任何 HyperFrames 视频的中英双语生产通用层，与视频类型无关。
---

# Bilingual video production — the general layer (any video type)

This is the **shared foundation** for all bilingual video production, independent of video type. First route by intent via `/hyperframes` to a concrete workflow (faceless-explainer / product-launch-video / pr-to-video / talking-head-recut / embedded-captions / music-to-video / motion-graphics / general-video); this skill supplies the five things that stay invariant on top of all of them.

For technical explainer videos, use this repo's `bilingual-tech-explainer` directly (it depends on this skill).

## 0. Ask for the colour direction before building anything

The first question of a video project is not "what's the script" — it is **what colour is it**.
A film's ground (warm paper vs dark technical) is a taste call the author owns, it is expensive to
change late (a re-theme is cheap; a re-render is minutes; a re-authoring of 18 beats is a day), and
no default is right more than half the time. Ask once, up front, and record the answer:

1. **Ground** — light or dark?
2. **Register** — machinery / infra / systems usually wants a cool technical dark; people,
   process, and office-worker casts usually want a warm paper light. This one is a strong prior,
   not a rule — ask anyway.
3. **How loud is the accent** — one saturated family against neutrals, or several at equal weight?

Then thread the answer through, in this order, so it is set once and never re-litigated:
`frame.md` (design spec) → the theme sheet's named `--t-ground` / `--t-plate` → the contrast gate,
which must be **run against the chosen ground**, not against whatever the art tool defaulted to.
A palette re-asked at delivery is worse than a palette assumed at the start.

Per-family meanings (blue = knowledge, green = output, orange = methods, violet = the system,
yellow = human, red = walls, grey = annotation) stay fixed regardless of ground — a dark theme
re-picks values, it does not reassign meaning.

## 1. Dual projects, never parameterized

Build two independent projects, `videos/<name>-zh` and `videos/<name>-en`. Narration length can differ by up to 15% between languages; independent timelines are the only way to avoid contortions. Order: **build zh end-to-end to render first; then the EN project copies zh's `compositions/frames/`, translates frame by frame, and re-times to English word boundaries** — reveals must re-anchor to the word actually being spoken; uniform rescaling is forbidden. Mirrored edits are done twice and verified twice. Before the EN render, pass the derivation gate (pitfalls 35–37): re-assemble the index, CJK-scan every frame, re-run `check` for width-expansion overlaps.

## 2. Narration & captions (type-independent)

- **Chinese**: edge-tts `zh-CN-XiaoxiaoNeural --rate=+3%` (Kokoro's Chinese voices have an accent; its English voices are excellent). Use `scripts/gen-voice.py` — edge-tts's `boundary="WordBoundary"` native word boundaries directly produce an `audio_meta.json` compatible with the official pipeline, no Whisper needed:
  ```bash
  python3 -m venv scripts/.venv && scripts/.venv/bin/pip install edge-tts fonttools brotli
  scripts/.venv/bin/python <SKILL_DIR>/scripts/gen-voice.py --project .          # all lines
  scripts/.venv/bin/python <SKILL_DIR>/scripts/gen-voice.py --project . 3 4 5    # re-record only changed lines (merge)
  ```
- **English**: the official audio pipeline + Kokoro `af_sky` `--speed 1.05` (requires `pip install kokoro-onnx soundfile`, with `HYPERFRAMES_PYTHON` pointing at the venv).
- Both engines are deterministic. On both sides, use the official `audio.mjs sync-durations` to write durations back into the storyboard, and `captions.mjs` for captions.
- **Caption style (defaults for every video)**: plain text overlaid on the frame — no background pill/box (if legibility needs help, a subtle text shadow, never a panel). Groups are full phrases / breath groups (one sentence segment per line), never 2–4-word fragments. No underline on the currently-spoken word — highlight by accent color or weight if at all. Set these in the caption skin / `caption-overrides.json` before running `captions.mjs`.

## 3. The iteration loop (cheapest path for script edits)

Edit one line → re-record only that line (merge mode) → `sync-durations` → re-time only that frame (reveals re-anchor to the new word boundaries) → rebuild that frame's captions → `assemble-index` + `transitions inject` → `lint`/`check` → re-render. A single-line change costs minutes; never redo the whole film.

## 4. Publishing pack (the close-out, after the final render of each project)

Publishing materials are **generated from disk truth, never hand-copied** (pitfalls 41–42). Once a project's final render lands:

```bash
node <SKILL_DIR>/scripts/gen-publish-pack.mjs --project videos/<name>-zh
node <SKILL_DIR>/scripts/gen-publish-pack.mjs --project videos/<name>-en
```

Each run writes `PUBLISHING.md` in the project, computing everything that goes stale:

- **Render**: picks the newest mp4 in `renders/` and lists every other render as a verify-before-upload warning; cross-checks its duration against the index total.
- **Chapter timeline**: frame starts/durations from `index.html` (`data-start` / slot gaps) + titles from `STORYBOARD.md`; folds any <10s tail so the YouTube ≥10s rule holds automatically. Paste-ready blocks for the platform descriptions are embedded.
- **Cover**: highlight frame (default 70% into frame 1, tune with `--cover-at <s>`) → `crop=1920:890` + `pad` to 1080 in the frame's dominant color, cutting the caption band. An existing cover is kept; delete it to regenerate.
- **Health probe**: flatness-checks every frame close and every transition seam against the rendered mp4 — a blank/flat moment fails before an upload does.
- **Credits & checklists**: fonts from `assets/fonts/`, voice from `SCRIPT.md`, repo URL from git remote; Bilibili (科技→计算机技术, 原创) and YouTube (Science & Technology, tick **Altered content**) sections with the human pre-upload checklist.

Then fill only the prose: the `<!-- FILL -->` blocks (lede + title options, 2–4 sentences in the video's language). Never edit chapter timestamps or the deliverable table by hand — the script refuses to overwrite a hand-written `PUBLISHING.md` (marker check), and re-running regenerates everything else.

**A human must listen to the narration before publishing** (especially mixed zh/en words) — the model cannot hear itself (pitfall 26). The pack's checklist is the gate, not a formality.

## 5. Pitfalls checklist (45 rules, all universal)

`<SKILL_DIR>/references/pitfalls.md`: five categories — narration/captions, composition/timeline, animation/seek-safety, text/contrast, workflow/collaboration. Read it before dispatching tasks to any agent (or doing it yourself).
