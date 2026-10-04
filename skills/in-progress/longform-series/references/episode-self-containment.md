# Episode self-containment

The design law for every split in this series.

## The law: an episode works for a cold viewer

An episode is published alone, to a feed, with no master behind it and no episode 16 above it. Assume the viewer has seen none of this material. Every line either survives that assumption or is rewritten.

The test: hand an episode — its frames, title, description and cards — to someone who has never seen the film, and they can state what question it answers and what answer it gives.

## Lead-in poses that episode's own question

Each episode opens by posing **its own** question, in **its own** terms. Not the film's question, and not a narrowed version of it phrased as a recap. The lead-in is written from the episode's own content, after the boundaries are set — never inherited from the master's opening and trimmed.

## Lead-out is an invitation

The last lines name the next episode's subject as an **invitation**, never a prerequisite. "Next: why retrieval breaks at scale" invites. "You can't understand this without episode 3" is a prerequisite, and it makes the episode non-standalone.

## Deictic lines break the episode

These are the lines that kill self-containment, because the viewer of episode 17 has no referent for "these", "that", "before", or "now":

- "These practices…"
- "As mentioned earlier"
- "In the last episode"
- "Now it's its turn"

Split them by **who they address**:

- Lines addressing **the viewer** stay — "say back to yourself", "look at your own setup". The viewer really is the referent, and the line works cold.
- Lines addressing **another episode** go — their referent does not exist in this episode, so they resolve to nothing.

Rewriting a deictic line is usually a two-word change: name the thing instead of pointing at it ("these practices" → "retrieval practices").

## Split on narration, not on duration

**Narration-anchored**: a frame that opens by referring back — "now RAG makes sense" — stays with the frame it refers back to, however long that pair runs. A duration-anchored split that separates them leaves an episode opening on a word with no antecedent.

So a length cap is a **target, not a gate**. When comprehension beats the cap, the pair runs long and wins; record the exception in the split manifest with its reason, so the next person reads it as a decision rather than as an unfixed bug.

Each boundary therefore sits on a narration boundary, and the split manifest records episode → in/out → the narration line at each edge.

## The cold open is the front door of episode 1

A cold open that enumerates the film's contents becomes a spoiler the moment the film is an episode series — the viewer has not seen any of it, and the enumeration tells them what they are about to get instead of making them want it. Meanwhile a standalone episode that only promises other episodes contains nothing at all: it is an advertisement for a film, published where a film cannot play.

**Decision**: the cold open belongs to episode 1 as its front door, not as an episode of its own. Episode 1 is allowed to be the long one — it is carrying the setup the rest of the series assumes.

## Machine-scan every publishable string

Cross-episode references hide in copy, not just in narration, and they hide most often in the strings nobody re-reads. After the copy is written and before the cut runs, scan **every publishable string** in both languages: titles, descriptions, chapter titles, tags, and every card line.

The scan is a **per-language banned-pattern list** of the deictic constructions above, run as a substring/regex match over those five string sets. Any hit is a rewrite, not a warning.

Run it as a script with a non-zero exit on any hit, so an added episode cannot quietly reintroduce a banned pattern into 25 packages at once.