from __future__ import annotations


from amelie_md.renderers.components.html_blocks import (
    render_admonition_block,
    render_code_block,
    render_paragraph,
)
from amelie_md.renderers.registry import RendererRegistry


def build_html_registry(
    *,
    render_inline,
    render_table,
    escape_html,
) -> RendererRegistry:
    registry = RendererRegistry()

    registry.register(
        "paragraph",
        lambda block: render_paragraph(
            block,
            render_inline,
        ),
    )

    registry.register(
        "code",
        lambda block: render_code_block(
            block,
            escape_html,
        ),
    )

    registry.register(
        "table",
        lambda block: render_table(
            block.get("rows", []),
        ),
    )

    registry.register(
        "admonition",
        lambda block: render_admonition_block(
            block,
            render_inline,
        ),
    )

    return registry
