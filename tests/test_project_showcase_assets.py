from pathlib import Path


def test_project_showcase_assets_exist():
    base = Path("examples/project_showcase")

    assert (base / "amelie.toml").exists()
    assert (base / "references.json").exists()
    assert (base / "chapters" / "01_intro.md").exists()
    assert (base / "chapters" / "02_architecture.md").exists()
    assert (base / "chapters" / "03_references.md").exists()


def test_project_showcase_contains_project_markers():
    base = Path("examples/project_showcase")
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((base / "chapters").glob("*.md"))
    )

    assert "{{ref:def-project}}" in combined
    assert "{{ref:fig-project-structure}}" in combined
    assert "[@amelie2026]" in combined
    assert "[[BIBLIOGRAPHY]]" in combined
