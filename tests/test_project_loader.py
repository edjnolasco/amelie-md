
from amelie_md.projects.project_loader import load_project_markdown


def test_load_project_markdown_orders_chapters(tmp_path):
    chapters = tmp_path / "chapters"
    chapters.mkdir()

    (chapters / "01_intro.md").write_text(
        "# Intro",
        encoding="utf-8",
    )

    (chapters / "02_results.md").write_text(
        "# Results",
        encoding="utf-8",
    )

    markdown = load_project_markdown(tmp_path)

    assert "# Intro" in markdown
    assert "# Results" in markdown
    assert markdown.index("# Intro") < markdown.index("# Results")
