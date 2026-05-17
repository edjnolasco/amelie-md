from __future__ import annotations

from pathlib import Path


def load_project_markdown(project_dir: str | Path) -> str:
    project_path = Path(project_dir)

    chapters_dir = project_path / "chapters"

    if not chapters_dir.exists():
        raise FileNotFoundError("Project chapters directory not found.")

    chapter_files = sorted(chapters_dir.glob("*.md"))

    if not chapter_files:
        raise FileNotFoundError("No Markdown chapters found.")

    contents: list[str] = []

    for chapter in chapter_files:
        contents.append(
            chapter.read_text(encoding="utf-8").strip()
        )

    return "\n\n".join(contents).strip()
