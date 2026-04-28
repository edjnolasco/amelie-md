---
title: "Code Highlighting Test"
author: "Edwin José Nolasco"
date: "2026-04-27"
---

# Python

```python
from pathlib import Path

def build_document(input_path: Path) -> str:
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    return input_path.read_text(encoding="utf-8")