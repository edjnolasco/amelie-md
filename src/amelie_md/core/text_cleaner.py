from __future__ import annotations

import ftfy


def repair_text_encoding(text: str) -> str:
    import ftfy
    import re

    fixed = ftfy.fix_text(text)

    # eliminar basura unicode agresivamente
    fixed = re.sub(r"[\uFFFE\uFFFF]", "", fixed)

    # eliminar caracteres invisibles problemáticos
    fixed = fixed.replace("￾", "")

    return fixed