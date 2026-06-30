---
name: career-layering
user-invocable: false
description: Canonical information-layering architecture for career content. Documents the three-layer flow — changelog.html (gold mine) → resume.json (source of truth) → docx/PDF (ATS-ready) — and the distillation rules for each layer. Auto-consulted by career-role-enrich.
allowed-tools: Read
---

# Career information layering

Career content lives in three layers, each with a distinct audience and level of detail. Information originates in the richest layer and distills down to the most concise.

## The three layers

### Layer 1: `_includes/career/changelog.html` — the gold mine

Audience: the curious reader, the thorough interviewer, yourself.

This is where all detail lives. Every technology, pattern, project, relationship, and "Use of" item belongs here. Nothing is too granular. Links to external resources (articles, docs, LinkedIn profiles) are encouraged. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with Semantic Versioning.

**Write here first.** When adding new career content, start in the changelog. Get the full story down with all the nuance. Then distill into the layers below.

### Layer 2: `resume.json` — the source of truth

Audience: the ATS, the recruiter, the hiring manager scanning quickly.

Structured as [JSON Resume](https://jsonresume.org/schema/). Each role gets:
- A **summary** (1-3 sentences framing the role — what you did, why it mattered)
- **Highlights** (5-7 bullets per recent role, 0 for roles older than ~5 years)

Bullets use action-approach-impact style with concrete numbers where available. The tone is professional and third-person. Earlier roles (pre-2020) are condensed to summary-only with merged company tenures. Each summary captures the role's essence; highlights carry the evidence.

The CI pipeline (`scripts/sync-resume.sh`) auto-generates `resume.yml` and `resume-full.html` from this file on push to main. Never edit those generated files directly.

**Distill here second.** From the changelog, extract the most impactful contributions. Drop "Use of" items (they stay in skills). Drop relationships and internal process details. Keep the patterns, the scale, and the outcomes.

### Layer 3: `.docx` → PDF — the ATS-ready resume

Audience: applicant tracking systems, the 30-second scan.

The most condensed layer. Must fit 2 pages. No separate "summary" field per role — the role summary becomes the first bullet or is woven into the professional summary at the top. Bullets are the same as resume.json highlights but may be slightly trimmed for space. The professional summary paragraph at the top is the single most important piece of text: it must name the industries, the specializations, and the scale.

**Distill here last.** From resume.json, take the highlights verbatim or lightly trim. The professional summary is hand-crafted, not auto-generated.

## Distillation rules

Rules use the `CL-` prefix for stable cross-referencing. The number is fixed; the title may evolve.

When moving content from layer N to layer N+1:

**CL-01 — Drop links.** Changelog has them, resume.json and docx don't.

**CL-02 — Drop "Use of" items.** They live in skills sections, not work entries.

**CL-03 — Drop relationships.** "Shout-out to X" and "key relationships" stay in the changelog.

**CL-04 — Merge same-company tenures.** One entry per company with the latest title and a "Hired as X; promoted to Y" note.

**CL-05 — Collapse older roles.** Roles older than ~5 years get summary-only, no highlights.

**CL-06 — Keep the patterns, not the process.** "Used EventStorming and BPMN to map workflows" stays; "met weekly for 3-4 weeks of part-time iterative work" doesn't.

**CL-07 — Numbers survive all layers.** Team sizes, service counts, adoption metrics travel from changelog through to PDF.

**CL-08 — "Incubated" is the user's term.** It describes the pattern of building locally with long-term ecosystem adoption in mind. Not AI puffery. Keep it.

**CL-09 — Staff+ summaries focus on domains and business impact, not technologies learned.** At 25+ years of experience, learning a new language or framework is table stakes. The summary should name industries, patterns, and outcomes. Technology detail belongs in highlights and skills.

**CL-10 — Scope claims must survive distillation accurately.** "Owned the migration" means the whole thing; "owned the migration of one table" means what it says. "Designed and implemented" means both were done; "designed... and implemented the foundational pieces" means implementation was partial. The changelog has the nuance; preserve it.

**CL-11 — Adoption claims need humility.** "Adopted across the 60+ service ecosystem" implies broad uptake; "a handful of services progressively adopted" is honest. If patterns became defaults for new services (via a template repo), say so. If they only influenced a few existing services, say that instead.

**CL-12 — Pure-context bullets have no place in the docx.** A bullet that only says "Dove into the crypto space" or "Learned Ruby on Rails" with no engineering action should be merged into an adjacent engineering bullet or dropped. Three valid docx first-bullet patterns exist: context-only (acceptable when the company name carries strong signal, e.g., Shopify), merged context+engineering (standard, e.g., Octav), and no lead-in bullet at all (Deliverr, SSENSE — self-explanatory from the role title).

**CL-13 — Partial work is framed honestly without flagging the exit.** "Built the foundation of" (then layoffs), "Designed... and implemented the foundational pieces" — own what was done without overclaiming. "My role was eliminated" is fine; "a layoff" when it was only you is misleading.

**CL-14 — The docx professional summary is the anchor.** It names every industry, specialization, and scale signal. If an industry domain appears in role summaries but not in the professional summary at the top, it's effectively invisible to a 30-second scan. When adding an industry to role summaries, check whether the professional summary needs it too.

**CL-15 — Docx suggestions are always full sentences or full paragraphs.** Never suggest a fragment like "change X to Y" for the docx. Provide the complete replacement text so the user can copy-paste it regardless of whether their document was saved, dirty, or in an intermediate state. Assume the document on disk may not match the last extraction.

**CL-16 — Bio.json is the voice source for the docx professional summary.** `_data/bio.json`'s `summary` and `summaryLong` fields are the canonical source for the industries, years of experience, and core value proposition that the docx professional summary must reflect. They use different tones (bio.json is first-person casual; docx is third-person professional) but must agree on: industries listed, years of experience, specializations, and the career narrative.

**CL-17 — Earlier Experience conventions.** The docx condenses 4+ older roles into a single paragraph in forward-chronological order (oldest company first) with no bullets. The paragraph names the companies, industries, and types of contributions. Resume.json keeps each older role as a separate summary-only entry. These are equivalent representations; they don't need per-bullet parity.

**CL-18 — Parenthetical context in docx headers.** Acquisition context like "(Shopify sold its logistics division to Flexport)" or "(Shopify acquired Deliverr)" only lives in the docx headers. Resume.json has no equivalent field — the acquisition context is implicit in the role summaries. The docx headers are the canonical place for this signal.

**CL-19 — Per-role titles are factual, not harmonized.** `basics.label` is the harmonized umbrella identity. Each work entry's `position` preserves the actual title the company granted, even if it varies across roles (Principal at Octav, Staff at Shopify, Senior Staff at Flexport). The label attracts the search; the work entries prove the trajectory.

## Cross-file consistency

Three files share the career narrative and must stay in sync on facts (tone varies by audience):

| File | Field(s) | Tone | Audience |
|---|---|---|---|
| `resume.json` | `basics.summary` | Professional, third-person | ATS, recruiters, JSON Resume consumers |
| `_data/bio.json` | `basics.summary`, `basics.summaryLong` | Casual, first-person | Website visitors (`/resume.html`) |
| `.docx` | Professional summary paragraph | Professional, third-person | ATS, recruiters, PDF readers |

All three must agree on: job titles, industry domains, years of experience, technology keywords, and core specializations. When updating the industry list or career narrative in any of these files, check the other two.

`resume.json` and `_data/bio.json` also share `basics.label`, `interests`, and `skills`. Different tones but same facts.
