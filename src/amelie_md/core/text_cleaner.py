from __future__ import annotations

import ftfy


def repair_text_encoding(text: str) -> str:
    """
    Repair common mojibake / broken encoding issues.

    Examples:
    resoluci贸n -> resolución
    sem谩ntica -> semántica
    Rep煤blica -> República
    """

    return ftfy.fix_text(text)