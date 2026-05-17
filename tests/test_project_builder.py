from amelie_md.projects.project_builder import load_project


def test_load_project(tmp_path):
    chapters = tmp_path / "chapters"
    chapters.mkdir()

    (chapters / "01_intro.md").write_text(
        "# Intro",
        encoding="utf-8",
    )

    (tmp_path / "amelie.toml").write_text(
        """
title = "Test Project"
author = "Edwin José Nolasco"
theme = "academic"
""".strip(),
        encoding="utf-8",
    )

    (tmp_path / "references.json").write_text(
        "{}",
        encoding="utf-8",
    )

    project = load_project(tmp_path)

    assert project.config.title == "Test Project"
    assert "# Intro" in project.markdown
    assert project.references_path is not None
