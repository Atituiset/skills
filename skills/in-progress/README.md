# in-progress

Skills being incubated. They are installable and runnable, but they have not yet been exercised on a real production task — treat every rule inside as a hypothesis, not a lesson.

Boundary rules (from [ADR-0001](../../.agents/adr/0001-skill-directory-layout.md)):

- A skill lands here when it is drafted from design discussion or a single worked example, **before** it has shipped a real artifact.
- It graduates to a real category once it has been exercised end-to-end on a real task and revised from what that run taught. Graduation = move the directory, add it to the root README reference table and `.claude-plugin/plugin.json`.
- Skills here stay out of the root README reference table and out of `plugin.json` — they are not published through the plugin marketplace while incubating.

## Currently incubating

| Skill | Hypothesis being tested | Graduation test |
|---|---|---|
| [visual-storytelling](visual-storytelling/) | Abstract concepts teach better as one hand-drawn diagram world that grows beat by beat (progressive visual disclosure) than as per-scene slides; a fixed visual grammar keeps agent-drawn diagrams consistent. | Produce one real explainer video whose diagrams are built with this skill's beat sheet + grammar, then revise the skill from what broke. |
