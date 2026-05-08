from amelie_md.renderers.components.html_blocks import render_code_block


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
