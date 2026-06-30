"""Shared helpers for resume processing scripts.

Both ``extract-resume-text.py`` (text extraction) and ``lint-resume-docx.py``
(docx validation) consume ``resume.json`` and share date formatting, marker
validation, and cutoff logic.
"""

import sys
from calendar import month_abbr

MONTH_ABBR = list(month_abbr)  # ['', 'Jan', 'Feb', ..., 'Dec']


def fmt_date(iso: str) -> str:
    """Convert '2025-08-01' to 'Aug 2025'."""
    y, m, _ = iso.split("-")
    return f"{MONTH_ABBR[int(m)]} {y}"


def validate_marker(work: list[dict]) -> list[int]:
    """Return indices of entries with docxLastRoleBeforeEarlierExperience set.

    Raises SystemExit if more than one entry has the marker.
    """
    indices = [
        i for i, w in enumerate(work) if w.get("docxLastRoleBeforeEarlierExperience")
    ]
    if len(indices) > 1:
        names = [work[i]["name"] for i in indices]
        print(
            f"ERROR: multiple work entries have docxLastRoleBeforeEarlierExperience: {names}. "
            f"At most one entry may have this marker.",
            file=sys.stderr,
        )
        sys.exit(1)
    return indices


def get_cutoff(work: list[dict]) -> int:
    """Return the cutoff index for full-bullet vs earlier-experience roles.

    Validates the single-marker invariant before computing the cutoff.
    Returns ``len(work)`` if no marker is set (all roles get full treatment).
    """
    marker_indices = validate_marker(work)
    return marker_indices[0] if marker_indices else len(work)
