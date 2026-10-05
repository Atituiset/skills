---
name: remotion-video
description: Produce or revise Remotion videos from articles, scripts, or existing video projects, with purposeful motion, narration-aligned scenes, quiet bottom captions, verified exports, and companion publication copy. Supports Chinese first and independently timed bilingual versions. Use when making a video with Remotion, improving a Remotion video's visual storytelling, or rebuilding a HyperFrames video in Remotion.
---

# Remotion video

Own the production workflow, while leaving visual direction to the brief. A new rendering framework alone does not improve a film: the mechanism must become visible through movement.

## Start from the actual request

- Inspect the existing brief, script, timeline, assets and package versions. Reuse correct narration and timings; preserve the original project when rebuilding in another framework.
- Infer topic, language and destination from the conversation and source material. Ask only for a missing decision that blocks useful work. A request for Chinese produces Chinese; create English only when requested.
- Record a short `BRIEF.md`: audience, message, duration target, format, visual direction, voice, music, caption mode and requested deliverable (preview, sample or complete MP4). Update it with accepted feedback.
- For an existing edit, change the requested behavior and complete the corresponding delivery. A sample complements a requested full film; it does not silently replace it.

## Set up the production

Use installed official Remotion skills for current APIs and project setup. If unavailable, consult [official documentation](https://www.remotion.dev/docs/ai/skills); this skill's workflow remains usable without other local skill directories. Install matching Remotion packages per project and pin their versions. Global AI skills and project runtime dependencies are different installations.

For project setup, reuse/migration, language versions, timing and rendering, read [production.md](references/production.md). For narrated output, also read [narration-and-captions.md](references/narration-and-captions.md). For an English or bilingual adaptation, follow the language-version guidance in those references: localize the whole film and validate its own voice, captions, animation cues and publication copy.

Complete setup when the project runs in Studio, required assets resolve locally, and the chosen preview URL is reachable. Keep that preview available while building when the environment permits it.

## Write a story the viewer can follow

For an explainer, start with a human situation and a reason to care. Introduce a limitation before its solution; use natural spoken pivots between ideas. One main idea per scene, with enough time to observe its mechanism and an ending hold. Derive duration from measured speech, not a fixed seconds-per-scene template.

For an existing project, inspect its actual content model, history data, paper references and interactive mechanisms before inventing a generic story. A framework migration must improve the explanation, not just reskin old scenes. For research histories, show what each paper changes in the mechanism; distinguish chronological order, direct lineage and parallel approaches.

Check technical claims against primary sources when uncertain. Distinguish mechanism diagrams, complexity sketches and measured results. Reusing a script does not make its claims correct; revise and re-record only affected lines.

Review the full narration consecutively before synthesis and again after structural edits. Check that each scene answers a question established earlier, pronouns and transition phrases have clear referents, terminology stays consistent, and the ending fulfills the opening promise. Match each claim to what its visual actually demonstrates; update stale headings and delivery notes along with spoken lines.

For excerpts, read the selected narration without the omitted scenes. Prefer a contiguous passage that establishes its own premise; rewrite dependent bridges and re-record them when needed. Refresh word cues, captions and durations after changing speech.

## Design movement before styling

Read [motion-direction.md](references/motion-direction.md) before authoring scenes or responding to “more dynamic / more creative”. Define the actor, action and visible result for each scene. Choose palette, typography, dimensionality and camera treatment to serve the content; the dark spatial example is one direction, not a required preset.

Build a representative motion passage early. Inspect actual playback as well as stills: color changes and particles alone are insufficient evidence of better motion. Continue through the authorized deliverable without imposing an unsolicited approval gate.

Use React/SVG/CSS or 3D as appropriate. Frame-driven transforms must remain deterministic under seeking. Give substantial scenes independent source components and editable timeline entries. Use a shared stage or visual anchor to connect scenes; compensate transition overlap explicitly.

Complete scene construction when actions match narration cues, the key state change is legible on mute, and the camera keeps important labels inside the frame throughout its travel.

## Quiet captions by default

Use whole phrases with punctuation, centered near the actual bottom edge. At 1920×1080, start with 34 px type, 24 px bottom inset, line-height 1.35, a soft white color and a restrained shadow. Scale with resolution and allow destination-specific safe-area changes.

Default to a single steady text color: no per-word highlighting, jumping, underline, pill or separate subtitle band. Keep scene explanation text visually distinct from narration captions and remove redundant sentences that compete for attention.

Use one caption owner for each active spoken phrase. [QuietCaptions.tsx](assets/QuietCaptions.tsx) is a reusable frame-driven component, not a complete scene template. If captions are burned into the video, keep optional SRT exports under `subtitles/`, away from the MP4, so players do not auto-load a second layer.

## Verify and deliver

- Run the project's lint/type checks, then inspect meaningful frames at scene starts, the largest camera displacement, mechanism changes and transitions. Verify movement with a playable short cut when it is central to the request.
- For complete-video delivery, render the full requested composition. Check resolution, fps, total frame count, duration and audio stream against the authored timeline. Use [verify-render.py](scripts/verify-render.py) for the bundled timeline format.
- Check CJK glyphs, caption readability, audio presence, broken assets and accidental overlapping subtitle sources. After an edit, verify the affected frames before re-rendering; broaden checks when new evidence warrants it.
- Link the actual current MP4 and, when helpful, a short preview or Studio URL. Use a new filename for a material revision so playback caches cannot conceal it. State what changed and any unverified part candidly.

## Publication copy, covers and screenshots

For each completed language version intended for sharing, deliver the MP4, a saved `PUBLISH.md`, a publication cover and a representative screenshot extracted from the final video, unless the user narrows the deliverables. Read [publication-copy.md](references/publication-copy.md) for this delivery and for requests about 发布文稿, 封面, 截图, titles or social posts. Verify that every requested language has its own files and links; copy written only in chat is not a saved deliverable. A narrow revision needs updates only to assets made inaccurate by that change.

Drafting publication copy does not authorize uploading or posting. External publication remains a separate user instruction.
