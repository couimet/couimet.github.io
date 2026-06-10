---
name: article-critique
description: Editor-in-chief review of a draft article. Runs /humanizer on the draft, compares tone against your voice corpus, and writes a structured critique /note with all findings.
argument-hint: <path-to-draft.md>
allowed-tools: Read, Edit, Write, Bash(git branch --show-current), Bash(date *), Bash(ls *), Bash(mkdir *), Bash(test *), AskUserQuestion, Skill
---

# Article Critique

Project-local skill that runs the editor-in-chief pass on a draft article: run /humanizer on the draft, sample your voice corpus, write a structured critique note you can act on. The humanizer findings go into the note — this skill does not edit the draft.

**Input:** `$ARGUMENTS` — path to the draft markdown file (relative to the repo root or absolute).

## Step 0: Validate Input

If `$ARGUMENTS` is empty, STOP and ask the user for the draft path.

If the path does not exist, STOP and report the missing file. Do not guess or search.

## Step 1: Confirm Scope

Use `AskUserQuestion` to confirm the three review knobs before doing any work. Defaults shown in brackets.

1. **Critique depth.** Options: structural + tone only, line-by-line, both structured [default].
2. **Corpus weighting.** Options: all three folders equally [default], couimet.github.io canonical, most-recent wins.
3. **Anything specific to flag?** Free-form follow-up the user might add (e.g., "check the conclusion specifically", "I'm worried the analogy doesn't carry").

Only ask the questions whose default you have a reason to second-guess based on the draft. If the draft is under 200 lines AND the user passed no custom flags or concerns AND the draft has no prior edits from this run, skip AskUserQuestion and use defaults. Otherwise ask. Record which defaults were used and why in the critique note when the prompt is skipped.

## Step 2: Read the Draft

Read the file at `$ARGUMENTS` end-to-end. Do not skim. Note:

- Opener: does it set a concrete scene?
- Structural shape: where are the section breaks, where is the payoff, where is the conclusion?
- First-person presence: how many "I" sentences, where?
- Concrete numbers vs. generic placeholders.
- Analogies: introduced, sustained, paid off?

## Step 3: Sample the Voice Corpus

The three corpus locations (relative to this repo's root):

- `articles/_sources/` — published dev.to posts from this repo (DeepSeek pieces, etc.)
- `../rangeLink/media/` — RangeLink release posts
- `../my-claude-skills/media/` — Claude skills / workflow posts

For each folder, `ls` the contents and read at least one recent article. Goal: re-anchor on the writer's voice before judging the draft. If the user picked "most-recent wins" in Step 1, sort by filename date prefix and read the newest first.

Voice anchors to look for (from prior reviews):

- Heavy first-person, often in the opening paragraph.
- Concrete personal stakes (dollar amounts, hour counts, incident callbacks).
- Self-deprecating asides ("Classic Coyote", "Yeah, I'm looking at you, Joel").
- Short punchy paragraphs (1–2 sentences) mixed with longer ones.
- Always has a sign-off — sometimes italicized, sometimes a callback to the opener.
- Section headings in sentence case.
- Em-dashes used, but not on every line.

## Step 4: Run /humanizer

Always invoke the `humanizer` skill on the draft. It detects AI writing patterns the reader will feel even if they can't name them.

```text
Skill: humanizer
args: <draft-path>
```

Do not edit the draft. Collect the humanizer findings — they go in the critique note under "What the humanizer pass found."

## Step 5: Write the Critique Note

Invoke the `note` skill with description `editor-critique-<draft-slug>`. Structure the note this way (this is what worked on the first run):

1. **TL;DR** — 3–5 sentences. The honest top-line read. Lead with the biggest structural problem, then the biggest voice problem.
2. **Structural critique** — numbered findings. For each: state the problem, contrast against a corpus article that does it better (cite the corpus filename and the specific move), suggest a fix.
3. **Tone-vs-corpus deltas** — a small markdown table with columns "Dimension | Your corpus | This draft". Rows: first-person voice, concrete stakes, self-deprecating asides, specific numbers, paragraph cadence, sign-off.
4. **Line-level notes** — keyed by line number. Mix of "keep this, it's the benchmark" callouts and specific suggested rewrites. Don't be afraid to call good prose good; the writer needs to know what to keep.
5. **Concrete suggestions for [whichever section is weakest]** — usually the conclusion. Offer 2–3 distinct angles (callback closer, opinion closer, personal closer) the writer can pick from.
6. **What the humanizer pass found** — a short numbered list of findings from Step 4.

## Step 6: Report

Print only:

1. The path to the critique note (from the `note` skill output).
2. A one-sentence summary of the biggest finding (so the user knows whether to open the note now or later).

Do not paste the note contents into the chat.

## Notes for Future Runs

- Skip Step 3 (corpus sampling) only if the same skill ran in the same session and the corpus is already in context. Cold-start runs must re-sample — voice drifts and your taste evolves.
- If the draft is not yet in `articles/_sources/`, that is fine. The skill operates on any markdown path. CLAUDE.md's "in-repo drafts only" rule applies to *publishing*, not to *drafting*.
- If the user pushes back on a finding ("no, that's intentional"), record the disagreement in a short follow-up note rather than re-editing the critique. The original critique is a snapshot of the editor read; the follow-up is the conversation.
