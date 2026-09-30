# Worked example: 《一文讲通 LLM、RAG、Agent、Skill、Claude Code、Codex 和 WorkBuddy》

The complete 18-beat sheet for the source article — rendered, stacked, and pixel-verified — and the reference for beat-sheet format and granularity. The teaching spine: a chatbot that only answers → hits wall after wall (doesn't know your data, forgets you, has no hands, no method, no system access, no fixed flow) → each fix adds one object to the same world → the grown world is enclosed as an Agent → the agent gets a loop, a workflow, a team, a screen, a permission fence, an exam → the real products land on top.

Note how the final beat equals the article's own §25 summary diagram — `final-frame.svg` is that diagram, assembled only at the end, never shown before. Beats cover the article through §25; §26–§30 and 结语 add no new art: §26 (a real task walkthrough) narrates over the assembled world — the composition may pulse or re-highlight existing `data-beat` groups — and §30 + 结语 hold `final-frame.svg`.

```yaml
scene: llm-becomes-agent
objects:
  - id: user
    primitive: actor
    label: 用户
    position: left
  - id: llm
    primitive: actor
    label: LLM
    metaphor: brain
    position: center, on the desk
  - id: barrier_answer
    primitive: barrier
    label: "✗ 只答不做"
    position: on llm
  - id: barrier_data
    primitive: barrier
    label: "✗ 桌上没有这份文件"
    position: on desk
  - id: desk
    primitive: container
    label: Context · 办公桌
    position: around llm
  - id: kb
    primitive: document
    label: 公司知识库
    position: top-left, outside every container
  - id: rag
    primitive: magnifier
    label: RAG
    position: below kb, outside every container
  - id: docs
    primitive: document
    label: (no label — they are the documents)
    position: on desk
  - id: memory
    primitive: memory
    label: Memory · 笔记本
    position: llm side
  - id: tools
    primitive: tool
    label: Tools · 手
    position: llm side
  - id: mcp
    primitive: tool
    label: MCP
    position: below tools
  - id: systems
    primitive: tool
    label: 邮件 / CRM / 数据库
    position: right of mcp
  - id: skill
    primitive: document
    label: Skill · SOP 手册
    position: above the desk
  - id: agent
    primitive: container
    label: Agent · 数字员工
    position: encloses [llm, desk, docs, memory, tools, mcp, skill]
  - id: loop
    primitive: loop
    label: 观察 → 思考 → 行动 → 检查
    position: inside agent
  - id: workflow
    primitive: workflow
    label: Workflow · 提前写死
    position: inside agent, top-right
  - id: team
    primitive: team
    label: Multi-Agent · AI 团队
    position: right of agent
  - id: computer-use
    primitive: tool
    label: Computer Use
    position: right of tools (screen variant)
  - id: gate
    primitive: gate
    label: Human-in-the-loop
    position: on the agent's wall, flowing out to user
  - id: fence
    primitive: fence
    label: Permission · Sandbox
    position: around agent
  - id: eval
    primitive: checklist
    label: Eval · 给 AI 做考试
    position: outside the fence, bottom-right
  - id: products
    primitive: container
    label: Claude Code · Codex · WorkBuddy
    position: top, above the fence

beats:
  # Act 1 — the chatbot and its first walls (article §1–§6)
  - at: "最早我们用 AI，就是你问一句、它答一句"
    reveal: [user, llm]
    connect: user -> llm
  - at: "它很聪明，但它只回答，不干活——知道怎么做和真的做完是两回事"
    reveal: barrier_answer
  - at: "而且它也不是什么都知道，它只能看到桌上摊着的材料"
    reveal: desk
  - at: "你问它公司出差能不能报销商务舱，它不可能天然知道"
    reveal: barrier_data
  - at: "于是回答问题之前，先让它去资料库查一查——不是按关键词，是按意思"
    reveal: [kb, rag, docs]
    connect: kb -> rag -> llm
    actions:
      - { type: annotate, target: rag, label: "按意思搜索" }
      - { type: mutate, target: barrier_data, to: "✓ + strikethrough" }

  # Act 2 — growing the employee (article §7–§14)
  - at: "它还会忘记你上次说过的话，所以给它一个笔记本"
    reveal: memory
    connect: llm -.-> memory
  - at: "光会回答还不够，真正干活需要手——打开 Excel、运行程序、操作浏览器"
    reveal: tools
    connect: llm -> tools
  - at: "但公司真正重要的数据在邮件、CRM、数据库里，需要一个标准插头"
    reveal: [mcp, systems]
    connect: tools -> mcp -> systems
  - at: "再给它一本 SOP：周报怎么做、合同怎么审，写成可复用的工作方法"
    reveal: skill
    connect: skill -> desk

  # Act 3 — the agent appears (article §15–§21)
  - at: "把这些装进一个身体，它就不再是顾问，而是数字员工"
    actions:
      - { type: enclose, targets: [llm, desk, docs, memory, tools, mcp, skill], label: "Agent · 数字员工" }
      - { type: mutate, target: barrier_answer, to: "✓ + strikethrough" }
  - at: "它干活的方式是一个循环：观察、思考、行动、检查"
    reveal: loop
  - at: "固定流程交给 Workflow，复杂判断交给 Agent"
    reveal: workflow
  - at: "一个员工还能变成一个团队"
    reveal: team
    connect: agent -> team
  - at: "现实里大量系统没有接口——让 AI 像人一样看屏幕、点鼠标、输入文字"
    reveal: computer-use
    connect: tools -> computer-use
  - at: "但关键环节必须让人确认——真正发送之前，人点头"
    reveal: gate
    connect: agent -> gate -> user
  - at: "还要有权限边界：能做什么、不能做什么、到哪步必须停下来"
    reveal: fence
  - at: "怎么知道一个 Agent 到底靠不靠谱？给 AI 做考试和质量验收"
    reveal: eval
    connect: agent -.-> eval

  # Act 4 — products land on the grown world (article §22–§25)
  - at: "Claude Code、Codex、WorkBuddy，就是把这些能力组合起来的 Agent 工作平台"
    reveal: products
    connect: products -> agent
```

## Assets

`agent-article-beats/` holds the rendered output of this sheet:

- `beat-01.svg` … `beat-18.svg` — **delta** assets: each contains only the shapes that beat adds. Every root `<g>` carries `data-beat="<n>"`, and all files share one pinned 1280×720 world coordinate system — stack them in beat order on a single canvas to build the world (stacking beats 1..N was verified pixel-identical to exporting the cumulative world at beat N).
- `final-frame.svg` — the whole world in beat-18 state: the §25 summary diagram, the hold frame for §26–§30 and 结语.
- `fonts.css` — the single base64 `@font-face` every SVG imports via `@import url("fonts.css")`. Keep it beside the SVGs. When inlining SVGs into a composition, the `@import` resolves against the *document*, so copy `fonts.css` next to `index.html` or paste its contents into the composition's `<style>`.

All assets pass the timing contract: no `<script>`, no SMIL, no animation elements anywhere; text is `<foreignObject>` (so the composition must **inline** the SVG — an `<img>` reference drops all text).

## Rendering notes (tldraw SDK path)

- Rendered with the tldraw SDK in a headless Chromium page (its SVG export needs DOM measurement): shapes are created beat by beat, then `editor.getSvgString(ids, { bounds: new Box(0, 0, 1280, 720), background: false, padding: 0 })` is called per beat with that beat's ids; a post-pass verifies export order == creation order and stamps `data-beat`.
- Exports deltas for beats 1–18, then one final export with all ids → `final-frame.svg`.
- tldraw embeds ~200 KB of font `@font-face` per export — extracted once to `fonts.css` (assets shrank ~70%).
- Geometry lessons encoded in `references/visual-grammar.md`: inline geo labels impose a minimum height (small boxes use overlay text); arrow `bend` is an absolute sagitta in px and ring arrows must bow outward (the worked example's loop arrows originally bowed inward and were flipped).
- Default reveal handed downstream: per `data-beat` group, stroke draw-on (dashoffset) for paths/arrows/rules, fill + label fade for solids and text — re-timed to each language's TTS word boundaries.

## What this example demonstrates

- **Progressive visual disclosure**: the `agent` enclosure in beat 10 wraps objects the viewer has watched appear one by one — it lands as a payoff, not as a diagram to be walked through.
- **Barrier → bridge rhythm with one event per beat**: each wall (`barrier_data` beat 4, `barrier_answer` beat 2) flips ✓ in the *same* beat as the bridge that crosses it (RAG + docs in beat 5; the enclosure itself in beat 10) — a narrative event, not two beats.
- **One world, one palette**: color follows the concept families (blue knowledge, green tools, orange methods, violet agent, yellow human/memory, red walls) across all 18 beats — nothing is re-colored per scene.
- **Beats anchor to narration lines, never timestamps** — the zh and en cuts re-time every reveal independently downstream.
- **Primitives reused, not reinvented**: RAG, Skill, MCP, loop, workflow, team, gate, fence, computer-use (tool screen variant), and eval (checklist) all use the fixed syntaxes from `references/visual-grammar.md`.
