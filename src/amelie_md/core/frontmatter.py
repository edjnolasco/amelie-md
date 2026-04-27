from __future__ import annotations

from typing import Any

import yaml


def parse_frontmatter(markdown_text: str) -> tuple[dict[str, Any], str]:
    if not markdown_text.startswith("---"):
        return {}, markdown_text

    parts = markdown_text.split("---", 2)

    if len(parts) != 3:
        return {}, markdown_text

    _, yaml_block, content = parts

    try:
        metadata = yaml.safe_load(yaml_block) or {}
    except yaml.YAMLError:
        metadata = {}

    if not isinstance(metadata, dict):
        metadata = {}

    return metadata, content.strip()