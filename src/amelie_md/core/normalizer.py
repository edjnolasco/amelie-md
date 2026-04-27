from __future__ import annotations

import re


HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$")


def normalize_headings(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    normalized_lines: list[str] = []

    last_level = 0

    for line in lines:
        match = HEADING_PATTERN.match(line)

        if not match:
            normalized_lines.append(line)
            continue

        heading_marks, heading_text = match.groups()
        current_level = len(heading_marks)

        if last_level == 0:
            normalized_level = current_level
        elif current_level > last_level + 1:
            normalized_level = last_level + 1
        else:
            normalized_level = current_level

        last_level = normalized_level
        normalized_lines.append(f"{'#' * normalized_level} {heading_text}")

    return "\n".join(normalized_lines)