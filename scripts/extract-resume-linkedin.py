"""Extract sections from resume.json for copy-paste into LinkedIn profile fields.

Sections are delimited by ``# `` comment headers. Highlight lines are
prefixed with ``• `` for easy copy-paste into LinkedIn.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from resume_utils import fmt_date


def fmt_date_range(start: str, end: str | None) -> str:
    """Format a start–end date range for display."""
    s = fmt_date(start)
    if end:
        return f"{s} – {fmt_date(end)}"
    return f"{s} – Present"


def load_resume(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def emit_section(out: list[str], title: str) -> None:
    out.append(f"# {title}")
    out.append("")


def build_headline(data: dict) -> list[str]:
    out: list[str] = []
    emit_section(out, "Headline")
    out.append(data["basics"]["label"])
    out.append("")
    return out


def build_about(bio: dict) -> list[str]:
    out: list[str] = []
    emit_section(out, "About")
    for paragraph in bio["basics"]["summaryLong"]:
        out.append(paragraph)
        out.append("")
    return out


def build_experience(data: dict) -> list[str]:
    out: list[str] = []
    emit_section(out, "Experience")
    for w in data.get("work", []):
        dates = fmt_date_range(w["startDate"], w.get("endDate"))
        out.append(f"## {w['position']}")
        out.append(f"{w['name']}, {dates}")
        out.append("")
        if w.get("summary"):
            out.append(w["summary"])
            out.append("")
        for h in w.get("highlights", []):
            out.append(f"• {h}")
        out.append("")
    return out


def build_skills(data: dict) -> list[str]:
    out: list[str] = []
    emit_section(out, "Skills")
    for skill in data.get("skills", []):
        keywords = ", ".join(skill["keywords"])
        out.append(f"{skill['name']}: {keywords}")
    out.append("")
    return out


def build_education(data: dict) -> list[str]:
    out: list[str] = []
    emit_section(out, "Education")
    for edu in data.get("education", []):
        if edu.get("docxSkip"):
            continue
        area = edu.get("area", "")
        inst = edu["institution"]
        end_year = edu["endDate"][:4] if edu.get("endDate") else ""
        out.append(f"{area}, {inst} ({end_year})")
    for cert in data.get("certificates", []):
        if cert.get("docxSkip"):
            continue
        issuer = f", {cert['issuer']}" if cert.get("issuer") else ""
        date = cert["date"][:4] if cert.get("date") else ""
        out.append(f"{cert['name']}{issuer} ({date})")
    out.append("")
    return out


def build_projects(data: dict) -> list[str]:
    out: list[str] = []
    emit_section(out, "Projects")
    for p in data.get("projects", []):
        if p.get("docxSkip"):
            continue
        out.append(p["name"])
        if p.get("description"):
            out.append(p["description"])
        if p.get("url"):
            out.append(p["url"])
        out.append("")
    return out


def build_volunteer(data: dict) -> list[str]:
    out: list[str] = []
    emit_section(out, "Volunteer")
    for v in data.get("volunteer", []):
        if v.get("docxSkip"):
            continue
        dates = fmt_date_range(v["startDate"], v.get("endDate"))
        out.append(f"{v['organization']} — {v['position']} ({dates})")
        if v.get("summary"):
            out.append(v["summary"])
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
        out.append(f"{a['title']}{awarder} ({date})")
        if a.get("summary"):
            out.append(a["summary"])
        out.append("")
    return out


def build_output(data: dict, bio: dict) -> str:
    sections: list[list[str]] = [
        build_headline(data),
        build_about(bio),
        build_experience(data),
        build_skills(data),
        build_education(data),
        build_projects(data),
        build_volunteer(data),
        build_awards(data),
    ]
    lines: list[str] = []
    for section in sections:
        lines.extend(section)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract resume.json content as text for LinkedIn copy-paste"
    )
    parser.add_argument(
        "--input",
        default="resume.json",
        help="Path to resume.json (default: resume.json)",
    )
    parser.add_argument(
        "--output",
        default=f"resume-linkedin-content-{datetime.now(tz=timezone.utc).strftime('%Y%m%d-%H%M%S')}.txt",
        help="Output path for the generated text file (default: resume-linkedin-content-YYYYMMDD-HHMMSS.txt)",
    )
    parser.add_argument(
        "--bio",
        default=str(Path(__file__).resolve().parent.parent / "_data" / "bio.json"),
        help="Path to bio.json for the About section",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    bio_input = Path(args.bio)
    if not bio_input.exists():
        print(f"ERROR: {bio_input} not found", file=sys.stderr)
        sys.exit(1)

    data = load_resume(input_path)
    bio = load_resume(bio_input)
    output = build_output(data, bio)

    output_path = Path(args.output)
    output_path.write_text(output)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
