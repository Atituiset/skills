# Production and timing

## Project and official guidance

Use a separate project for a framework rebuild, retaining old scripts and media as source assets. A HyperFrames HTML/GSAP timeline cannot run unchanged in Remotion. Rewrite scene components and frame-driven motion; reuse suitable narration, screenshots and measured word boundaries.

Use the installed official `remotion-create`, `remotion-markup`, `remotion-captions`, `remotion-studio` and `remotion-render` instructions when relevant. Otherwise consult the current official docs. Scaffold with the supported CLI, retain exact versions in `package.json` and the lockfile, and use matching `@remotion/*` versions. Avoid copying a historical version number from this skill.

Put render assets under `public/` and reference them through `staticFile()`. Bundle fonts that cover every actual glyph, especially Chinese. Verify image URLs and font loading in rendered frames rather than assuming Studio fallback matches export.

## Narrated timeline

Use one measured timeline as the source of truth. The bundled helper reads `audio_meta.json` and emits `src/generated/timeline.json`:

```bash
python3 <skill-dir>/scripts/prepare-timeline.py --project <project> --fps 30 --hold 0.8
```

Its scene entries contain `id`, `from`, `durationInFrames`, `audio`, and local `captionPages`. All scene starts are integer frames. Duration is `ceil(audioSeconds * fps) + holdFrames`, so rounding never trims the measured audio. It also exports an optional SRT to `subtitles/`.

Each scene's caption component reads its local frame. A short selection can reuse a scene at a different parent start without carrying stale global caption offsets. Apply the standalone narration review in `SKILL.md` before reusing that selection. A global caption track instead needs explicit remapping for excerpts; choose one ownership model per film.

If a transition overlaps by `k` frames while narration starts must remain fixed, extend the preceding visual slot by `k` and subtract the transition's overlap. Account for final holds, audio duration and composition metadata together. Independently editable authored JSX is useful, but duplicated timing literals must be synchronized with generated data; runtime drift is not an acceptable source of truth.

## Language versions

Produce only requested languages. Chinese and English need independent measured timelines even if they share reusable scene components. Translate first, regenerate voice and word cues, then re-anchor each reveal to the new language. Uniform timeline scaling does not preserve semantic timing.

Keep locale-specific scripts, audio, generated timings, outputs and publication copy separate; independent project folders or clearly isolated locale directories both work. Share visual components only where that preserves independent timing and layout.

Localize titles, diagram labels, legend text, citations' explanatory notes and closing text, as well as speech and captions. Preserve paper titles, proper names and intentional translation examples. Review line widths with the target font instead of forcing translated text into the original label size.

Match animation cues against the target-language word boundaries. Normalize case, spacing and punctuation consistently for English lookup; prefer distinctive phrases. Validate every cue before export and surface missing matches instead of silently falling back to the source-language timing. Generate chapter timestamps and `PUBLISH.md` from that language's final cut.

## Preview and export

Start Studio as soon as the project runs. Verify its real URL. Shell backgrounding does not guarantee that a process survives the agent session; keep the session alive or use a persistent mechanism supported by the environment. Report honestly if only the MP4 is available.

Choose render concurrency from available memory and CPU; don't run multiple heavy exports merely because they are independent. Put verbose frame progress in a log and report meaningful milestones. Use an installed compatible browser when appropriate, or let Remotion fetch its supported browser within environment permissions.

For a revision, render a new output filename and link it explicitly. Preserve requested resolution and narration unless the user asks otherwise. A short style sample supplements the full film when both are in scope.

Verify bundled timeline exports:

```bash
python3 <skill-dir>/scripts/verify-render.py --project <project> --video renders/final.mp4 --width 1920 --height 1080
```

This checks container metadata and flags a same-basename sidecar subtitle under the default burned-in caption mode. It does not replace visual inspection or listening. Use `--caption-mode external` for an intentionally uncaptioned picture delivered with external subtitles.

## Targeted recovery

A native bundler crash after an interrupted install may come from a truncated binary. Reproduce the failure with the smallest module load, inspect the file, and reinstall the affected pinned package when corruption is demonstrated. Do not treat every crash as corruption or change framework versions blindly. A successful module load plus the original build/render command closes that diagnosis.
