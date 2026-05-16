from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InlineRun:
    text: str
    bold: bool = False
    italic: bool = False
    code: bool = False
    link: str | None = None