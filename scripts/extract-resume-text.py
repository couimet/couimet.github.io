#!/usr/bin/env python3
"""Extract plain text from resume.json for copy-paste into a formatted docx.

Sections are delimited by ``# `` comment headers. Bullet content is raw
newline-separated lines (no ``*`` or ``-`` prefix — docx styling handles that).

The ``docxLastRoleBeforeEarlierExperience`` boolean on a work entry marks the
cutoff between full-bullet roles and the Earlier Experience summary block.
"""

import argparse
import json
import sys
from calendar import month_abbr
from pathlib import Path

MONTH_ABBR = list(month_abbr)  # ['', 'Jan', 'Feb', ..., 'Dec']


def fmt_date(iso: str) -> str:
    """Convert '2025-08-01' to 'Aug 2025'."""
    y, m, _ = iso.split("-")
    return f"{MONTH_ABBR[int(m)]} {y}"


def fmt_date_range(start: str, end: str | None) -> str:
    """Format a start–end date range for display."""
    s = fmt_date(start)
    if end:
        return f"{s} – {fmt_date(end)}"
    return f"{s} – Present"


def load_resume(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def validate_marker(work: list[dict]) -> list[int]:
    """Return indices of entries with docxLastRoleBeforeEarlierExperience set.

    Raises SystemExit if more than one entry has the marker.
    """
    indices = [i for i, w in enumerate(work) if w.get("docxLastRoleBeforeEarlierExperience")]
    if len(indices) > 1:
        names = [work[i]["name"] for i in indices]
        print(
            f"ERROR: multiple work entries have docxLastRoleBeforeEarlierExperience: {names}. "
            f"At most one entry may have this marker.",
            file=sys.stderr,
        )
        sys.exit(1)
    return indices


def emit_section(out: list[str], title: str) -> None:
    out.append(f"# {title}")
    out.append("")


def emit_job_header(out: list[str], w: dict) -> None:
    dates = fmt_date_range(w["startDate"], w.get("endDate"))
    out.append(f"## {w['position']} — {w['name']} | {dates}")
    out.append("")


def emit_highlights(out: list[str], w: dict) -> None:
    for h in w.get("highlights", []):
        out.append(h)
    out.append("")


def build_header(data: dict) -> list[str]:
    out: list[str] = []
    basics = data["basics"]
    emit_section(out, "Header")
    out.append(f"{basics['name']} — {basics['label']}")
    contact_parts = []
    if basics.get("location"):
        loc = basics["location"]
        contact_parts.append(f"{loc['city']}, {loc['region']}")
    if basics.get("phone"):
        contact_parts.append(basics["phone"])
    if basics.get("email"):
        contact_parts.append(basics["email"])
    for p in basics.get("profiles", []):
        if p["network"] in ("LinkedIn",):
            contact_parts.append(p["url"])
    if basics.get("url"):
        contact_parts.append(basics["url"])
    out.append(" · ".join(contact_parts))
    out.append("")
    return out


def build_keywords(data: dict) -> list[str]:
    out: list[str] = []
    emit_section(out, "Keyword Sub-Tag")
    out.append(
        "Event-Driven Architecture · Monolith Decomposition · Observability · "
        "AI-Assisted Development"
    )
    out.append("")
    return out


def build_summary(data: dict) -> list[str]:
    out: list[str] = []
    emit_section(out, "Summary")
    out.append(data["basics"]["summary"])
    out.append("")
    return out


def build_skills(data: dict) -> list[str]:
    out: list[str] = []
    emit_section(out, "Technical Skills")
    for skill in data.get("skills", []):
        keywords = ", ".join(skill["keywords"])
        out.append(f"{skill['name']}: {keywords}")
    out.append("")
    return out


def build_work(data: dict) -> list[str]:
    out: list[str] = []
    emit_section(out, "Work Experience")
    work = data.get("work", [])
    marker_indices = validate_marker(work)
    cutoff = marker_indices[0] if marker_indices else len(work)

    # Full-bullet roles (up to and including the marker)
    for w in work[: cutoff + 1]:
        emit_job_header(out, w)
        emit_highlights(out, w)

    # Earlier Experience (everything after the marker)
    earlier = work[cutoff + 1 :]
    if earlier:
        years = sorted(
            {int(w["startDate"][:4]) for w in earlier}
            | {int(w["endDate"][:4]) for w in earlier if w.get("endDate")}
        )
        year_range = f"{min(years)}–{max(years)}"
        emit_section(out, f"Earlier Experience ({year_range})")
        out.append("[AI-generated narrative — see prompt template below this block]")
        out.append("")
        for w in earlier:
            dates = fmt_date_range(w["startDate"], w.get("endDate"))
            out.append(f"{w['position']} — {w['name']} | {dates}")
        out.append("")
        out.append(
            "[Copy the prompt below into Claude. First, create a RangeLink to the "
            "work entries in resume.json (select all lines from the first earlier role "
            "through the last), then replace RANGELINK in the prompt. Paste Claude's "
            "one-sentence output above this block and delete this instruction.]"
        )
        out.append("")
        out.append("---")
        out.append(
            "Given these earlier career roles from my resume.json (full context at "
            "RANGELINK), write a one-sentence summary for the Earlier Experience "
            "section of a staff-level backend developer resume. Mention the companies, "
            "roles, industries, and cross-cutting themes. Keep it under 280 characters. "
            "Style reference: \"Held senior backend engineering and architect roles at "
            "[companies], contributing to [industries] through [themes].\""
        )
        out.append("")
        out.append("Roles:")
        for w in earlier:
            dates = fmt_date_range(w["startDate"], w.get("endDate"))
            summary = w.get("summary", "")
            out.append(f"- {w['position']} at {w['name']} ({dates}): {summary}")
        out.append("---")
        out.append("")
    return out


def build_education(data: dict) -> list[str]:
    out: list[str] = []
    emit_section(out, "Education & Credentials")
    for edu in data.get("education", []):
        if edu.get("docxSkip"):
            continue
        area = edu.get("area", "")
        inst = edu["institution"]
        end_year = edu["endDate"][:4] if edu.get("endDate") else ""
        out.append(f"• {area}, {inst} ({end_year})")
    for cert in data.get("certificates", []):
        if cert.get("docxSkip"):
            continue
        issuer = f", {cert['issuer']}" if cert.get("issuer") else ""
        date = cert["date"][:4] if cert.get("date") else ""
        out.append(f"• {cert['name']}{issuer} ({date})")
    out.append("")
    return out


def build_volunteer(data: dict) -> list[str]:
    out: list[str] = []
    emit_section(out, "Volunteer")
    for v in data.get("volunteer", []):
        if v.get("docxSkip"):
            continue
        dates = fmt_date_range(v["startDate"], v.get("endDate"))
        out.append(f"• {v['organization']} — {v['position']} ({dates})")
        if v.get("summary"):
            out.append(f"{v['summary']}")
        out.append("")
    return out


def build_awards(data: dict) -> list[str]:
    out: list[str] = []
    emit_section(out, "Awards")
    for a in data.get("awards", []):
        if a.get("docxSkip"):
            continue
        awarder = f", {a['awarder']}" if a.get("awarder") else ""
        date = a["date"][:4] if a.get("date") else ""
        out.append(f"• {a['title']}{awarder} ({date})")
        if a.get("summary"):
            out.append(f"{a['summary']}")
        out.append("")
    return out


def build_projects(data: dict) -> list[str]:
    out: list[str] = []
    emit_section(out, "Personal Projects")
    for p in data.get("projects", []):
        if p.get("docxSkip"):
            continue
        out.append(f"• {p['name']}")
        if p.get("description"):
            out.append(f"{p['description']}")
        if p.get("url"):
            out.append(f"{p['url']}")
        out.append("")
    return out


def build_output(data: dict) -> str:
    sections: list[list[str]] = [
        build_header(data),
        build_keywords(data),
        build_summary(data),
        build_skills(data),
        build_work(data),
        build_education(data),
        build_volunteer(data),
        build_awards(data),
        build_projects(data),
    ]
    lines: list[str] = []
    for section in sections:
        lines.extend(section)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract resume.json content as plain text for docx copy-paste"
    )
    parser.add_argument(
        "--input",
        default="resume.json",
        help="Path to resume.json (default: resume.json)",
    )
    parser.add_argument(
        "--output",
        default="resume-docx-content.txt",
        help="Output path for the generated text file (default: resume-docx-content.txt)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    data = load_resume(input_path)
    output = build_output(data)

    output_path = Path(args.output)
    output_path.write_text(output)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
