---
name: article-critique
description: Editor-in-chief review of a draft article. Runs /humanizer on the draft (editing in place), compares tone against your voice corpus (couimet.github.io, rangeLink, my-claude-skills), and writes a structured critique /note with structural + line-level findings.
argument-hint: <path-to-draft.md>
allowed-tools: Read, Edit, Write, Bash(git branch --show-current), Bash(date *), Bash(ls *), Bash(mkdir *), Bash(test *), AskUserQuestion, Skill
---

# Article Critique

Project-local skill that runs the editor-in-chief pass on a draft article. The same workflow you used on the correlation-id-vs-request-id draft: humanize the file in place, sample your voice corpus, write a structured critique note you can act on.

**Input:** `$ARGUMENTS` — path to the draft markdown file (relative to the repo root or absolute).

## Step 0: Validate Input

If `$ARGUMENTS` is empty, STOP and ask the user for the draft path.

If the path does not exist, STOP and report the missing file. Do not guess or search.

## Step 1: Confirm Scope

Use `AskUserQuestion` to confirm the four review knobs before doing any work. Defaults shown in brackets are the answers from the original run on the correlation-id draft.

1. **Humanizer scope.** Options: edit in place [default], analyze only, suggest edits in note.
2. **Critique depth.** Options: structural + tone only, line-by-line, both structured [default].
3. **Corpus weighting.** Options: all three folders equally [default], couimet.github.io canonical, most-recent wins.
4. **Anything specific to flag?** Free-form follow-up the user might add (e.g., "check the conclusion specifically", "I'm worried the analogy doesn't carry").

Only ask the questions whose default you have a reason to second-guess based on the draft. For a routine review, skip the prompt and use the defaults — record the assumption in the note.

## Step 2: Read the Draft

Read the file at `$ARGUMENTS` end-to-end. Do not skim. Note:

- Opener: does it set a concrete scene?
- Structural shape: where are the section breaks, where is the payoff, where is the conclusion?
- First-person presence: how many "I" sentences, where?
- Concrete numbers vs. generic placeholders.
- Analogies: introduced, sustained, paid off?

## Step 3: Sample the Voice Corpus

The three corpus folders:

- `/Users/couimet/geek/couimet.github.io/articles/_sources/` — published dev.to posts (DeepSeek pieces, etc.)
- `/Users/couimet/geek/rangeLink/media/` — RangeLink release posts
- `/Users/couimet/geek/my-claude-skills/media/` — Claude skills / workflow posts

For each folder, `ls` the contents and read at least one recent article. Goal: re-anchor on the writer's voice before judging the draft. If the user picked "most-recent wins" in Step 1, sort by filename date prefix and read the newest first.

Voice anchors to look for (from prior reviews):

- Heavy first-person, often in the opening paragraph.
- Concrete personal stakes (dollar amounts, hour counts, incident callbacks).
- Self-deprecating asides ("Classic Coyote", "Yeah, I'm looking at you, Joel").
- Short punchy paragraphs (1–2 sentences) mixed with longer ones.
- Always has a sign-off — sometimes italicized, sometimes a callback to the opener.
- Section headings in sentence case.
- Em-dashes used, but not on every line.

## Step 4: Apply /humanizer in Place

If Step 1 said "edit in place" (default), invoke the `humanizer` skill on the draft path:

```text
Skill: humanizer
args: <draft-path>
```

When the humanizer guide loads, do focused edits — not a full rewrite. The user's voice is already present in most drafts; the goal is to remove the AI tells without over-editing. Typical edits per draft: 3–8 small replacements.

Patterns to watch most carefully (these show up in nearly every draft):

- Signposting: "To make this concrete", "The principle:", "Let's dive in", "It is important to note", "At its core".
- Passive voice in technical sections ("prevents X from being passed", "is handled by").
- "This article assumes..." / "While specific details are limited" — textbook tics.
- "The difference between X and Y" framing.
- Rule-of-three constructions that aren't earned.
- Em-dash density above ~1 per paragraph for an extended stretch.
- **Self-referential closers**: "That's the difference the opener promised", "as we've seen", "to recap". Callbacks should land via echoed words or images, not by announcing themselves. If a sentence in a proposed closer references "the opener" or "the article" by name, delete it — the surrounding sentences are doing the work.
- **Walkthrough prose for an image you haven't read**: if the article includes an image (`![...]`) and you're proposing prose around it, read the source first (the .png, or better, the Mermaid/SVG source if it's in the repo). Describing a sequence diagram as a "table with columns" because you assumed the layout is exactly the kind of mistake that signals you didn't look. Search `articles/_sources/` for a sibling .md file with the same slug — diagram sources often live next to the article.
- **Meta paragraph placement**: a personal/meta beat (e.g. "I wrote this because…") should bridge BETWEEN sections, not detour OUT of a setup before the answer lands. If the prior paragraph sets an expectation ("two identifiers answer these questions"), let the answer land first, then place the meta beat as the transition into the next section. Wrong placement reads as a flow break; right placement reads as a graceful pivot.
- **Lead-in phrases that are doing a heading's job**: watch for sentences like "Until then, the approach stays small:" or "When you need more:" at the start of a paragraph. If a transitional clause is framing what the rest of the paragraph is about, it's a heading wearing a paragraph's clothes — promote it to a `##` (or pull the framing into the existing heading) and let the prose stand. Same pattern: "The takeaway:" at the start of a paragraph, "What I'd do differently:" inline, "The catch:" as a lead-in. All headings in disguise.
- **Reference-section labels must be literally true**: a heading like "### Cited in this article" implies the listed works are referenced inline. Verify by grepping the body for each URL — if 5 of 6 references don't appear in the prose, the heading is dishonest. Prefer narrative labels that name the writer's actual relationship to the references: "What I read getting here" (articles found in research), "What I keep bookmarked" (docs referenced while shipping), "Prior art" (academic flavor), etc. Also: separate articles from technical docs — they serve different reader purposes (one to learn, the other to consult while implementing) and one-line intros under each heading help frame the contents.
- **Per-bullet descriptions in reference lists are usually AI noise**: if a section already has a heading + intro line doing the framing job, adding `- [Title](url) — one-line description of what the reader will get` on every bullet is redundant. The description repeats what the intro already said, just per-item. Strip them; keep the bullets as `- [Title](url)` (plus `([archive](...))` where applicable). Exception: a single bullet that needs disambiguation in a mixed list (e.g. "this one is the only video, the rest are articles") can carry a short note.
- **Industry-coded padding phrases**: "before the bug ships", "in production", "at scale", "moving forward", "going forward", "out of the box". These pad a sentence with industry-flavored vagueness without adding meaning. If "and the compiler stops you before the bug ships" reads the same as "and the compiler stops you," drop the suffix. Test: read the sentence aloud with and without the phrase — if the meaning is identical, the phrase was decoration.
- **Forward references to concepts not yet introduced**: parenthetical examples like "any code downstream — including the outbound interceptor — reads from it" assume the reader already knows what an "outbound interceptor" is when the section introducing it is 60+ lines away. The reader can't verify the example, so it adds noise instead of concreteness. Two fixes: (a) drop the example entirely, the surrounding sentence usually stands on its own; (b) swap for a concept the reader already has ("like HTTP calls to other services"). Avoid signposting ("the X you'll see later") — that's its own AI tic.
- **Prose mechanism descriptions must match the actual code**: when prose describes *how* a system works (e.g. "X registers with Y", "Y subscribes to X", "the middleware pushes into the logger"), verify the real implementation actually uses that mechanism. If the code does something different (e.g. the logger *pulls* from context on every call rather than receiving a push at registration), the prose is technically wrong even if the outcome described is right. Two fixes: (a) correct the prose to match the real mechanism, (b) abstract away the mechanism and just name the property ("the logger is X-aware"). Option (b) is usually cleaner — it lets the reader infer "however it works, here's the outcome" without committing to one implementation choice.
- **Local-variable-shadows-auto-injection bug**: when prose claims a logger or framework auto-injects field X, and the code sample also creates a *local* value named X with a different meaning (e.g. an "auto-injected `requestId` from ExecutionContext" vs a "local `requestId` for an outbound call"), trace through the auto-injection's override order. If the auto-injection runs last (a common defensive pattern), the local value gets silently clobbered in the log output, and the code sample is subtly wrong. Two fixes: (a) rename the local variable to a non-colliding name (e.g. `outboundRequestId`), (b) add prose that explicitly calls out the collision and shows the workaround. Both is best — the rename makes the code correct, the prose protects future readers from re-introducing the same pattern.
- **Audit summary lists after mid-article edits**: closers often contain a "here's the whole kit" list ("Two value objects, one async-local context, a couple of middlewares, one interceptor"). When a mid-article edit introduces a new concept or component (e.g. an `ExecutionContext`-aware logger), the summary list goes stale silently — the reader hits a count mismatch between the body and the closer. After any structural body edit, grep the closer for component lists and verify completeness. Same applies to abstracted phrases that used to anchor to specifics: when "two more legs" becomes "in complexity", check whether the two orphaned examples still earn their keep or have been silently downgraded to leftovers.

Record every edit applied. They go in the final section of the critique note.

## Step 5: Write the Critique Note

Invoke the `note` skill with description `editor-critique-<draft-slug>`. Structure the note this way (this is what worked on the first run):

1. **TL;DR** — 3–5 sentences. The honest top-line read. Lead with the biggest structural problem, then the biggest voice problem.
2. **Structural critique** — numbered findings. For each: state the problem, contrast against a corpus article that does it better (cite the corpus filename and the specific move), suggest a fix.
3. **Tone-vs-corpus deltas** — a small markdown table with columns "Dimension | Your corpus | This draft". Rows: first-person voice, concrete stakes, self-deprecating asides, specific numbers, paragraph cadence, sign-off.
4. **Line-level notes** — keyed by line number. Mix of "keep this, it's the benchmark" callouts and specific suggested rewrites. Don't be afraid to call good prose good; the writer needs to know what to keep.
5. **Concrete suggestions for [whichever section is weakest]** — usually the conclusion. Offer 2–3 distinct angles (callback closer, opinion closer, personal closer) the writer can pick from.
6. **What the humanizer pass already changed** — a short numbered list of the edits applied in Step 4, with before/after for each.

## Step 6: Report

Print only:

1. The path to the critique note (from the `note` skill output).
2. A one-sentence summary of the biggest finding (so the user knows whether to open the note now or later).

Do not paste the note contents into the chat.

## Notes for Future Runs

- Skip Step 3 (corpus sampling) only if the same skill ran in the same session and the corpus is already in context. Cold-start runs must re-sample — voice drifts and your taste evolves.
- If the draft is not yet in `articles/_sources/`, that is fine. The skill operates on any markdown path. CLAUDE.md's "in-repo drafts only" rule applies to *publishing*, not to *drafting*.
- If the user pushes back on a finding ("no, that's intentional"), record the disagreement in a short follow-up note rather than re-editing the critique. The original critique is a snapshot of the editor read; the follow-up is the conversation.
