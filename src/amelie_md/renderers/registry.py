# src/amelie_md/renderers/registry.py

from __future__ import annotations

from collections.abc import Callable
from typing import Any


BlockRenderer = Callable[[dict[str, Any]], str]


class RendererRegistry:
    def __init__(self) -> None:
        self._registry: dict[str, BlockRenderer] = {}

    def register(self, block_type: str, renderer: BlockRenderer) -> None:
        block_type = block_type.strip()

        if not block_type:
            raise ValueError("Block type cannot be empty.")

        if block_type in self._registry:
            raise ValueError(f"Renderer already registered for '{block_type}'")

        self._registry[block_type] = renderer

    def get(self, block_type: str) -> BlockRenderer:
        block_type = block_type.strip()

        if block_type not in self._registry:
            raise ValueError(f"No renderer registered for '{block_type}'")

        return self._registry[block_type]

    def has(self, block_type: str) -> bool:
        return block_type.strip() in self._registry