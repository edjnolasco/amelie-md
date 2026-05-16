from amelie_md.renderers.components.html_blocks import (
    render_semantic_definition,
    render_semantic_figure,
)


class MockBlock:
    def __init__(
        self,
        semantic_type=None,
        identifier=None,
        title=None,
        content=None,
    ):
        self.semantic_type = semantic_type
        self.identifier = identifier
        self.title = title
        self.content = content


def test_semantic_definition_html():
    block = MockBlock(
        semantic_type="definition",
        identifier="ai",
        title="Artificial Intelligence",
        content="AI content",
    )

    html = render_semantic_definition(block)

    assert "semantic-definition" in html
    assert "Artificial Intelligence" in html


def test_semantic_figure_html():
    block = MockBlock(
        semantic_type="figure",
        identifier="fig-1",
        title="Architecture",
        content="Figure content",
    )

    html = render_semantic_figure(block)

    assert "semantic-figure" in html
    assert "Architecture" in html
