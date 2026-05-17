from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(slots=True)
class AmelieProjectConfig:
    title: str = "Untitled Project"
    author: str = ""
    theme: str = "academic"


def load_project_config(project_dir: str | Path) -> AmelieProjectConfig:
    project_path = Path(project_dir)
    config_path = project_path / "amelie.toml"

    if not config_path.exists():
        return AmelieProjectConfig()

    data = tomllib.loads(config_path.read_text(encoding="utf-8"))

    return AmelieProjectConfig(
        title=str(data.get("title", "Untitled Project")).strip(),
        author=str(data.get("author", "")).strip(),
        theme=str(data.get("theme", "academic")).strip(),
    )
