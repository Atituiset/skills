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

## Style rules for compositions

- Color encodes the **concept family**, fixed for the whole series (never re-colored per scene): blue = knowledge & context (desk, kb, RAG, docs) · green = hands & verification (tools, MCP, systems, computer use, eval, ✓) · orange = methods (skill, workflow) · violet = the agent itself (enclosure, loop, team, products) · yellow = human & memory (user, gate, notebook) · red = walls · grey = annotations · ink = structure. One family per object.
- Labels are identity only ("LLM", "RAG", "差旅制度") — the narration explains; the diagram names.
- Metaphors stay in the office-worker family (desk, notebook, toolbox, manual, gate) so primitives compose into one coherent world. Introducing a second metaphor family mid-video (space, machinery) breaks the world.
- Arrows may curve: `bend` is an absolute sagitta in px. An arrow riding a ring bows **outward** with the ring — never toward its centre (the bend sign flips with direction, so verify the rendered curve against the ring every time). Arrows crossing a scene bow gently (≤ 8 px) and end ~2 px short of the target's edge, which reads as contact. Never route a curve through a card or label — re-anchor the arrow or go around.
- Small labelled boxes: draw the box without an inline label and overlay fixed-width centred text. Inline geo labels impose a minimum height and grow the box — a wall card that grows reads as a different object.
- Every primitive must be stroke-able paths in the draw dash style with fills as separate elements, so the composition can draw it on (`data-beat` groups + stroke-dashoffset — timing contract in `SKILL.md`).
