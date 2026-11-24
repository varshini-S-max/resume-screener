import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from screener import clean, load_skills, skill_gap

SKILLS = load_skills()


def gap(resume, job):
    return skill_gap(clean(resume), clean(job), SKILLS)


def test_clean_lowercases_and_strips_symbols():
    assert clean("Python, SQL!!  Git") == "python sql git"


def test_case_insensitive():
    matched, missing = gap("PYTHON and Sql", "Need python, SQL")
    assert matched == ["python", "sql"] and missing == []


def test_short_form_in_resume_matches_full_name_in_job():
    matched, _ = gap("Worked on ML projects", "Need machine learning")
    assert "machine learning" in matched


def test_full_name_in_resume_matches_short_form_in_job():
    matched, _ = gap("Strong in Machine Learning", "Need ML skills")
    assert "machine learning" in matched


def test_other_aliases():
    matched, _ = gap("JS, sklearn, Postgres, OOPs", "javascript, scikit-learn, postgresql, oop")
    assert {"javascript", "scikit-learn", "postgresql", "oop"} <= set(matched)


def test_missing_skill():
    matched, missing = gap("I know Python", "Need Python and Docker")
    assert matched == ["python"] and missing == ["docker"]


def test_java_does_not_match_javascript():
    matched, missing = gap("I know JavaScript", "Need Java")
    assert "java" in missing and "java" not in matched


def test_ai_not_matched_inside_words():
    matched, missing = gap("I maintain email servers", "Need AI")
    assert "artificial intelligence" in missing
