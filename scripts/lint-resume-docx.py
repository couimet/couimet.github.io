#!/usr/bin/env python3
"""Lint a formatted .docx resume against resume.json for discrepancies.

Flags typos, date mismatches, missing content, double punctuation, extra
whitespace, and structural issues. Uses python-docx to extract text directly
from the .docx file.
"""

import argparse
import json
import re
import sys
from calendar import month_abbr
from difflib import SequenceMatcher
from pathlib import Path

import docx

MONTH_ABBR = list(month_abbr)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_resume(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def extract_docx_text(path: Path) -> tuple[str, list[str]]:
    """Return (full_text, paragraphs) from a .docx file."""
    doc = docx.Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs), paragraphs


def best_match(needle: str, paragraphs: list[str]) -> tuple[float, str]:
    """Return (similarity, best_paragraph) for *needle* against each paragraph.

    Similarity is 0.0–1.0. A score >= 0.95 means essentially identical;
    >= 0.70 is a plausible fuzzy match; < 0.70 means likely missing.
    """
    needle_lower = needle.lower().strip()
    best_score = 0.0
    best_para = ""
    for para in paragraphs:
        para_lower = para.lower().strip()
        if not para_lower:
            continue
        # Fast path: exact substring — but only if the shorter string is at
        # least 50% the length of the longer one. Otherwise short labels like
        # "Senior Developer" would falsely match highlights that mention them.
        shorter = min(len(needle_lower), len(para_lower))
        longer = max(len(needle_lower), len(para_lower))
        if shorter / longer >= 0.5:
            if needle_lower in para_lower or para_lower in needle_lower:
                return (1.0, para)
        # Slow path: SequenceMatcher on the whole strings
        score = SequenceMatcher(None, needle_lower, para_lower).ratio()
        if score > best_score:
            best_score = score
            best_para = para
    return (best_score, best_para)


def fmt_date_iso(iso: str) -> str:
    """Convert '2025-08-01' to 'Aug 2025'."""
    y, m, _ = iso.split("-")
    return f"{MONTH_ABBR[int(m)]} {y}"


# ---------------------------------------------------------------------------
# Lint checks
# ---------------------------------------------------------------------------

WARNINGS: list[str] = []


def warn(msg: str) -> None:
    WARNINGS.append(msg)


def check_name_contact(data: dict, text: str) -> None:
    basics = data["basics"]
    name = basics["name"]
    if name not in text:
        warn(f"Name '{name}' not found in docx")
    email = basics.get("email", "")
    if email and email not in text:
        warn(f"Email '{email}' not found in docx")
    phone = basics.get("phone", "")
    if phone and phone not in text:
        warn(f"Phone '{phone}' not found in docx")
    url = basics.get("url", "")
    if url and url.replace("https://", "") not in text:
        warn(f"URL '{url}' not found in docx")


def check_company_names(data: dict, text: str) -> None:
    marker_indices = [i for i, w in enumerate(data.get("work", [])) if w.get("docxLastRoleBeforeEarlierExperience")]
    cutoff = marker_indices[0] if marker_indices else len(data["work"])
    for w in data["work"][: cutoff + 1]:
        name = w["name"]
        if name not in text:
            warn(f"Company '{name}' not found in docx")


def check_position_titles(data: dict, text: str) -> None:
    marker_indices = [i for i, w in enumerate(data.get("work", [])) if w.get("docxLastRoleBeforeEarlierExperience")]
    cutoff = marker_indices[0] if marker_indices else len(data["work"])
    for w in data["work"][: cutoff + 1]:
        pos = w["position"]
        if pos not in text:
            warn(f"Position '{pos}' not found in docx")


def check_date_ranges(data: dict, text: str) -> None:
    marker_indices = [i for i, w in enumerate(data.get("work", [])) if w.get("docxLastRoleBeforeEarlierExperience")]
    cutoff = marker_indices[0] if marker_indices else len(data["work"])
    for w in data["work"][: cutoff + 1]:
        start = fmt_date_iso(w["startDate"])
        end = fmt_date_iso(w["endDate"]) if w.get("endDate") else "Present"
        if start not in text:
            warn(f"Start date '{start}' for {w['name']} not found in docx")
        if end != "Present" and end not in text:
            warn(f"End date '{end}' for {w['name']} not found in docx")


def check_highlights(data: dict, paragraphs: list[str]) -> None:
    marker_indices = [i for i, w in enumerate(data.get("work", [])) if w.get("docxLastRoleBeforeEarlierExperience")]
    cutoff = marker_indices[0] if marker_indices else len(data["work"])
    for w in data["work"][: cutoff + 1]:
        for h in w.get("highlights", []):
            score, best = best_match(h, paragraphs)
            if score >= 0.995:
                continue  # essentially identical
            if score >= 0.95:
                warn(
                    f"Highlight for {w['name']} has minor difference (similarity {score:.1%}):\n"
                    f"  resume.json: \"{h}\"\n"
                    f"  docx:        \"{best}\""
                )
            elif score >= 0.70:
                warn(
                    f"Highlight for {w['name']} may be edited (similarity {score:.0%}):\n"
                    f"  resume.json: \"{h}\"\n"
                    f"  docx:        \"{best}\""
                )
            else:
                warn(f"Highlight for {w['name']} may be missing (similarity {score:.0%}): \"{h}\"")


def check_earlier_experience_cutoff(data: dict, paragraphs: list[str]) -> None:
    marker_indices = [i for i, w in enumerate(data.get("work", [])) if w.get("docxLastRoleBeforeEarlierExperience")]
    if not marker_indices:
        return
    cutoff = marker_indices[0]
    earlier = data["work"][cutoff + 1 :]
    for w in earlier:
        for h in w.get("highlights", []):
            score, _ = best_match(h, paragraphs)
            if score >= 0.95:
                warn(
                    f"Earlier Experience role '{w['name']}' may have full bullets in docx "
                    f"(found highlight matching: \"{h[:60]}...\")"
                )


def check_sections(text: str) -> None:
    text_lower = text.lower()
    required = [
        ("technical skills", "Technical Skills"),
        ("work experience", "Work Experience"),
        ("experience", "Work Experience"),
        ("earlier experience", "Earlier Experience"),
        ("education", "Education"),
    ]
    seen: set[str] = set()
    for pattern, label in required:
        if pattern in text_lower:
            seen.add(label)
    # At least one of "Work Experience" or "Experience" must be present
    for label in {"Technical Skills", "Earlier Experience", "Education"}:
        if label not in seen:
            warn(f"Required section '{label}' not found in docx")
    if "Work Experience" not in seen:
        warn("Required section 'Work Experience' (or 'Experience') not found in docx")


def check_double_punctuation(text: str) -> None:
    for pattern, label in [
        (r"\.\.", "double period"),
        (r",,", "double comma"),
        (r"--(?!\d)", "double dash (outside date range)"),
    ]:
        for m in re.finditer(pattern, text):
            ctx = text[max(0, m.start() - 20): m.end() + 20]
            warn(f"Double punctuation ({label}): \"...{ctx}...\"")


def check_whitespace(text: str) -> None:
    for i, line in enumerate(text.splitlines(), 1):
        if line.endswith(" ") or line.endswith("\t"):
            snippet = line.strip()[-60:] if len(line.strip()) > 60 else line.strip()
            warn(f"Trailing whitespace on line {i}: \"...{snippet}\"")
        # Skip the contact-info line (contains phone numbers, emails, URLs
        # separated by spaces rather than middle dots)
        if "@" in line and "514" in line:
            continue
        if "  " in line and "·" not in line:
            for m in re.finditer(r"(?<![\.\,\:\;])  (?![\.,\;:])", line):
                ctx = line[max(0, m.start() - 10): m.end() + 10]
                warn(f"Double space on line {i}: \"...{ctx}...\"")


def check_certificates_awards(data: dict, text: str) -> None:
    for cert in data.get("certificates", []):
        if cert.get("docxSkip"):
            continue
        if cert["name"] not in text:
            warn(f"Certificate '{cert['name']}' not found in docx")
    for award in data.get("awards", []):
        if award.get("docxSkip"):
            continue
        if award["title"] not in text:
            warn(f"Award '{award['title']}' not found in docx")
    for proj in data.get("projects", []):
        if proj.get("docxSkip"):
            continue
        if proj["name"] not in text:
            warn(f"Project '{proj['name']}' not found in docx")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def lint_docx(docx_path: Path, resume_data: dict) -> list[str]:
    global WARNINGS
    WARNINGS = []
    text, paragraphs = extract_docx_text(docx_path)

    checks = [
        ("name & contact", lambda: check_name_contact(resume_data, text)),
        ("company names", lambda: check_company_names(resume_data, text)),
        ("position titles", lambda: check_position_titles(resume_data, text)),
        ("date ranges", lambda: check_date_ranges(resume_data, text)),
        ("highlights", lambda: check_highlights(resume_data, paragraphs)),
        ("earlier experience cutoff", lambda: check_earlier_experience_cutoff(resume_data, paragraphs)),
        ("sections", lambda: check_sections(text)),
        ("double punctuation", lambda: check_double_punctuation(text)),
        ("whitespace", lambda: check_whitespace(text)),
        ("certificates & awards", lambda: check_certificates_awards(resume_data, text)),
    ]
    for label, fn in checks:
        before = len(WARNINGS)
        fn()
        after = len(WARNINGS)
        found = after - before
        if found:
            print(f"  {label}: {found} warning(s)", file=sys.stderr)
    print(f"  {len(checks)} checks run", file=sys.stderr)

    return WARNINGS


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lint a formatted .docx resume against resume.json"
    )
    parser.add_argument(
        "docx",
        help="Path to the formatted .docx resume file",
    )
    parser.add_argument(
        "--resume",
        default="resume.json",
        help="Path to resume.json (default: resume.json)",
    )
    args = parser.parse_args()

    docx_path = Path(args.docx)
    if not docx_path.exists():
        print(f"ERROR: {docx_path} not found", file=sys.stderr)
        sys.exit(1)

    resume_path = Path(args.resume)
    if not resume_path.exists():
        print(f"ERROR: {resume_path} not found", file=sys.stderr)
        sys.exit(1)

    data = load_resume(resume_path)
    warnings = lint_docx(docx_path, data)

    if warnings:
        for w in warnings:
            print(f"WARNING: {w}")
        print(f"\n{warnings.__len__()} warning(s) found.")
        sys.exit(1)
    else:
        print("No issues found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
