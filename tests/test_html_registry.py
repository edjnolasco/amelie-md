from amelie_md.renderers.html_registry import build_html_registry


def test_build_html_registry_registers_safe_blocks():
    registry = build_html_registry(
        render_inline=lambda text: text,
        render_table=lambda rows: "<table></table>" if rows else "",
        escape_html=lambda text: text,
    )

    assert registry.has("paragraph")
    assert registry.has("code")
    assert registry.has("table")
    assert registry.has("admonition")


def test_html_registry_renders_paragraph():
    registry = build_html_registry(
        render_inline=lambda text: text.upper(),
        render_table=lambda rows: "",
        escape_html=lambda text: text,
    )

    html = registry.get("paragraph")({"type": "paragraph", "text": "hello"})

    assert html == "<p>HELLO</p>"


def test_html_registry_renders_admonition():
    registry = build_html_registry(
        render_inline=lambda text: text,
        render_table=lambda rows: "",
        escape_html=lambda text: text,
    )

    html = registry.get("admonition")(
        {
            "type": "admonition",
            "kind": "note",
            "title": "Note",
            "text": "Content",
        }
    )

    assert "amelie-admonition-note" in html
    assert "Content" in html
