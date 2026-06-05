# Professional Portfolio

For details on this professional portfolio, please see https://ouimet.info.

## Local Development

See more details at https://techfolios.github.io/docs/user-guide/local-development.

Install dependencies:

```bash
rbenv install 3.1.4
rbenv local 3.1.4
bundle install
```

Run the server:

```bash
bundle exec jekyll serve
```

## Career Changelog

`_includes/career/changelog.html` is the source-of-truth narrative for my career experience, organized per role using the Keep-a-Changelog format. `resume.json:work[]` carries the compact, recruiter-facing distillation that the [Resume](#resume) pipeline converts into `resume.yml` and `resume-full.html`.

The intended editing flow is changelog-first: changes land in `_includes/career/changelog.html`, then the matching `resume.json:work[]` entry gets a synced summary and highlights per the "summary is a compact distillation of self-sufficient highlights" rule.

To enrich one role at a time, invoke the project-local skill:

```
/career-role-enrich <role-slug>
```

Slugs match the role's `resume.json:work[].name` field with lowercase + hyphenation: `ssense`, `deliverr`, `shopify-logistics`, `flexport`, `octav`, `shopify`.

The skill walks 7 phases: resolve target → audit → intake (via `/question`) → draft (via `/note`) → review iteration → apply edits → wrap up. Style conventions (additive `Use of X` rule, role-scoped IDs, role-voice) live in the `career-style` helper skill, auto-consulted during the draft phase.

Skill files (project-local):

- `.claude/skills/career-role-enrich/SKILL.md`
- `.claude/skills/career-style/SKILL.md`

### Catch-up: bootstrapping from the PDF (temporary)

The current `resume.json` was originally bootstrapped from a Word-authored resume PDF. Roles in the changelog are being back-ported from that PDF one at a time, treating it as the upstream source of truth until each role's narrative lives in `_includes/career/changelog.html` with the matching `resume.json:work[]` entry as a compact distillation.

For roles still in catch-up, the `/career-role-enrich` skill's audit phase performs a three-way comparison (PDF × changelog × resume) to surface gaps. Once all roles are migrated, this subsection can be deleted and the audit phase can simplify (PDF reference dropped).

Reference PRs:

- SSENSE: https://github.com/couimet/couimet.github.io/pull/65
- Deliverr: https://github.com/couimet/couimet.github.io/pull/67
- Shopify Logistics: TBD

## Resume

The resume pipeline converts `resume.json` (JSON Resume format) into `resume.yml` (YAMLResume) and `resume-full.html` (styled HTML). The conversion runs automatically when `resume.json` changes on `main`.

Run locally (requires Docker):

```bash
./scripts/sync-resume.sh
```

## Deployment

Pushes to `main` are automatically deployed to ouimet.info via `.github/workflows/deploy-ouimet-info.yml` (SSH keypair auth). See the workflow file header for required repository secrets.

The `scripts/sync-ouimet-info.sh` script is kept as a manual recovery tool for rollbacks and direct-from-release syncs.
