from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import tomllib


@dataclass(slots=True)
class AmelieProjectConfig:
    title: str = "Untitled Project"
    author: str = ""
    date: str = ""
    subtitle: str = ""
    keywords: list[str] = field(default_factory=list)
    description: str = ""
    theme: str = "academic"


def _as_clean_string(value: object, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _as_string_list(value: object) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    return [str(value).strip()] if str(value).strip() else []


def load_project_config(project_dir: str | Path) -> AmelieProjectConfig:
    project_path = Path(project_dir)
    config_path = project_path / "amelie.toml"

    if not config_path.exists():
        return AmelieProjectConfig()

    data = tomllib.loads(config_path.read_text(encoding="utf-8"))

    return AmelieProjectConfig(
        title=_as_clean_string(data.get("title"), "Untitled Project"),
        author=_as_clean_string(data.get("author")),
        date=_as_clean_string(data.get("date")),
        subtitle=_as_clean_string(data.get("subtitle")),
        keywords=_as_string_list(data.get("keywords")),
        description=_as_clean_string(data.get("description")),
        theme=_as_clean_string(data.get("theme"), "academic"),
    )
