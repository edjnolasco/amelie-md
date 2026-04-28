from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from charset_normalizer import from_bytes


@dataclass(frozen=True)
class DecodedText:
    text: str
    encoding: str
    confidence: float


def read_text_with_encoding_detection(path: Path) -> DecodedText:
    raw = path.read_bytes()
    result = from_bytes(raw).best()

    if result is None:
        return DecodedText(
            text=raw.decode("utf-8", errors="replace"),
            encoding="utf-8",
            confidence=0.0,
        )

    encoding = result.encoding or "utf-8"

    return DecodedText(
        text=str(result),
        encoding=encoding,
        confidence=float(result.percent_coherence or 0.0),
    )