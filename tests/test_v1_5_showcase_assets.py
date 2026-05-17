from pathlib import Path


def test_v1_5_showcase_assets_exist():
    base = Path("examples/v1_5_citations_crossrefs")

    assert (base / "paper.md").exists()
    assert (base / "references.json").exists()


def test_v1_5_showcase_contains_expected_markers():
    paper = Path("examples/v1_5_citations_crossrefs/paper.md").read_text(
        encoding="utf-8"
    )

    assert "{{ref:def-semantic-publishing}}" in paper
    assert "{{ref:fig-semantic-pipeline}}" in paper
    assert "[@vaswani2017]" in paper
    assert "[@knuth1984]" in paper
    assert "[[BIBLIOGRAPHY]]" in paper
