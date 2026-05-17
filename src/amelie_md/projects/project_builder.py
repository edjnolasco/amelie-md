from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from amelie_md.projects.project_config import (
    AmelieProjectConfig,
    load_project_config,
)
from amelie_md.projects.project_loader import load_project_markdown


@dataclass(slots=True)
class LoadedAmelieProject:
    project_dir: Path
    config: AmelieProjectConfig
    markdown: str
    references_path: Path | None


def load_project(project_dir: str | Path) -> LoadedAmelieProject:
    project_path = Path(project_dir)

    config = load_project_config(project_path)
    markdown = load_project_markdown(project_path)

    references_path = project_path / "references.json"

    if not references_path.exists():
        references_path = None

    return LoadedAmelieProject(
        project_dir=project_path,
        config=config,
        markdown=markdown,
        references_path=references_path,
    )
