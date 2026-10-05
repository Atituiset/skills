# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- New incubating skill `skills/in-progress/longform-series/`: turn one finished long-form
  bilingual film into a separately published series. Three laws — the master renders once and
  everything downstream is ffmpeg; an episode works for a viewer who has never seen the film or
  any other episode (its lead-in poses its own question, deictic lines break self-containment,
  the cold open becomes episode 1's front door rather than its own episode); and a shorter
  version is **written for its runtime, not cut from the master** — trimming inside a scene to hit
  a duration ceiling drops the point of the passage, not just its tail, so the fix is
  purpose-written narration plus a piecewise cue warp built from an LCS alignment of the old and
  new word timings with cue anchors on top. Ships with `references/render-pitfalls.md` (a
  symptom → cause → fix catalog of everything that cost a 20–35 minute render here, including
  the three classes of false positive a hygiene scan produces) and `scripts/check-hygiene.py`,
  a pre-render gate that hard-fails authored `will-change`, CSS animation and remote references
  and warns on a tweened `filter` against the hold boundary. Also records the abandoned 9:16
  branch — three attempts, ~8 hours, unreached — with the measured cost of each crop-based
  treatment, because a 9:16 deliverable is a re-composition and not a crop. Per CONTRIBUTING:
  incubating, not in the plugin marketplace.
- New incubating skill `skills/in-progress/tldraw-video-assets/`: integrate tldraw-exported SVG
  artwork into a deterministic video pipeline, which is a separate concern from
  `visual-storytelling`'s design layer. The export is a **document, not an image**: labels are
  live HTML inside `<foreignObject>` in the language the diagram was drawn in, every label inlines
  a full computed-style dump (one inert `will-change: auto` each, ~300 per project — all noise),
  declared boxes are padded far past their ink (up to 111×), `opacity="0"` clip rects declare a
  far larger box than anything painted, and path `d` numbers must be walked rather than paired
  two-by-two (a 300 px connector measured 1413 px wide, and every downstream conclusion rested on
  that number). Verification is by pixels — stacked beats reproduced `final-frame.svg` at zero
  differing pixels of 921,600 — because a composition can render successfully and still be blank.
- New incubating skill `skills/in-progress/visual-storytelling/`: turn an article's
  narrative into a growing hand-drawn cartoon diagram world — progressive visual
  disclosure (one world that grows beat by beat), a fixed visual grammar
  (`references/visual-grammar.md`), and a narration-anchored beat sheet that renders
  to static SVG assets. Timing is never baked into assets; HyperFrames owns the
  timeline, keeping bilingual re-timing independent. Ships with a complete worked
  beat sheet for a real LLM/RAG/Agent explainer article plus its rendered output
  (18 per-beat delta SVGs, a final frame, and shared `fonts.css` — stacked and
  pixel-verified). Incubating per CONTRIBUTING: not yet exercised on a shipped video.

### Changed

- Root `README.md` / `README.zh-CN.md`: the "why these skills exist" failure-mode list grew from
  three to six, adding the three that only a long-form production surfaces — a render that
  succeeds and is still wrong, tooling that misreports in both directions (noise-only scans and
  phantom findings), and concurrency being unsound on a small host. The iteration entry now
  carries measured numbers (a 25–35 minute master re-render → 11 s for the one frame that
  changed) and the corollary that most of that pain is a granularity mistake rather than a
  renderer limitation. Both files also describe the in-progress cycle and the 29-minute
  production behind it, linking to `skills/in-progress/` rather than listing incubating skills in
  the reference table, per ADR-0001.

## [0.3.3] - 2026-09-28

### Added

- **Publishing close-out as a skill step** (from the third production's delivery run):
  new `bilingual-video/scripts/gen-publish-pack.mjs` generates a project's `PUBLISHING.md`
  from disk truth — newest render in `renders/` (older cuts listed as a verify-before-upload
  warning + duration cross-check), chapter timeline from `index.html` slot gaps and
  `STORYBOARD.md` titles (folds <10s tails for the YouTube ≥10s rule), cover
  (`crop=1920:890` + `pad` in the frame's dominant color; existing cover kept), a
  flatness probe over every frame close and transition seam, credits (fonts / voice /
  repo URL) and the Bilibili (科技→计算机技术 · 原创) + YouTube (Science & Technology ·
  Altered content) sections with the human pre-upload checklist. Only the `<!-- FILL -->`
  prose blocks stay hand-written; the script refuses to clobber a hand-authored file.
- Pitfalls 41–42 (new "Publishing" category): generate the pack from disk truth
  (hand-copied chapter times go stale on the first re-render); `renders/` accumulates
  stale cuts — confirm the final file by mtime/size before uploading.

### Changed

- `bilingual-video` SKILL.md §4 rewritten from a conventions list into the executable
  close-out step; pitfall counts 40 → 42 across both skills' READMEs and SKILL.md files.

## [0.3.2] - 2026-09-26

### Added

- Pitfalls 34–40, from the second production's finishing run:
  - 34 (Caption style): official `captions.mjs` 2–4-word cap violates rule 32
    for EN — patch a copy (SILENCE_GAP 0.18→0.55, wordCap→12), build, restore.
  - 35–37 (EN derivation gate): re-assemble index after copying frames;
    CJK-scan all frames before render; translation width expansion breaks
    absolute layouts — reposition, don't allow-overlap.
  - 38–40 (Agent-run operations): non-interactive runs need auto-approve for
    external paths; invoke pipeline scripts via realpath (symlinked skill dirs
    silently no-op); long autonomous runs stall — bounded stages, `--continue`,
    verify by filesystem mtimes.
- `bilingual-video` SKILL.md §1 now points at the EN derivation gate.

## [0.3.1] - 2026-09-26

### Added

- Caption style rules, from viewer feedback on the second production:
  pitfalls 31–33 (new "Caption style" category: plain-text captions without
  background pill, phrase-length groups instead of 2–4-word fragments, no
  underline on the spoken word) and a matching caption-style bullet in
  `bilingual-video` SKILL.md §2.

## [0.3.0] - 2026-09-26

### Added

- Pitfalls 27–30, new "Narrative & pacing" category, distilled from viewer
  feedback on the second production: never cold-open on the technical origin;
  walls narrated as natural questions, not "boundary N" chrome; mandatory
  pivot sentences between knowledge points; never compress storyboard pacing
  (~15–20s per frame, ≥3min for multi-layer topics).
- `bilingual-tech-explainer` SKILL.md narrative spine rewritten as four hard
  requirements matching those rules.

### Changed

- Rule count references updated 26 → 30 across all READMEs and SKILL.md files.

## [0.2.1] - 2026-09-26

### Changed

- `examples/README.md` rewritten English-primary (short zh pointer kept).
- `storyboard-skeleton.md` gained an English orientation note; the body stays
  Chinese by design (frozen `language: zh` recipe — zh is built first, EN derives).
- Root READMEs gained CI / release / license badges.

## [0.2.0] - 2026-09-26

### Changed

- SKILL.md bodies and the 26-rule pitfalls checklist rewritten English-primary
  (short zh summary kept in each `description` for zh routing). Recipe and
  storyboard skeletons intentionally stay Chinese — they are content templates
  for the zh project. This is the internationalization milestone.

## [0.1.0] - 2026-09-25

First structured release.

### Added

- Category layout `skills/<category>/<skill>/` with taxonomy rules in
  `skills/README.md`, governed by ADR-0001 (`.agents/adr/`).
- `video` category containing the two existing skills:
  `bilingual-video` and `bilingual-tech-explainer`.
- Claude Code plugin manifests (`.claude-plugin/plugin.json`,
  `marketplace.json`) — installable via `/plugin marketplace add`.
- CI validating the skill contract (frontmatter, name/directory match,
  relative links) via `scripts/validate-skills.mjs`.
- `CONTRIBUTING.md`, GitHub issue templates (bug report, skill proposal).

### Changed

- Root README rewritten (EN + zh-CN): narrative "why these skills exist"
  structure, 30-second install for all channels, per-category reference table.
- LICENSE copyright holder corrected to the current project identity.
