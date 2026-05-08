from __future__ import annotations

import re

from amelie_md.core.inline import InlineRun


TOKEN_PATTERN = re.compile(
    r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\))"
)


def parse_inline(text: str) -> list[InlineRun]:
    if not text:
        return []

    runs: list[InlineRun] = []
    position = 0

    for match in TOKEN_PATTERN.finditer(text):
        start, end = match.span()

        if start > position:
            runs.append(InlineRun(text=text[position:start]))

        token = match.group(0)

        if token.startswith("**") and token.endswith("**"):
            runs.append(InlineRun(text=token[2:-2], bold=True))

        elif token.startswith("*") and token.endswith("*"):
            runs.append(InlineRun(text=token[1:-1], italic=True))

        elif token.startswith("`") and token.endswith("`"):
            runs.append(InlineRun(text=token[1:-1], code=True))

        elif token.startswith("["):
            label, url = _parse_link(token)
            runs.append(InlineRun(text=label, link=url))

        position = end

    if position < len(text):
        runs.append(InlineRun(text=text[position:]))

    return [run for run in runs if run.text]


def _parse_link(token: str) -> tuple[str, str]:
    match = re.match(r"\[([^\]]+)\]\(([^)]+)\)", token)

    if not match:
        return token, ""

    return match.group(1), match.group(2)