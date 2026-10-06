# Visual grammar

The fixed primitive vocabulary for `visual-storytelling`. Cast every concept into one of these before inventing anything. When a real beat sheet needs a primitive that is missing, add it here in the same commit — the catalog grows from production, not from anticipation.

Each primitive lists: what it means, and its canonical composition (the default way to draw it). Canonical compositions exist so that "RAG" looks the same in every video; deviate only with a narrative reason.

## Primitives

| Primitive | Means | Canonical composition |
|---|---|---|
| `actor` | A thinking entity — user, LLM, agent | Simple character (round head + body); a brain mark 🧠 above when it is an LLM; labeled beneath |
| `container` | A system boundary — agent, context window, platform | Rounded rectangle enclosing other objects, label on the top edge |
| `tool` | A capability the actor operates — Excel, browser, shell | Hand/tool icon in a small box, hung off the actor's side. **Screen variant (Computer Use)**: a monitor/screen box beside the tools box — for systems with no API the tool works like a person: look at the screen, click, type |
| `document` | Knowledge at rest — file, PDF, wiki page | Stacked pages glyph; a stack of them = knowledge base |
| `memory` | Remembered experience — notebook, not knowledge base | Notebook glyph attached to the actor with a dashed line |
| `flow` | Data or control moving — question in, answer out | Arrow with a small label on it; direction always reads left→right or top→down |
| `barrier` | A limitation or wall — the thing that breaks | Brick-wall card or ✗ card across a flow; when the fix lands it flips to ✓ + strikethrough — the flip is the same beat's `mutate`, sharing the beat with the bridge that crosses it (one narrative event, never a beat of its own) |
| `bridge` | The fix that crosses a barrier | The new object landing exactly where the barrier stood |
| `magnifier` | Retrieval, search, analysis | Magnifier glyph over a document stack |
| `loop` | Iteration — observe → think → act → check | Ring of 3–4 arrows around the actor, one stage highlighted per beat |
| `team` | Multiple actors cooperating | One larger `actor` (lead) with smaller actors fanned beneath, connected by lines |
| `gate` | Human approval point | Checkpoint barrier on a flow with a person glyph; flow pauses at it |
| `fence` | Permission / sandbox boundary | Dashed fence around the `container`; objects outside are visibly unreachable |
| `workflow` | A pre-written fixed flow | Chain of small labelled boxes in two snake rows with arrows between, plus a wrap arrow carrying row 1's end back to row 2's start; label "Workflow · 提前写死". Contrasts with `loop`: workflow decides up front, loop decides per step |
| `checklist` | An exam / quality acceptance (Eval) | Clipboard glyph (clipped rectangle + ruled lines) reached by a **dotted** flow from the system it tests; label "Eval · 给 AI 做考试". The system is the candidate, the clipboard is the test |
| `machine` | The thing that does one job at a time — a GPU, a server, a queue, a scheduler | Rounded card + its name on the top edge + ONE mono line stating its single-lane rule ("一次只能干一件事"). Its interior holds `chip`s, never free-floating labels | violet (the system itself) |
| `chip` | One resource inside a machine — compute, bandwidth, memory, a queue | A small labelled plate inside the machine, one per resource, never two of the same kind. Two lines of type: identity on line 1, its character ("计算密集 · 喂饱算力") on line 2 | the family's own colour, one per chip |
| `lane` | The passage of time through a machine | A horizontal ink rule with an arrowhead at the right end and a mono label at its left ("GPU 时间轴"). Blocks *ride* it — a block's height is the lane, not the machine | ink (structure) |
| `chunk` | A slice of one long input | A stack of equal plates, each labelled `C1..Cn`, with one mono line giving the size ("4096 token / 块"). On a `lane`, a chunk is a wide plate and the gaps between chunks are the other work | blue (knowledge) |
| `stream` | Data in motion between two places | A thick arrow whose thickness is the payload, with its label on the shaft | grey (annotation) → green when it carries output |
| `loop` | One thing that repeats until it is done | Boxes left→right + a **self-loop arrow** curving from the last box back under them to the first (never a closed ring — the ring reads as "this runs forever", the returning arrow reads "this runs again"). The one-shot boxes before the loop stay *outside* it | blue (knowledge); the step that emits output turns green |

## Zone discipline (added on the scheduling-series run)

A world with two *kinds* of thing in it — people on one side, machinery on the other —
needs layout rules the office-worker casts never had to state, because there was only ever
one kind of thing.

1. **Zones, and no migration.** Input (left) · the machine (centre) · output (right) · the
   time lane (a bottom band spanning input + machine). Every object belongs to exactly one
   zone and never moves out of it; growth adds *inside* the owning zone. A world that
   reflows on reveal has restarted, not grown.
2. **`connect` is dropped, not bent, when it would cross a foreign zone.** An arrow from the
   prompt to the users has to cross the machine; an arrow from the chunks to the machine has
   to cross the cache card that only appears later. Both read as false flows. Drop them, let
   the lane and the arrival order carry the flow, and **record each drop with its reason** —
   a dropped arrow is a decision, not an omission.
3. **A wall straddles the edge it blocks**, and a flip is not a recolour. The flip beat paints
   a second plate over the wall, then **re-draws the old label in red with a strike through
   it** and puts the verdict on a second line. A green plate whose own new text is struck
   reads as "the wall is still there and now broken" — the strike has to land on the text it
   cancels.
4. **Type is budgeted, not guessed.** In the toolchain below, a `size: s` label measures
   ≈18.5 px per CJK glyph and ≈10.8 px per ASCII character, and it wraps when its estimated
   width exceeds its declared width. Budget a card's label from those numbers; a card whose
   text wraps grows and stops reading as the object it was.

## Fixed diagram syntaxes

Recurring concept patterns with a canonical layout. Use these verbatim before composing freely.

### RAG (retrieval)

```text
question ──flow──▶ magnifier ──▶ [document stack: 知识库]
                                        │
                                        ▼
                                  top-k documents
                                        │
                                        ▼
                                      actor (LLM)
```

The teaching beat: documents *enter the desk*, they do not merge into the brain. Open-book exam, not training.

### Skill (SOP)

```text
            📕 Skill · SOP 手册
                   │
                   ▼  (laid on the desk)
   [Context desk: documents + the manual]
                   │
             actor (LLM)
```

The manual joins the documents on the desk — same open-book-exam rule as RAG: the actor *reads* it, it is not merged into the brain. Contrast with `memory`: Skill is a manual *given to* the actor (solid line, top); Memory is the actor's own notebook (dashed line, side).

### Workflow (pre-written flow)

```text
[读取发票] ─▶ [识别金额] ─▶ [校验日期]
                     │ (wrap, sweeps down-left)
                     ▼
[检查制度] ─▶ [输出结果]
```

Two snake rows of small labelled boxes; the wrap arrow carries the flow from row 1's end back to row 2's start. Every box is fixed — nothing here decides anything. When the narration contrasts it with an Agent, keep the `loop` ring on screen: workflow decides up front, loop decides per step.

### MCP / Connector

```text
              actor (Agent)
                   │
              🔌 MCP 接口
        ┌──────────┼──────────┐
        ▼          ▼          ▼
     system A   system B   system C
```

One standardized plug, many systems — the plug glyph is the whole point; drawing N bespoke connectors loses it.

### Agent loop

```text
        observe
       ↗       ↘
   check        think
       ↖       ↙
         act
```

Ring around the actor; highlight one stage per beat while the narration walks a real task through it.

### Multi-agent

```text
              lead actor
        ┌────────┼────────┐
        ▼        ▼        ▼
    actor    actor     actor
   research  analysis  review
```

Fan-out under a lead. Dashed return flow from the leaves back to the lead = the lead aggregates.

### Human-in-the-loop

```text
   actor ──flow──▶ [gate: 人确认] ──flow──▶ action
```

The gate sits *on* the flow, not beside it: the point is that execution pauses there.

## The diagram layer and the frame layer

Two palettes meet here, and the seam has to be declared or a reviewer reads the artwork as a
brand violation:

- The **frame** owns cream / ink / one coral, a display serif, and a type floor (≥1.4 cqw).
- The **diagram** owns the seven-family concept palette and is exempt from the frame's
  one-accent rule. Its labels are identity only.
- **Evidence numbers are not diagram labels.** A measured TTFT or tok/s is a `number-lockup`
  in the frame chrome, never a line inside a card. A card that counts stops naming, and a
  diagram that counts stops being a picture.
- **A world is authored at the film's canvas size.** A 1280×720 world placed on a 1920×1080
  frame lands at ~1.0× of its authored type size, so an 18 px diagram label sits *below* the
  frame's 27 px floor — legible on a desktop, unreadable on a phone. Either author the world
  at 1920×1080 (same beat count, same rules, 1.5× the coordinates) or give the art its own
  full-bleed band and keep the frame's chrome out of it. Measured on the scheduling series:
  1280×720 at scale 1.05 → 19 px labels, under the floor.
- **The art gets its own band.** Head band (rail + kicker + title) above, art below it,
  caption band below that. A full-width chrome row that crosses the art's box is a layout
  collision by construction — at scale 1.24 the world's top edge landed *inside* the head
  band and every evidence row sat on the diagram's own labels.

## Style rules for compositions

- Color encodes the **concept family**, fixed for the whole series (never re-colored per scene): blue = knowledge & context (desk, kb, RAG, docs) · green = hands & verification (tools, MCP, systems, computer use, eval, ✓) · orange = methods (skill, workflow) · violet = the agent itself (enclosure, loop, team, products) · yellow = human & memory (user, gate, notebook) · red = walls · grey = annotations · ink = structure. One family per object.
- Labels are identity only ("LLM", "RAG", "差旅制度") — the narration explains; the diagram names.
- Metaphors stay in the office-worker family (desk, notebook, toolbox, manual, gate) so primitives compose into one coherent world. Introducing a second metaphor family mid-video (space, machinery) breaks the world.
- Arrows may curve: `bend` is an absolute sagitta in px. An arrow riding a ring bows **outward** with the ring — never toward its centre (the bend sign flips with direction, so verify the rendered curve against the ring every time). Arrows crossing a scene bow gently (≤ 8 px) and end ~2 px short of the target's edge, which reads as contact. Never route a curve through a card or label — re-anchor the arrow or go around.
- Small labelled boxes: draw the box without an inline label and overlay fixed-width centred text. Inline geo labels impose a minimum height and grow the box — a wall card that grows reads as a different object.
- Every primitive must be stroke-able paths in the draw dash style with fills as separate elements, so the composition can draw it on (`data-beat` groups + stroke-dashoffset — timing contract in `SKILL.md`).
