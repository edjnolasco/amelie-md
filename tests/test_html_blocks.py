from amelie_md.renderers.components.html_blocks import (
    render_code_block,
    render_heading_block,
    render_list,
    render_list_item,
    render_toc,
    render_toc_item,
)


def test_render_code_block_escapes_html():
    block = {"type": "code", "code": "x < y && y > z"}

    html = render_code_block(
        block,
        lambda text: (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        ),
    )

    assert html == "<pre><code>x &lt; y &amp;&amp; y &gt; z</code></pre>"


def test_render_code_block_returns_empty_for_blank_code():
    assert render_code_block({"type": "code", "code": ""}, lambda text: text) == ""


def test_render_heading_block_with_anchor():
    html = render_heading_block(2, "1. Título", "1-titulo")

    assert html == '<h2 id="1-titulo">1. Título</h2>'


def test_render_heading_block_clamps_level():
    html = render_heading_block(9, "Título", "titulo")

    assert html == '<h6 id="titulo">Título</h6>'


def test_render_list_item():
    html = render_list_item(
        "**bold**",
        lambda text: f"<strong>{text[2:-2]}</strong>",
    )

    assert html == "<li><strong>bold</strong></li>"


def test_render_unordered_list():
    html = render_list(
        ["<li>A</li>", "<li>B</li>"],
        ordered=False,
    )

    assert '<ul class="amelie-list">' in html
    assert "<li>A</li>" in html
    assert "<li>B</li>" in html


def test_render_ordered_list():
    html = render_list(
        ["<li>A</li>", "<li>B</li>"],
        ordered=True,
    )

    assert '<ol class="amelie-list">' in html


def test_render_toc_item():
    html = render_toc_item(
        2,
        "1. Introducción",
        "1-introduccion",
    )

    assert 'class="toc-level-2"' in html
    assert 'href="#1-introduccion"' in html


def test_render_toc():
    html = render_toc(
        [
            '<li class="toc-level-1">A</li>',
            '<li class="toc-level-2">B</li>',
        ]
    )

    assert '<ul class="amelie-toc">' in html
    assert "toc-level-1" in html
    assert "toc-level-2" in html
