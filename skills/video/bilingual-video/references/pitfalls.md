# Pitfalls checklist (self-contained)

All rules distilled from one full production run (long technical article → bilingual 17-frame explainer video, five rework rounds), viewer feedback on a second production, and the publishing close-out of a third. Have any agent read this file before dispatching tasks to it.

## Narration & captions

1. Chinese TTS: edge-tts `zh-CN-XiaoxiaoNeural --rate=+3%`. Kokoro's Chinese voices have an accent, but its English voice (af_sky 1.05x) is excellent.
2. edge-tts's `Communicate(..., boundary="WordBoundary")` provides native word boundaries (the default is SentenceBoundary — you must pass it explicitly). It can directly generate an `audio_meta.json` compatible with the official pipeline (shape: `{bgm, voices:[{frame, path, duration_s, words:[{id,text,start,end}]}], sfx}`) — more accurate and cheaper than Whisper alignment.
3. SCRIPT.md frame headings must use half-width `(Frame N)` — full-width `（Frame N）` is not matched by the parser and silently generates 0 narration lines.
4. Kokoro/edge-tts output is deterministic: for script edits, re-record only the changed lines and merge them into audio_meta.json; untouched frames need no work at all.
5. Duration estimation: ~4.5 chars/second for Chinese is optimistic; dense technical explainers overrun by 10–16%. Remember to sync the storyboard's duration values.

## Caption style

31. Captions are plain text overlaid on the frame — no background pill/box. If legibility needs help, use a subtle text shadow, never a panel.
32. Caption groups are full phrases / breath groups (one sentence segment per line), not 2–4-word fragments — fragment captions flicker and read as rushed.
33. Never underline the currently-spoken word; highlight with accent color or weight if at all — underline reads as a hyperlink.
34. The official `captions.mjs` caps groups at 2–4 words (`wordCap` by density) — that violates rule 32, and English always hits the smallest cap. Before building EN captions, patch a copy of the script (`SILENCE_GAP` 0.18→0.55, `wordCap`→12), build, then restore the original file. Never ship the 2–4-word default for EN.

## Composition & timeline

6. DOM ids/classes starting with a digit (`01-hook-bg`) make querySelectorAll throw SyntaxError and kill the whole frame's script — they must start with a letter. The lint warning `id_requires_css_escape` is the omen.
7. Every full-length clip owns its own `data-track-index` lane; overlaps within one lane are rejected by the assembler.
8. Nested GSAP timelines are not scrubbed by the capture engine — to shift a timeline as a whole, mechanically shift all tweens with a script instead of nesting.
9. When renumbering frames / reordering the storyboard, heading replacement must use exact full-heading matches (a partial regex first matches a newly inserted same-prefix frame block, misaligning entire caption segments). After edits, reconcile frame# × duration × src.
10. Absolutely-positioned decorative elements belong directly under `#root`; inside a child container with `position:absolute` they are positioned relative to it and fly off-canvas.

## Animation & seek safety

11. Don't animate SVG arcs with GSAP `attr: stroke-dashoffset` — a same-named CSS declaration overrides it, leaving only the endpoints (the "broken arrow"). Tween the CSS property `strokeDashoffset` instead.
12. Arrow's three laws: tip stops ≥14px from the target; use an explicit polygon triangle placed after the node in DOM order (later paints on top); verify direction against the path tangent. Don't use SVG `marker-end` (refX semantics are a pit).
13. A touring highlight dot's parking positions must avoid all arrows.
14. Elements "flying into a container" should dock at the container's edge with a visible gap; flying to the center and fading out makes hold frames read as "the stage is empty".
15. `tl.set(el, {innerText})` is not seek-safe — flip state with stacked dual elements + autoAlpha crossfade.
16. GSAP's onUpdate orbit computations are skipped under `seek()` (suppressEvents) — do orbit-type motion with seekable transform tweens (e.g. rotating a parent `<g>`).

## Text & contrast

17. All text uses solid colors at ≥4.5:1 contrast — `check` samples animation mid-states, and low-opacity decorative text will always blow up the WCAG audit.
18. `mask-image` fade-outs turn scrolling text into ghost text whose contrast mathematically cannot pass (1:1), and no color change saves it — hard-cut outbound elements with `tl.set(opacity: 0)` at the moment they cross the boundary; lines that must remain visible use a solid dimmed color (e.g. rgb(129,128,126)).
19. CJK fonts: never put a font name that doesn't exist on the machine into a font stack; subset with `pyftsubset --text-file=<project glyphs> --flavor=woff2` (16MB → ~112KB) into `assets/fonts/` and reference via `@font-face`.

## Workflow & collaboration

20. System Python is protected by PEP 668 → build a venv inside the project (`scripts/.venv`). Kokoro needs `kokoro-onnx + soundfile` + `HYPERFRAMES_PYTHON` pointing at the venv.
21. Extracting only the body text of a saved web page loses all images — scan the `_files/` directory first; real benchmark screenshots / data figures are the best "evidence cards" for case frames.
22. The transition lands on the first 0.5s of the next frame — every frame must erect its stage scaffolding (kicker + title + diagram skeleton) by t≤0.45s, otherwise the audience repeatedly sees a blank canvas.
23. Cross-frame continuity comes from a persistent element shared across the whole film (the top evolution rail), not from transitions.
24. Large parallel sub-agent fan-out (>10) easily hits usage limits; if hit, recover with resume. Sub-agents' temporary verification files are deleted right after use (loose html files in the project root trigger multiple_root_compositions).
25. Parallel sub-agents overwrite each other's shared `snapshots/` directory — copy verification frames to a private path immediately after capture.
26. The model cannot hear the narration itself — a human must listen before publishing (especially mixed zh/en words). If unsatisfied, re-record by line + re-time the single frame; the cost is minutes.

## Narrative & pacing

27. Never cold-open on the technical origin ("1943, the neuron model"). Frame 1 establishes a human scenario and a reason to care before any term appears.
28. The wall→fix spine is scaffolding, not chrome: introduce each wall as a natural question or pain ("but here's the problem —"), never narrate mechanical labels like "boundary N". Wall cards appear once per layer opening, subtly.
29. Pivot sentences between knowledge points are mandatory; where the blueprint allows, transform a shared stage instead of hard-cutting.
30. Don't compress the storyboard into fewer frames — compression reads as a rushed slideshow (赶场). Budget ~15–20s per frame, one core idea per frame, ≥3min total for multi-layer topics; reveals fill each frame's full duration and every frame ends on a held beat.

## EN derivation gate

35. After copying frames into the EN project, re-run `assemble-index` + `transitions inject` — a stale `index.html` referencing renamed/deleted frames fails the render at compile time. And rebuild captions **before** assembling: the captions track is keyed on `compositions/captions.html` existing.
36. Never render EN before a CJK scan: `grep -cP '[\x{4e00}-\x{9fff}]' compositions/frames/*.html` must come back zero. Partial translation (later frames left Chinese) is the most common EN defect — agents translate the first frames and run out of steam.
37. Translation expands text width (自回归 → `autoregressive` is ~4×) and breaks absolute-positioned layouts — badges and labels collide. After translating, re-run `check` and expect overlap errors; reposition or shrink the element, don't silence them with `data-layout-allow-overlap`.

## Agent-run operations

38. Non-interactive agent runs (e.g. `opencode run`) auto-reject file access outside the working directory — copying fonts/scripts from skill dirs dies mid-pipeline. Use auto-approve (`opencode run --auto`) for full-pipeline jobs.
39. Invoke pipeline scripts via their **realpath**: skill dirs are often symlinked (`~/.config/opencode/skills/x` → `~/.claude/skills/x`), and under a symlink `process.argv[1] !== import.meta.url`, so the script's main block is silently skipped — exit 0, no output, no files written. Debug symptom: a pipeline script that "does nothing".
40. Long autonomous agent runs stall (small/free models especially) — typically after hours of good progress, in a long unstructured phase. Split the pipeline into bounded stages, resume stalled sessions with `--continue` (state is on disk), and judge progress by filesystem mtimes, never by the agent's own report.

## Publishing

41. The publishing close-out is **generated, not remembered**: run `scripts/gen-publish-pack.mjs` after each final render. Chapter timestamps must come from `index.html` (`data-start` / slot gaps) — hand-copied times go stale on the first re-render; the cover must `crop=1920:890` + `pad` (caption band out); and the pack's flatness probe over every frame close and transition seam catches a broken timeline before the upload, not after. Only the prose blocks in `PUBLISHING.md` are written by hand.
42. `renders/` accumulates stale cuts — the flashiest filename is not always the final render. Identify the final file by mtime and size before anything is uploaded (the pack lists every render and marks the selected one); a stale upload ships yesterday's film.
