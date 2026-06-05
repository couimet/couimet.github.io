---
name: career-style
user-invocable: false
description: Canonical style rules for the career changelog (_includes/career/changelog.html) and resume.json. Three rule sets bundled in one helper: additive Use-of convention, role-scoped IDs, role-voice. Auto-consulted by career-role-enrich.
allowed-tools: Read
---

# Career Style

Single source of truth for the SSENSE-derived conventions that govern `_includes/career/changelog.html` and `resume.json` for this repo. Auto-consulted by `career-role-enrich`. Not user-invocable directly; reference these rules from any skill or task that writes to the career changelog or the resume.

Three rule sets follow. Each is a section.

## Rule 1: Additive `Use of X` convention

The changelog organizes tools and practices additively across roles. Each `Use of X` bullet captures something that first appeared at that role. Tools and practices already mentioned at earlier roles are NOT repeated at later roles, even when they carried forward.

### Mechanics

- **First appearance**: `Use of <a href="...">X</a>.` — short standalone bullet at the role where X was first encountered.
- **Sibling-component bullets** (e.g., AWS components introduced incrementally): use `Use of additional X components: <list>.` The word `additional` signals "additional vs. what was already mentioned at earlier roles." Do NOT use `Use of more X components` (legacy wording; rename any occurrence to `Use of additional`).
- **Contextual mention** of a tool already introduced at an earlier role: fold into a project bullet (e.g., `Used X for ... in Y's trunk-based workflow`), not a fresh `Use of X` standalone.

### When applying to a role's draft

- For each candidate `Use of X` bullet: search prior roles' blocks (`<h2 id="changelog-<earlier-version>">` blocks) for any existing mention of X. If X is already there, do NOT re-add at this role.
- For component-list bullets (`Use of additional ...`): list only components NEW at this role. Components carried from earlier roles stay implicit.

## Rule 2: Role-scoped IDs

HTML `id` attributes on project bullets follow the pattern `changelog-<role>-added-<slug>`.

### When to assign an ID

- **Yes**: distinct multi-faceted projects. Examples: `changelog-ssense-added-distributed-oms`, `changelog-ssense-added-cbsa-b13`, `changelog-ssense-added-po-platform`.
- **No**: single-sentence tool / practice bullets (`Use of CQRS`, `Use of GitHub Copilot`).
- **No**: knowledge / context bullets (`Knowledge in the luxury e-commerce industry`).

### Slug shape

- Lowercase, hyphenated.
- Captures the project's essence in 1-3 words.
- Examples: `distributed-oms`, `cbsa-b13`, `dev-onboarding`, `po-platform`.

### Legacy exception

The bullets at `_includes/career/changelog.html` with IDs `changelog-added-ruby` and `changelog-added-ruby-on-rails` are unscoped (no `<role>` segment) and stay that way. They describe one-time "first encounter with a tool" events that can never repeat. Do NOT rename them. Future "first encounter" bullets MAY use the unscoped pattern only when the encounter is genuinely irreproducible (rare).

## Rule 3: Role-voice

Factual, not summary.

### Mechanics

- State facts. Let the reader infer significance. Avoid editorial framing ("This was a massive undertaking", "I led the team to success").
- **No `<strong>` micro-headings inside sub-bullets**. They read as AI-generated topic-sentence framing.
- **No em-dashes (`—`)**. Use commas, semicolons, parentheses, or sentence breaks instead. Cross-reference `/humanizer`.
- **Link on first mention** within a bullet only. Subsequent mentions of the same term in the same bullet stay plain text. Across sibling bullets in the same role block, re-link sparingly when the link genuinely helps navigation (e.g., when a sub-bullet references a tool the lead-in didn't link).
- **No first-person self-evaluation** ("I was the de facto expert", "I was uniquely qualified"). State what happened and let observers carry the implicit signal (e.g., "TAG members routed teams to me for serverless reviews" lets the reader infer expertise without claiming it).

### Strict Keep-a-Changelog noun-phrase form

Every entry under `Added` / `Changed` / `Deprecated` should read as a noun phrase describing what shipped, not as narrative or commentary.

- **No first-person action verbs** in the bullet body: `I built`, `I led`, `I created`, `I maintained`, `I developed`, `I designed`, `I implemented`, `I authored`, `I introduced`, `I oversaw`, `I delivered`, `I shipped`, `I wrote`. Use noun-phrase form: `Presentations and video capsules on X` not `Presentations and video capsules I built on X`.
- **No editorial flourishes**: `ramping observability up to the highest bar`, `world-class`, `best-in-class`, `highest-impact`, etc. State the fact; let the reader infer significance.
- **No vague filler**: `and more`, `and beyond`, loose `etc.` outside parenthetical examples.
- **No contrast clauses for framing**: drop `rather than X` / `instead of Y` unless the contrast carries a load-bearing fact rather than just orienting the reader.
- **Two-sentence bullets must add facts in the second sentence**, not justify or re-explain the first. If sentence 2 reads as defense or context-setting for sentence 1, fold or cut.

#### Exception: Key-relationships sub-bullets

Sub-bullets inside a `Key relationships at <Role>:` parent ARE allowed first-person voice (`his mentorship was often framed around...`, `sponsored my level-up to...`). The entry IS the relationship; the personal lens is the point. Exception scoped to bullets inside `Key relationships at <Role>:` parents only.

### Summary-as-distillation

In `resume.json:work[].summary`: every claim must be backed by a bullet in the same entry's `highlights[]`. The `highlights[]` array must read coherently if `summary` were stripped.

Two reasons:

- Resume consumers may render highlights but not summary (yamlresume's `json2yamlresume` did this until upstream issue #225 — the bug persists in older versions).
- Recruiters often skim highlights first.

### Self-check before finalizing a role draft

- For each summary claim, identify the backing highlight. If a claim has no backing highlight, either add a highlight or cut the claim from the summary.
- For each `<li>` you wrote, verify it's a fact, not a summary or evaluation.
- For each tool mention, verify it's the first mention in the role block. If not, drop the link; keep plain text.
- For each `<li>` you wrote (outside `Key relationships at <Role>:` sub-bullets), verify it carries no first-person action verbs, no editorial flourishes, no vague filler (`and more` / loose `etc.`), and no framing-only contrast clauses. Two-sentence bullets must add a fact in sentence 2.
