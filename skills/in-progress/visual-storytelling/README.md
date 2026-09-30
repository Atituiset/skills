# visual-storytelling

**Incubating** — see [skills/in-progress/](../README.md) for what that means.

Turns an article or topic into a growing hand-drawn cartoon diagram world: one world that builds up beat by beat (progressive visual disclosure), drawn from a fixed visual grammar, exported as static SVG scene assets. Timing is never baked into assets — HyperFrames owns the timeline, which keeps bilingual (zh+en) re-timing independent.

Pairs with [bilingual-video](../../video/bilingual-video/) and [bilingual-tech-explainer](../../video/bilingual-tech-explainer/): those skills own the film; this one owns the diagrams inside it.

## Layout

- `SKILL.md` — the agent-facing workflow (spine → cast → beat sheet → render → hand off)
- `references/visual-grammar.md` — the primitive catalog and fixed diagram syntaxes (RAG, Skill, Workflow, MCP, agent loop, multi-agent, human-in-the-loop, eval)
- `examples/agent-article-beats.md` — a complete beat sheet for a real article, the format to copy
- `examples/agent-article-beats/` — that sheet rendered: 18 delta SVGs, `final-frame.svg`, shared `fonts.css`

## Status

Drafted from design discussion plus one worked example; that example has since been rendered end-to-end (deltas stacked and pixel-verified, rules revised from the run), but not yet validated by a shipped video. The graduation test is one real explainer whose diagrams were built with this skill, after which the rules get revised from what broke.
