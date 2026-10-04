# Vertical short-form (Douyin / TikTok)

A 9:16 deliverable is a **re-composition**, not a crop. That sentence is the whole branch, and it was learned the expensive way: three attempts on one project, ~8 hours, none publishable. Read the failure table before planning anything.

## The law: direction has to be re-laid out, not re-scaled

Landscape compositions run **left-to-right**. A portrait frame runs **top-to-bottom**. Anything that keeps the original direction keeps the original problem, because the composition still wants width the canvas does not have — and the only two ways out are losing content or shrinking type.

So a crop is never the default, it is a fallback that has to be earned per shot:

> Choose the **layout** first. Reach for a crop only where the content genuinely wants the original direction, and prove on that shot that the crop keeps everything it needs.

## A growing diagram grows downward

This matters most when the source is a **progressive-disclosure diagram** — one world that accumulates beat by beat, which is what `visual-storytelling` produces. Landscape grows rightward. Portrait grows **downward**: stack the beat deltas top-to-bottom, first beat in the upper third, second below it, third below that. The film's grammar survives; only its axis changes. On the project that failed, this translation is the only approach that reached a readable type floor — every crop-based attempt landed at 16–22 px body type, and the beat stack reached 24–38 px.

The beat sources are already *deltas*, designed to be stacked in order over one another. Read the diagram skill's `SKILL.md` and its visual grammar before composing; several beats are meaningless alone, and a tldraw export pads every label box to the shape's full export width, so a naive bounding-box measurement reads a two-glyph word as 1400 px wide and makes a portrait layout look impossible when it is not.

## What was tried and what it cost

Every row is measured from delivered files, not estimated.

| Attempt | What it did | Measured outcome |
|---|---|---|
| Strict 9:16 centre crop | crop to a 608 px window (32% of a 1920 frame), upscale | **24/24 hooks clipped.** One hook's caption lost its own first character — the caption box was wider than the window |
| Union-bbox reflow | scale the bounding box of all artwork to 1080 wide | The box is mostly whitespace, so scaling to fit it shrank the type that mattered: 16–22 px, with dead bands above and below |
| Essential-bbox crop | scale to fit only text-bearing ink | Better, but still a crop of a left-right composition. Four hooks stuck at **16.3–18.6 px** because their text ink is one contiguous 1.4–1.8 k px band — question on one side, answer on the other, no cream gutter to cut at |
| Beat stack | restack the beats vertically | Reached 24–38 px. The only approach that cleared the floor |

Three of the four share one root cause: they solve a **crop** problem. The fourth changed the question.

## A hook is a post; a sequence of hooks is not a film

Individually sound hooks played back-to-back were judged **incoherent**, because each one independently picked its own claim text, its own beats and its own scale — so a beat was carrying half an idea when the next hook started a different one.

Treat the two deliverables as separate work:

- **A hook** is a standalone post. One question, its answer, a hook-first opening line. It is allowed to arrive cold.
- **A vertical film** needs **one portrait composition per source frame**, so the film flows instead of restarting every 20 seconds. It is not assembled from hooks, and its claim lines have to read as a continuous thread in order. Write them in sequence and check them in sequence.

## Captions are subordinate

This one came from the reviewer as a correction, and it is the rule: **captions must not be large, must not upstage or overwhelm the content** (「字幕不要太大，影响内容，会喧宾夺主」). In practice, on 1080×1920: a **46 px ceiling**, weight 400, ink quieter than the artwork's own spoken-group value, no filled pill behind the text, the band low, and **≥200 px of clear ground between the bottom of the picture and the top of the caption**. Captions and layout fail independently — check both.

A large share of viewers on these platforms watch **muted**, so burned-in captions are mandatory. In-picture captions are an advantage here rather than a compromise: they carry the narration with no audio at all, and they are already rendered per language.

## The lower bound is a real constraint, and it binds the art

English sentences are wider than Chinese at the same point size, and that changed the answer materially: captions measured at 30–45 px could not fit any 9:16 window, and the fix was **not** to enlarge them — which is what the first pass tried, and which made the problem worse. Smaller captions plus a subtitle track or a two-line re-set is the only route. Do not resolve an overflow by growing type past the ceiling.

The same floor applies to the diagram's own labels: when a beat's labels would scale under it, lift the label type inside that band rather than shrinking the band. Per-band, recorded, not global.

## Record hook spans as metadata, during copy writing

Every episode records **at least one hook span**, written at the same time as its copy:

- the span in **episode-relative** time (in/out on the episode, not on the master)
- the **reason** it is the strongest self-contained question-plus-answer moment — the question posed and the answer landed inside the span

Captured during copy writing because that is when the candidate moment is obvious; recovered later it is a search. With spans recorded, the vertical pass is a cut list; without them it is a manual hunt through half an hour, once per language.

Every declared span needs checking before it is trusted. On the project that failed, **24 of 25 declared spans per language cut mid-word**, because the declared times had never been mapped onto the master clock, and several overlapped the hook's own title card.

## Verify the delivered file, not the manifest

A treatment that reads well in a manifest can still be wrong in the pixels. Measure the output: ink touching the outer edge columns means content is cut; the gap between the lowest picture ink and the caption band tells you whether the caption is stuck to the picture; the caption band's ink height and bottom edge tell you whether it upstages the content and whether it has fallen under the platform's UI.

Build the verifier **before** the rebuild, run it on the files you are about to replace, and require it to pass on the new set before anything is promoted over the old. Inherited hooks are the fallback; do not delete them first. Two different instruments disagreeing is information — find out which one is measuring the shared layout rather than the content before you trust either.

## Cost, honestly

Budget a vertical deliverable as a **first-class re-composition** or do not ship it. Three attempts on one project consumed roughly eight hours and still did not reach publishable quality. A crop-based version is cheap to produce and reliably poor; if it has to be right, the layout work is most of the cost and should be scoped as such.

## Design tokens do not survive the aspect change

Caption size, title size and padding tuned for a 1080-tall frame do not read on a phone held vertically at 1080×1920, where the caption sits under a thumb and beside a UI overlay. Reconsider those tokens for the vertical composition — they are a per-layout decision, not an inherited value.