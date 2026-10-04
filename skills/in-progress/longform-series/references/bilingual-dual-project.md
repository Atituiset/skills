# Bilingual dual-project mechanics for a series

The general dual-project construction — build order, TTS engine choice, per-line re-record — belongs to `video/bilingual-video`. What is here is what changes once the film is also an **episode series**.

## Two timelines, because zh runs longer

zh and en are **separate projects with separate timelines**, and in this run zh narration ran ~15% longer than en. A shared timeline would drag one language's reveals off its own speech to fit the other, and every caption would inherit the error.

Everything downstream of the master is therefore per language: one master per language, one episode list per language, one publishing package per episode per language, one set of hook spans per episode per language. The two episode lists share their **content** — the same boundaries in the same order — and nothing else.

## Word boundaries are the reveal clock

Word-level TTS boundary data drives **both** caption timing **and** card word reveals. It is the only clock in the project that is anchored to the actual speech.

- Reveal on **spoken words, with a 0.10–0.20 s lead**, so the word is already there when it is said.
- An **even grid** of reveals looks fine in a still and desyncs from the voice by the end of a card.
- Reveal **between** words, never mid-word — a reveal that lands inside a spoken word reads as a stutter in the card, not as timing.

When an en frame is re-timed from its zh original, reveals re-anchor to the en word being spoken. Scaling zh timestamps by a ratio is the same defect as a shared timeline, one layer down.

## A card that holds to the seam has no exit tween

When a card is authored to hold past the cut into the next clip, it takes **no exit tween**. The cut is hard — a fade-out across that boundary animates into footage that is no longer there. Its last visible state is its authored state, and the next clip picks up the frame.

## The split offsets are language-relative

Episode boundaries are recorded against each language's own master. A boundary named in master time is not portable: the zh and en masters drift apart by the length difference, so master-time boundaries land in different narration lines in the two languages. Record in/out in **episode-relative** time once the episode is cut, and keep the master-time edge beside it only for the ffmpeg call that produces the cut.