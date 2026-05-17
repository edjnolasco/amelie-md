from pathlib import Path


def test_academic_css_contains_semantic_citation_styles():
    css = Path("src/amelie_md/styles/academic.css").read_text(encoding="utf-8")

    assert ".semantic-citation" in css
    assert ".semantic-bibliography" in css


def test_report_css_contains_semantic_citation_styles():
    css = Path("src/amelie_md/styles/report.css").read_text(encoding="utf-8")

    assert ".semantic-citation" in css
    assert ".semantic-bibliography" in css
