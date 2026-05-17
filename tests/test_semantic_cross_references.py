from amelie_md.core.semantic_pipeline import prepare_semantic_blocks


def test_semantic_cross_reference_resolution():
    blocks = [
        {
            "type": "definition",
            "id": "def-ai",
            "title": "Artificial Intelligence",
            "text": "Definition body",
            "label": "Definition 1",
        },
        {
            "type": "paragraph",
            "text": "See {{ref:def-ai}} for details.",
        },
    ]

    prepared = prepare_semantic_blocks(
        blocks,
        html_links=True,
        inject_indexes=False,
    )

    paragraph = prepared[1]["text"]

    assert 'href="#def-ai"' in paragraph
    assert "Definition 1" in paragraph
