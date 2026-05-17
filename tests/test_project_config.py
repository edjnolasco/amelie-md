from amelie_md.projects.project_config import (
    AmelieProjectConfig,
    load_project_config,
)


def test_load_project_config_defaults(tmp_path):
    config = load_project_config(tmp_path)

    assert isinstance(config, AmelieProjectConfig)
    assert config.title == "Untitled Project"
    assert config.theme == "academic"


def test_load_project_config_from_toml(tmp_path):
    config_file = tmp_path / "amelie.toml"

    config_file.write_text(
        """
title = "Research Paper"
author = "Edwin José Nolasco"
theme = "report"
""".strip(),
        encoding="utf-8",
    )

    config = load_project_config(tmp_path)

    assert config.title == "Research Paper"
    assert config.author == "Edwin José Nolasco"
    assert config.theme == "report"
