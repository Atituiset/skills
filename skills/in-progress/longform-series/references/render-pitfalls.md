# Render pitfalls

Every rule here was bought with a wasted 20–35 minute render or a false-fix loop on this run. Each entry is **symptom → cause → fix**. Match on the symptom.

## Motion: judder and shimmer

### An element that animates for the whole composition jitters every frame

**Symptom**: persistent per-frame shimmer on one element. Rounds of false fixes — opacity, transform sub-pixel values, quality settings — all changed nothing.

**Cause**: `will-change` held on an element for the composition's whole life. The hint is a browser optimisation for continuous interactive animation; per-frame-seek rendering has no such animation, so the promotion buys nothing and persists a composited layer across the entire shot, which fights the raster.

**Fix**: this pipeline carries **no `will-change` at all**. GSAP tweens the properties directly and the rasteriser handles it. Clearing the hint was the single change that ended the judder.

### Judder that survives every motion fix

**Symptom**: judder persists after the motion layer has been cleaned up, and the element's blur is not doing anything visible.

**Cause**: the element's `filter` property is animated *across a hold* — the tween runs, then the filtered state stays for the seconds the viewer reads the frame. A live filter forces a re-raster every one of those seconds, which reads as judder. `filter: blur(0px)` is the worst offender because it looks like a no-op and gets treated as one.

**Fix**: the boundary is the **hold**, not the tween. A short entry reveal that resolves and then releases the filter is within the size-scaled blur allowance from `cut-the-curve` (a 2px→0px reveal under a second, on one element, is fine and shipped in this project). A filter left alive for the read is the judder — drop it and get softness from opacity, scale, or a static filter value.

This trap cost the most time in the run, because the failing case is the one that looks most inert.

### Card content disappears behind the caption band

**Symptom**: the bottom row of card text is hidden under the captions.

**Cause**: authored content extends below `y = 896` while a caption band occupies the bottom of the frame.

**Fix**: authored content stays within `y ≤ 896`. Check it in the frame's own coordinate space, at every variant.

## Identifiers and selectors

### The runtime crashes on load and the frame renders empty

**Symptom**: a hard failure with a selector/CSS parse error, frame blank.

**Cause**: a CSS id selector starting with a digit.

**Fix**: attribute selectors (`[data-…]`) for anything whose name is derived from a number — card index, episode number, beat number.

### Every card animates in lockstep, and only card #1 ever moves

**Symptom**: one card tweens correctly; the rest sit still, or the whole set moves as one.

**Cause**: a generator emitted the **same id** for all 24 card instances, so every tween resolved to card #1. Duplicated markup plus hand-assigned ids is a bug factory — the duplication is invisible in review because the markup looks right on the first instance.

**Fix**: any block of markup instantiated N times takes its ids from a template, and uniqueness is *proven* by parsing the ids back out of the file and counting them before rendering. Generation plus a uniqueness check is the pair; either alone repeats this bug.

## Caption runtime

### A render that blows the navigation budget, sometimes

**Symptom**: the render stalls and eventually fails against the renderer's 10-second navigation budget. It regressed twice, in two different shapes.

**Cause**: a naive per-word `tl.set()` — about 15,000 synchronous timeline calls in this run.

**Fix**: flat `Float64Array` tables for the timing, binary search for the currently active group, and painting only the on-screen group from `tl.eventCallback("onUpdate")` with a `gsap.ticker` backstop. The runtime decides what is visible per frame; the timeline never holds per-word work.

### Chinese captions break mid-token, or get spaces between characters

**Symptom**: captions are unreadable or read as separate letters.

**Fix**: segment CJK without splitting a token and without inserting spaces between characters. Treat the TTS boundary as the guide and the word as the unit — do not let a character count decide the split.

### Injected caption skin renders in a fallback font

**Cause**: `font src` written composition-relative inside an injected skin, so it resolves against the composition instead of the document root.

**Fix**: `font src` is root-relative in any injected skin.

### Caption accent reads as a hyperlink

**Cause**: a saturated accent colour on the active word.

**Fix**: monochrome accent — ink opacity and weight carry unspoken / active / spoken. A saturated accent is read as "link" and pulls the eye off the thing being said.

### Two captions on screen, a frame caption under a card

**Symptom**: a card appears over a caption that is already painted.

**Cause**: an episodes-timeline merge that reuses master-timeline groups, so two caption groups are live at once.

**Fix**: the episodes timeline owns its own groups; the merge re-keys rather than reuses, and a variant renders exactly one caption group.

### Captions drift off the narration after an episodes variant is re-timed

**Cause**: counting lead-in **plus** lead-out when shifting a re-timed variant. Double-counting shifts every caption downstream.

**Fix**: count lead-out only.

## Seams

### A white flash at a crossfade on a dark film

**Symptom**: a one-frame white pop at every crossfade; invisible on light footage, glaring on dark.

**Cause**: the stage ground behind overlapping wrappers is transparent, so the transition's opacity dip composites to the page background.

**Fix**: an opaque `#root` background. Dark films need the stage ground opaque before any crossfade seam is trusted.

## Tooling, environment and delivery

### A scan that cries wolf is worse than no scan

**Symptom**: a scan for `will-change` returns ~300 hits and the project looks contaminated. The project is fine; the scan is noisy.

**Cause**: tldraw's exported SVGs inline a full computed-style dump (`tl-export-embed-styles`) on every `foreignObject` child, and that dump carries hundreds of literal `will-change: auto` plus inert `transition`/`animation`/`filter` defaults. None of it was authored.

**Fix**: treat only a **non-default** value as authored — `auto` is `will-change`'s initial value — and filter the dump before deciding anything. `scripts/check-hygiene.py` does both; a raw `grep -c will-change` does neither.

So **calibrate** the scan before trusting it: prove it against a project you know is clean, and know its expected inert-hit count for this project so a count above it is a finding. Once one run's output is mostly inert, every later run gets skipped unread — including the one real defect.

### A scan reports a defect that is not there

**Symptom**: the pre-render gate reports a tweened `filter` with a duration, on a statement that contains no `filter` at all. Three phantom findings in a row sent the work chasing a problem that did not exist.

**Cause**: the gate read a fixed-size **lookahead window** after each tween call. The window ran past the closing paren into the next statement, so that statement's `duration` was attributed to this one's `filter`.

**Fix**: parse the construct's **own argument body** — walk the delimiters to the matching close — never a character window. A window is a guess about where a construct ends; a matched delimiter is the answer. Any scanner that reads "after the match" for context has this bug waiting.

### Audio metadata replaced by an empty SFX set

**Symptom**: tracks that were previously voiced come back silent or unmapped after running a helper.

**Cause**: an SFX-fetching helper was run against a project that has no SFX, so it wrote its own metadata over the real one.

**Fix**: check for the project's SFX directory or manifest before running that helper. On a project without SFX it does not run at all.

### A long render dies partway with no error

**Cause**: the run was launched detached from a path under `/tmp`, which gets cleaned out from under a long job.

**Fix**: launch long renders detached from a durable path in the project or home directory, so the process survives anything that cleans temporary space.

### Hundreds of `content_overlap` lint warnings appear at once

**Cause**: stacked SVG beats overlap by design, and lint reports each overlap.

**Fix**: none needed. Know the expected count for the stacked-beat project and treat it as the baseline — a count above it is a real finding, the baseline itself is structural.

### A run that should take 20 minutes fails partway through

**Cause**: one of the long-timeout flags was left off on a software GPU.

**Fix**: take all three long-timeout flags together from the render-economics table in `SKILL.md`, every run, not only the long ones.

### The render captures every frame, then fails on a CDN fetch

**Symptom**: a full-length render runs to completion — 25 minutes of capture — and then reports `sub_timeline_script_failure: … gsap.min.js` and writes no output file. Two renders launched together fail identically.

**Cause**: the animation library is loaded from a CDN, once per composition. With ~30 compositions and one Chrome instance per worker, a single render issues dozens of concurrent requests for the same 72 KB file, and the run dies at the *validation* step — after all the pixels are already gone. Transient, and therefore invisible until it costs a whole run.

**Fix**: vendor the library once into `assets/vendor/` and point every composition at it with the same root-relative path the fonts already use. Local assets resolve from the project root in every composition, sub-compositions included, so one path form works everywhere. This also removes the last network dependency, which determinism required anyway.

**Before re-running a long render after any composition-level change, prove the change in one frame** — a `-c` draft render of a single frame costs seconds, and its pixel variance proves the library actually loaded. A successful render is not proof: a missing library yields a valid black video.

### Two projects in parallel took the machine down

**Symptom**: both renders die partway with no useful error, or the host itself becomes unresponsive. Memory looks fine at launch and collapses twenty minutes in.

**Cause**: core count is not memory. Each render worker is a headless Chrome holding a full composition DOM — with many sub-compositions and large inlined SVG, a worker costs far more than the ~256 MB the tooling quotes — and a long render accumulates. Six workers across two concurrent masters exhausted the host.

**Fix**: **one render at a time.** Measure the worker count against *available* memory, not total, and refuse to start below your own floor.

The measurement that guided the wrong decision was taken on a **proxy workload**. Worker scaling was measured on a light 48-card reel and read as "concurrency is 20% faster" — a true number about that reel and a false one about the film; the same numbers applied to two full masters exhausted memory and killed WSL. **Never extrapolate a measurement taken on a proxy workload.** Scaling does not transfer from a short card reel to a 29-sub-composition film: measure concurrency on the workload you will actually run, or take the conservative arrangement.

Verify from a **later** command that the process count and free memory both held — a launch-time check reads healthy long before the peak.

### A rebuild overwrote the only working copy

**Symptom**: a rebuild that failed partway left the artifact set with nothing usable — half-written new files and no intact old ones.

**Cause**: the rebuild wrote **in place**, so there was never a moment when the old set was whole and the new set was unproven.

**Fix**: build into `next/`, verify there, and promote over the old set only once the new set passes. The inherited files are the fallback, so they stay until the promotion; the interrupted state is never the delivered state.

### Two verification instruments disagree

**Symptom**: one verifier passes a file set and another fails it, on the same pixels. Neither is obviously wrong.

**Cause**: both instruments are keyed to a property the artifacts **share** — geometry, layout, an ink signature — instead of the property under test. Artifacts derived from one composition share their layout, so a layout instrument returns the same verdict for every file in the set and reads a layout change as a content change. In this project a grey luma signature and a plain IoU were both measuring the layout.

**Fix**: name the property each instrument measures before trusting either, and give content and layout separate instruments. Two instruments disagreeing is information, not noise — the shared input is the first suspect.

### A derived artifact ships with less packaging than the originals

**Symptom**: the master had publishing copy but no cover image, while all 25 episodes had both. The derived set looked finished, because finishing it had never been written down.

**Cause**: the packaging pass enumerated the artifacts it already knew about — the episodes — and treated anything else as a leftover rather than as an artifact class of its own. Cover + copy were a follow-up, not part of an artifact's definition.

**Fix**: enumerate the **artifact classes** first (master, episode, condensed version, any re-layout), then treat cover + copy as part of each one's definition of done. A class with no cover is not done.

### Detaching a long run so it survives its launcher

**Symptom**: a detached render dies within a minute with `render_cancelled_parent_exited`.

**Cause**: the launch command backgrounded the job with a trailing `&` inside the tool's shell, so the job stayed in the launcher's process group and was killed when the launcher returned.

**Fix**: put the whole detach *inside* the spawned shell and give the outer command no `&`:

```
setsid bash -c 'exec setsid nohup /path/to/run.sh > /path/to/durable.log 2>&1 < /dev/null &' < /dev/null > /dev/null 2>&1
```

Log to a durable path, not `/tmp`. Confirm survival by checking the process count from a **later** command, not from the launching one.

### Determinism

**Cause of every ghost bug**: anything that varies per run makes the frame un-re-renderable and destroys any before/after comparison.

**Fix**: every value in a composition derives from `hf-seek` time or from an authored constant. Wall-clock time, randomness, network fetches and CSS transitions/keyframes all belong outside the composition, which is why the composition is the only thing worth caching.