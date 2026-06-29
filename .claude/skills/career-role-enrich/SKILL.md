---
name: career-role-enrich
description: Enrich a career-changelog role block and sync the matching resume.json work entry. Walks intake → audit → draft → review → apply for one role at a time.
argument-hint: <role-slug>
allowed-tools: Read, Edit, Write, Bash(grep *), Bash(git status), Bash(git branch --show-current), AskUserQuestion
---

# Career Role Enrich

Project-local skill for enriching one role at a time in `_includes/career/changelog.html` and the matching `resume.json` work entries. Captures the SSENSE-iteration workflow as a reusable process so future role rounds (Deliverr, Flexport, Octav, Shopify Logistics, Shopify) can ride the same rails without re-deriving conventions.

**Input:** $ARGUMENTS (a role slug like `deliverr`, `flexport`, `octav`, `shopify-logistics`, `shopify`)

## Step 0: Validate Input

If `$ARGUMENTS` is empty, STOP and ask the user for a role slug. Recommended slugs match the role's display name with lowercase + hyphenated transformation (e.g., `Shopify Logistics` → `shopify-logistics`).

The slug MUST match `^[a-z0-9-]+$`. If it contains anything else (spaces, slashes, shell metacharacters), STOP and ask for a clean slug.

## Step 1: Resolve Target

Use the slug to locate three things:

1. **Changelog block** in `_includes/career/changelog.html`. The block is the `<h2 id="changelog-<version>">` heading and everything until the next `<h2>` (or the closing `</div>`). To find it, grep for the role's display name (e.g., `Deliverr`) and walk up to the nearest `<h2>`.
2. **Resume entries** in `resume.json`. Grep for `"name": "<role-display>"`. There may be multiple entries per role (SSENSE has Tech Lead + Senior Developer; Vidéotron has two; AFS has two). All entries with the matching `name` are in scope.
3. **Published PDF**. The source of truth is `https://ouimet.info/charles/resume/Charles%20Ouimet%20-%20Principal%20Developer%20-%20Resume%202026-05.pdf`. Read it via the Read tool when needed for cross-referencing.

Record the changelog block's line range and the resume entries' line ranges for later steps.

## Step 2: Audit

Three-way compare: PDF role sub-section × changelog block × resume entries.

For each PDF bullet, classify as:

- **Already covered**: present in both changelog and resume in equivalent form.
- **Missing from changelog**: present in resume only.
- **Missing from resume**: present in changelog only.
- **Stale wording**: present but using outdated phrasing (e.g., `Use of more` instead of `Use of additional`, `Technical Architecture Group` instead of `Technology`).

Produce a `/note` describing the audit table. Use description `audit-<role-slug>`. The audit `/note` is the input to Step 3 intake decisions.

## Step 3: Intake

Use `/question` to gather context the audit can't infer from existing files. The question file uses description `intake-<role-slug>` and includes these reusable prompts as `Q001`-`Q005`:

1. **Headline projects or initiatives at this role.** For each: a one-line "what" and a one-line "what was hard about it."
2. **Scope and scale.** Team size, services owned, request volumes, deploy cadence, geographic scope, departments coordinated with.
3. **Shout-outs.** Collaborators, mentors, key allies. LinkedIn URLs help.
4. **Problems solved framed as outcomes, not tools.** Pick 2-4 problems where the outcome matters and the tool was the means.
5. **Anything missing from the PDF / changelog / resume.** Internal talks, mentorship, hiring contributions, incidents handled, etc.

Wait for the user to fill in answers before proceeding to Step 4.

## Step 4: Draft

Produce a plan `/note` (description `plan-<role-slug>`) with concrete proposals for:

1. **Changelog block HTML**: full proposed text for the role's `Added` block (and `Changed` / `Deprecated` if applicable). Apply `career-style` conventions throughout (see "Conventions consulted" below).
2. **Resume entries**: proposed `summary` text and `highlights[]` array for each `resume.json:work[]` entry under this role.
3. **Skills additions** (if any): tools introduced at this role that need to be added to `resume.json:skills`. Do NOT re-add tools already in `skills` from earlier roles.
4. **Decision points flagged** for Step 5 review: anything ambiguous goes into one or more `/question` files.

Consult `/prose-style` (hard-wrap, code refs, GitHub refs) and `/humanizer` (em-dash sweep, AI-vocabulary check) before writing the plan note.

## Step 5: Review Iteration

For each decision cluster, create a `/question` file (description `<cluster-name>-<role-slug>`). Common clusters from the SSENSE precedent:

- **Bullet structure**: nested `<ul>` vs flat; sub-bullet split points; lead-in content.
- **Tool fold-in**: fold standalone `Use of X` bullets into a project bullet (matches OMS's state machine / Step Functions / event storming fold-in pattern) vs keep standalone.
- **ID assignment**: which new project bullets get `changelog-<role>-added-<slug>` IDs.
- **Trim vs keep**: existing content that overlaps with new additions.
- **Summary scope** for `resume.json`: which summary fields get refreshed; what they say.

The user edits answers in the question files; the skill reads them back and iterates. Repeat until all decisions resolve.

## Step 6: Apply

Edit `_includes/career/changelog.html` and `resume.json` per the agreed plan.

After applying, run post-edit verification:

1. **JSON validity**: `python3 -c "import json; json.load(open('resume.json'))"`. Must succeed.
2. **Additive convention sweep**: `grep -n "Use of more" _includes/career/changelog.html`. Should return empty. Any match is a stale-wording bug; rename to `Use of additional`.
3. **Em-dash sweep within the role's block**: extract the block's line range from Step 1, then `sed -n "<start>,<end>p" _includes/career/changelog.html | grep -n "—"`. Should return empty.
4. **No `<strong>` micro-headings inside sub-bullets**: `grep -n "<li><strong>" _includes/career/changelog.html`. Should return empty.
5. **First-person verb sweep within the role's block** (excluding `Key relationships at <Role>:` sub-bullets, which are allowed first-person voice per `career-style` Rule 3 exception): `sed -n "<start>,<end>p" _includes/career/changelog.html | sed '/<li>Key relationships at .*:/,/<\/ul>/d' | grep -nE "\bI (built|led|created|maintained|developed|designed|implemented|authored|introduced|oversaw|delivered|shipped|wrote)\b"`. Should return empty. Matches indicate narrative voice that needs reshaping into noun-phrase form. The middle `sed` deletes the Key-relationships parent through its closing `</ul>` so the first-person exception scoped to those sub-bullets doesn't produce false positives.
6. **Vague-filler sweep within the role's block**: `sed -n "<start>,<end>p" _includes/career/changelog.html | grep -nE "(and more[.,]|\betc\.\s)"`. Investigate matches; `and more` is almost always cuttable; `etc.` outside parenthetical examples is usually filler.
7. **Rigorous K-a-C re-read (manual)**: re-read the edited block as a stranger encountering this changelog cold. For each `<li>`, ask: is this a fact, or is it narrative/editorial framing? Flag any sentence whose value is `context` or `justification` rather than `what was added/changed/done`. Iterate with the user if anything looks off.

## Step 7: Wrap Up

Print a status report:

```text
=== Role '<slug>' enrichment applied ===

Audit:        <path-to-audit-note>
Intake:       <path-to-intake-question-file>
Plan:         <path-to-plan-note>
Decisions:    <paths-to-decision-cluster-question-files>
Files edited: _includes/career/changelog.html, resume.json

Next: invoke /finish-issue when the branch is ready to ship.
```

The skill does NOT invoke `/finish-issue` automatically. The user runs it when ready.

## Conventions consulted

- `/prose-style` — hard-wrap rule, code reference syntax, GitHub reference syntax. Auto-consulted when writing any file content.
- `/humanizer` — em-dash overuse, AI vocabulary words, passive voice, filler phrases.
- `career-style` (project-local, non-invocable) — additive `Use of X` convention, role-scoped IDs, role-voice. Auto-consulted by this skill.
- `career-layering` (project-local, non-invocable) — three-layer information architecture (changelog → resume.json → docx/PDF), distillation rules, cross-file consistency. Auto-consulted by this skill.

## Quality Checklist

Before reporting Step 7:

- [ ] Resolved target (changelog block + resume entries + PDF reference)
- [ ] Audit `/note` produced
- [ ] Intake `/question` answered
- [ ] Plan `/note` produced and reviewed
- [ ] Decision-cluster `/question` files resolved
- [ ] Changelog edits applied; additive-convention sweep returns empty
- [ ] Resume edits applied; JSON validates
- [ ] Em-dash sweep within role block returns empty
- [ ] No `<strong>` micro-headings in sub-bullets
- [ ] First-person verb sweep returns empty (excluding `Key relationships at <Role>:` sub-bullets)
- [ ] Vague-filler sweep investigated (no remaining `and more` / loose `etc.`)
- [ ] Rigorous K-a-C re-read complete (no narrative/editorial sentences remaining)
- [ ] Skills additions reviewed (no duplicates from earlier roles)
