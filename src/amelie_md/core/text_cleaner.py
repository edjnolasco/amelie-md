from __future__ import annotations

import ftfy
import re


def repair_text_encoding(text: str) -> str:
    fixed = ftfy.fix_text(text)

    # limpieza agresiva
    fixed = re.sub(r"[\uFFFE\uFFFF]", "", fixed)
    fixed = fixed.replace("￾", "")

    return fixed