import importlib
import sys
import unittest
from pathlib import Path

SCRIPT_DIR = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, SCRIPT_DIR)

_mod = importlib.import_module("extract-resume-linkedin")
build_awards = _mod.build_awards
build_about = _mod.build_about
build_education = _mod.build_education
build_experience = _mod.build_experience
build_headline = _mod.build_headline
build_output = _mod.build_output
build_projects = _mod.build_projects
build_skills = _mod.build_skills
build_volunteer = _mod.build_volunteer
emit_section = _mod.emit_section
fmt_date_range = _mod.fmt_date_range
load_resume = _mod.load_resume


class TestFmtDateRange(unittest.TestCase):
    def test_with_end_date(self):
        self.assertEqual(
            fmt_date_range("2025-08-01", "2026-05-01"), "Aug 2025 – May 2026"
        )

    def test_present(self):
        self.assertEqual(fmt_date_range("2025-02-01", None), "Feb 2025 – Present")

    def test_same_year(self):
        self.assertEqual(
            fmt_date_range("2023-01-01", "2023-12-01"), "Jan 2023 – Dec 2023"
        )


class TestEmitSection(unittest.TestCase):
    def test_emits_header_and_blank_line(self):
        out: list[str] = []
        emit_section(out, "Headline")
        self.assertEqual(out, ["# Headline", ""])


class TestLoadResume(unittest.TestCase):
    def test_loads_valid_json(self):
        data = load_resume(Path(SCRIPT_DIR) / ".." / "resume.json")
        self.assertIn("basics", data)
        self.assertIn("work", data)

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_resume(Path("/nonexistent/path.json"))


class TestBuildHeadline(unittest.TestCase):
    def setUp(self):
        self.data = {"basics": {"label": "Staff Developer"}}

    def test_outputs_section_header_and_label(self):
        result = build_headline(self.data)
        self.assertIn("# Headline", result)
        self.assertIn("Staff Developer", result)

    def test_ends_with_blank_line(self):
        result = build_headline(self.data)
        self.assertEqual(result[-1], "")


class TestBuildAbout(unittest.TestCase):
    def setUp(self):
        self.data = {"basics": {"summary": "Experienced developer."}}

    def test_outputs_section_header_and_summary(self):
        result = build_about(self.data)
        self.assertIn("# About", result)
        self.assertIn("Experienced developer.", result)

    def test_replaces_literal_backslash_n_with_real_newlines(self):
        self.data["basics"]["summary"] = "Line one.\\nLine two."
        result = build_about(self.data)
        joined = "\n".join(result)
        self.assertIn("Line one.\nLine two.", joined)
        self.assertNotIn("\\n", joined)


class TestBuildExperience(unittest.TestCase):
    def setUp(self):
        self.data = {
            "work": [
                {
                    "name": "Acme Corp",
                    "position": "Senior Developer",
                    "startDate": "2020-01-01",
                    "endDate": "2023-06-01",
                    "summary": "Built great things.",
                    "highlights": ["Shipped feature X", "Mentored juniors"],
                },
                {
                    "name": "Startup Inc",
                    "position": "Developer",
                    "startDate": "2018-03-01",
                    "endDate": "2019-12-01",
                    "highlights": ["Built MVP"],
                },
            ]
        }

    def test_outputs_section_header(self):
        result = build_experience(self.data)
        self.assertIn("# Experience", result)

    def test_includes_all_roles_no_cutoff(self):
        result = build_experience(self.data)
        joined = "\n".join(result)
        self.assertIn("Acme Corp", joined)
        self.assertIn("Startup Inc", joined)

    def test_each_role_has_position_as_section_header(self):
        result = build_experience(self.data)
        self.assertIn("## Senior Developer", result)
        self.assertIn("## Developer", result)

    def test_includes_company_and_dates(self):
        result = build_experience(self.data)
        self.assertIn("Acme Corp, Jan 2020 – Jun 2023", result)

    def test_includes_summary_when_present(self):
        result = build_experience(self.data)
        self.assertIn("Built great things.", result)

    def test_includes_highlights(self):
        result = build_experience(self.data)
        self.assertIn("Shipped feature X", result)
        self.assertIn("Mentored juniors", result)

    def test_no_bullet_prefix_on_highlights(self):
        result = build_experience(self.data)
        for line in result:
            if line.startswith("#"):
                continue
            stripped = line.lstrip()
            self.assertFalse(
                stripped.startswith(("•", "-", "*")),
                f"Line has bullet prefix: {line!r}",
            )

    def test_role_without_summary_still_renders(self):
        result = build_experience(self.data)
        joined = "\n".join(result)
        self.assertIn("Startup Inc", joined)

    def test_ignores_docxLastRoleBeforeEarlierExperience_marker(self):
        self.data["work"][0]["docxLastRoleBeforeEarlierExperience"] = True
        result = build_experience(self.data)
        joined = "\n".join(result)
        self.assertIn("Acme Corp", joined)
        self.assertIn("Startup Inc", joined)
        # No Earlier Experience section
        self.assertNotIn("Earlier Experience", joined)

    def test_empty_work_list(self):
        result = build_experience({"work": []})
        self.assertIn("# Experience", result)


class TestBuildSkills(unittest.TestCase):
    def setUp(self):
        self.data = {
            "skills": [
                {"name": "Backend", "keywords": ["Python", "TypeScript"]},
                {"name": "Frontend", "keywords": ["React"]},
            ]
        }

    def test_outputs_section_header(self):
        result = build_skills(self.data)
        self.assertIn("# Skills", result)

    def test_outputs_all_categories(self):
        result = build_skills(self.data)
        joined = "\n".join(result)
        self.assertIn("Backend: Python, TypeScript", joined)
        self.assertIn("Frontend: React", joined)

    def test_empty_skills(self):
        result = build_skills({"skills": []})
        self.assertIn("# Skills", result)


class TestBuildEducation(unittest.TestCase):
    def setUp(self):
        self.data = {
            "education": [
                {
                    "institution": "UQAM",
                    "area": "Computer Science",
                    "studyType": "Bachelor",
                    "startDate": "1997-09-01",
                    "endDate": "2001-06-01",
                }
            ],
            "certificates": [
                {
                    "name": "AWS Certified",
                    "date": "2019-01-01",
                    "issuer": "AWS",
                },
                {
                    "name": "Claude 101",
                    "date": "2026-06-01",
                    "issuer": "Anthropic",
                    "docxSkip": True,
                },
            ],
        }

    def test_outputs_section_header(self):
        result = build_education(self.data)
        self.assertIn("# Education", result)

    def test_formats_education_entry(self):
        result = build_education(self.data)
        self.assertIn("Computer Science, UQAM (2001)", result)

    def test_includes_non_skipped_certificates(self):
        result = build_education(self.data)
        joined = "\n".join(result)
        self.assertIn("AWS Certified, AWS (2019)", joined)

    def test_skips_docxSkip_certificates(self):
        result = build_education(self.data)
        joined = "\n".join(result)
        self.assertNotIn("Claude 101", joined)

    def test_skips_docxSkip_education(self):
        self.data["education"][0]["docxSkip"] = True
        result = build_education(self.data)
        joined = "\n".join(result)
        self.assertNotIn("UQAM", joined)

    def test_education_without_area(self):
        self.data["education"][0].pop("area")
        result = build_education(self.data)
        self.assertIn(", UQAM (2001)", result)

    def test_certificate_without_issuer(self):
        self.data["certificates"][0].pop("issuer")
        result = build_education(self.data)
        joined = "\n".join(result)
        self.assertIn("AWS Certified (2019)", joined)

    def test_certificate_without_date(self):
        self.data["certificates"][0].pop("date")
        result = build_education(self.data)
        joined = "\n".join(result)
        self.assertIn("AWS Certified, AWS ()", joined)


class TestBuildProjects(unittest.TestCase):
    def setUp(self):
        self.data = {
            "projects": [
                {
                    "name": "my-claude-skills",
                    "description": "A library of Claude Code skills.",
                    "url": "https://ouimet.info/projects/my-claude-skills.html",
                },
                {
                    "name": "Skipped Project",
                    "description": "Should not appear.",
                    "docxSkip": True,
                },
            ]
        }

    def test_outputs_section_header(self):
        result = build_projects(self.data)
        self.assertIn("# Projects", result)

    def test_includes_project_name_description_url(self):
        result = build_projects(self.data)
        joined = "\n".join(result)
        self.assertIn("my-claude-skills", result)
        self.assertIn("A library of Claude Code skills.", result)
        self.assertIn("https://ouimet.info/projects/my-claude-skills.html", joined)

    def test_skips_docxSkip_projects(self):
        result = build_projects(self.data)
        joined = "\n".join(result)
        self.assertNotIn("Skipped Project", joined)

    def test_project_without_description(self):
        self.data["projects"][0].pop("description")
        result = build_projects(self.data)
        self.assertIn("my-claude-skills", result)
        self.assertNotIn("A library of Claude Code skills.", "\n".join(result))

    def test_project_without_url(self):
        self.data["projects"][0].pop("url")
        result = build_projects(self.data)
        self.assertIn("my-claude-skills", result)
        self.assertNotIn("https://ouimet.info/projects/my-claude-skills.html", "\n".join(result))


class TestBuildVolunteer(unittest.TestCase):
    def setUp(self):
        self.data = {
            "volunteer": [
                {
                    "organization": "Escadron 96",
                    "position": "Volunteer",
                    "startDate": "2023-09-01",
                    "endDate": "2025-06-01",
                    "summary": "Supported weekly meetings.",
                },
                {
                    "organization": "Skipped Org",
                    "position": "Helper",
                    "startDate": "2020-01-01",
                    "docxSkip": True,
                },
            ]
        }

    def test_outputs_section_header(self):
        result = build_volunteer(self.data)
        self.assertIn("# Volunteer", result)

    def test_formats_volunteer_entry(self):
        result = build_volunteer(self.data)
        self.assertIn("Escadron 96 — Volunteer (Sep 2023 – Jun 2025)", result)

    def test_includes_summary_when_present(self):
        result = build_volunteer(self.data)
        self.assertIn("Supported weekly meetings.", result)

    def test_skips_docxSkip_entries(self):
        result = build_volunteer(self.data)
        joined = "\n".join(result)
        self.assertNotIn("Skipped Org", joined)

    def test_volunteer_without_summary(self):
        self.data["volunteer"][0].pop("summary")
        result = build_volunteer(self.data)
        self.assertIn("Escadron 96 — Volunteer (Sep 2023 – Jun 2025)", result)


class TestBuildAwards(unittest.TestCase):
    def setUp(self):
        self.data = {
            "awards": [
                {
                    "title": "Rookie Rockstar",
                    "date": "2022-06-01",
                    "awarder": "Deliverr",
                    "summary": "Highest-impact contribution.",
                },
                {
                    "title": "Skipped Award",
                    "date": "2020-01-01",
                    "docxSkip": True,
                },
            ]
        }

    def test_outputs_section_header(self):
        result = build_awards(self.data)
        self.assertIn("# Awards", result)

    def test_formats_award_entry(self):
        result = build_awards(self.data)
        self.assertIn("Rookie Rockstar, Deliverr (2022)", result)

    def test_includes_summary_when_present(self):
        result = build_awards(self.data)
        self.assertIn("Highest-impact contribution.", result)

    def test_skips_docxSkip_entries(self):
        result = build_awards(self.data)
        joined = "\n".join(result)
        self.assertNotIn("Skipped Award", joined)

    def test_award_without_awarder(self):
        self.data["awards"][0].pop("awarder")
        result = build_awards(self.data)
        self.assertIn("Rookie Rockstar (2022)", result)

    def test_award_without_summary(self):
        self.data["awards"][0].pop("summary")
        result = build_awards(self.data)
        self.assertIn("Rookie Rockstar, Deliverr (2022)", result)


class TestBuildOutput(unittest.TestCase):
    def test_includes_all_sections(self):
        data = load_resume(Path(SCRIPT_DIR) / ".." / "resume.json")
        output = build_output(data)
        for header in [
            "# Headline",
            "# About",
            "# Experience",
            "# Skills",
            "# Education",
            "# Projects",
            "# Volunteer",
            "# Awards",
        ]:
            with self.subTest(header=header):
                self.assertIn(header, output)

    def test_no_docx_only_sections(self):
        data = load_resume(Path(SCRIPT_DIR) / ".." / "resume.json")
        output = build_output(data)
        self.assertNotIn("# Header", output)
        self.assertNotIn("Keyword Sub-Tag", output)
        self.assertNotIn("Earlier Experience", output)
        self.assertNotIn("RANGELINK", output)

    def test_no_bullet_prefixes_anywhere(self):
        data = load_resume(Path(SCRIPT_DIR) / ".." / "resume.json")
        output = build_output(data)
        for line in output.split("\n"):
            stripped = line.lstrip()
            self.assertFalse(
                stripped.startswith("• ")
                or stripped.startswith("- ")
                or stripped.startswith("* "),
                f"Line has bullet prefix: {line!r}",
            )

    def test_all_work_entries_present(self):
        data = load_resume(Path(SCRIPT_DIR) / ".." / "resume.json")
        output = build_output(data)
        # All 10 companies, including those after the docxLastRoleBeforeEarlierExperience marker
        for company in [
            "Shopify",
            "Octav",
            "Flexport",
            "Shopify Logistics",
            "Deliverr",
            "SSENSE",
            "Zola",
            "AFS Technologies Inc.",
            "Vidéotron Ltée",
            "Markzware Software",
        ]:
            with self.subTest(company=company):
                self.assertIn(company, output)

    def test_claude_101_certificate_excluded(self):
        data = load_resume(Path(SCRIPT_DIR) / ".." / "resume.json")
        output = build_output(data)
        self.assertNotIn("Claude 101", output)

    def test_empty_data_minimal_output(self):
        data = {
            "basics": {"label": "Dev", "summary": ""},
            "work": [],
            "skills": [],
            "education": [],
            "certificates": [],
            "projects": [],
            "volunteer": [],
            "awards": [],
        }
        output = build_output(data)
        self.assertIn("# Headline", output)
        self.assertIn("# About", output)
        self.assertIn("# Experience", output)


if __name__ == "__main__":
    unittest.main()
